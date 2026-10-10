# VisionVault 📦🔍

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.0-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev/)
[![YOLO-World](https://img.shields.io/badge/Ultralytics-YOLO--World-00FFFF?style=flat-square)](https://docs.ultralytics.com/models/yolo-world/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

**VisionVault** is an AI-driven video intelligence platform designed to scan walkthrough videos of homes, offices, or commercial spaces and automatically generate structured, itemized inventory lists grouped by room and category.

By combining open-vocabulary Vision-Language Models (Microsoft Florence-2), zero-shot object detection (Ultralytics YOLO-World v2), and intelligent temporal aggregation, VisionVault identifies furniture, appliances, electronics, and fixtures without manual tagging or tedious data entry.

---

## 🌟 Key Features

- **Dynamic Open-Vocabulary AI**: Uses **Microsoft Florence-2** (`<OD>`) on key frames to dynamically discover scene objects, injecting novel classes on-the-fly into **YOLO-World v2** (`yolov8x-worldv2.pt`) alongside a curated household taxonomy.
- **Adaptive Frame Sampling**: Dynamically samples video walkthroughs up to a maximum cap (60 frames), preventing processing bottlenecks and guaranteeing turnaround within ~2 minutes on standard hardware regardless of video length.
- **Quality-Aware Filtering**: Automatically drops blurry or unreadable frames using Laplacian variance heuristics to avoid inaccurate detections.
- **Deduplication & Spatial Aggregation**: Employs class-agnostic Non-Maximum Suppression (NMS) and cross-frame maximum instance tracking to prevent duplicate item counts caused by camera panning.
- **Automated Room & Category Mapping**: Maps identified objects into standard rooms (*Living Room, Bedroom, Kitchen, Bathroom, Hallway, Office*) via rule taxonomy and MobileNetV3 visual context.
- **Glassmorphic Interactive Dashboard**: A React frontend with live progress polling, search & filtering, annotated bounding-box inspection carousels, and single-click PDF export.

---

## 🏗️ System Architecture

```text
[Walkthrough Video]
        │
        ▼
[Frame Extractor (OpenCV)]  ──► Downscale to 640w & Cap at 60 Frames
        │
        ▼
[Quality Filter]            ──► Rejects motion blur via Laplacian variance
        │
        ▼
[Florence-2 VLM]            ──► Extracts scene-specific dynamic vocabulary
        │
        ▼
[Zero-Shot YOLO-World]      ──► Predicts objects using combined household vocabulary
        │
        ▼
[Tracking & Normalization]  ──► Canonical mapping, synonym merging & max instance counts
        │
        ▼
[Room & Category Classifier]──► Rule taxonomy + MobileNetV3 room categorization
        │
        ▼
[Dashboard & PDF Export]    ──► Real-time UI updates, annotated preview frames, and PDF
```

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, Vite, Tailwind CSS, Lucide Icons, jsPDF, Axios |
| **Backend API** | Python 3.9+, FastAPI, Uvicorn, SQLAlchemy |
| **Asynchronous Engine** | FastAPI BackgroundTasks (default standalone) / Celery + Redis |
| **Computer Vision / AI** | Ultralytics YOLO-World v2, Microsoft Florence-2, MobileNetV3, OpenCV, PyTorch |
| **Data & Blob Storage** | SQLite (default development) / PostgreSQL, Local filesystem / MinIO S3 |

---

## 📁 Project Structure

```text
VisionVault/
├── backend/
│   ├── api/                    # REST API endpoints & upload handlers
│   │   └── routes.py
│   ├── db/                     # Database schema & session management
│   │   └── postgres.py         # SQLAlchemy models (Jobs, Inventory, Detections)
│   ├── services/               # Core vision & processing services
│   │   ├── detection/          # YOLO-World, Florence-2 VLM, YOLO11s
│   │   ├── fusion/             # Multi-model hybrid inference engine
│   │   ├── inventory/          # Taxonomy, canonical normalization & merging
│   │   ├── room/               # Rule taxonomy & MobileNetV3 room classifier
│   │   ├── tracking/           # ByteTrack & object tracking algorithms
│   │   └── video/              # Frame extraction & quality filtering
│   ├── storage/                # MinIO S3 integration helpers
│   ├── worker/                 # Async task runner & Celery configuration
│   ├── config.py               # Application configuration & env vars
│   ├── main.py                 # FastAPI application entrypoint
│   └── requirements.txt        # Backend Python dependencies
├── frontend/                   # React + Vite web dashboard
│   ├── src/
│   │   ├── App.jsx             # Main dashboard, upload flow, table & viewer
│   │   ├── index.css           # Tailwind styling & glassmorphic theme
│   │   └── main.jsx            # React root
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml          # Optional Redis, MinIO, and PostgreSQL services
├── start_app.bat               # Windows one-click launcher (backend + frontend)
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- **Node.js**: v18+ and `npm`
- **Python**: 3.9+ (with CUDA support recommended for GPU acceleration)
- *(Optional)* **Docker Desktop** (only if using Celery, Redis, and MinIO in distributed mode)

---

### Quick Start (Windows)

Launch both backend and frontend servers simultaneously using the automated batch script:

```bat
start_app.bat
```

Once loaded:
- **Frontend Dashboard**: [http://localhost:5173](http://localhost:5173)
- **Backend API**: [http://localhost:8001](http://localhost:8001)
- **Swagger Documentation**: [http://localhost:8001/docs](http://localhost:8001/docs)

---

### Manual Setup

#### 1. Backend

1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. *(Optional)* Configure environment variables by copying `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Start the FastAPI server:
   ```bash
   python main.py
   ```
   *Server starts at `http://localhost:8001`.*

---

#### 2. Frontend

1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *Dashboard opens at `http://localhost:5173`.*

---

### Optional: Distributed Infrastructure (Docker)

If deploying with PostgreSQL, Redis, and MinIO enabled:

```bash
docker-compose up -d
```

- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`
- **MinIO S3**: `localhost:9000` (Console: `localhost:9001`)

To run the background worker via Celery:
```bash
cd backend
celery -A worker.tasks worker --loglevel=info --pool=solo
```

---

## 🔌 API Reference

### `POST /api/upload`
Uploads a video walkthrough file (`.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`) to begin processing.
- **Request**: Multipart form data with `file`
- **Response**:
  ```json
  {
    "job_id": "a3f4c21b-8c44-4829-9e12-32a2f4bc972e",
    "message": "Processing started"
  }
  ```

### `GET /api/status/{job_id}`
Returns current processing status and frame counts for polling.
- **Response**:
  ```json
  {
    "job_id": "a3f4c21b-8c44-4829-9e12-32a2f4bc972e",
    "status": "analyzing",
    "video_name": "living_room_tour.mp4",
    "frames_extracted": 32,
    "frames_analyzed": 18,
    "pipeline": "florence2 + yolov8x-worldv2",
    "error": null
  }
  ```

### `GET /api/inventory/{job_id}`
Fetches the finalized inventory list and annotated preview frame URLs once `status == "completed"`.
- **Response**:
  ```json
  {
    "job_id": "a3f4c21b-8c44-4829-9e12-32a2f4bc972e",
    "inventory": [
      { "name": "sofa", "quantity": 1, "room": "Living Room" },
      { "name": "coffee table", "quantity": 1, "room": "Living Room" },
      { "name": "chair", "quantity": 4, "room": "Kitchen" }
    ],
    "annotated_frames": [
      "/static/annotated/a3f4c21b_0.jpg",
      "/static/annotated/a3f4c21b_1.jpg"
    ]
  }
  ```

---

## ⚙️ Configuration Reference

| Environment Variable | Default Value | Description |
| :--- | :--- | :--- |
| `FAST_MODE` | `false` | When `true`, lowers frame limits and raises confidence thresholds for rapid CPU testing |
| `MAX_FRAMES` | `6` (or `60` cap in extractor) | Maximum number of frames to extract from video |
| `FRAME_INTERVAL_SEC` | `1.0` | Target time interval in seconds between sampled frames |
| `FRAME_QUALITY` | `80` (or `60` in fast mode) | JPEG compression quality percentage for extracted frames |
| `YOLO_CONF` | `0.08` | Detection confidence threshold for YOLO models |
| `YOLO_WEIGHTS` | `weights/yolo11s.pt` | Default fallback YOLO model weights |
| `FLORENCE_MODEL` | `microsoft/Florence-2-base` | Hugging Face model identifier for Florence-2 VLM |
| `DATABASE_URL` | `sqlite:///./visionvault.db` | SQLAlchemy database connection URI |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis broker URI for Celery worker |
| `MINIO_ENDPOINT` | `localhost:9000` | S3 endpoint for MinIO object storage |

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
