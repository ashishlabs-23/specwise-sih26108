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
  const contextOnly = decision === "ABSTAIN" || decision === "OUT_OF_CORPUS";

  const getRoleBadge = (type: string, stdId: string) => {
    if (stdId.includes("14536") || type === "related_practice") {
      return { label: "CODE OF PRACTICE", style: "bg-purple-100 text-purple-800 border-purple-200" };
    }
    if (stdId.includes("11346") || type === "test_method") {
      return { label: "TEST METHOD", style: "bg-amber-100 text-amber-800 border-amber-200" };
    }
    if (type === "normative_reference") {
      return { label: "RELATED STANDARD", style: "bg-indigo-100 text-indigo-800 border-indigo-200" };
    }
    return { label: "RELATED STANDARD", style: "bg-slate-100 text-slate-700 border-slate-200" };
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
    if (stdId.includes("1239"))
      return "Mild Steel Tubes, Tubulars and Other Wrought Steel Fittings (GI Pipes)";
    if (stdId.includes("694"))
      return "PVC Insulated Cables for Working Voltages up to 1100 V";
    if (stdId.includes("1554"))
      return "PVC Insulated (Heavy Duty) Electric Cables for Working Voltages up to 1100 V";
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
              <p className="text-[11px] text-slate-500 font-medium truncate">
                Normative refs, test methods & practice codes
              </p>
              {contextOnly && related_standards.length > 0 && (
                <p className="text-[10px] font-semibold text-amber-700">
                  Context only — not a recommendation
                </p>
              )}
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
            related_standards.slice(0, 2).map((rel, idx) => {
              const roleInfo = getRoleBadge(rel.relationship_type, rel.to_standard);
              return (
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
                          <span className={`text-[9px] px-1.5 py-0.2 rounded font-extrabold uppercase border ${roleInfo.style}`}>
                            {roleInfo.label}
                          </span>
                          {rel.hop && (
                            <span className="text-[10px] px-1 py-0.2 rounded bg-slate-200/70 text-slate-600 font-semibold flex-shrink-0">
                              Hop {rel.hop}
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-slate-600 line-clamp-2 mt-1 break-words">
                          {getTitle(rel.to_standard)}
                        </p>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-[#0B57D0] transition-transform group-hover:translate-x-0.5 mt-1 flex-shrink-0" />
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Footer Link */}
      <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <span>Non-primary reference standards</span>
        <button
          type="button"
          onClick={onViewAll}
          className="inline-flex items-center gap-1 text-xs font-bold text-[#0B57D0] hover:text-[#0A47A8] transition-colors cursor-pointer"
        >
          <span>View all ({related_standards.length})</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}
