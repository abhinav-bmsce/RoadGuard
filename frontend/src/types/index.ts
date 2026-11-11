export type SeverityLevel = 'Low' | 'Medium' | 'High';

export interface BoundingBox {
  xmin: number;
  ymin: number;
  xmax: number;
  ymax: number;
}

export interface DamageInstance {
  id?: number;
  class_id: number;
  class_name: string;
  confidence: number;
  bbox: BoundingBox;
  area_ratio: number;
  instance_severity: number;
  severity_tag: SeverityLevel;
}

export interface DetectionResult {
  id: string;
  created_at: string;
  original_filename: string;
  image_width: number;
  image_height: number;
  original_image_url: string;
  annotated_image_url: string;
  total_damages: number;
  severity_level: SeverityLevel;
  severity_score: number;
  inference_time_ms: number;
  damage_summary: Record<string, number>;
  damages: DamageInstance[];
  location_notes?: string;
  status: string;
}

export interface HistoryItem {
  id: string;
  created_at: string;
  original_filename: string;
  original_image_url: string;
  annotated_image_url: string;
  total_damages: number;
  severity_level: SeverityLevel;
  severity_score: number;
  inference_time_ms: number;
  damage_summary: Record<string, number>;
  location_notes?: string;
}

export interface HistoryListResponse {
  items: HistoryItem[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface DamageTypeCount {
  class_code: string;
  class_name: string;
  count: number;
  percentage: number;
}

export interface AnalyticsOverview {
  total_inspections: number;
  total_damages_detected: number;
  average_severity_score: number;
  average_inference_time_ms: number;
  severity_breakdown: {
    low: number;
    medium: number;
    high: number;
  };
  damage_type_breakdown: DamageTypeCount[];
  timeline: Array<{
    date: string;
    inspections_count: number;
    high_severity_count: number;
  }>;
}

export interface ReportResponse {
  id: string;
  detection_id: string;
  report_title: string;
  download_url: string;
  file_size_bytes: number;
  generated_at: string;
}

export interface HealthStatus {
  status: string;
  service: string;
  version: string;
  database: string;
  deep_learning: {
    model_loaded: boolean;
    device: string;
    architecture: string;
  };
}

