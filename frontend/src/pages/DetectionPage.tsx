import React, { useState } from 'react';
import { apiService, getFullApiUrl } from '../services/api';
import { DetectionResult } from '../types';
import { ImageUploader } from '../components/ImageUploader';
import { DamageCanvas } from '../components/DamageCanvas';
import { DamageCard } from '../components/DamageCard';
import { SeverityBadge } from '../components/SeverityBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';
import {
  FileText,
  RotateCcw,
  Activity,
  Layers,
  MapPin,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

interface DetectionPageProps {
  initialDetectionId?: string | null;
  onClearInitialId?: () => void;
}

export const DetectionPage: React.FC<DetectionPageProps> = ({
  initialDetectionId,
  onClearInitialId,
}) => {
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [generatingReport, setGeneratingReport] = useState<boolean>(false);

  // Load initial detection if passed from history/dashboard
  React.useEffect(() => {
    if (initialDetectionId) {
      const loadRecord = async () => {
        setIsLoading(true);
        try {
          const data = await apiService.getDetection(initialDetectionId);
          setResult(data);
        } catch (err: any) {
          setError('Failed to fetch selected inspection record.');
        } finally {
          setIsLoading(false);
          if (onClearInitialId) onClearInitialId();
        }
      };
      loadRecord();
    }
  }, [initialDetectionId]);

  const handleUploadAndDetect = async (
    file: File,
    confidence?: number,
    locationNotes?: string
  ) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiService.detectRoadDamage(file, confidence, locationNotes);
      setResult(data);
    } catch (err: any) {
      console.error('Detection error:', err);
      setError(
        err.response?.data?.detail ||
          'Failed to execute deep learning model. Please check the backend connection.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!result) return;
    setGeneratingReport(true);
    try {
      const reportRes = await apiService.generateReport(result.id, {
        title: `RoadGuard Inspection - ${result.original_filename}`,
        location_notes: result.location_notes,
      });
      // Trigger download
      window.open(getFullApiUrl(reportRes.download_url), '_blank');
    } catch (err) {
      console.error('Failed to generate PDF:', err);
      // Fallback: direct download link
      window.open(apiService.getPdfUrl(result.id), '_blank');
    } finally {
      setGeneratingReport(false);
    }
  };

  const resetDetection = () => {
    setResult(null);
    setError(null);
  };

  return (
    <div className="py-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-900 pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black font-mono tracking-tight text-white flex items-center gap-3">
            <span>AI Road Distress Detection</span>
            <span className="text-xs font-sans px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30">
              Live PyTorch YOLOv8n
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Detect longitudinal, transverse, alligator cracks, and potholes with mathematical severity index estimation.
          </p>
        </div>

        {result && (
          <button
            onClick={resetDetection}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5 text-amber-400" />
            <span>New Inspection</span>
          </button>
        )}
      </div>

      {/* Error Alert */}
      {error && (
        <div className="glass-panel rounded-xl p-4 border border-rose-500/50 bg-rose-950/40 text-rose-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-400" />
            <span>{error}</span>
          </div>
          <button onClick={() => setError(null)} className="text-rose-400 hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="glass-panel rounded-2xl border border-slate-800">
          <LoadingSpinner
            message="Executing Deep Learning Model..."
            submessage="Running YOLOv8 forward pass, non-maximum suppression (NMS), and computing Road Damage Severity Index (RDSI)..."
          />
        </div>
      )}

      {/* Initial Upload State */}
      {!isLoading && !result && (
        <div className="max-w-3xl mx-auto">
          <ImageUploader onUpload={handleUploadAndDetect} isLoading={isLoading} />
        </div>
      )}

      {/* Inspection Results View */}
      {!isLoading && result && (
        <div className="space-y-6">
          {/* Executive Scorecard Banner */}
          <div className="glass-panel-glow rounded-2xl p-6 border border-amber-500/30 flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-3">
                <SeverityBadge level={result.severity_level} score={result.severity_score} size="lg" />
                <span className="text-xs font-mono text-slate-400 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5" />
                  {new Date(result.created_at).toLocaleString()}
                </span>
                {result.location_notes && (
                  <span className="text-xs font-mono text-slate-400 flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-amber-400" />
                    {result.location_notes}
                  </span>
                )}
              </div>
              <h2 className="text-lg font-bold text-white font-mono">
                Audit Result: {result.original_filename}
              </h2>
            </div>

            {/* Quick Metrics & Actions */}
            <div className="flex flex-wrap items-center gap-4">
              <div className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-center">
                <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-mono">
                  Defects
                </span>
                <span className="text-xl font-bold font-mono text-amber-400">
                  {result.total_damages}
                </span>
              </div>

              <div className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-center">
                <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-mono">
                  AI Latency
                </span>
                <span className="text-xl font-bold font-mono text-emerald-400">
                  {result.inference_time_ms.toFixed(1)} ms
                </span>
              </div>

              <button
                onClick={handleDownloadPdf}
                disabled={generatingReport}
                className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs uppercase tracking-wider flex items-center gap-2 shadow-lg shadow-amber-500/20 transition-all cursor-pointer"
              >
                <FileText className="w-4 h-4" />
                <span>{generatingReport ? 'Generating...' : 'Download PDF Report'}</span>
              </button>
            </div>
          </div>

          {/* Main Visualizer & Damage Inventory Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Visual Canvas (7 cols on desktop) */}
            <div className="lg:col-span-7">
              <DamageCanvas
                originalImageUrl={result.original_image_url}
                annotatedImageUrl={result.annotated_image_url}
                damages={result.damages}
                imageWidth={result.image_width}
                imageHeight={result.image_height}
                overallSeverity={result.severity_level}
                hoveredIndex={hoveredIndex}
                onHoverIndex={setHoveredIndex}
              />
            </div>

            {/* Damage Inventory & Breakdown (5 cols on desktop) */}
            <div className="lg:col-span-5 space-y-4">
              <div className="glass-panel rounded-2xl p-5 border border-slate-800">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 font-mono flex items-center gap-2">
                    <Layers className="w-4 h-4 text-amber-400" />
                    <span>Detected Distress Inventory</span>
                  </h3>
                  <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded-md bg-slate-800 text-slate-300">
                    {result.damages.length} Items
                  </span>
                </div>

                {/* List of Detected Damages */}
                <div className="mt-4 space-y-3 max-h-[460px] overflow-y-auto pr-1">
                  {result.damages.length === 0 ? (
                    <div className="p-8 text-center text-slate-400 text-xs">
                      <CheckCircle className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                      <p className="font-semibold text-white">No Pavement Defects Detected</p>
                      <p className="mt-1 text-[11px] text-slate-400">
                        Road surface appears structurally sound under selected confidence threshold.
                      </p>
                    </div>
                  ) : (
                    result.damages.map((dmg, idx) => (
                      <DamageCard
                        key={idx}
                        damage={dmg}
                        index={idx}
                        isHovered={hoveredIndex === idx}
                        onHover={setHoveredIndex}
                      />
                    ))
                  )}
                </div>
              </div>

              {/* Maintenance Directive Notice */}
              <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 font-mono flex items-center gap-1.5">
                  <Activity className="w-3.5 h-3.5 text-amber-400" />
                  <span>Civil Engineering Action Directive</span>
                </h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  {result.severity_level === 'High' && (
                    <span className="text-rose-300">
                      <strong>URGENT CIVIL ACTION:</strong> High structural hazard index ({result.severity_score.toFixed(1)}/100).
                      Pothole or advanced fatigue alligator cracking identified. Recommended action: Emergency asphalt patching within 24-48 hours.
                    </span>
                  )}
                  {result.severity_level === 'Medium' && (
                    <span className="text-amber-300">
                      <strong>SCHEDULED REPAIR:</strong> Moderate pavement distress detected ({result.severity_score.toFixed(1)}/100).
                      Recommended action: Schedule joint routing and hot-pour crack sealant within 30 days.
                    </span>
                  )}
                  {result.severity_level === 'Low' && (
                    <span className="text-emerald-300">
                      <strong>ROUTINE SURVEILLANCE:</strong> Pavement is in acceptable operational condition ({result.severity_score.toFixed(1)}/100).
                      Recommended action: Log baseline condition and re-survey in next scheduled annual cycle.
                    </span>
                  )}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
