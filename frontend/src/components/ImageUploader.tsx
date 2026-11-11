import React, { useState, useRef } from 'react';
import { UploadCloud, Sliders, MapPin, X, ArrowRight, Sparkles } from 'lucide-react';

interface ImageUploaderProps {
  onUpload: (file: File, confidence?: number, locationNotes?: string) => void;
  isLoading: boolean;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({ onUpload, isLoading }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [confidence, setConfidence] = useState<number>(0.25);
  const [locationNotes, setLocationNotes] = useState<string>('');
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File) => {
    setErrorMessage(null);
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!validTypes.includes(file.type)) {
      setErrorMessage('Invalid file format. Please upload a JPG, JPEG, or PNG image.');
      return;
    }
    if (file.size > 25 * 1024 * 1024) {
      setErrorMessage('Image exceeds the maximum allowed size of 25MB.');
      return;
    }

    setSelectedFile(file);
    const reader = new FileReader();
    reader.onload = () => setPreviewUrl(reader.result as string);
    reader.readAsDataURL(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;
    onUpload(selectedFile, confidence, locationNotes);
  };

  const clearSelection = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setErrorMessage(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // Quick sample test loader
  const loadSampleImage = async (sampleName: string, label: string) => {
    try {
      const response = await fetch(`/uploads/images/${sampleName}.jpg`);
      let blob: Blob;
      if (response.ok) {
        blob = await response.blob();
      } else {
        // Fallback: create synthetic canvas sample directly
        const canvas = document.createElement('canvas');
        canvas.width = 640;
        canvas.height = 640;
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.fillStyle = '#4a4d52';
          ctx.fillRect(0, 0, 640, 640);
          ctx.fillStyle = '#1e2022';
          ctx.beginPath();
          ctx.arc(320, 360, 65, 0, Math.PI * 2);
          ctx.fill();
        }
        blob = await new Promise<Blob>((resolve) => canvas.toBlob((b) => resolve(b!), 'image/jpeg'));
      }
      const testFile = new File([blob], `${sampleName}.jpg`, { type: 'image/jpeg' });
      handleFile(testFile);
      setLocationNotes(`Automated Benchmark Test Link (${label})`);
    } catch (err) {
      console.error('Failed to load sample:', err);
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 shadow-xl">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Dropzone */}
        {!previewUrl ? (
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 flex flex-col items-center justify-center min-h-[240px] ${
              isDragging
                ? 'border-amber-500 bg-amber-500/10 scale-[0.99]'
                : 'border-slate-700 bg-slate-900/40 hover:border-amber-500/60 hover:bg-slate-900/80'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".jpg,.jpeg,.png"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
            />

            <div className="w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 mb-4 shadow-inner">
              <UploadCloud className="w-7 h-7" />
            </div>

            <h3 className="text-base font-semibold text-white">
              Drag & Drop Road Surface Image Here
            </h3>
            <p className="mt-1 text-xs text-slate-400">
              Supports JPEG, JPG, and PNG files up to 25MB
            </p>

            <button
              type="button"
              className="mt-4 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 shadow-sm transition-all"
            >
              Browse Local Files
            </button>
          </div>
        ) : (
          /* Preview Banner */
          <div className="relative rounded-xl overflow-hidden border border-slate-700 bg-slate-950 p-3 flex flex-col sm:flex-row items-center gap-4">
            <img
              src={previewUrl}
              alt="Road Preview"
              className="w-full sm:w-40 h-32 object-cover rounded-lg border border-slate-800"
            />
            <div className="flex-1 w-full text-left space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-amber-400 uppercase tracking-wide">
                  Image Ready for Inference
                </span>
                <button
                  type="button"
                  onClick={clearSelection}
                  className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800"
                  title="Remove image"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <p className="text-sm font-semibold text-white truncate max-w-xs sm:max-w-md">
                {selectedFile?.name}
              </p>
              <p className="text-xs text-slate-400 font-mono">
                Size: {((selectedFile?.size || 0) / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
          </div>
        )}

        {errorMessage && (
          <div className="p-3 rounded-lg bg-rose-950/80 border border-rose-500/50 text-rose-300 text-xs">
            {errorMessage}
          </div>
        )}

        {/* Quick Sample Selector */}
        {!selectedFile && (
          <div className="pt-2">
            <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>Or Test With Sample Road Imagery</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <button
                type="button"
                onClick={() => loadSampleImage('sample_pothole', 'RDD2022 Pothole')}
                className="px-3 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-amber-500/50 text-left text-xs transition-all"
              >
                <span className="font-semibold text-white block">Pothole</span>
                <span className="text-[10px] text-rose-400">Class D40 (RDD2022)</span>
              </button>
              <button
                type="button"
                onClick={() => loadSampleImage('sample_longitudinal', 'RDD2022 Longitudinal')}
                className="px-3 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-amber-500/50 text-left text-xs transition-all"
              >
                <span className="font-semibold text-white block">Longitudinal</span>
                <span className="text-[10px] text-emerald-400">Class D00 (RDD2022)</span>
              </button>
              <button
                type="button"
                onClick={() => loadSampleImage('sample_transverse', 'RDD2022 Transverse')}
                className="px-3 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-amber-500/50 text-left text-xs transition-all"
              >
                <span className="font-semibold text-white block">Transverse</span>
                <span className="text-[10px] text-cyan-400">Class D10 (RDD2022)</span>
              </button>
              <button
                type="button"
                onClick={() => loadSampleImage('sample_multi_hazard', 'RDD2022 Multi-Hazard')}
                className="px-3 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-amber-500/50 text-left text-xs transition-all"
              >
                <span className="font-semibold text-white block">Multi-Hazard</span>
                <span className="text-[10px] text-amber-400">D20 & D40 (RDD2022)</span>
              </button>
            </div>
          </div>
        )}

        {/* Configuration Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t border-slate-800/80">
          {/* Confidence Slider */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-300 font-medium flex items-center gap-1.5">
                <Sliders className="w-3.5 h-3.5 text-amber-400" />
                Detection Confidence Threshold:
              </span>
              <span className="font-mono font-bold text-amber-400">
                {(confidence * 100).toFixed(0)}%
              </span>
            </div>
            <input
              type="range"
              min="0.10"
              max="0.85"
              step="0.05"
              value={confidence}
              onChange={(e) => setConfidence(parseFloat(e.target.value))}
              className="w-full accent-amber-500 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
            />
            <p className="text-[10px] text-slate-400">
              Higher values filter faint cracks; lower values capture micro-distress.
            </p>
          </div>

          {/* Location notes */}
          <div className="space-y-1.5">
            <label className="text-xs text-slate-300 font-medium flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-amber-400" />
              Inspection Location / Highway Reference:
            </label>
            <input
              type="text"
              placeholder="e.g. Route 4 Southbound, Chainage 14+200"
              value={locationNotes}
              onChange={(e) => setLocationNotes(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
            />
          </div>
        </div>

        {/* Submit Action */}
        <div className="pt-2 flex justify-end">
          <button
            type="submit"
            disabled={!selectedFile || isLoading}
            className={`w-full sm:w-auto px-6 py-3 rounded-xl font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-lg transition-all duration-200 ${
              selectedFile && !isLoading
                ? 'bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 shadow-amber-500/20 cursor-pointer'
                : 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700/50'
            }`}
          >
            <span>Run Deep Learning Audit</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
};
