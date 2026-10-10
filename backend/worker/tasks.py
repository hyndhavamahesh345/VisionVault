import json  # noqa: F401
import time  # noqa: F401
from pathlib import Path
from celery import shared_task  # noqa: F401
from sqlalchemy.orm import Session

from config import logger, FRAMES_DIR, USE_HYBRID, OUTPUT_DIR  # noqa: F401
from worker.redis import celery_app
from storage.minio import download_video
from db.postgres import SessionLocal, Job, Inventory, Detection  # noqa: F401

from services.video.frame_extractor import extract_frames
from services.fusion.fusion_engine import (
    run_hybrid_pipeline,
    run_simulated_pipeline
)
from services.inventory.builder import merge_detections
from services.room.classifier import get_local_room_assignment


from typing import Optional

def update_job_status(
    db: Session,
    job_id: str,
    status: str,
    pipeline: Optional[str] = None,
    error: Optional[str] = None,
    frames_extracted: int = 0,
    frames_analyzed: int = 0
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job:
        job.status = status  # type: ignore
        if pipeline:
            job.pipeline = pipeline  # type: ignore
        if error:
            job.error = error  # type: ignore
        if frames_extracted:
            job.frames_extracted = frames_extracted  # type: ignore
        if frames_analyzed:
            job.frames_analyzed = frames_analyzed  # type: ignore
        db.commit()


def process_video_task(job_id: str, local_video_path: str):
    logger.info("[%s] Starting task for video: %s", job_id, local_video_path)
    db = SessionLocal()

    try:
        update_job_status(db, job_id, "extracting",
                          pipeline="extracting frames")
        frames = extract_frames(job_id, local_video_path)
        update_job_status(db, job_id, "extracting",
                          frames_extracted=len(frames))

        if not frames:
            update_job_status(db, job_id, "error", error="No frames extracted")
            return

        update_job_status(db, job_id, "analyzing")

        if USE_HYBRID:
            pipeline_name, all_detections = run_hybrid_pipeline(
                job_id, local_video_path, frames
            )
            flat_count = sum(len(f) for f in all_detections)
            if flat_count == 0:
                pipeline_name = "simulated fallback"
                all_detections = run_simulated_pipeline(job_id, frames)
        else:
            pipeline_name = "simulated"
            all_detections = run_simulated_pipeline(job_id, frames)

        update_job_status(
            db, job_id, "merging", pipeline=pipeline_name, frames_analyzed=len(frames)
        )

        inventory = merge_detections(all_detections)

        # Save to database
        for item in inventory:
            name = item.get("name", "")
            count = item.get("quantity", 0)
            room = get_local_room_assignment(name)

            db_inv = Inventory(job_id=job_id, room=room,
                               object=name, count=count)
            db.add(db_inv)

        update_job_status(db, job_id, "completed")
        db.commit()

    except Exception as e:
        logger.exception("[%s] ERROR in Celery task: %s", job_id, e)
        update_job_status(db, job_id, "error", error=str(e))
    finally:
        db.close()
        # Clean up local video file
        if Path(local_video_path).exists():
            Path(local_video_path).unlink()
