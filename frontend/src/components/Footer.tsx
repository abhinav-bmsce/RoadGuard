import React from 'react';
import { ShieldCheck, BookOpen, Database, Github } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="mt-20 border-t border-slate-900 bg-slate-950/90 text-slate-400 py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Col 1 */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-amber-500 flex items-center justify-center font-bold text-slate-950 text-xs">
                RG
              </div>
              <span className="text-white font-mono font-bold tracking-tight">RoadGuard AI</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Automated road damage localization and mathematical Road Damage Severity Index (RDSI) assessment based on RDD2022 benchmarks.
            </p>
          </div>

          {/* Col 2 */}
          <div className="space-y-2">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-200">RDD2022 Categories</h4>
            <ul className="text-xs space-y-1.5 font-mono text-slate-400">
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                D00: Longitudinal Crack
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                D10: Transverse Crack
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                D20: Alligator Crack
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
                D40: Pothole
              </li>
            </ul>
          </div>

          {/* Col 3 */}
          <div className="space-y-2">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-200">Civil Standards</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Formulated in accordance with ASTM D6433 & US Army Corps of Engineers Pavement Condition Index (PCI) deduct criteria.
            </p>
            <div className="flex items-center gap-2 text-xs text-amber-400 pt-1">
              <ShieldCheck className="w-4 h-4" />
              <span>Validated Severity Engine</span>
            </div>
          </div>

          {/* Col 4 */}
          <div className="space-y-2">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-200">Platform Links</h4>
            <div className="flex flex-col space-y-2 text-xs">
              <a href="/docs" target="_blank" className="hover:text-amber-400 transition-colors flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5" />
                FastAPI Swagger Docs
              </a>
              <span className="text-slate-400 flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5" />
                PostgreSQL & Alembic
              </span>
              <span className="text-slate-400 flex items-center gap-1.5">
                <Github className="w-3.5 h-3.5" />
                YOLOv8 PyTorch Core
              </span>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-4">
          <p>© {new Date().getFullYear()} RoadGuard Infrastructure AI. Academic & Engineering Research Project.</p>
          <p className="font-mono text-[11px] text-slate-400">
            Primary Ground Truth: Sekilab RDD2022 (Japan / India / Czech)
          </p>
        </div>
      </div>
    </footer>
  );
};

