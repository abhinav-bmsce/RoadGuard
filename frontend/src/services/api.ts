import axios from 'axios';
import {
  DetectionResult,
  HistoryListResponse,
  AnalyticsOverview,
  ReportResponse,
  HealthStatus,
} from '../types';

export const getBackendOrigin = (): string => {
  if (typeof window !== 'undefined' && window.location) {
    const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
    const hostname = window.location.hostname || 'localhost';
    return `${protocol}//${hostname}:8000`;
  }
  return 'http://127.0.0.1:8000';
};

export const getApiBaseUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (envUrl && typeof envUrl === 'string' && envUrl.trim() !== '') {
    return envUrl;
  }
  return `${getBackendOrigin()}/api/v1`;
};

export const API_BASE_URL = getApiBaseUrl();

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Accept': 'application/json',
  },
  timeout: 60000,
});

export const getFullImageUrl = (relativePath: string): string => {
  if (!relativePath) return '';
  if (relativePath.startsWith('http://') || relativePath.startsWith('https://')) {
    return relativePath;
  }
  const cleanPath = relativePath.startsWith('/') ? relativePath : `/${relativePath}`;
  return `${getBackendOrigin()}${cleanPath}`;
};

export const getFullApiUrl = (relativePath: string): string => {
  if (!relativePath) return '';
  if (relativePath.startsWith('http://') || relativePath.startsWith('https://')) {
    return relativePath;
  }
  const cleanPath = relativePath.startsWith('/') ? relativePath : `/${relativePath}`;
  return `${getBackendOrigin()}${cleanPath}`;
};

export const apiService = {
  // Health & Model Status
  async getHealth(): Promise<HealthStatus> {
    const response = await apiClient.get<HealthStatus>('/health');
    return response.data;
  },

  // Image Detection
  async detectRoadDamage(
    file: File,
    confidence?: number,
    locationNotes?: string
  ): Promise<DetectionResult> {
    const formData = new FormData();
    formData.append('file', file);
    if (confidence !== undefined) {
      formData.append('confidence', confidence.toString());
    }
    if (locationNotes) {
      formData.append('location_notes', locationNotes);
    }

    const response = await apiClient.post<DetectionResult>('/detect', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getDetection(id: string): Promise<DetectionResult> {
    const response = await apiClient.get<DetectionResult>(`/detect/${id}`);
    return response.data;
  },

  // History
  async getHistory(params?: {
    page?: number;
    limit?: number;
    severity?: string;
    search?: string;
  }): Promise<HistoryListResponse> {
    const response = await apiClient.get<HistoryListResponse>('/history', { params });
    return response.data;
  },

  async deleteDetection(id: string): Promise<{ message: string }> {
    const response = await apiClient.delete<{ message: string }>(`/history/${id}`);
    return response.data;
  },

  // Analytics
  async getAnalytics(): Promise<AnalyticsOverview> {
    const response = await apiClient.get<AnalyticsOverview>('/analytics/overview');
    return response.data;
  },

  // Reports
  async generateReport(
    detectionId: string,
    payload?: {
      title?: string;
      inspector_name?: string;
      location_notes?: string;
      additional_notes?: string;
    }
  ): Promise<ReportResponse> {
    const response = await apiClient.post<ReportResponse>(
      `/reports/${detectionId}/generate`,
      payload || {}
    );
    return response.data;
  },

  getPdfUrl(detectionId: string): string {
    return `${getBackendOrigin()}/api/v1/reports/${detectionId}/pdf`;
  },
};

