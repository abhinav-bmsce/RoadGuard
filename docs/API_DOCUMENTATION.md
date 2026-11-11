# RoadGuard REST API Documentation

RoadGuard provides an OpenAPI/Swagger compliant RESTful API powering road damage detection, audit history retrieval, analytical metrics, and PDF generation.

Interactive Swagger documentation is available at `http://localhost:8000/docs` when the backend is running.

---

## 1. System Health & Status

### `GET /api/v1/health`
Returns system status, active database connectivity, and loaded PyTorch deep learning model metadata.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "RoadGuard Backend API",
  "version": "1.0.0",
  "database": "connected",
  "deep_learning": {
    "model_loaded": true,
    "device": "cpu",
    "architecture": "YOLOv8n (RDD2022)"
  }
}
```

---

## 2. Detection Endpoints

### `POST /api/v1/detect`
Uploads a road surface image, executes YOLOv8 inference, calculates the Road Damage Severity Index (RDSI), renders an annotated visualization, stores the results in the database, and returns the detection details.

**Request:**
- **Content-Type**: `multipart/form-data`
- **Form Fields**:
  - `file`: Image file (JPEG, JPG, or PNG, max 25MB) `[Required]`
  - `confidence`: Optional float between 0.05 and 0.95 (default: 0.25)
  - `location_notes`: Optional string description of road link or chainage

**Response (200 OK):**
```json
{
  "id": "e7b0c39f-1d44-42b3-9e4a-5f5a894371bf",
  "created_at": "2026-11-07T03:09:48.214000",
  "original_filename": "road_scan.jpg",
  "image_width": 640,
  "image_height": 640,
  "original_image_url": "/uploads/images/e7b0c39f-1d44-42b3-9e4a-5f5a894371bf.jpg",
  "annotated_image_url": "/uploads/annotated/annotated_e7b0c39f-1d44-42b3-9e4a-5f5a894371bf.jpg",
  "total_damages": 2,
  "severity_level": "High",
  "severity_score": 78.4,
  "inference_time_ms": 34.2,
  "damage_summary": {
    "D40": 1,
    "D10": 1
  },
  "damages": [
    {
      "id": 1,
      "class_id": 3,
      "class_name": "D40_Pothole",
      "confidence": 0.89,
      "bbox": {
        "xmin": 238.3,
        "ymin": 283.2,
        "xmax": 402.1,
        "ymax": 432.6
      },
      "area_ratio": 0.098,
      "instance_severity": 82.5,
      "severity_tag": "High"
    }
  ],
  "location_notes": "Highway 101 Mile 42",
  "status": "completed"
}
```

### `GET /api/v1/detect/{id}`
Retrieves a previous inspection record by ID.

---

## 3. History Endpoints

### `GET /api/v1/history`
Returns a paginated list of previous inspections.

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Number of items per page (default: 10, max 100)
- `severity`: Filter by severity (`Low`, `Medium`, `High`, or `all`)
- `search`: Filter by location notes substring

### `DELETE /api/v1/history/{id}`
Deletes an inspection record along with associated stored images.

---

## 4. Analytics Endpoints

### `GET /api/v1/analytics/overview`
Provides high-level metrics for the analytics dashboard.

**Response (200 OK):**
```json
{
  "total_inspections": 45,
  "total_damages_detected": 88,
  "average_severity_score": 42.6,
  "average_inference_time_ms": 36.1,
  "severity_breakdown": {
    "low": 18,
    "medium": 20,
    "high": 7
  },
  "damage_type_breakdown": [
    { "class_code": "D00", "class_name": "Longitudinal Crack", "count": 32, "percentage": 36.4 },
    { "class_code": "D10", "class_name": "Transverse Crack", "count": 24, "percentage": 27.3 },
    { "class_code": "D20", "class_name": "Alligator Crack", "count": 18, "percentage": 20.5 },
    { "class_code": "D40", "class_name": "Pothole", "count": 14, "percentage": 15.9 }
  ],
  "timeline": [
    { "date": "Nov 01", "inspections_count": 5, "high_severity_count": 1 },
    { "date": "Nov 02", "inspections_count": 8, "high_severity_count": 2 }
  ]
}
```

---

## 5. Report Endpoints

### `POST /api/v1/reports/{id}/generate`
Compiles an official PDF inspection report using ReportLab.

**Request Body:**
```json
{
  "title": "Bridge Deck Pavement Inspection Report",
  "inspector_name": "Lead Highway Auditor",
  "location_notes": "Interstate 80 Eastbound",
  "additional_notes": "Recommend crack sealing within 30 days."
}
```

### `GET /api/v1/reports/{id}/pdf`
Downloads the certified PDF inspection report.

