# RoadGuard Deployment Guide

## 1. Quickstart: Local Development on Apple Silicon (M2, 8GB RAM)

### Prerequisites:
- Python 3.10+
- Node.js 18+ and npm
- Git

### Backend Setup:
```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Apply database migrations (SQLite or PostgreSQL)
PYTHONPATH=. alembic upgrade head

# 4. Start FastAPI server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
The backend API is now running at `http://localhost:8000` with Swagger docs at `http://localhost:8000/docs`.

### Frontend Setup:
```bash
# In a new terminal window:
cd frontend
npm install
npm run dev
```
The application interface is now running at `http://localhost:5173`.

---

## 2. Docker Compose Deployment (Production / PostgreSQL)

For complete multi-container production deployment with PostgreSQL:

```bash
# Build and launch all services
docker compose up --build -d

# Verify container status
docker compose ps
```

- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **PostgreSQL**: `localhost:5432`

To shut down:
```bash
docker compose down
```

---

## 3. Google Colab GPU Training Workflow

To train or fine-tune models on NVIDIA GPUs without local hardware strain:
1. Open [Google Colab](https://colab.research.google.com).
2. Upload `ml/notebooks/RoadGuard_RDD2022_Training_Colab.ipynb`.
3. Set Runtime Type to **GPU (T4 or A100)**.
4. Run all cells: the notebook downloads RDD2022, converts annotations, trains YOLOv8n and YOLOv8s with high-resolution crack tuning, and prompts you to download the trained checkpoint `roadguard_yolov8n.pt`.
5. Place the downloaded checkpoint in `RoadGuard/ml/models/roadguard_yolov8n.pt`.

