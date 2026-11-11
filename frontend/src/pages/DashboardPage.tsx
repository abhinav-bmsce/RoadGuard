import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  Legend,
} from 'recharts';
import {
  FileCheck2,
  AlertTriangle,
  Zap,
  Activity,
  ArrowRight,
  RefreshCw,
} from 'lucide-react';
import { apiService, getFullImageUrl } from '../services/api';
import { AnalyticsOverview, HistoryItem } from '../types';
import { StatCard } from '../components/StatCard';
import { SeverityBadge } from '../components/SeverityBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';

interface DashboardPageProps {
  onSelectDetection: (id: string) => void;
  onNavigateDetect: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  onSelectDetection,
  onNavigateDetect,
}) => {
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);
  const [recentHistory, setRecentHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [analyticsData, historyData] = await Promise.all([
        apiService.getAnalytics(),
        apiService.getHistory({ page: 1, limit: 5 }),
      ]);
      setAnalytics(analyticsData);
      setRecentHistory(historyData.items);
    } catch (err: any) {
      console.error('Failed to load dashboard data:', err);
      setError('Unable to connect to RoadGuard analytics service.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading) {
    return <LoadingSpinner message="Loading Analytics Engine..." submessage="Querying PostgreSQL detection history and computing statistical distributions..." />;
  }

  if (error || !analytics) {
    return (
      <div className="glass-panel rounded-2xl p-12 text-center max-w-xl mx-auto border border-rose-500/30">
        <AlertTriangle className="w-12 h-12 text-rose-400 mx-auto mb-4" />
        <h3 className="text-lg font-bold text-white">Dashboard Offline</h3>
        <p className="text-sm text-slate-400 mt-2">{error || 'No analytics data available.'}</p>
        <button
          onClick={fetchDashboardData}
          className="mt-6 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg inline-flex items-center gap-2"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Retry Connection
        </button>
      </div>
    );
  }

  // Severity Pie Data
  const severityPieData = [
    { name: 'Low Risk', value: analytics.severity_breakdown.low, color: '#10b981' },
    { name: 'Medium Risk', value: analytics.severity_breakdown.medium, color: '#f59e0b' },
    { name: 'High Hazard', value: analytics.severity_breakdown.high, color: '#ef4444' },
  ].filter((item) => item.value > 0);

  // Category Bar Data
  const categoryBarData = analytics.damage_type_breakdown.map((item) => ({
    name: item.class_code,
    fullName: item.class_name,
    count: item.count,
    percentage: item.percentage,
  }));

  return (
    <div className="space-y-8 py-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black font-mono tracking-tight text-white">
            Infrastructure Analytics Dashboard
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time pavement distress telemetry and severity distributions
          </p>
        </div>

        <button
          onClick={fetchDashboardData}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5 text-amber-400" />
          <span>Refresh Metrics</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Total Road Audits"
          value={analytics.total_inspections}
          subtitle="Cumulative frames processed"
          icon={<FileCheck2 className="w-5 h-5 text-amber-400" />}
          accentColor="amber"
        />
        <StatCard
          title="Detected Defects"
          value={analytics.total_damages_detected}
          subtitle="Cracks and potholes localized"
          icon={<AlertTriangle className="w-5 h-5 text-rose-400" />}
          accentColor="rose"
        />
        <StatCard
          title="Mean RDSI Index"
          value={`${analytics.average_severity_score.toFixed(1)} / 100`}
          subtitle="Standard ASTM D6433 rating"
          icon={<Activity className="w-5 h-5 text-emerald-400" />}
          accentColor="emerald"
        />
        <StatCard
          title="Inference Latency"
          value={`${analytics.average_inference_time_ms.toFixed(1)} ms`}
          subtitle="Apple Silicon / CUDA forward pass"
          icon={<Zap className="w-5 h-5 text-sky-400" />}
          accentColor="sky"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown Bar Chart */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
          <div className="mb-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 font-mono">
              RDD2022 Distress Class Breakdown
            </h3>
            <p className="text-xs text-slate-400">Total detected instances by pavement damage category</p>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryBarData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} fontFamily="monospace" />
                <YAxis stroke="#64748b" fontSize={11} fontFamily="monospace" allowDecimals={false} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-slate-900 border border-slate-700 p-2.5 rounded-lg shadow-xl text-xs font-mono">
                          <p className="text-amber-400 font-bold">{data.name}: {data.fullName}</p>
                          <p className="text-white mt-1">Instances: {data.count}</p>
                          <p className="text-slate-400">Share: {data.percentage}%</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="count" fill="#f59e0b" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800/80 grid grid-cols-4 gap-2 text-center text-[11px] font-mono text-slate-400">
            <div>D00: Longitudinal</div>
            <div>D10: Transverse</div>
            <div>D20: Alligator</div>
            <div>D40: Pothole</div>
          </div>
        </div>

        {/* Severity Distribution Donut Chart */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
          <div className="mb-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 font-mono">
              Severity Assessment Proportion
            </h3>
            <p className="text-xs text-slate-400">Road Damage Severity Index (RDSI) distribution</p>
          </div>

          <div className="h-64 w-full flex items-center justify-center">
            {severityPieData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={severityPieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={85}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {severityPieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} stroke="#0f172a" strokeWidth={2} />
                    ))}
                  </Pie>
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0];
                        return (
                          <div className="bg-slate-900 border border-slate-700 p-2.5 rounded-lg shadow-xl text-xs font-mono">
                            <p style={{ color: data.payload.color }} className="font-bold">{data.name}</p>
                            <p className="text-white mt-1">Count: {data.value}</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Legend
                    verticalAlign="bottom"
                    height={36}
                    formatter={(val) => <span className="text-xs text-slate-300 font-mono">{val}</span>}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-xs text-slate-500 font-mono">No inspection data recorded yet.</p>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span>Low Risk: &lt; 25 RDSI</span>
            <span>Medium Risk: 25 - 59 RDSI</span>
            <span>High Hazard: &ge; 60 RDSI</span>
          </div>
        </div>
      </div>

      {/* Activity Timeline Chart */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="mb-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 font-mono">
            Inspection Throughput & Hazard Volume
          </h3>
          <p className="text-xs text-slate-400">Daily survey density and high-hazard pavement detection history</p>
        </div>

        <div className="h-60 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={analytics.timeline} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="totalColor" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="highColor" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" stroke="#64748b" fontSize={11} fontFamily="monospace" />
              <YAxis stroke="#64748b" fontSize={11} fontFamily="monospace" allowDecimals={false} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
              />
              <Area type="monotone" dataKey="inspections_count" name="Total Scans" stroke="#f59e0b" fillOpacity={1} fill="url(#totalColor)" strokeWidth={2} />
              <Area type="monotone" dataKey="high_severity_count" name="Critical Hazards" stroke="#ef4444" fillOpacity={1} fill="url(#highColor)" strokeWidth={2} />
              <Legend verticalAlign="top" height={30} formatter={(val) => <span className="text-xs text-slate-300 font-mono">{val}</span>} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Inspections Table */}
      <div className="glass-panel rounded-2xl overflow-hidden border border-slate-800">
        <div className="px-6 py-4 bg-slate-900/80 border-b border-slate-800/80 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 font-mono">
              Recent Inspection Log
            </h3>
            <p className="text-xs text-slate-400">Latest pavement scans processed by RoadGuard AI</p>
          </div>
          <button
            onClick={onNavigateDetect}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-500 hover:bg-amber-400 text-slate-950 transition-colors"
          >
            <span>New Scan</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {recentHistory.length === 0 ? (
          <div className="p-8 text-center text-slate-400 text-xs">
            No inspection records in database yet. Run an AI scan to populate.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/60 border-b border-slate-800 text-slate-400 font-mono uppercase text-[10px]">
                <tr>
                  <th className="py-3 px-4">Preview</th>
                  <th className="py-3 px-4">Filename / Location</th>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Defects</th>
                  <th className="py-3 px-4">Severity Level</th>
                  <th className="py-3 px-4">Latency</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {recentHistory.map((item) => (
                  <tr
                    key={item.id}
                    onClick={() => onSelectDetection(item.id)}
                    className="hover:bg-slate-900/60 transition-colors cursor-pointer group"
                  >
                    <td className="py-2.5 px-4">
                      <img
                        src={getFullImageUrl(item.annotated_image_url || item.original_image_url)}
                        alt="Thumbnail"
                        className="w-12 h-10 object-cover rounded-md border border-slate-800"
                      />
                    </td>
                    <td className="py-2.5 px-4">
                      <p className="font-semibold text-white group-hover:text-amber-400 transition-colors truncate max-w-xs">
                        {item.original_filename}
                      </p>
                      <p className="text-[11px] text-slate-400 truncate max-w-xs">
                        {item.location_notes || 'Road Link Unspecified'}
                      </p>
                    </td>
                    <td className="py-2.5 px-4 font-mono text-slate-400">
                      {new Date(item.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                    </td>
                    <td className="py-2.5 px-4 font-mono font-bold text-white">
                      {item.total_damages}
                    </td>
                    <td className="py-2.5 px-4">
                      <SeverityBadge level={item.severity_level} score={item.severity_score} size="sm" />
                    </td>
                    <td className="py-2.5 px-4 font-mono text-slate-400">
                      {item.inference_time_ms.toFixed(1)} ms
                    </td>
                    <td className="py-2.5 px-4 text-right">
                      <span className="text-amber-400 text-xs font-semibold group-hover:underline">
                        Details &rarr;
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

