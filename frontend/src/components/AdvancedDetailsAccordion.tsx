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

interface AdvancedDetailsAccordionProps {
  response: AnalysisResponse;
  onOpenReportModal: () => void;
}

export function AdvancedDetailsAccordion({
  response,
  onOpenReportModal,
}: AdvancedDetailsAccordionProps) {
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

  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden transition-all">
      {/* Header Toggle */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-6 py-4 flex items-center justify-between bg-slate-50/80 hover:bg-slate-100/80 text-left transition-colors cursor-pointer"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-100 text-[#0A3871] flex items-center justify-center font-bold text-xs">
            <FileCheck2 className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900">
              Detailed Procurement Audit & Technical Traceability
            </h3>
            <p className="text-xs text-slate-500">
              Progressive disclosure of deterministic policy checks, graph hops, coverage matrix, and provenance
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs font-semibold text-[#0B57D0]">
          <span>{isOpen ? "Hide Advanced Details" : "Show Advanced Details"}</span>
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {/* Collapsible Content */}
      {isOpen && (
        <div className="p-6 border-t border-slate-200">
          {/* Sub-Tabs */}
          <div className="flex flex-wrap items-center gap-1.5 pb-4 border-b border-slate-200">
            {[
              { id: "requirements", label: `Requirements (${requirements.length})` },
              { id: "applicability", label: `Applicability (${applicability.length})` },
              { id: "lifecycle", label: `Lifecycle (${lifecycle.length})` },
              { id: "graph", label: `Graph / Normative (${related_standards.length})` },
              { id: "coverage", label: `Coverage & Gaps (${coverage.length + gaps.length})` },
              { id: "conflicts", label: `Conflicts (${conflicts.length})` },
              { id: "evidence", label: `Evidence Provenance (${evidence.length})` },
              { id: "timings", label: `Performance Timings` },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
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
              className="ml-auto inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-300 hover:bg-emerald-100 transition-colors"
            >
              <FileCode className="w-3.5 h-3.5" />
              <span>Full Audit HTML Report</span>
            </button>
          </div>

          {/* Tab 1: Requirements */}
          {activeTab === "requirements" && (
            <div className="pt-4 space-y-3">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Extracted Tender Requirements
              </h4>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border border-slate-200 rounded-lg overflow-hidden">
                  <thead className="bg-slate-100 text-slate-700 font-bold">
                    <tr>
                      <th className="p-2.5">ID</th>
                      <th className="p-2.5">Category</th>
                      <th className="p-2.5">Extracted Text</th>
                      <th className="p-2.5">Attribute / Value</th>
                      <th className="p-2.5">Method</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {requirements.map((r, i) => (
                      <tr key={i} className="hover:bg-slate-50/80">
                        <td className="p-2.5 font-mono text-slate-500">{r.requirement_id}</td>
                        <td className="p-2.5">
                          <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-semibold text-[10px]">
                            {r.category}
                          </span>
                        </td>
                        <td className="p-2.5 text-slate-800 font-medium">{r.text}</td>
                        <td className="p-2.5 text-slate-600">
                          {r.attribute ? `${r.attribute}: ${r.value || ""}` : "—"}
                        </td>
                        <td className="p-2.5 text-slate-500 font-mono text-[11px]">
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
            <div className="pt-4 space-y-3">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Deterministic Applicability Assessment
              </h4>
              <div className="space-y-2">
                {applicability.map((a, i) => (
                  <div
                    key={i}
                    className="p-3 rounded-xl border border-slate-200 bg-slate-50/60 flex items-start justify-between gap-3 text-xs"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-slate-900">{a.standard_id}</span>
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
                      <ul className="mt-1.5 space-y-1 text-slate-600 list-disc list-inside">
                        {a.reasons.map((r, ri) => (
                          <li key={ri}>{r}</li>
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
            <div className="pt-4 space-y-3">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Lifecycle & Standard Edition Assessment
              </h4>
              <div className="space-y-2">
                {lifecycle.map((l, i) => (
                  <div key={i} className="p-3 rounded-xl border border-slate-200 bg-slate-50 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-slate-900">{l.standard_id}</span>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          l.state === "supported"
                            ? "bg-emerald-100 text-emerald-800"
                            : "bg-amber-100 text-amber-800"
                        }`}
                      >
                        {l.state.toUpperCase()}
                      </span>
                    </div>
                    <ul className="mt-1.5 space-y-1 text-slate-600">
                      {l.reasons.map((r, ri) => (
                        <li key={ri}>• {r}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tab 4: Graph */}
          {activeTab === "graph" && (
            <div className="pt-4 space-y-3">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Normative Reference & Dependency Graph (Max 2 Hops)
              </h4>
              <div className="space-y-2">
                {related_standards.map((rel, i) => (
                  <div
                    key={i}
                    className="p-3 rounded-xl border border-slate-200 bg-slate-50/80 flex items-center justify-between text-xs"
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-[#0A3871]">{rel.from_standard}</span>
                      <span className="text-slate-400">───({rel.relationship_type})───▶</span>
                      <span className="font-mono font-bold text-indigo-700">{rel.to_standard}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded bg-indigo-100 text-indigo-800 font-semibold text-[10px]">
                        Hop {rel.hop || 1}
                      </span>
                      {rel.verified && (
                        <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 font-semibold text-[10px]">
                          Verified
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
            <div className="pt-4 space-y-3">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Specification Coverage Matrix
              </h4>
              <div className="space-y-2">
                {coverage.map((c, i) => (
                  <div key={i} className="p-2.5 rounded-lg border border-slate-200 bg-emerald-50/50 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900">{c.requirement_id}</span>
                      <span className="text-[10px] font-bold text-emerald-800 uppercase">{c.state}</span>
                    </div>
                    <p className="text-slate-600 mt-0.5">{c.reason}</p>
                  </div>
                ))}
                {gaps.map((g, i) => (
                  <div key={i} className="p-2.5 rounded-lg border border-amber-200 bg-amber-50/50 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900">{g.requirement_id}</span>
                      <span className="text-[10px] font-bold text-amber-800 uppercase">{g.state}</span>
                    </div>
                    <p className="text-slate-600 mt-0.5">{g.reason}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tab 6: Conflicts */}
          {activeTab === "conflicts" && (
            <div className="pt-4 space-y-3">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Conflict & Contradiction Detection
              </h4>
              {conflicts.length === 0 ? (
                <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 font-medium flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>No conflicting standard citations or contradictory requirements detected.</span>
                </div>
              ) : (
                conflicts.map((conf, i) => (
                  <div key={i} className="p-3 rounded-xl border border-red-200 bg-red-50 text-xs text-red-900">
                    <span className="font-bold block">{conf.conflict_type}</span>
                    <p className="mt-0.5">{conf.description}</p>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Tab 7: Evidence Provenance */}
          {activeTab === "evidence" && (
            <div className="pt-4 space-y-3">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Full Evidence Provenance Records
              </h4>
              <div className="space-y-2">
                {evidence.map((ev, i) => (
                  <div key={i} className="p-3 rounded-xl border border-slate-200 bg-slate-50 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900 font-mono">{ev.evidence_id}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-semibold">
                        {ev.verified ? "Verified Official BIS" : "Secondary Summary"}
                      </span>
                    </div>
                    <p className="text-slate-700 mt-1 font-medium">{ev.source_name}</p>
                    <p className="text-slate-600 mt-0.5">{ev.text}</p>
                    <a
                      href={ev.url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 text-[#0B57D0] hover:underline mt-1 font-mono text-[11px]"
                    >
                      <span>{ev.url}</span>
                      <ExternalLink className="w-3 h-3" />
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
                Pipeline Execution Timings & Latency
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
