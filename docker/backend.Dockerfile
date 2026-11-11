# RoadGuard Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV and ReportLab
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code, models, and alembic
COPY backend/ backend/
COPY ml/models/ ml/models/
COPY alembic.ini .

# Set environment
ENV PYTHONPATH=/app
ENV YOLO_CONFIG_DIR=/tmp/ultralytics

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

