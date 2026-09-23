"use client";

import React from "react";
import { FileText, ArrowRight, Check, Tag } from "lucide-react";
import { AnalysisResponse, StandardRecord } from "@/types/api";

interface KeyDetailsCardProps {
  response: AnalysisResponse;
  primaryStandard?: StandardRecord | null;
  onViewStandardOnBis?: () => void;
}

export function KeyDetailsCard({
  response,
  primaryStandard,
  onViewStandardOnBis,
}: KeyDetailsCardProps) {
  const { decision, applicability, lifecycle, candidates } = response;
  const strongApp = applicability.find((a) => a.result === "strong");
  const stdId = strongApp?.standard_id || candidates[0]?.standard_id || "N/A";

  const lc = lifecycle.find((l) => l.standard_id === stdId);
  const statusLabel =
    lc?.state === "supported"
      ? "Active (In Force)"
      : lc?.state === "warning"
      ? "Revision / Superseded Warning"
      : decision === "RECOMMEND"
      ? "Active (In Force)"
      : "Not Formally Confirmed";

  // Infer product and use from primary standard or input text
  const getProduct = () => {
    if (stdId.includes("14220")) return "Openwell Submersible Pumpset";
    if (stdId.includes("8034")) return "Borewell / Borehole Submersible Pumpset";
    if (stdId.includes("9079")) return "Monoset Pump for Clear Cold Water";
    if (primaryStandard?.product_terms?.length) return primaryStandard.product_terms.join(", ");
    return response.requirements.find((r) => r.category === "product")?.product || "Pumpset Equipment";
  };

  const getUse = () => {
    if (stdId.includes("14220")) return "Agricultural irrigation & water supply";
    if (stdId.includes("8034")) return "Borewell agricultural irrigation / water supply";
    if (stdId.includes("9079")) return "Agricultural & municipal clear water supply";
    if (primaryStandard?.application_terms?.length) return primaryStandard.application_terms.join(", ");
    return "Industrial / Agricultural Fluid Transfer";
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col justify-between hover:border-slate-300 transition-all">
      <div>
        {/* Card Header */}
        <div className="flex items-center gap-2 pb-4 border-b border-slate-100">
          <div className="w-8 h-8 rounded-lg bg-blue-50 text-[#0B57D0] flex items-center justify-center">
            <FileText className="w-4 h-4" />
          </div>
          <h3 className="text-base font-bold text-slate-900">Key Details</h3>
        </div>

        {/* Details Table */}
        <dl className="mt-4 space-y-3.5 text-xs sm:text-sm">
          <div className="flex items-start justify-between gap-2">
            <dt className="text-slate-500 font-medium">Product</dt>
            <dd className="text-slate-900 font-semibold text-right max-w-[60%]">
              {decision === "OUT_OF_CORPUS" ? "Outside Pump Sector" : getProduct()}
            </dd>
          </div>

          <div className="flex items-start justify-between gap-2">
            <dt className="text-slate-500 font-medium">Use / Application</dt>
            <dd className="text-slate-900 font-semibold text-right max-w-[60%]">
              {decision === "OUT_OF_CORPUS" ? "N/A" : getUse()}
            </dd>
          </div>

          <div className="flex items-start justify-between gap-2">
            <dt className="text-slate-500 font-medium">Standard No.</dt>
            <dd className="text-[#0B57D0] font-mono font-bold text-right">
              {stdId}
            </dd>
          </div>

          <div className="flex items-start justify-between gap-2">
            <dt className="text-slate-500 font-medium">Status</dt>
            <dd className="text-right">
              <span
                className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold ${
                  lc?.state === "warning"
                    ? "bg-amber-100 text-amber-800 border border-amber-300"
                    : "bg-emerald-100 text-emerald-800 border border-emerald-200"
                }`}
              >
                <span className="w-1.5 h-1.5 rounded-full bg-current" />
                <span>{statusLabel}</span>
              </span>
            </dd>
          </div>

          {primaryStandard?.scope && (
            <div className="pt-2 border-t border-slate-100">
              <dt className="text-slate-500 text-xs font-medium mb-1">Scope</dt>
              <dd className="text-slate-600 text-xs leading-relaxed line-clamp-3">
                {primaryStandard.scope}
              </dd>
            </div>
          )}
        </dl>
      </div>

      {/* Footer Link */}
      <div className="mt-6 pt-4 border-t border-slate-100">
        <a
          href="https://www.services.bis.gov.in"
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#0B57D0] hover:text-[#0A47A8] transition-colors"
        >
          <span>View standard on BIS portal</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </a>
      </div>
    </div>
  );
}
