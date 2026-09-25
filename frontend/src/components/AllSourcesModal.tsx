"use client";

import React, { useState } from "react";
import { X, ExternalLink, CheckCircle2, BookOpen, FileText, Layers, Bookmark } from "lucide-react";
import { Evidence } from "@/types/api";

interface AllSourcesModalProps {
  isOpen: boolean;
  onClose: () => void;
  evidence: Evidence[];
}

export function AllSourcesModal({ isOpen, onClose, evidence }: AllSourcesModalProps) {
  const [activeTab, setActiveTab] = useState<"evidence" | "sources">("evidence");

  if (!isOpen) return null;

  // Deduplicate unique sources
  const uniqueSourcesMap = new Map<
    string,
    { source_id: string; source_name: string; url: string; evidence_ids: string[] }
  >();

  evidence.forEach((ev) => {
    if (!uniqueSourcesMap.has(ev.source_id)) {
      uniqueSourcesMap.set(ev.source_id, {
        source_id: ev.source_id,
        source_name: ev.source_name,
        url: ev.url,
        evidence_ids: [ev.evidence_id],
      });
    } else {
      const existing = uniqueSourcesMap.get(ev.source_id)!;
      if (!existing.evidence_ids.includes(ev.evidence_id)) {
        existing.evidence_ids.push(ev.evidence_id);
      }
    }
  });

  const uniqueSources = Array.from(uniqueSourcesMap.values());

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-2 sm:p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[88vh] sm:max-h-[85vh] flex flex-col shadow-2xl border border-slate-200 relative animate-in fade-in zoom-in-95 duration-150 overflow-hidden">
        
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-slate-200 flex items-center justify-between bg-slate-50 rounded-t-2xl gap-2">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center font-bold flex-shrink-0">
              <BookOpen className="w-5 h-5" />
            </div>
            <div className="min-w-0">
              <h3 className="text-sm sm:text-base font-bold text-slate-900 truncate">
                Evidence & Sources Provenance
              </h3>
              <p className="text-[11px] sm:text-xs text-slate-500 font-medium truncate">
                {uniqueSources.length} Source Documents • {evidence.length} Evidence Claims
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-200 cursor-pointer flex-shrink-0"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center px-4 sm:px-6 pt-3 border-b border-slate-200 bg-white gap-2">
          <button
            type="button"
            onClick={() => setActiveTab("evidence")}
            className={`pb-2.5 px-3 text-xs font-bold border-b-2 transition-all cursor-pointer ${
              activeTab === "evidence"
                ? "border-[#0B57D0] text-[#0B57D0]"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            Evidence Findings ({evidence.length})
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("sources")}
            className={`pb-2.5 px-3 text-xs font-bold border-b-2 transition-all cursor-pointer ${
              activeTab === "sources"
                ? "border-[#0B57D0] text-[#0B57D0]"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            Source Documents ({uniqueSources.length})
          </button>
        </div>

        {/* Content list */}
        <div className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-4 divide-y divide-slate-100 min-w-0">
          {activeTab === "evidence" && (
            <div className="space-y-4">
              {evidence.map((ev, idx) => (
                <div key={idx} className="pt-4 first:pt-0 min-w-0">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono text-xs font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded break-words">
                        {ev.evidence_id}
                      </span>
                      {(ev.page || ev.section) && (
                        <span className="text-[11px] text-slate-500 font-medium">
                          {ev.page ? `Page ${ev.page}` : ""} {ev.section ? `§ ${ev.section}` : ""}
                        </span>
                      )}
                      {ev.verified ? (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 flex-shrink-0">
                          <CheckCircle2 className="w-3 h-3" />
                          <span>Verified Official BIS</span>
                        </span>
                      ) : (
                        <span className="text-[10px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200 flex-shrink-0">
                          Unverified
                        </span>
                      )}
                    </div>
                  </div>

                  <p className="text-xs sm:text-sm text-slate-700 mt-2 font-medium leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-200 break-words">
                    "{ev.text}"
                  </p>

                  <div className="mt-2 flex flex-wrap items-center justify-between gap-1 text-xs">
                    <span className="text-slate-600 text-[11px] font-semibold truncate max-w-[70%]">
                      Source: {ev.source_name} ({ev.source_id})
                    </span>
                    {ev.url && (
                      <a
                        href={ev.url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-[#0B57D0] hover:underline font-mono text-[11px] max-w-full truncate"
                      >
                        <span>Open Source URL</span>
                        <ExternalLink className="w-3 h-3 flex-shrink-0" />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === "sources" && (
            <div className="space-y-4">
              <p className="text-xs text-slate-500">
                Original BIS documents referenced by verified evidence claims in this analysis.
              </p>
              {uniqueSources.map((src, idx) => (
                <div key={idx} className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/70 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4 text-[#0B57D0]" />
                      <h4 className="text-xs sm:text-sm font-bold text-slate-900">{src.source_name}</h4>
                    </div>
                    <span className="font-mono text-[10px] bg-white px-2 py-0.5 rounded border border-slate-200 text-slate-600">
                      {src.source_id}
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
                    <span className="text-slate-500 font-medium">Evidence Citations ({src.evidence_ids.length}):</span>
                    {src.evidence_ids.map((eid) => (
                      <span key={eid} className="font-mono bg-blue-50 text-blue-800 px-1.5 py-0.2 rounded text-[10px] font-semibold border border-blue-200">
                        {eid}
                      </span>
                    ))}
                  </div>

                  {src.url && (
                    <div className="pt-1 flex justify-end">
                      <a
                        href={src.url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-xs font-semibold text-[#0B57D0] hover:underline font-mono"
                      >
                        <span>Open Official Document URL</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-200 bg-slate-50 flex justify-between items-center rounded-b-2xl text-xs text-slate-500">
          <span>Source = Original Document • Evidence = Verified Finding</span>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-slate-900 text-white hover:bg-slate-800 cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
