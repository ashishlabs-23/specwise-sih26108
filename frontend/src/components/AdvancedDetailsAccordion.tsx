"use client";

import React, { useState } from "react";
import {
  ChevronDown,
  ChevronUp,
  FileCheck2,
  CheckCircle2,
  AlertTriangle,
  History,
  GitFork,
  CheckSquare,
  ShieldCheck,
  Timer,
  FileCode,
  ExternalLink,
} from "lucide-react";
import { AnalysisResponse } from "@/types/api";
import { useLanguage } from "@/context/LanguageContext";

interface AdvancedDetailsAccordionProps {
  response: AnalysisResponse;
  onOpenReportModal: () => void;
}

export function AdvancedDetailsAccordion({
  response,
  onOpenReportModal,
}: AdvancedDetailsAccordionProps) {
  const { t } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<
    "requirements" | "applicability" | "lifecycle" | "graph" | "coverage" | "conflicts" | "evidence" | "timings"
  >("requirements");

  const {
    requirements,
    applicability,
    lifecycle,
    related_standards,
    coverage,
    gaps,
    conflicts,
    evidence,
    timings_ms,
  } = response;

  const tabs = [
    { id: "requirements", label: `${t.tabRequirements} (${requirements.length})` },
    { id: "applicability", label: `${t.tabApplicability} (${applicability.length})` },
    { id: "lifecycle", label: `${t.tabLifecycle} (${lifecycle.length})` },
    { id: "graph", label: `${t.tabGraph} (${related_standards.length})` },
    { id: "coverage", label: `${t.tabCoverage} (${coverage.length + gaps.length})` },
    { id: "conflicts", label: `${t.tabConflicts} (${conflicts.length})` },
    { id: "evidence", label: `${t.tabEvidence} (${evidence.length})` },
    { id: "timings", label: t.tabTimings },
  ];

  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden transition-all">
      {/* Header Toggle */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-4 sm:px-6 sm:py-4 flex items-center justify-between bg-slate-50/80 hover:bg-slate-100/80 text-left transition-colors cursor-pointer gap-3"
      >
        <div className="flex items-start sm:items-center gap-3 min-w-0 flex-1">
          <div className="w-8 h-8 rounded-lg bg-blue-100 text-[#0A3871] flex items-center justify-center font-bold text-xs flex-shrink-0 mt-0.5 sm:mt-0">
            <FileCheck2 className="w-4 h-4" />
          </div>
          <div className="min-w-0 flex-1">
            <h3 className="text-xs sm:text-sm font-bold text-slate-900 break-words">
              {t.auditTitle}
            </h3>
            <p className="text-[11px] sm:text-xs text-slate-500 line-clamp-2 sm:line-clamp-none break-words">
              {t.auditSubtitle}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-xs font-semibold text-[#0B57D0] flex-shrink-0">
          <span className="hidden sm:inline">{isOpen ? t.hideDetails : t.showDetails}</span>
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {/* Collapsible Content */}
      {isOpen && (
        <div className="p-4 sm:p-6 border-t border-slate-200 min-w-0">
          {/* Sub-Tabs */}
          <div className="flex flex-wrap items-center gap-1.5 pb-4 border-b border-slate-200 min-w-0">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-2.5 sm:px-3 py-1.5 rounded-lg text-[11px] sm:text-xs font-semibold transition-all cursor-pointer ${
                  activeTab === tab.id
                    ? "bg-[#0A3871] text-white shadow-xs"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {tab.label}
              </button>
            ))}

            <button
              onClick={onOpenReportModal}
              className="mt-1 sm:mt-0 sm:ml-auto inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-300 hover:bg-emerald-100 transition-colors cursor-pointer flex-shrink-0"
            >
              <FileCode className="w-3.5 h-3.5" />
              <span>{t.auditHtmlReport}</span>
            </button>
          </div>

          {/* Tab 1: Requirements */}
          {activeTab === "requirements" && (
            <div className="pt-4 space-y-3 min-w-0">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                {t.extractedRequirements}
              </h4>
              <div className="overflow-x-auto w-full">
                <table className="w-full text-left text-xs border border-slate-200 rounded-lg overflow-hidden min-w-[500px]">
                  <thead className="bg-slate-100 text-slate-700 font-bold">
                    <tr>
                      <th className="p-2.5">{t.colId}</th>
                      <th className="p-2.5">{t.colCategory}</th>
                      <th className="p-2.5">{t.colExtractedText}</th>
                      <th className="p-2.5">{t.colAttributeValue}</th>
                      <th className="p-2.5">{t.colSourcePage}</th>
                      <th className="p-2.5">{t.colMethod}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {requirements.map((r, i) => (
                      <tr key={i} className="hover:bg-slate-50/80">
                        <td className="p-2.5 font-mono text-slate-500 whitespace-nowrap">{r.requirement_id}</td>
                        <td className="p-2.5 whitespace-nowrap">
                          <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-semibold text-[10px]">
                            {r.category}
                          </span>
                        </td>
                        <td className="p-2.5 text-slate-800 font-medium break-words">{r.text}</td>
                        <td className="p-2.5 text-slate-600 break-words">
                          {r.attribute ? `${r.attribute}: ${r.value || ""}` : "—"}
                        </td>
                        <td className="p-2.5 text-slate-600 whitespace-nowrap">
                          {r.source_page ? (
                            <span className="inline-flex items-center px-1.5 py-0.5 rounded bg-purple-50 text-purple-700 font-mono text-[10px] font-bold border border-purple-200">
                              {t.pdfPage} {r.source_page}
                            </span>
                          ) : (
                            <span className="text-slate-400 font-mono text-[10px]">
                              {t.textInput}
                            </span>
                          )}
                        </td>
                        <td className="p-2.5 text-slate-500 font-mono text-[11px] whitespace-nowrap">
                          {r.extraction_method}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Tab 2: Applicability */}
          {activeTab === "applicability" && (
            <div className="pt-4 space-y-3 min-w-0">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                {t.applicabilityTitle}
              </h4>
              <div className="space-y-2 min-w-0">
                {applicability.map((a, i) => (
                  <div
                    key={i}
                    className="p-3 rounded-xl border border-slate-200 bg-slate-50/60 flex flex-col sm:flex-row sm:items-start justify-between gap-3 text-xs min-w-0"
                  >
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-mono font-bold text-slate-900 break-words">{a.standard_id}</span>
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            a.result === "strong"
                              ? "bg-emerald-100 text-emerald-800"
                              : a.result === "possible"
                              ? "bg-blue-100 text-blue-800"
                              : "bg-slate-200 text-slate-700"
                          }`}
                        >
                          {a.result.toUpperCase()}
                        </span>
                      </div>
                      <ul className="mt-1.5 space-y-1 text-slate-600 list-disc list-inside break-words">
                        {a.reasons.map((r, ri) => (
                          <li key={ri} className="break-words">{r}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tab 3: Lifecycle */}
          {activeTab === "lifecycle" && (
            <div className="pt-4 space-y-3 min-w-0">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                {t.lifecycleTitle}
              </h4>
              <div className="space-y-2 min-w-0">
                {lifecycle.map((l, i) => (
                  <div key={i} className="p-3 rounded-xl border border-slate-200 bg-slate-50 text-xs min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-mono font-bold text-slate-900 break-words">{l.standard_id}</span>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold flex-shrink-0 ${
                          l.state === "supported"
                            ? "bg-emerald-100 text-emerald-800"
                            : "bg-amber-100 text-amber-800"
                        }`}
                      >
                        {l.state.toUpperCase()}
                      </span>
                    </div>
                    <ul className="mt-1.5 space-y-1 text-slate-600 break-words">
                      {l.reasons.map((r, ri) => (
                        <li key={ri} className="break-words">• {r}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tab 4: Graph */}
          {activeTab === "graph" && (
            <div className="pt-4 space-y-3 min-w-0">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                {t.graphTitle}
              </h4>
              <div className="space-y-2 min-w-0">
                {related_standards.map((rel, i) => (
                  <div
                    key={i}
                    className="p-3 rounded-xl border border-slate-200 bg-slate-50/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 text-xs min-w-0"
                  >
                    <div className="flex flex-wrap items-center gap-2 min-w-0">
                      <span className="font-mono font-bold text-[#0A3871] break-words">{rel.from_standard}</span>
                      <span className="inline-flex items-center px-1.5 py-0.5 rounded bg-slate-200 text-slate-700 text-[10px] font-medium">
                        {rel.relationship_type.replace(/_/g, " ")} →
                      </span>
                      <span className="font-mono font-bold text-indigo-700 break-words">{rel.to_standard}</span>
                    </div>
                    <div className="flex items-center gap-2 self-start sm:self-auto flex-shrink-0">
                      <span className="px-2 py-0.5 rounded bg-indigo-100 text-indigo-800 font-semibold text-[10px]">
                        {t.hop} {rel.hop || 1}
                      </span>
                      {rel.verified && (
                        <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 font-semibold text-[10px]">
                          {t.verified}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tab 5: Coverage & Gaps */}
          {activeTab === "coverage" && (
            <div className="pt-4 space-y-3 min-w-0">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                {t.coverageTitle}
              </h4>
              <div className="space-y-2 min-w-0">
                {coverage.map((c, i) => (
                  <div key={i} className="p-2.5 rounded-lg border border-slate-200 bg-emerald-50/50 text-xs min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-bold text-slate-900 break-words">{c.requirement_id}</span>
                      <span className="text-[10px] font-bold text-emerald-800 uppercase flex-shrink-0">{c.state}</span>
                    </div>
                    <p className="text-slate-600 mt-0.5 break-words">{c.reason}</p>
                  </div>
                ))}
                {gaps.map((g, i) => (
                  <div key={i} className="p-2.5 rounded-lg border border-amber-200 bg-amber-50/50 text-xs min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-bold text-slate-900 break-words">{g.requirement_id}</span>
                      <span className="text-[10px] font-bold text-amber-800 uppercase flex-shrink-0">{g.state}</span>
                    </div>
                    <p className="text-slate-600 mt-0.5 break-words">{g.reason}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tab 6: Conflicts */}
          {activeTab === "conflicts" && (
            <div className="pt-4 space-y-3 min-w-0">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                {t.conflictsTitle}
              </h4>
              {conflicts.length === 0 ? (
                <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 font-medium flex items-center gap-2 min-w-0">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                  <span className="break-words">{t.noConflicts}</span>
                </div>
              ) : (
                conflicts.map((conf, i) => (
                  <div key={i} className="p-3 rounded-xl border border-red-200 bg-red-50 text-xs text-red-900 min-w-0">
                    <span className="font-bold block break-words">{conf.conflict_type}</span>
                    <p className="mt-0.5 break-words">{conf.description}</p>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Tab 7: Evidence Provenance */}
          {activeTab === "evidence" && (
            <div className="pt-4 space-y-3 min-w-0">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                {t.evidenceTitle}
              </h4>
              <div className="space-y-2 min-w-0">
                {evidence.map((ev, i) => (
                  <div key={i} className="p-3 rounded-xl border border-slate-200 bg-slate-50 text-xs min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-bold text-slate-900 font-mono break-words">{ev.evidence_id}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-semibold flex-shrink-0">
                        {ev.verified ? t.verifiedOfficial : t.secondarySummary}
                      </span>
                    </div>
                    <p className="text-slate-700 mt-1 font-medium break-words">{ev.source_name}</p>
                    <p className="text-slate-600 mt-0.5 break-words">{ev.text}</p>
                    <a
                      href={ev.url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 text-[#0B57D0] hover:underline mt-1 font-mono text-[11px] max-w-full truncate"
                    >
                      <span className="truncate">{ev.url}</span>
                      <ExternalLink className="w-3 h-3 flex-shrink-0" />
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tab 8: Timings */}
          {activeTab === "timings" && (
            <div className="pt-4 space-y-3">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                {t.timingsTitle}
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                {Object.entries(timings_ms).map(([k, v]) => (
                  <div key={k} className="p-3 rounded-xl border border-slate-200 bg-slate-50">
                    <span className="text-slate-500 font-medium block">{k}</span>
                    <span className="text-base font-bold text-[#0A3871] font-mono mt-1 block">
                      {v.toFixed(1)} ms
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>
      )}
    </div>
  );
}
