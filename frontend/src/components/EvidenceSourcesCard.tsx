"use client";

import React from "react";
import { BookMarked, ExternalLink, CheckCircle2, FileText, ChevronRight } from "lucide-react";
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
            <h3 className="text-base font-bold text-slate-900 truncate">
              Evidence / Sources
            </h3>
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
                className="p-3 rounded-xl border border-slate-200 bg-slate-50/50 flex items-start justify-between gap-3 min-w-0"
              >
                <div className="flex items-start gap-2.5 min-w-0 flex-1">
                  <div className="w-6 h-6 rounded-md bg-white border border-slate-200 flex items-center justify-center text-slate-600 mt-0.5 flex-shrink-0">
                    <FileText className="w-3.5 h-3.5" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-1.5 min-w-0">
                      <h4 className="text-xs font-bold text-slate-900 truncate">
                        {ev.source_name}
                      </h4>
                      {ev.verified && (
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                      )}
                    </div>
                    <p className="text-[11px] text-slate-600 line-clamp-2 mt-0.5 break-words">
                      {ev.text}
                    </p>
                    <a
                      href={ev.url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 text-[11px] text-[#0B57D0] hover:underline mt-1 font-mono max-w-full truncate"
                    >
                      <span className="truncate">{truncateUrl(ev.url)}</span>
                      <ExternalLink className="w-3 h-3 flex-shrink-0" />
                    </a>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Footer Link */}
      <div className="mt-6 pt-4 border-t border-slate-100">
        <button
          type="button"
          onClick={onViewAllSources}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#0B57D0] hover:text-[#0A47A8] transition-colors cursor-pointer"
        >
          <span>View all sources</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}
