"use client";

import React from "react";
import { FileText, ArrowRight, Sparkles, HelpCircle, ShieldAlert, Layers } from "lucide-react";
import { AnalysisResponse, StandardRecord } from "@/types/api";
import { useLanguage } from "@/context/LanguageContext";

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
  const { t } = useLanguage();
  const { decision, applicability, lifecycle, candidates, decision_reasons } = response;

  // A primary standard is valid ONLY if there is a strong applicability assessment
  // AND decision is RECOMMEND or REVIEW, AND it is a primary product standard.
  const strongApp = applicability.find((a) => a.result === "strong");
  const hasStrongPrimary =
    (decision === "RECOMMEND" || decision === "REVIEW") &&
    !!strongApp &&
    primaryStandard?.standard_role === "PRIMARY_PRODUCT_STANDARD" &&
    primaryStandard.standard_id === strongApp.standard_id;
  const stdId = hasStrongPrimary ? strongApp.standard_id : null;

  const lc = stdId ? lifecycle.find((l) => l.standard_id === stdId) : null;
  const statusLabel =
    lc?.state === "supported"
      ? t.activeInForce
      : lc?.state === "warning"
      ? t.revisionWarning
      : t.notFormallyConfirmed;

  // Infer product and use from primary standard
  const getProduct = () => {
    if (!stdId) return "N/A";
    if (stdId.includes("14220")) return "Openwell Submersible Pumpset";
    if (stdId.includes("8034")) return "Borewell / Borehole Submersible Pumpset";
    if (stdId.includes("9079")) return "Monoset Pump for Clear Cold Water";
    if (primaryStandard?.product_terms?.length) return primaryStandard.product_terms.join(", ");
    return response.requirements.find((r) => r.category === "product")?.product || "Pumpset Equipment";
  };

  const getUse = () => {
    if (!stdId) return "N/A";
    if (stdId.includes("14220")) return "Agricultural irrigation & water supply";
    if (stdId.includes("8034")) return "Borewell agricultural irrigation / water supply";
    if (stdId.includes("9079")) return "Agricultural & municipal clear water supply";
    if (primaryStandard?.application_terms?.length) return primaryStandard.application_terms.join(", ");
    return "Industrial / Agricultural Fluid Transfer";
  };

  const matchReasons = strongApp?.reasons || [];

  // ── Render Fallback / Non-Primary Card when no strong primary standard exists ──
  if (!hasStrongPrimary) {
    const isAbstain = decision === "ABSTAIN";
    const isOutOfCorpus = decision === "OUT_OF_CORPUS";

    return (
      <div className="bg-white rounded-2xl border border-slate-200 p-5 sm:p-6 shadow-sm flex flex-col justify-between hover:border-slate-300 transition-all w-full min-w-0">
        <div className="min-w-0">
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-slate-100 gap-2">
            <div className="flex items-center gap-2 min-w-0">
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                isAbstain ? "bg-slate-100 text-slate-600" : isOutOfCorpus ? "bg-purple-50 text-purple-600" : "bg-amber-50 text-amber-600"
              }`}>
                {isAbstain ? <HelpCircle className="w-4 h-4" /> : isOutOfCorpus ? <ShieldAlert className="w-4 h-4" /> : <Layers className="w-4 h-4" />}
              </div>
              <div className="min-w-0">
                <h3 className="text-base font-bold text-slate-900 truncate">
                  {t.noPrimary}
                </h3>
                <p className="text-[11px] text-slate-500 font-medium truncate">
                  {isAbstain
                    ? "Input not specific enough for a definitive product standard"
                    : isOutOfCorpus
                    ? "Scope is outside the verified prototype corpus"
                    : "Technical review required across candidates"}
                </p>
              </div>
            </div>
            <span className={`px-2 py-0.5 rounded text-[10px] font-extrabold uppercase border flex-shrink-0 ${
              isAbstain
                ? "bg-slate-100 text-slate-700 border-slate-200"
                : isOutOfCorpus
                ? "bg-purple-100 text-purple-800 border-purple-200"
                : "bg-amber-100 text-amber-800 border-amber-200"
            }`}>
              {isAbstain ? "NO PRIMARY MATCH" : isOutOfCorpus ? "OUT OF CORPUS" : "REVIEW REQUIRED"}
            </span>
          </div>

          {/* Explanation Section */}
          <div className="mt-4 p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 text-xs text-slate-700 space-y-2">
            <p className="font-semibold text-slate-900">
              {isAbstain
                ? t.noPrimaryDescription
                : isOutOfCorpus
                ? t.noRecommendation
                : "Multiple candidates match or tender specifications require technical review before procurement."}
            </p>
            {decision_reasons && decision_reasons.length > 0 && (
              <p className="text-slate-600 leading-relaxed text-[11px]">
                {decision_reasons[0]}
              </p>
            )}
          </div>

          {/* Matched Weak / Related Candidates — Explicitly Labeled as Context Only */}
          {candidates && candidates.length > 0 && !isOutOfCorpus && (
            <div className="mt-4 pt-3 border-t border-slate-100">
              <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center justify-between">
                <span>{t.contextStandards}</span>
                <span className="text-[10px] lowercase font-normal text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200">
                  {t.contextOnly}
                </span>
              </div>
              <div className="space-y-2">
                {candidates.slice(0, 2).map((cand, idx) => (
                  <div key={idx} className="p-2 rounded-lg bg-slate-50/80 border border-slate-200 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-slate-800">{cand.standard_id}</span>
                      <span className="text-[10px] text-slate-500">{cand.retrieval_paths.join(", ")}</span>
                    </div>
                    <p className="text-[11px] text-slate-600 line-clamp-1 mt-0.5">{cand.title}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <span>{t.productName} {t.primaryStandard}</span>
          <span className="text-xs font-semibold text-slate-400">MED 20 Verified</span>
        </div>
      </div>
    );
  }

  // ── Render Primary Product Standard Card ──
  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 sm:p-6 shadow-sm flex flex-col justify-between hover:border-slate-300 transition-all w-full min-w-0">
      <div className="min-w-0">
        {/* Card Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 gap-2">
          <div className="flex items-center gap-2 min-w-0">
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-[#0B57D0] flex items-center justify-center flex-shrink-0">
              <FileText className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <h3 className="text-base font-bold text-slate-900 truncate">{t.primaryStandard}</h3>
              <p className="text-[11px] text-slate-500 font-medium truncate">{t.recommendedCore}</p>
            </div>
          </div>
          <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-blue-100 text-blue-800 border border-blue-200 flex-shrink-0">
            PRIMARY PRODUCT STANDARD
          </span>
        </div>

        {/* Details Table */}
        <dl className="mt-4 space-y-3 text-xs sm:text-sm min-w-0">
          <div className="flex items-start justify-between gap-2 min-w-0">
            <dt className="text-slate-500 font-medium flex-shrink-0">{t.standardNumber}</dt>
            <dd className="text-[#0B57D0] font-mono font-bold text-right break-words">
              {stdId}
            </dd>
          </div>

          <div className="flex items-start justify-between gap-2 min-w-0">
            <dt className="text-slate-500 font-medium flex-shrink-0">{t.product}</dt>
            <dd className="text-slate-900 font-semibold text-right max-w-[65%] break-words">
              {getProduct()}
            </dd>
          </div>

          <div className="flex items-start justify-between gap-2 min-w-0">
            <dt className="text-slate-500 font-medium flex-shrink-0">{t.application}</dt>
            <dd className="text-slate-900 font-semibold text-right max-w-[65%] break-words">
              {getUse()}
            </dd>
          </div>

          <div className="flex items-start justify-between gap-2 min-w-0">
            <dt className="text-slate-500 font-medium flex-shrink-0">{t.status}</dt>
            <dd className="text-right min-w-0">
              <span
                className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] sm:text-xs font-semibold break-words text-left ${
                  lc?.state === "warning"
                    ? "bg-amber-100 text-amber-800 border border-amber-300"
                    : "bg-emerald-100 text-emerald-800 border border-emerald-200"
                }`}
              >
                <span className="w-1.5 h-1.5 rounded-full bg-current flex-shrink-0" />
                <span className="break-words">{statusLabel}</span>
              </span>
            </dd>
          </div>

          {/* Why it matched */}
          {matchReasons.length > 0 && (
            <div className="pt-2.5 border-t border-slate-100 min-w-0">
              <dt className="text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-[#0B57D0]" />
                <span>{t.whyMatched}</span>
              </dt>
              <dd className="space-y-1">
                {matchReasons.slice(0, 3).map((reason, idx) => (
                  <div key={idx} className="flex items-start gap-1.5 text-[11px] text-slate-600">
                    <span className="text-emerald-600 font-bold">•</span>
                    <span className="leading-snug">{reason}</span>
                  </div>
                ))}
              </dd>
            </div>
          )}

          {primaryStandard?.scope && (
            <div className="pt-2 border-t border-slate-100 min-w-0">
              <dt className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1">{t.scope}</dt>
              <dd className="text-slate-600 text-xs leading-relaxed line-clamp-2 break-words">
                {primaryStandard.scope}
              </dd>
            </div>
          )}
        </dl>
      </div>

      <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <span>MED 20 · {t.verifiedData}</span>
        <a
          href="https://www.services.bis.gov.in"
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1 text-xs font-semibold text-[#0B57D0] hover:underline"
        >
          <span>{t.bisPortal}</span>
          <ArrowRight className="w-3 h-3" />
        </a>
      </div>
    </div>
  );
}
