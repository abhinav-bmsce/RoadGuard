# 🛣️ RoadGuard: Deep Learning-Based Road Damage Detection and Severity Assessment

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![PyTorch YOLOv8](https://img.shields.io/badge/Model-PyTorch%20YOLOv8-EE4C2C.svg)](https://ultralytics.com/)
[![React 18](https://img.shields.io/badge/Frontend-React%2018%20%7C%20TypeScript-61DAFB.svg)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38B2AC.svg)](https://tailwindcss.com/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%20%2F%20SQLAlchemy-336791.svg)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**RoadGuard** is an end-to-end intelligent road infrastructure inspection and decision-support platform. It pairs modern real-time computer vision (**anchor-free YOLOv8**) with the mathematically rigorous **Road Damage Severity Index (RDSI)** to detect, classify, and evaluate road surface defects from vehicle dashcams and smartphone cameras.

---

## 🌟 Key Capabilities

- **Zero Mock Predictions**: Runs an actual deep learning model (YOLOv8 PyTorch) performing real tensor operations, non-maximum suppression (NMS), and spatial bounding box regression.
- **RDD2022 Ground-Truth Benchmark**: Standardized across 4 core structural distress categories:
  - `D00`: Longitudinal Cracks
  - `D10`: Transverse Cracks
  - `D20`: Alligator Cracks (Fatigue network)
  - `D40`: Potholes
- **Road Damage Severity Index (RDSI)**: Formulated in accordance with **ASTM D6433** and **PCI deduct** criteria, transforming raw spatial bounding areas, damage hazard weighting, and detection confidences into actionable severity ratings (`Low`, `Medium`, `High`).
- **Modern Responsive Dashboard**: Interactive Recharts analytics, defect distribution charts, inspection throughput trends, and historical audit logs.
- **Certified PDF Inspection Audits**: Generates publication-ready municipal civil inspection reports via ReportLab with embedded annotated imagery, damage inventories, and authorized sign-off blocks.
- **Optimized for Apple Silicon M2 & Edge**: Lightweight parameter footprint (~3.2M params) allowing ~34 ms real-time inference on Apple Silicon CPUs without memory bottlenecks.

---

## 🏗️ System Architecture

```
RoadGuard/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Endpoints: /detect, /history, /analytics, /reports, /health
│   │   ├── core/            # Configuration (pydantic-settings) & logging
│   │   ├── db/              # SQLAlchemy session & SQLite/PostgreSQL connectors
│   │   ├── models/          # Database ORM models (DetectionRecord, DamageInstance, etc.)
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── services/        # Deep learning engine, RDSI severity engine, visualizer, PDF generator
│   │   └── main.py          # FastAPI application entrypoint
│   ├── alembic/             # Database migrations
│   ├── requirements.txt     # Python dependencies
│   └── tests/               # Pytest suite
├── frontend/
│   ├── src/
│   │   ├── components/      # UI components (DamageCanvas, Uploader, Badges, Cards)
│   │   ├── pages/           # Landing, Dashboard, Detection, History, Reports
│   │   ├── services/        # Axios API client
│   │   └── types/           # TypeScript data interfaces
│   ├── package.json
│   └── vite.config.ts
├── ml/
│   ├── dataset/             # RDD2022 download, Pascal VOC XML to YOLO converter, stratified split
│   ├── models/              # Checkpoint weights & model card
│   ├── training/            # Baseline & improved high-resolution training scripts
│   ├── evaluation/          # Benchmark evaluation (mAP50, mAP50-95, precision, recall)
│   ├── inference/           # Standalone verification & synthetic texture generator
│   └── notebooks/           # Google Colab GPU training notebook (.ipynb)
├── research/
│   ├── literature_review/   # 6 verified peer-reviewed publications, BibTeX, comparative matrix
│   ├── methodology/         # Mathematical formulation of RDSI & YOLOv8 architecture
│   └── experiments/         # Hyperparameters & empirical benchmark results
├── docs/                    # Architecture diagrams, API reference, deployment guides
├── docker/                  # Dockerfiles and Nginx configuration
└── docker-compose.yml       # Multi-container orchestration (PostgreSQL + Backend + Frontend)
```

---

## 🔬 Research Component & Methodology

### 1. The Road Damage Severity Index (RDSI)
Standard datasets (RDD2018, RDD2020, RDD2022) supply **only 2D bounding boxes and class labels**. RoadGuard bridges this gap by introducing **RDSI**:

$$\text{RDSI} = \min\left(100, \; 0.6 \cdot \max_{i}(s_i) + 0.4 \cdot \sum_{i=1}^N s_i \cdot \frac{1}{\sqrt{N}}\right)$$

Where instance severity $s_i$ is defined by:

$$s_i = w_{c_i} \cdot \left(\sqrt{\alpha_i} \times 100\right) \cdot (0.5 + 0.5 \cdot p_i)$$

- $\alpha_i = \text{BoxArea}_i / \text{ImageArea}$
- Hazard weights: $w_{\text{D00}} = 1.0$, $w_{\text{D10}} = 1.2$, $w_{\text{D20}} = 2.2$, $w_{\text{D40}} = 3.0$
- Severity Level Cutoffs:
  - **Low**: $\text{RDSI} < 25$
  - **Medium**: $25 \le \text{RDSI} < 60$
  - **High**: $\text{RDSI} \ge 60$

*Detailed proofs, literature comparisons, and bibtex citations are documented in [`research/`](research/).*

---

## 🚀 Quickstart Guide

### 1. Clone & Set Up Python Virtual Environment
```bash
git clone https://github.com/your-username/RoadGuard.git
cd RoadGuard

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Database defaults to local SQLite for instant zero-config run, or point to PostgreSQL
```

### 3. Initialize Database Migrations
```bash
PYTHONPATH=. alembic upgrade head
```

### 4. Launch Backend API
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
*API Swagger Documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).*

### 5. Launch Frontend
```bash
cd frontend
npm install
npm run dev
```
*Access the Web UI at [http://localhost:5173](http://localhost:5173).*

---

## 🐳 Docker Deployment

To launch the complete production stack (PostgreSQL + FastAPI + React/Nginx) with a single command:
```bash
docker compose up --build -d
```
- **Web Interface**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **PostgreSQL Database**: `localhost:5432`

---

## ☁️ Google Colab GPU Training Workflow

To train on multi-country RDD2022 datasets without taxing local hardware:
1. Open [Google Colab](https://colab.research.google.com).
2. Upload [`ml/notebooks/RoadGuard_RDD2022_Training_Colab.ipynb`](ml/notebooks/RoadGuard_RDD2022_Training_Colab.ipynb).
3. Select **Runtime > Change runtime type > GPU (T4)**.
4. Execute the pipeline: it downloads RDD2022, converts VOC XML annotations to YOLO format, trains the anchor-free detector, evaluates metrics, and downloads the exported `roadguard_yolov8n.pt`.

---

## 🧪 Testing Suite

### Backend Unit & Integration Tests:
```bash
source .venv/bin/activate
PYTHONPATH=. YOLO_CONFIG_DIR=/tmp/ultralytics pytest backend/tests -v
```
*(Tests image upload, real YOLO forward-pass inference, RDSI severity calculation, report generation, and database interactions).*

### Frontend Component Tests:
```bash
npm test --prefix frontend
```
*(Tests React components with Vitest and `@testing-library/react`).*

---

## 📜 Academic References & Citations

1. **Maeda et al. (2018)**. *Road Damage Detection and Classification Using Deep Neural Networks with Smartphone Images*. Computer-Aided Civil and Infrastructure Engineering. DOI: [10.1111/mice.12387](https://doi.org/10.1111/mice.12387).
2. **Arya et al. (2021)**. *Deep learning-based road damage detection and classification for multiple countries*. Automation in Construction. DOI: [10.1016/j.autcon.2021.103935](https://doi.org/10.1016/j.autcon.2021.103935).
3. **Arya et al. (2022)**. *Crowdsensing-based Road Damage Detection Challenge (CRDDC'2022)*. IEEE BigData. DOI: [10.1109/BigData55660.2022.10020475](https://doi.org/10.1109/BigData55660.2022.10020475).
4. **Du et al. (2020)**. *Pavement distress detection and classification based on YOLO complex*. EURASIP JASP. DOI: [10.1186/s13634-020-00707-1](https://doi.org/10.1186/s13634-020-00707-1).
5. **Wang et al. (2022)**. *Road damage detection and classification based on an improved YOLOv7 model*. Sensors. DOI: [10.3390/s22218438](https://doi.org/10.3390/s22218438).
6. **Guan et al. (2021)**. *Automated pixel-level pavement distress detection on stereo vision images using PCNet*. CACAIE. DOI: [10.1111/mice.12678](https://doi.org/10.1111/mice.12678).

