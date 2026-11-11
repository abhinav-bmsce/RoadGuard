# RoadGuard System Architecture

## 1. High-Level Architecture Overview

RoadGuard is an end-to-end intelligent road infrastructure inspection and decision-support system. It integrates computer vision (anchor-free YOLOv8), deterministic civil engineering assessment (Road Damage Severity Index - RDSI), a high-performance REST API backend (FastAPI), and a modern reactive dashboard (React, TypeScript, Tailwind CSS, Recharts).

```mermaid
graph TD
    User["Civil Engineer / Dashcam Stream"] -->|Uploads Image| FE["React + TypeScript Frontend (Vite)"]
    FE -->|REST API Requests| BE["FastAPI Application"]
    
    subgraph "Backend Engine"
        BE --> DL["Inference Engine (YOLOv8 PyTorch)"]
        BE --> SA["Severity Analyzer (RDSI Engine)"]
        BE --> VIZ["Visualizer (OpenCV Anti-Aliased Annotation)"]
        BE --> RG["Report Generator (ReportLab PDF)"]
        BE --> DB[("PostgreSQL / SQLite Database")]
    end
    
    DL -->|BBoxes & Classes| SA
    SA -->|RDSI Severity Score| BE
    VIZ -->|Annotated Overlay Image| Storage[("Disk Storage: uploads/")]
    RG -->|Certified PDF Document| Storage
    DB -->|History & Analytics| FE
```

---

## 2. Deep Learning Pipeline & Inference Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Client as Web Client / Browser
    participant API as FastAPI Router (/api/v1/detect)
    participant Engine as YOLOv8 Inference Engine
    participant Severity as RDSI Severity Engine
    participant Viz as OpenCV Visualizer
    participant DB as PostgreSQL Database

    Client->>API: POST /detect (Image multipart/form-data)
    API->>API: Validate MIME type & file size (<25MB)
    API->>Engine: Forward pass (YOLOv8 PyTorch)
    Engine-->>API: Bounding boxes [xmin, ymin, xmax, ymax], Class IDs, Confidences
    API->>Severity: Compute instance area ratios & RDSI score
    Severity-->>API: Cumulative RDSI (0-100) & Severity Level (Low/Med/High)
    API->>Viz: Annotate image with color-coded bounding boxes & banner
    Viz-->>API: Annotated image path
    API->>DB: Store ImageMetadata, DetectionRecord, DamageInstances
    DB-->>API: Saved record ID
    API-->>Client: DetectionResultResponse (JSON)
```

---

## 3. Database Entity-Relationship (ER) Schema

```mermaid
erDiagram
    IMAGE_METADATA ||--o{ DETECTION_RECORD : "contains"
    MODEL_VERSION ||--o{ DETECTION_RECORD : "executes"
    DETECTION_RECORD ||--|{ DAMAGE_INSTANCE : "localizes"
    DETECTION_RECORD ||--o{ DETECTION_REPORT : "generates"

    IMAGE_METADATA {
        int id PK
        string original_filename
        string file_path
        int file_size_bytes
        string mime_type
        int width
        int height
        string hash_md5
        datetime uploaded_at
    }

    MODEL_VERSION {
        int id PK
        string name
        string version
        string architecture
        string weights_path
        boolean is_active
        datetime created_at
    }

    DETECTION_RECORD {
        string id PK
        int image_id FK
        int model_version_id FK
        string annotated_image_path
        int total_damages
        string severity_level
        float severity_score
        float inference_time_ms
        json damage_summary
        string status
        string location_notes
        datetime created_at
    }

    DAMAGE_INSTANCE {
        int id PK
        string detection_id FK
        int class_id
        string class_name
        float confidence
        float bbox_xmin
        float bbox_ymin
        float bbox_xmax
        float bbox_ymax
        float area_ratio
        float instance_severity
        string severity_tag
    }

    DETECTION_REPORT {
        string id PK
        string detection_id FK
        string report_title
        string pdf_path
        int file_size_bytes
        text summary_notes
        datetime generated_at
    }
```

---

## 4. Hardware Optimization (Apple Silicon M2 / CPU)
- **Model Size**: YOLOv8n has ~3.2M parameters (~12 MB checkpoint size), making it ideal for the 8GB RAM constraints of the development MacBook Air M2.
- **Hardware Acceleration**: Automatic device detection switches between PyTorch MPS (Metal Performance Shaders on Apple Silicon), CUDA on Google Colab GPUs, and CPU fallback with zero code changes.
- **Asynchronous Execution**: Image parsing, inference, database transactions, and PDF compilation execute asynchronously without blocking FastAPI event loops.

