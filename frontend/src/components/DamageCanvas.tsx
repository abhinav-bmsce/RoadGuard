import React, { useState, useRef } from 'react';
import { DamageInstance, SeverityLevel } from '../types';
import { getFullImageUrl } from '../services/api';
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Eye,
  Layers,
  Download,
} from 'lucide-react';

interface DamageCanvasProps {
  originalImageUrl: string;
  annotatedImageUrl: string;
  damages: DamageInstance[];
  imageWidth: number;
  imageHeight: number;
  overallSeverity: SeverityLevel;
  hoveredIndex: number | null;
  onHoverIndex: (index: number | null) => void;
}

export const DamageCanvas: React.FC<DamageCanvasProps> = ({
  originalImageUrl,
  annotatedImageUrl,
  damages,
  imageWidth,
  imageHeight,
  overallSeverity,
  hoveredIndex,
  onHoverIndex,
}) => {
  const [showAnnotated, setShowAnnotated] = useState(true);
  const [zoomLevel, setZoomLevel] = useState(1);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleZoom = (delta: number) => {
    setZoomLevel((prev) => Math.min(3.0, Math.max(0.75, prev + delta)));
  };

  const handleReset = () => {
    setZoomLevel(1);
  };

  const getBoxColor = (tag: SeverityLevel) => {
    switch (tag) {
      case 'High':
        return '#ef4444';
      case 'Medium':
        return '#f59e0b';
      case 'Low':
      default:
        return '#10b981';
    }
  };

  const currentSrc = showAnnotated
    ? getFullImageUrl(annotatedImageUrl)
    : getFullImageUrl(originalImageUrl);

  return (
    <div className="glass-panel rounded-2xl overflow-hidden border border-slate-800 flex flex-col">
      {/* Top Toolbar */}
      <div className="px-4 py-3 bg-slate-900/90 border-b border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
        {/* Toggle Mode */}
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => setShowAnnotated(true)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
              showAnnotated
                ? 'bg-amber-500 text-slate-950 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            Annotated (AI)
          </button>
          <button
            onClick={() => setShowAnnotated(false)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
              !showAnnotated
                ? 'bg-slate-800 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            Original
          </button>
        </div>

        {/* Zoom & Download Controls */}
        <div className="flex items-center gap-2">
          <div className="flex items-center bg-slate-950 border border-slate-800 rounded-lg p-0.5">
            <button
              onClick={() => handleZoom(-0.25)}
              className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-md"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <span className="text-[11px] font-mono text-slate-300 px-2 min-w-[48px] text-center">
              {Math.round(zoomLevel * 100)}%
            </span>
            <button
              onClick={() => handleZoom(0.25)}
              className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-md"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              onClick={handleReset}
              className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-md border-l border-slate-800"
              title="Reset View"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>

          <a
            href={currentSrc}
            download={`RoadGuard_Inspection_${showAnnotated ? 'Annotated' : 'Original'}.jpg`}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-amber-400" />
            <span>Save Image</span>
          </a>
        </div>
      </div>

      {/* Main Canvas Viewport */}
      <div
        ref={containerRef}
        className="relative bg-slate-950 overflow-auto flex items-center justify-center p-4 min-h-[420px] max-h-[640px] select-none highway-grid"
      >
        <div
          className="relative inline-block transition-transform duration-150 ease-out origin-center rounded-lg shadow-2xl border border-slate-800/80 overflow-hidden"
          style={{ transform: `scale(${zoomLevel})` }}
        >
          <img
            src={currentSrc}
            alt="Road Damage Inspection"
            className="max-w-full h-auto block max-h-[560px] object-contain"
          />

          {/* Interactive SVG Bounding Box Overlays (Active when showing original or hovering) */}
          {!showAnnotated && imageWidth > 0 && imageHeight > 0 && (
            <svg
              className="absolute inset-0 w-full h-full pointer-events-none"
              viewBox={`0 0 ${imageWidth} ${imageHeight}`}
              preserveAspectRatio="none"
            >
              {damages.map((dmg, idx) => {
                const isHovered = hoveredIndex === idx;
                const strokeColor = getBoxColor(dmg.severity_tag);
                const w = dmg.bbox.xmax - dmg.bbox.xmin;
                const h = dmg.bbox.ymax - dmg.bbox.ymin;

                return (
                  <g key={idx} className="pointer-events-auto cursor-pointer" onMouseEnter={() => onHoverIndex(idx)} onMouseLeave={() => onHoverIndex(null)}>
                    <rect
                      x={dmg.bbox.xmin}
                      y={dmg.bbox.ymin}
                      width={w}
                      height={h}
                      fill={isHovered ? strokeColor : 'none'}
                      fillOpacity={isHovered ? 0.25 : 0}
                      stroke={strokeColor}
                      strokeWidth={isHovered ? 4 : 2.5}
                      rx={3}
                    />
                    <text
                      x={dmg.bbox.xmin + 4}
                      y={Math.max(16, dmg.bbox.ymin - 6)}
                      fill="#ffffff"
                      fontSize="14"
                      fontWeight="bold"
                      fontFamily="monospace"
                      filter="drop-shadow(0px 1px 2px rgba(0,0,0,0.8))"
                    >
                      {dmg.class_name.split('_')[0]} ({(dmg.confidence * 100).toFixed(0)}%)
                    </text>
                  </g>
                );
              })}
            </svg>
          )}
        </div>
      </div>

      {/* Bottom Info Bar */}
      <div className="px-4 py-2 bg-slate-900/90 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400 font-mono">
        <span>
          Native Dimensions: {imageWidth} &times; {imageHeight} px
        </span>
        <span className="flex items-center gap-2">
          <span>Overall Distress:</span>
          <span className="font-semibold text-slate-200">{overallSeverity}</span>
        </span>
      </div>
    </div>
  );
};

