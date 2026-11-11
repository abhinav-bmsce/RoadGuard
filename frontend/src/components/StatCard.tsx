import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: {
    value: string;
    positive?: boolean;
  };
  accentColor?: 'amber' | 'emerald' | 'rose' | 'sky';
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  accentColor = 'amber',
}) => {
  const accentClasses = {
    amber: 'border-l-amber-500 text-amber-400 group-hover:border-amber-400',
    emerald: 'border-l-emerald-500 text-emerald-400 group-hover:border-emerald-400',
    rose: 'border-l-rose-500 text-rose-400 group-hover:border-rose-400',
    sky: 'border-l-sky-500 text-sky-400 group-hover:border-sky-400',
  };

  return (
    <div className={`glass-panel rounded-xl p-5 border-l-4 ${accentClasses[accentColor]} transition-all duration-300 hover:translate-y-[-2px] hover:shadow-lg`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        <div className="p-2 rounded-lg bg-slate-800/80 text-slate-200">
          {icon}
        </div>
      </div>
      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-3xl font-bold font-mono tracking-tight text-white">{value}</span>
        {trend && (
          <span className={`text-xs font-medium ${trend.positive ? 'text-emerald-400' : 'text-rose-400'}`}>
            {trend.value}
          </span>
        )}
      </div>
      {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
    </div>
  );
};

