import uuid
import os
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session  # type: ignore

from config import logger, UPLOAD_DIR
from db.postgres import get_db, Job, Inventory, init_db
from worker.tasks import process_video_task

router = APIRouter()


@router.on_event("startup")
def startup_event():
    init_db()


@router.post("/api/upload")
async def upload_video_endpoint(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    allowed = [".mp4", ".mov", ".avi", ".mkv", ".webm"]
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Invalid file type.")

    job_id = str(uuid.uuid4())

    # Save locally
    local_path = UPLOAD_DIR / f"{job_id}{ext}"
    with open(local_path, "wb") as f:
        f.write(await file.read())

    # Create job in database
    new_job = Job(id=job_id, status="uploaded",
                  video_name=file.filename, pipeline="initializing")
    db.add(new_job)
    db.commit()

    # Dispatch Background Task instead of Celery
    background_tasks.add_task(process_video_task, job_id, str(local_path))

    return {"job_id": job_id, "message": "Processing started via Celery"}


@router.get("/api/status/{job_id}")
async def get_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job.id,
        "status": job.status,
        "video_name": job.video_name,
        "frames_extracted": job.frames_extracted,
        "frames_analyzed": job.frames_analyzed,
        "pipeline": job.pipeline,
        "error": job.error,
        "models": {"groundingdino": False},
    }


@router.get("/api/inventory/{job_id}")
async def get_inventory(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Not completed")

    items = db.query(Inventory).filter(Inventory.job_id == job_id).all()
    inventory_list = [
        {"name": item.object, "quantity": item.count, "room": item.room} for item in items]

    # Check for annotated frames in the static directory
    from config import ANNOTATED_DIR
    annotated_frames = []
    if ANNOTATED_DIR.exists():
        # Match files like {job_id}_0.jpg
        for file in sorted(ANNOTATED_DIR.glob(f"{job_id}_*.jpg")):
            # Build the URL path
            annotated_frames.append(f"/static/annotated/{file.name}")

    return {
        "job_id": job_id,
        "inventory": inventory_list,
        "annotated_frames": annotated_frames
    }
