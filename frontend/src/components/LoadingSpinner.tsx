import React from 'react';
import { ScanLine, Cpu } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
  submessage?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = "Processing Road Image...",
  submessage = "Executing PyTorch YOLO forward pass & Road Damage Severity Index (RDSI) computation..."
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <div className="relative flex items-center justify-center w-24 h-24 mb-6">
        {/* Outer pulsating ring */}
        <div className="absolute inset-0 rounded-full border-2 border-amber-500/20 animate-ping" />
        {/* Rotating radar ring */}
        <div className="absolute inset-2 rounded-full border-2 border-dashed border-amber-500/60 animate-spin" style={{ animationDuration: '6s' }} />
        {/* Inner circle */}
        <div className="relative flex items-center justify-center w-16 h-16 rounded-full bg-slate-900 border border-amber-500/40 shadow-inner">
          <ScanLine className="w-8 h-8 text-amber-400 animate-pulse" />
        </div>
      </div>
      <h3 className="text-lg font-semibold text-white tracking-wide flex items-center gap-2">
        <Cpu className="w-5 h-5 text-amber-400 animate-bounce" />
        {message}
      </h3>
      <p className="mt-2 text-sm text-slate-400 max-w-md">
        {submessage}
      </p>
    </div>
  );
};

