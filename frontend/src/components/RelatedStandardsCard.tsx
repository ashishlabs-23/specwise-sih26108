"use client";

import React from "react";
import { Link2, ChevronRight, BookOpen, Layers, CheckCircle } from "lucide-react";
import { AnalysisResponse } from "@/types/api";

interface RelatedStandardsCardProps {
  response: AnalysisResponse;
  onSelectStandard?: (stdId: string) => void;
  onViewAll?: () => void;
}

export function RelatedStandardsCard({
  response,
  onSelectStandard,
  onViewAll,
}: RelatedStandardsCardProps) {
  const { related_standards, decision } = response;

  const getRelationshipBadge = (type: string, stdId: string) => {
    if (stdId.includes("14536")) return "Installation & Maintenance CoP";
    if (stdId.includes("9283")) return "Submersible Motor Specification";
    if (stdId.includes("11346")) return "Hydraulic Test & Acceptance";
    if (stdId.includes("10572")) return "Sampling & Inspection";
    if (type === "normative_reference") return "Normative Reference";
    if (type === "test_method") return "Test Standard";
    if (type === "related_practice") return "Code of Practice";
    return type.replace("_", " ");
  };

  const getTitle = (stdId: string) => {
    if (stdId.includes("14536"))
      return "Selection, Installation, Operation and Maintenance of Submersible Pumpset — Code of Practice";
    if (stdId.includes("9283"))
      return "Line Operated A.C. Motors for Submersible Pumpsets — Specification";
    if (stdId.includes("11346"))
      return "Tests for Agricultural and Water Supply Pumps — Code of Acceptance";
    if (stdId.includes("10572"))
      return "Methods of Sampling for Pumps";
    return "Referenced Indian Standard";
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 sm:p-6 shadow-sm flex flex-col justify-between hover:border-slate-300 transition-all w-full min-w-0">
      <div className="min-w-0">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 gap-2 min-w-0">
          <div className="flex items-center gap-2 min-w-0">
            <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center flex-shrink-0">
              <Link2 className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <h3 className="text-base font-bold text-slate-900 truncate">
                Related Standards
              </h3>
              <span className="text-[11px] text-slate-500 font-medium block truncate">
                (for reference & compliance)
              </span>
            </div>
          </div>
          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 flex-shrink-0">
            {related_standards.length} linked
          </span>
        </div>

        {/* List of Related Standards */}
        <div className="mt-4 space-y-3 min-w-0">
          {related_standards.length === 0 ? (
            <div className="py-6 text-center text-xs text-slate-500 break-words">
              {decision === "OUT_OF_CORPUS"
                ? "No related standards available for out-of-corpus query."
                : "No normative references found in current graph."}
            </div>
          ) : (
            related_standards.slice(0, 2).map((rel, idx) => (
              <div
                key={idx}
                onClick={() => onSelectStandard && onSelectStandard(rel.to_standard)}
                className="group p-3 rounded-xl border border-slate-200 hover:border-blue-400 bg-slate-50/50 hover:bg-blue-50/30 transition-all cursor-pointer min-w-0"
              >
                <div className="flex items-start justify-between gap-2 min-w-0">
                  <div className="flex items-start gap-2.5 min-w-0 flex-1">
                    <div className="w-6 h-6 rounded-md bg-white border border-slate-200 flex items-center justify-center text-slate-500 mt-0.5 flex-shrink-0">
                      <BookOpen className="w-3.5 h-3.5" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-1.5">
                        <span className="text-xs sm:text-sm font-bold font-mono text-slate-900 break-words">
                          {rel.to_standard}
                        </span>
                        {rel.hop && (
                          <span className="text-[10px] px-1 py-0.2 rounded bg-slate-200/70 text-slate-600 font-semibold flex-shrink-0">
                            Hop {rel.hop}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-slate-600 line-clamp-2 mt-0.5 break-words">
                        {getTitle(rel.to_standard)}
                      </p>
                      <div className="mt-2">
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-blue-100/70 text-[#0A3871] break-words">
                          {getRelationshipBadge(rel.relationship_type, rel.to_standard)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-[#0B57D0] transition-transform group-hover:translate-x-0.5 mt-1 flex-shrink-0" />
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
          onClick={onViewAll}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#0B57D0] hover:text-[#0A47A8] transition-colors cursor-pointer"
        >
          <span>View all related standards</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}
