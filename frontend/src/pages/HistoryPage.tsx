import React, { useState, useEffect } from 'react';
import { apiService, getFullImageUrl } from '../services/api';
import { HistoryItem } from '../types';
import { SeverityBadge } from '../components/SeverityBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';
import {
  Search,
  Filter,
  FileText,
  Trash2,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  Clock,
  MapPin,
  RefreshCw,
} from 'lucide-react';

interface HistoryPageProps {
  onSelectDetection: (id: string) => void;
}

export const HistoryPage: React.FC<HistoryPageProps> = ({ onSelectDetection }) => {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [limit] = useState<number>(8);
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await apiService.getHistory({
        page,
        limit,
        severity: severityFilter !== 'all' ? severityFilter : undefined,
        search: searchQuery.trim() || undefined,
      });
      setItems(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page, severityFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchHistory();
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this inspection audit record?')) {
      return;
    }
    setDeletingId(id);
    try {
      await apiService.deleteDetection(id);
      fetchHistory();
    } catch (err) {
      console.error('Failed to delete detection:', err);
    } finally {
      setDeletingId(null);
    }
  };

  const handleDownloadPdf = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    window.open(apiService.getPdfUrl(id), '_blank');
  };

  return (
    <div className="py-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-900 pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black font-mono tracking-tight text-white">
            Pavement Inspection Audit History
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Complete database of past automated surveys, detected distress categories, and severity ratings
          </p>
        </div>

        <button
          onClick={fetchHistory}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5 text-amber-400" />
          <span>Refresh List</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-panel rounded-2xl p-4 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Search */}
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-80">
          <input
            type="text"
            placeholder="Search by location notes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
          />
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
        </form>

        {/* Filters */}
        <div className="flex items-center gap-3 w-full md:w-auto justify-end">
          <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
            <Filter className="w-3.5 h-3.5 text-amber-400" />
            <span>Severity:</span>
          </div>
          <select
            value={severityFilter}
            onChange={(e) => {
              setSeverityFilter(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-amber-500 font-mono"
          >
            <option value="all">All Severities</option>
            <option value="High">High Hazard</option>
            <option value="Medium">Medium Risk</option>
            <option value="Low">Low / Minor</option>
          </select>
        </div>
      </div>

      {/* Content Area */}
      {loading ? (
        <LoadingSpinner message="Querying Inspection Archive..." submessage="Fetching historical detection records from PostgreSQL..." />
      ) : items.length === 0 ? (
        <div className="glass-panel rounded-2xl p-16 text-center border border-slate-800 max-w-lg mx-auto">
          <Clock className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-bold text-white font-mono">No Records Match Filters</h3>
          <p className="text-xs text-slate-400 mt-1">
            Try adjusting your search query or run a new inspection.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {items.map((item) => (
            <div
              key={item.id}
              onClick={() => onSelectDetection(item.id)}
              className="glass-panel rounded-2xl overflow-hidden border border-slate-800 hover:border-amber-500/50 hover:shadow-xl hover:shadow-amber-500/5 transition-all duration-300 cursor-pointer flex flex-col justify-between group"
            >
              <div>
                {/* Thumbnail Preview */}
                <div className="relative h-44 w-full bg-slate-950 overflow-hidden border-b border-slate-800">
                  <img
                    src={getFullImageUrl(item.annotated_image_url || item.original_image_url)}
                    alt="Road thumbnail"
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute top-2.5 right-2.5">
                    <SeverityBadge level={item.severity_level} score={item.severity_score} size="sm" />
                  </div>
                  <div className="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-slate-950/80 backdrop-blur-sm border border-slate-800 font-mono text-[10px] text-amber-400">
                    {item.total_damages} Defects
                  </div>
                </div>

                {/* Details */}
                <div className="p-4 space-y-2">
                  <h4 className="text-xs font-bold text-white truncate font-mono group-hover:text-amber-400 transition-colors">
                    {item.original_filename}
                  </h4>

                  <p className="text-[11px] text-slate-400 flex items-center gap-1.5 truncate">
                    <MapPin className="w-3 h-3 text-slate-500 shrink-0" />
                    <span>{item.location_notes || 'Road Link Unspecified'}</span>
                  </p>

                  <p className="text-[10px] text-slate-500 font-mono flex items-center gap-1.5">
                    <Clock className="w-3 h-3" />
                    <span>{new Date(item.created_at).toLocaleString()}</span>
                  </p>

                  {/* Damage pills */}
                  <div className="pt-2 flex flex-wrap gap-1">
                    {Object.entries(item.damage_summary || {}).map(([code, count]) => (
                      <span
                        key={code}
                        className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800/80 text-slate-300 border border-slate-700/60"
                      >
                        {code}: {count}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="px-4 py-3 bg-slate-900/60 border-t border-slate-800/80 flex items-center justify-between">
                <button
                  onClick={(e) => handleDownloadPdf(item.id, e)}
                  className="p-1.5 text-slate-400 hover:text-amber-400 hover:bg-slate-800 rounded-lg transition-colors flex items-center gap-1 text-[11px] font-medium"
                  title="Download PDF Report"
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>PDF</span>
                </button>

                <div className="flex items-center gap-2">
                  <button
                    onClick={(e) => handleDelete(item.id, e)}
                    disabled={deletingId === item.id}
                    className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors"
                    title="Delete record"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>

                  <span className="text-amber-400 text-xs font-semibold flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
                    <span>View</span>
                    <ExternalLink className="w-3 h-3" />
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="pt-4 flex items-center justify-between border-t border-slate-800 text-xs text-slate-400">
          <span className="font-mono">
            Showing {(page - 1) * limit + 1} - {Math.min(page * limit, total)} of {total} records
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-mono px-2 text-slate-200">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
