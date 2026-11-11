import React from 'react';
import { SeverityLevel } from '../types';
import { ShieldCheck, AlertTriangle, AlertOctagon } from 'lucide-react';

interface SeverityBadgeProps {
  level: SeverityLevel;
  score?: number;
  showScore?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({
  level,
  score,
  showScore = true,
  size = 'md',
}) => {
  const getBadgeConfig = () => {
    switch (level) {
      case 'High':
        return {
          bg: 'bg-rose-950/80 border-rose-500/50 text-rose-300',
          dot: 'bg-rose-500 animate-pulse',
          icon: <AlertOctagon className="w-3.5 h-3.5 text-rose-400" />,
          label: 'High Hazard',
        };
      case 'Medium':
        return {
          bg: 'bg-amber-950/80 border-amber-500/50 text-amber-300',
          dot: 'bg-amber-500',
          icon: <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />,
          label: 'Medium Risk',
        };
      case 'Low':
      default:
        return {
          bg: 'bg-emerald-950/80 border-emerald-500/50 text-emerald-300',
          dot: 'bg-emerald-500',
          icon: <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />,
          label: 'Low / Minor',
        };
    }
  };

  const config = getBadgeConfig();

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1.5',
    md: 'text-xs font-medium px-2.5 py-1 gap-2',
    lg: 'text-sm font-semibold px-3.5 py-1.5 gap-2.5',
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border shadow-sm ${config.bg} ${sizeClasses[size]}`}
    >
      <span className={`w-2 h-2 rounded-full ${config.dot}`} />
      {config.icon}
      <span>{config.label}</span>
      {showScore && score !== undefined && (
        <span className="ml-1 pl-1.5 border-l border-white/20 font-mono font-semibold">
          {score.toFixed(1)}
        </span>
      )}
    </span>
  );
};

