import React from 'react';
import {
  ScanEye,
  Activity,
  FileCheck2,
  Cpu,
  ArrowRight,
  CheckCircle2,
  Award
} from 'lucide-react';

interface LandingPageProps {
  onStartDetection: () => void;
  onViewDashboard: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onStartDetection,
  onViewDashboard,
}) => {
  const damageClasses = [
    {
      code: 'D00',
      title: 'Longitudinal Cracks',
      description: 'Linear distress parallel to traffic pavement joints caused by sub-base wear and asphalt shrinkage.',
      tag: 'Class 0',
      hazard: 'Low-Medium',
      color: 'border-emerald-500/40 bg-emerald-950/20 text-emerald-400',
    },
    {
      code: 'D10',
      title: 'Transverse Cracks',
      description: 'Cracks running perpendicular to traffic flow caused by daily thermal expansion and subgrade contraction.',
      tag: 'Class 1',
      hazard: 'Medium',
      color: 'border-emerald-500/40 bg-emerald-950/20 text-emerald-400',
    },
    {
      code: 'D20',
      title: 'Alligator Cracks',
      description: 'Interconnected fatigue cracking network signaling deep structural load failure and base breakdown.',
      tag: 'Class 2',
      hazard: 'Medium-High',
      color: 'border-amber-500/40 bg-amber-950/20 text-amber-400',
    },
    {
      code: 'D40',
      title: 'Potholes',
      description: 'Severe surface cavitations created by moisture infiltration, freeze-thaw cycles, and heavy traffic displacement.',
      tag: 'Class 3',
      hazard: 'Critical',
      color: 'border-rose-500/40 bg-rose-950/20 text-rose-400',
    },
  ];

  const workflowSteps = [
    {
      step: '01',
      title: 'Image Acquisition',
      desc: 'Ingests crowdsourced dashcam, smartphone, or UAV road surface imagery up to 25MB.',
      icon: <ScanEye className="w-6 h-6 text-amber-400" />,
    },
    {
      step: '02',
      title: 'YOLOv8 Detection',
      desc: 'Anchor-free decoupled network localizes bounding coordinates and predicts distress classes.',
      icon: <Cpu className="w-6 h-6 text-amber-400" />,
    },
    {
      step: '03',
      title: 'RDSI Severity Index',
      desc: 'Deterministic ASTM D6433 algorithm calculates physically calibrated Low, Medium, and High hazard ratings.',
      icon: <Activity className="w-6 h-6 text-amber-400" />,
    },
    {
      step: '04',
      title: 'PDF Engineering Audit',
      desc: 'Compiles certified municipal reports complete with annotated overlays and maintenance actions.',
      icon: <FileCheck2 className="w-6 h-6 text-amber-400" />,
    },
  ];

  return (
    <div className="space-y-24 py-8">
      {/* Hero Section */}
      <section className="relative text-center max-w-4xl mx-auto px-4 pt-10">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-mono mb-6">
          <Award className="w-3.5 h-3.5" />
          <span>RDD2022 Benchmark Validated Deep Learning</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-black tracking-tight text-white font-mono leading-tight">
          Next-Generation <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-amber-500 to-amber-600">
            Road Damage & Severity
          </span>{' '}
          Assessment
        </h1>

        <p className="mt-6 text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
          RoadGuard transforms standard road imagery into actionable civil engineering intelligence.
          Powered by anchor-free YOLOv8 and the mathematically formal{' '}
          <strong className="text-amber-400 font-semibold">Road Damage Severity Index (RDSI)</strong>.
        </p>

        {/* Action Buttons */}
        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            onClick={onStartDetection}
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-sm tracking-wide flex items-center justify-center gap-2.5 shadow-lg shadow-amber-500/25 transition-all hover:scale-105"
          >
            <ScanEye className="w-5 h-5" />
            <span>Launch AI Inspection</span>
            <ArrowRight className="w-4 h-4" />
          </button>

          <button
            onClick={onViewDashboard}
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-slate-200 border border-slate-700/80 font-semibold text-sm flex items-center justify-center gap-2 transition-all"
          >
            <span>View Analytics Dashboard</span>
          </button>
        </div>

        {/* Feature Highlights Pills */}
        <div className="mt-14 pt-8 border-t border-slate-900 grid grid-cols-2 md:grid-cols-4 gap-4 text-left">
          <div className="flex items-center gap-2.5 text-xs text-slate-300">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Real PyTorch YOLO Core</span>
          </div>
          <div className="flex items-center gap-2.5 text-xs text-slate-300">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Zero Mock Inference</span>
          </div>
          <div className="flex items-center gap-2.5 text-xs text-slate-300">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Deterministic Severity (RDSI)</span>
          </div>
          <div className="flex items-center gap-2.5 text-xs text-slate-300">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Certified PDF Exports</span>
          </div>
        </div>
      </section>

      {/* RDD2022 Distress Taxonomy Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h2 className="text-xs uppercase font-mono font-bold tracking-widest text-amber-400">
            Pavement Distress Taxonomy
          </h2>
          <h3 className="mt-2 text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Target Damage Categories (RDD2022)
          </h3>
          <p className="mt-2 text-sm text-slate-400">
            Standardized categories based on the Crowdsensing-based Road Damage Detection Challenge.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {damageClasses.map((item) => (
            <div
              key={item.code}
              className={`glass-panel rounded-2xl p-6 border ${item.color} flex flex-col justify-between hover:translate-y-[-4px] transition-all duration-300`}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="font-mono text-2xl font-black">{item.code}</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full border border-current">
                    {item.tag}
                  </span>
                </div>
                <h4 className="text-base font-bold text-white mb-2">{item.title}</h4>
                <p className="text-xs text-slate-400 leading-relaxed">{item.description}</p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                <span className="text-slate-500">Risk Profile:</span>
                <span className="font-mono font-semibold">{item.hazard}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works Architecture Pipeline */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-xs uppercase font-mono font-bold tracking-widest text-amber-400">
            End-To-End Architecture
          </h2>
          <h3 className="mt-2 text-2xl sm:text-3xl font-bold text-white tracking-tight">
            How RoadGuard Works
          </h3>
          <p className="mt-2 text-sm text-slate-400">
            From raw windshield dashcam scans to prioritized road maintenance work orders.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 relative">
          {workflowSteps.map((step) => (
            <div
              key={step.step}
              className="glass-panel rounded-2xl p-6 border border-slate-800 relative group hover:border-amber-500/50 transition-colors"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center group-hover:scale-110 transition-transform">
                  {step.icon}
                </div>
                <span className="font-mono text-3xl font-black text-slate-800 group-hover:text-amber-500/30 transition-colors">
                  {step.step}
                </span>
              </div>
              <h4 className="text-base font-bold text-white mb-2">{step.title}</h4>
              <p className="text-xs text-slate-400 leading-relaxed">{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Bottom CTA Banner */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="rounded-3xl glass-panel-glow p-8 sm:p-12 text-center relative overflow-hidden border border-amber-500/30">
          <div className="relative z-10 max-w-2xl mx-auto">
            <h3 className="text-2xl sm:text-3xl font-bold text-white font-mono">
              Ready to Inspect Pavement Integrity?
            </h3>
            <p className="mt-3 text-sm text-slate-300">
              Upload road surface photographs or select one of our pre-packaged benchmark images to evaluate real AI detection and severity calculation in real-time.
            </p>
            <div className="mt-6 flex justify-center">
              <button
                onClick={onStartDetection}
                className="px-8 py-3.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-sm tracking-wide flex items-center gap-2 shadow-lg shadow-amber-500/20 transition-all hover:scale-105"
              >
                <ScanEye className="w-5 h-5" />
                <span>Start Detection Now</span>
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
