import React from 'react';
import { DamageInstance } from '../types';
import { SeverityBadge } from './SeverityBadge';
import { Crosshair, Maximize2 } from 'lucide-react';

interface DamageCardProps {
  damage: DamageInstance;
  index: number;
  isHovered?: boolean;
  onHover?: (index: number | null) => void;
}

export const DamageCard: React.FC<DamageCardProps> = ({
  damage,
  index,
  isHovered = false,
  onHover,
}) => {
  const shortCode = damage.class_name.split('_')[0] || damage.class_name;
  const cleanTitle = damage.class_name.replace(/^[D\d]+_/, '').replace(/_/g, ' ');

  return (
    <div
      onMouseEnter={() => onHover && onHover(index)}
      onMouseLeave={() => onHover && onHover(null)}
      className={`p-4 rounded-xl border transition-all duration-200 cursor-pointer ${
        isHovered
          ? 'bg-slate-800/90 border-amber-500/80 shadow-md shadow-amber-500/10 -translate-y-0.5'
          : 'bg-slate-900/60 border-slate-800/80 hover:border-slate-700'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <span className="w-6 h-6 rounded-md bg-slate-800 border border-slate-700 font-mono text-xs font-bold text-amber-400 flex items-center justify-center">
            {index + 1}
          </span>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700">
                {shortCode}
              </span>
              <h4 className="text-sm font-semibold text-white capitalize">{cleanTitle}</h4>
            </div>
            <div className="flex items-center gap-3 mt-1.5 text-xs text-slate-400 font-mono">
              <span className="flex items-center gap-1">
                <Crosshair className="w-3 h-3 text-slate-500" />
                Conf: {(damage.confidence * 100).toFixed(1)}%
              </span>
              <span className="flex items-center gap-1">
                <Maximize2 className="w-3 h-3 text-slate-500" />
                Area: {(damage.area_ratio * 100).toFixed(2)}%
              </span>
            </div>
          </div>
        </div>

        <SeverityBadge level={damage.severity_tag} score={damage.instance_severity} size="sm" />
      </div>

      {/* Confidence Visual Bar */}
      <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center gap-2">
        <div className="flex-1 h-1.5 rounded-full bg-slate-800 overflow-hidden">
          <div
            className={`h-full rounded-full ${
              damage.confidence >= 0.75
                ? 'bg-emerald-500'
                : damage.confidence >= 0.45
                ? 'bg-amber-500'
                : 'bg-rose-500'
            }`}
            style={{ width: `${Math.min(100, damage.confidence * 100)}%` }}
          />
        </div>
        <span className="text-[10px] font-mono text-slate-400">
          Box: [{Math.round(damage.bbox.xmin)}, {Math.round(damage.bbox.ymin)}, {Math.round(damage.bbox.xmax)}, {Math.round(damage.bbox.ymax)}]
        </span>
      </div>
    </div>
  );
};

