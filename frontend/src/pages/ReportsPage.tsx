import React, { useState, useEffect } from 'react';
import { apiService, getFullImageUrl, getFullApiUrl } from '../services/api';
import { HistoryItem } from '../types';
import { SeverityBadge } from '../components/SeverityBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';
import {
  FileText,
  Download,
  Printer,
  ShieldCheck,
  Search,
} from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedRecord, setSelectedRecord] = useState<HistoryItem | null>(null);
  const [inspectorName, setInspectorName] = useState<string>('Senior Highway Engineer');
  const [reportTitle, setReportTitle] = useState<string>('Pavement Structural Distress Audit Report');
  const [notes, setNotes] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const data = await apiService.getHistory({ limit: 50 });
      setItems(data.items);
      if (data.items.length > 0) {
        setSelectedRecord(data.items[0]);
      }
    } catch (err) {
      console.error('Failed to load records for reports:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  const handleGeneratePdf = async () => {
    if (!selectedRecord) return;
    setIsGenerating(true);
    try {
      const res = await apiService.generateReport(selectedRecord.id, {
        title: reportTitle,
        inspector_name: inspectorName,
        location_notes: selectedRecord.location_notes,
        additional_notes: notes,
      });
      window.open(getFullApiUrl(res.download_url), '_blank');
    } catch (err) {
      console.error('Failed to generate report:', err);
      // Fallback direct URL
      window.open(apiService.getPdfUrl(selectedRecord.id), '_blank');
    } finally {
      setIsGenerating(false);
    }
  };

  const filteredItems = items.filter((item) =>
    item.original_filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (item.location_notes && item.location_notes.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="py-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
      {/* Header */}
      <div className="border-b border-slate-900 pb-4">
        <h1 className="text-2xl sm:text-3xl font-black font-mono tracking-tight text-white flex items-center gap-3">
          <FileText className="w-8 h-8 text-amber-400" />
          <span>Municipal Engineering PDF Reports</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Generate formal, publication-ready civil infrastructure inspection documents formatted per ASTM D6433 & PCI standards.
        </p>
      </div>

      {loading ? (
        <LoadingSpinner message="Loading Report Generator..." submessage="Compiling available inspection records..." />
      ) : items.length === 0 ? (
        <div className="glass-panel rounded-2xl p-16 text-center border border-slate-800 max-w-lg mx-auto">
          <FileText className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-bold text-white font-mono">No Records Available</h3>
          <p className="text-xs text-slate-400 mt-1">
            Perform an AI road inspection first to generate downloadable PDF reports.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left: Inspection Selection List (5 cols) */}
          <div className="lg:col-span-5 space-y-4">
            <div className="glass-panel rounded-2xl p-4 border border-slate-800">
              <div className="relative mb-3">
                <input
                  type="text"
                  placeholder="Filter records..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
                />
                <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              </div>

              <div className="space-y-2 max-h-[560px] overflow-y-auto pr-1">
                {filteredItems.map((item) => {
                  const isSelected = selectedRecord?.id === item.id;
                  return (
                    <div
                      key={item.id}
                      onClick={() => setSelectedRecord(item)}
                      className={`p-3 rounded-xl border transition-all duration-200 cursor-pointer flex items-center justify-between gap-3 ${
                        isSelected
                          ? 'bg-amber-500/10 border-amber-500/80 shadow-md'
                          : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <img
                          src={getFullImageUrl(item.annotated_image_url || item.original_image_url)}
                          alt="Thumbnail"
                          className="w-12 h-12 rounded-lg object-cover border border-slate-800 shrink-0"
                        />
                        <div className="min-w-0">
                          <p className={`text-xs font-bold truncate ${isSelected ? 'text-amber-400' : 'text-white'}`}>
                            {item.original_filename}
                          </p>
                          <p className="text-[10px] text-slate-400 truncate">
                            {item.location_notes || 'Road Link Unspecified'}
                          </p>
                          <p className="text-[9px] text-slate-500 font-mono">
                            {new Date(item.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>

                      <div className="shrink-0 text-right">
                        <SeverityBadge level={item.severity_level} score={item.severity_score} size="sm" showScore={false} />
                        <span className="text-[10px] font-mono text-slate-400 block mt-1">
                          {item.total_damages} defects
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Right: Report Configurator & Live Preview (7 cols) */}
          {selectedRecord && (
            <div className="lg:col-span-7 space-y-6">
              <div className="glass-panel-glow rounded-2xl p-6 border border-amber-500/30 space-y-6">
                <div>
                  <h3 className="text-base font-bold text-white font-mono flex items-center gap-2">
                    <Printer className="w-5 h-5 text-amber-400" />
                    <span>Configure Report Metadata</span>
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Customize author credentials and notes before exporting the certified PDF.
                  </p>
                </div>

                <div className="space-y-4">
                  {/* Title */}
                  <div className="space-y-1">
                    <label className="text-xs text-slate-300 font-semibold">Report Title:</label>
                    <input
                      type="text"
                      value={reportTitle}
                      onChange={(e) => setReportTitle(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:border-amber-500"
                    />
                  </div>

                  {/* Inspector Name */}
                  <div className="space-y-1">
                    <label className="text-xs text-slate-300 font-semibold">Authorized Inspector / Engineer:</label>
                    <input
                      type="text"
                      value={inspectorName}
                      onChange={(e) => setInspectorName(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:border-amber-500"
                    />
                  </div>

                  {/* Additional notes */}
                  <div className="space-y-1">
                    <label className="text-xs text-slate-300 font-semibold">Maintenance Directives / Observations:</label>
                    <textarea
                      rows={3}
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      placeholder="e.g. Section exhibits longitudinal cracking along center joint. Recommend hot-pour elastomeric sealant prior to winter freeze-thaw."
                      className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:border-amber-500"
                    />
                  </div>
                </div>

                {/* Selected Scan Preview Card */}
                <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block font-semibold">
                    Document Inclusion Summary:
                  </span>
                  <div className="flex items-center gap-4">
                    <img
                      src={getFullImageUrl(selectedRecord.annotated_image_url || selectedRecord.original_image_url)}
                      alt="Annotated Scan"
                      className="w-24 h-16 object-cover rounded-lg border border-slate-800"
                    />
                    <div className="space-y-1 text-xs">
                      <p className="font-semibold text-white">{selectedRecord.original_filename}</p>
                      <div className="flex items-center gap-3">
                        <SeverityBadge level={selectedRecord.severity_level} score={selectedRecord.severity_score} size="sm" />
                        <span className="font-mono text-slate-400">{selectedRecord.total_damages} localized defects</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Export Button */}
                <div className="pt-2 flex justify-end">
                  <button
                    onClick={handleGeneratePdf}
                    disabled={isGenerating}
                    className="w-full sm:w-auto px-6 py-3 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-lg shadow-amber-500/25 transition-all cursor-pointer"
                  >
                    <Download className="w-4 h-4" />
                    <span>{isGenerating ? 'Compiling PDF...' : 'Download PDF Inspection Report'}</span>
                  </button>
                </div>
              </div>

              {/* Compliance & Standards Note */}
              <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-2 text-xs text-slate-400">
                <div className="flex items-center gap-2 text-slate-200 font-bold font-mono">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span>Report Formulation Specifications</span>
                </div>
                <p className="leading-relaxed">
                  Every RoadGuard PDF includes certified cryptographic timestamps, high-contrast bounding box overlays, class-by-class deduct calculations, and engineer sign-off blocks complying with municipal Department of Transportation (DOT) documentation protocols.
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
