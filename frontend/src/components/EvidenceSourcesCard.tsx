"use client";

import React from "react";
import { BookMarked, ExternalLink, CheckCircle2, FileText, ChevronRight, Bookmark } from "lucide-react";
import { AnalysisResponse, Evidence } from "@/types/api";

interface EvidenceSourcesCardProps {
  response: AnalysisResponse;
  onViewAllSources?: () => void;
}

export function EvidenceSourcesCard({
  response,
  onViewAllSources,
}: EvidenceSourcesCardProps) {
  const { evidence, decision } = response;

  // Deduplicate unique sources
  const uniqueSourceIds = Array.from(new Set(evidence.map((e) => e.source_id)));

  const truncateUrl = (url: string) => {
    try {
      const u = new URL(url);
      return `${u.hostname}${u.pathname.length > 20 ? u.pathname.substring(0, 20) + "..." : u.pathname}`;
    } catch {
      return url.length > 30 ? url.substring(0, 30) + "..." : url;
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 sm:p-6 shadow-sm flex flex-col justify-between hover:border-slate-300 transition-all w-full min-w-0">
      <div className="min-w-0">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 gap-2 min-w-0">
          <div className="flex items-center gap-2 min-w-0">
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center flex-shrink-0">
              <BookMarked className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <h3 className="text-base font-bold text-slate-900 truncate">
                Evidence & Sources
              </h3>
              <p className="text-[11px] text-slate-500 font-medium truncate">
                {uniqueSourceIds.length} source docs • {evidence.filter((e) => e.verified).length} verified claims
              </p>
            </div>
          </div>
          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex-shrink-0">
            {evidence.filter((e) => e.verified).length} Verified
          </span>
        </div>

        {/* Evidence items */}
        <div className="mt-4 space-y-3 min-w-0">
          {evidence.length === 0 ? (
            <div className="py-6 text-center text-xs text-slate-500 break-words">
              {decision === "OUT_OF_CORPUS"
                ? "No evidence records required for out-of-corpus query."
                : "No verified evidence records."}
            </div>
          ) : (
            evidence.slice(0, 2).map((ev, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl border border-slate-200 bg-slate-50/50 flex flex-col gap-2 min-w-0"
              >
                {/* Evidence ID + Verification Badge */}
                <div className="flex flex-wrap items-center justify-between gap-1.5 min-w-0">
                  <div className="flex items-center gap-1.5 min-w-0">
                    <span className="font-mono text-[10px] sm:text-xs font-bold bg-white px-2 py-0.5 rounded border border-slate-200 text-slate-800">
                      {ev.evidence_id}
                    </span>
                    {(ev.page || ev.section) && (
                      <span className="text-[10px] text-slate-500 font-medium">
                        {ev.page ? `p. ${ev.page}` : ""} {ev.section ? `§ ${ev.section}` : ""}
                      </span>
                    )}
                  </div>
                  {ev.verified ? (
                    <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-50 px-1.5 py-0.2 rounded border border-emerald-200 flex-shrink-0">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>Verified BIS</span>
                    </span>
                  ) : (
                    <span className="text-[10px] font-bold text-amber-700 bg-amber-50 px-1.5 py-0.2 rounded border border-amber-200 flex-shrink-0">
                      Unverified
                    </span>
                  )}
                </div>

                {/* Concise Evidence Finding */}
                <p className="text-xs text-slate-700 font-medium leading-relaxed break-words">
                  "{ev.text}"
                </p>

                {/* Source Document Reference & Link */}
                <div className="pt-2 border-t border-slate-200/60 flex flex-wrap items-center justify-between gap-1 text-[11px] text-slate-500">
                  <div className="flex items-center gap-1 truncate max-w-[60%]">
                    <FileText className="w-3 h-3 text-slate-400 flex-shrink-0" />
                    <span className="truncate font-semibold text-slate-700" title={ev.source_name}>
                      {ev.source_name}
                    </span>
                  </div>
                  {ev.url && (
                    <a
                      href={ev.url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 text-[#0B57D0] hover:underline font-mono text-[10px] flex-shrink-0"
                    >
                      <span>Link</span>
                      <ExternalLink className="w-2.5 h-2.5" />
                    </a>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Footer Link */}
      <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between">
        <span className="text-[11px] text-slate-500">
          Source = Document | Evidence = Verified Finding
        </span>
        <button
          type="button"
          onClick={onViewAllSources}
          className="inline-flex items-center gap-1 text-xs font-bold text-[#0B57D0] hover:text-[#0A47A8] transition-colors cursor-pointer"
        >
          <span>View all ({evidence.length})</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}
