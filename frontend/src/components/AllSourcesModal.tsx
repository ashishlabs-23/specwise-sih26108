"use client";

import React from "react";
import { X, ExternalLink, CheckCircle2, BookOpen } from "lucide-react";
import { Evidence } from "@/types/api";

interface AllSourcesModalProps {
  isOpen: boolean;
  onClose: () => void;
  evidence: Evidence[];
}

export function AllSourcesModal({ isOpen, onClose, evidence }: AllSourcesModalProps) {
  if (!isOpen) return null;

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
                All Verified Sources & Evidence
              </h3>
              <p className="text-[11px] sm:text-xs text-slate-500 font-medium truncate">
                Official BIS publications, guidelines, and committee documents
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

        {/* Content list */}
        <div className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-4 divide-y divide-slate-100 min-w-0">
          {evidence.map((ev, idx) => (
            <div key={idx} className="pt-4 first:pt-0 min-w-0">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xs font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded break-words">
                    {ev.evidence_id}
                  </span>
                  {ev.verified && (
                    <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 flex-shrink-0">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>Verified Official BIS</span>
                    </span>
                  )}
                </div>
              </div>

              <h4 className="text-xs sm:text-sm font-bold text-slate-900 mt-2 break-words">
                {ev.source_name}
              </h4>
              <p className="text-xs text-slate-600 mt-1 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-200 break-words">
                "{ev.text}"
              </p>

              <div className="mt-2 flex flex-wrap items-center justify-between gap-1 text-xs">
                <span className="text-slate-400 text-[11px] font-mono">
                  Source ID: {ev.source_id}
                </span>
                <a
                  href={ev.url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-[#0B57D0] hover:underline font-mono text-[11px] max-w-full truncate"
                >
                  <span className="truncate">Open Source URL</span>
                  <ExternalLink className="w-3 h-3 flex-shrink-0" />
                </a>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-200 bg-slate-50 flex justify-end rounded-b-2xl">
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
