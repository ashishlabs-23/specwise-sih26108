"use client";

import React, { useState } from "react";
import { Info, ArrowRight, ShieldAlert, CheckCircle2, AlertCircle, X } from "lucide-react";
import { AnalysisResponse, CertificationResult } from "@/types/api";

interface CertificationBannerProps {
  response: AnalysisResponse;
}

export function CertificationBanner({ response }: CertificationBannerProps) {
  const [showModal, setShowModal] = useState(false);
  const { certification, applicability, candidates } = response;

  const strongApp = applicability.find((a) => a.result === "strong");
  const stdId = strongApp?.standard_id || candidates[0]?.standard_id;

  const certData: CertificationResult | undefined = stdId
    ? certification[stdId]
    : Object.values(certification)[0];

  const isProposed =
    certData?.rule_type === "QCO_PROPOSED" ||
    certData?.state === "not_verified_in_prototype_corpus";

  const description =
    certData?.description ||
    "Proposed Quality Control Order (QCO) for pumps is under consideration by DPIIT. Details not formally verified in prototype corpus.";

  return (
    <>
      <div className="rounded-xl border border-blue-200 bg-gradient-to-r from-blue-50/90 to-indigo-50/70 p-4 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 w-full min-w-0">
        <div className="flex items-start gap-3 min-w-0 flex-1">
          <div className="w-8 h-8 rounded-full bg-blue-100 text-[#0B57D0] flex items-center justify-center flex-shrink-0 mt-0.5 sm:mt-0 border border-blue-200">
            <Info className="w-4 h-4" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
              <span className="text-[11px] sm:text-xs font-extrabold uppercase tracking-wide text-[#0A3871]">
                Certification / QCO Status
              </span>
              <span className="inline-flex items-center px-1.5 py-0.2 rounded text-[10px] font-semibold bg-amber-100 text-amber-800 border border-amber-200 flex-shrink-0">
                {isProposed ? "QCO Proposed / Unconfirmed" : "Regulatory Notice"}
              </span>
            </div>
            <p className="text-xs text-slate-700 mt-1 max-w-3xl leading-relaxed break-words">
              {description}
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-1 text-xs font-bold text-[#0B57D0] hover:text-[#0A47A8] hover:underline flex-shrink-0 self-end sm:self-center cursor-pointer"
        >
          <span>Learn more</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Modal Dialog for Certification Details */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 relative animate-in fade-in zoom-in-95 duration-150">
            <button
              onClick={() => setShowModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-3 pb-4 border-b border-slate-100">
              <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center border border-amber-200">
                <AlertCircle className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900">
                  Regulatory & QCO Verification Notice
                </h3>
                <p className="text-xs text-slate-500 font-medium">
                  Bureau of Indian Standards / DPIIT Quality Control Order
                </p>
              </div>
            </div>

            <div className="mt-4 space-y-3 text-xs sm:text-sm text-slate-700 leading-relaxed">
              <div className="p-3 bg-amber-50/70 border border-amber-200 rounded-xl">
                <span className="font-bold text-amber-900 block mb-1">
                  Source Access & Evidence Policy:
                </span>
                <p className="text-amber-800 text-xs">
                  The prototype corpus strictly enforces evidence grounding. Unconfirmed gazette numbers or secondary reports are marked as <code className="bg-amber-100 px-1 py-0.5 rounded font-mono font-bold">not_verified_in_prototype_corpus</code>.
                </p>
              </div>

              <p>
                <strong>Covered Standards:</strong> Proposed DPIIT Pumps QCO 2023 was cited to encompass submersible pumpsets (IS 8034) and openwell submersible pumpsets (IS 14220) under BIS Certification Scheme-I (ISI Mark).
              </p>

              <p>
                <strong>Current Status:</strong> The definitive enforcement date and official Gazette of India publication should be confirmed through official portals (dpiit.gov.in or bis.gov.in) prior to commercial procurement.
              </p>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                type="button"
                onClick={() => setShowModal(false)}
                className="px-4 py-2 text-xs font-semibold rounded-lg bg-slate-900 text-white hover:bg-slate-800"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
