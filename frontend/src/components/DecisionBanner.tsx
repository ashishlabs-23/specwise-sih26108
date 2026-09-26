"use client";

import React from "react";
import {
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  ShieldAlert,
  ArrowLeft,
  Share2,
  Download,
  Info,
  Play,
  FileDown,
} from "lucide-react";
import { AnalysisResponse, StandardRecord } from "@/types/api";
import { getDecisionTheme, formatDecisionLabel } from "@/lib/utils";
import { useLanguage } from "@/context/LanguageContext";

interface DecisionBannerProps {
  response: AnalysisResponse;
  primaryStandard?: StandardRecord | null;
  onNewSearch: () => void;
  onDownloadReport: () => void;
}

export function DecisionBanner({
  response,
  primaryStandard,
  onNewSearch,
  onDownloadReport,
}: DecisionBannerProps) {
  const { t } = useLanguage();
  const { decision, decision_reasons, applicability, candidates } = response;
  const theme = getDecisionTheme(decision);

  // Find strong primary standard ID
  const strongApp = applicability.find((a) => a.result === "strong");
  const hasStrongPrimary = (decision === "RECOMMEND" || decision === "REVIEW") && !!strongApp;
  const primaryId = hasStrongPrimary ? strongApp.standard_id : null;
  const primaryTitle = hasStrongPrimary ? (primaryStandard?.title || "") : "";

  // Plain-language summary logic
  const getSimpleTermsExplanation = () => {
    if (decision === "RECOMMEND" && primaryId) {
      if (primaryId.includes("14220")) {
        return "IS 14220 specifies requirements for openwell submersible pumpsets used for agricultural irrigation.";
      }
      if (primaryId.includes("8034")) {
        return "IS 8034 specifies safety, construction, and acceptance criteria for borewell submersible pumpsets.";
      }
      if (primaryId.includes("9079")) {
        return "IS 9079 specifies monoset pumps for clear cold water applications.";
      }
      return t.matchedEvidence;
    }

    if (decision === "REVIEW") {
      return t.reviewDescription;
    }

    if (decision === "ABSTAIN") {
      return t.noPrimaryDescription;
    }

    return t.noRecommendation;
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: `SpecWise BIS Assessment: ${primaryId || decision}`,
        text: `BIS Standard Recommendation for: ${response.input_text}`,
        url: window.location.href,
      }).catch(() => {});
    } else {
      navigator.clipboard.writeText(window.location.href);
      alert("Page link copied to clipboard!");
    }
  };

  return (
    <div className="space-y-4 w-full min-w-0">
      {/* Action Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2.5 pt-2 w-full min-w-0">
        <button
          type="button"
          onClick={onNewSearch}
          className="inline-flex items-center gap-1.5 text-xs sm:text-sm font-semibold text-slate-700 hover:text-[#0B57D0] transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{t.newSearch}</span>
        </button>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={handleShare}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-xs sm:text-sm font-medium text-slate-700 shadow-sm transition-colors cursor-pointer"
          >
            <Share2 className="w-3.5 h-3.5 text-slate-500" />
            <span>{t.share}</span>
          </button>

          <button
            type="button"
            onClick={onDownloadReport}
            className="inline-flex items-center gap-1.5 px-3 sm:px-3.5 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-xs sm:text-sm font-semibold text-slate-800 shadow-sm transition-colors cursor-pointer"
          >
            <Download className="w-3.5 h-3.5 text-[#0B57D0]" />
            <span className="hidden sm:inline">{t.reportDownload}</span>
            <span className="sm:hidden">{t.auditReport}</span>
          </button>
        </div>
      </div>

      {/* Main Decision Card */}
      <div
        className={`rounded-2xl border p-4 sm:p-7 shadow-sm transition-all w-full min-w-0 ${theme.bg} ${theme.border}`}
      >
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 sm:gap-6 items-start lg:items-center min-w-0">
          
          {/* Left Column: Decision & Primary Standard */}
          <div className="lg:col-span-5 flex items-start gap-3.5 sm:gap-4 min-w-0">
            <div className="flex-shrink-0 mt-1">
              {decision === "RECOMMEND" && (
                <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-emerald-600 text-white flex items-center justify-center shadow-md">
                  <CheckCircle2 className="w-6 h-6 sm:w-7 sm:h-7" />
                </div>
              )}
              {decision === "REVIEW" && (
                <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-amber-500 text-white flex items-center justify-center shadow-md">
                  <AlertTriangle className="w-6 h-6 sm:w-7 sm:h-7" />
                </div>
              )}
              {decision === "ABSTAIN" && (
                <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-slate-600 text-white flex items-center justify-center shadow-md">
                  <HelpCircle className="w-6 h-6 sm:w-7 sm:h-7" />
                </div>
              )}
              {decision === "OUT_OF_CORPUS" && (
                <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-purple-600 text-white flex items-center justify-center shadow-md">
                  <ShieldAlert className="w-6 h-6 sm:w-7 sm:h-7" />
                </div>
              )}
            </div>

            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
                <span
                  className={`text-[10px] sm:text-xs uppercase font-extrabold tracking-wider px-2 py-0.5 rounded ${theme.lightBadge}`}
                >
                  {formatDecisionLabel(decision)}
                </span>
                <span className="text-[11px] sm:text-xs text-slate-500">
                  {decision === "RECOMMEND" ? t.definitiveMatch : t.evaluationResult}
                </span>
              </div>

              <h2 className="text-xl sm:text-3xl font-extrabold text-slate-900 tracking-tight mt-1 break-words">
                {decision === "RECOMMEND" && primaryId
                  ? primaryId
                  : decision === "REVIEW" && primaryId
                  ? `Review: ${primaryId}`
                  : decision === "REVIEW"
                  ? t.reviewRequired
                  : decision === "ABSTAIN"
                  ? t.noPrimary
                  : t.outOfCorpus}
              </h2>

              <p className="text-xs sm:text-sm font-medium text-slate-700 mt-0.5 line-clamp-2 break-words">
                {primaryTitle ||
                  (decision === "ABSTAIN"
                    ? t.noPrimaryDescription
                    : decision === "OUT_OF_CORPUS"
                    ? t.outOfCorpusDescription
                    : t.reviewDescription)}
              </p>
            </div>
          </div>

          {/* Middle Column: Why this standard? */}
          <div className="lg:col-span-4 lg:border-l lg:border-slate-300/60 lg:pl-6 min-w-0">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
              <Info className="w-3.5 h-3.5 text-[#0B57D0] flex-shrink-0" />
              <span>{t.whyDecision}</span>
            </h3>
            <p className="text-xs sm:text-sm text-slate-700 mt-1.5 leading-relaxed break-words">
              {decision_reasons && decision_reasons.length > 0
                ? decision_reasons[0]
                : t.matchedEvidence}
            </p>
          </div>

          {/* Right Column: In Simple Terms */}
          <div className="lg:col-span-3 lg:border-l lg:border-slate-300/60 lg:pl-6 bg-white/50 p-3.5 rounded-xl border border-white/60 min-w-0">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-1.5">
              <span className="w-4 h-4 rounded-full bg-emerald-600 text-white flex items-center justify-center text-[9px] flex-shrink-0">
                ✓
              </span>
              <span>{t.simpleTerms}</span>
            </h3>
            <p className="text-xs text-slate-600 mt-1.5 leading-normal break-words">
              {getSimpleTermsExplanation()}
            </p>
          </div>

        </div>
      </div>
    </div>
  );
}
