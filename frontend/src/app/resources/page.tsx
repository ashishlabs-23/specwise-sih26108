"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { AboutModal } from "@/components/AboutModal";
import { fetchResources, ResourcesResponse } from "@/lib/api";
import {
  BookOpen,
  FileCheck,
  Link2,
  CheckCircle2,
  ExternalLink,
  Search,
  ArrowRight,
  ShieldAlert,
  Info,
  Database,
  Building,
  Calendar,
  Sparkles,
  Loader2,
  AlertCircle,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

export default function ResourcesPage() {
  const [isAboutModalOpen, setIsAboutModalOpen] = useState(false);
  const [data, setData] = useState<ResourcesResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [activeTab, setActiveTab] = useState<
    "standards" | "evidence" | "relationships" | "benchmark" | "sources"
  >("standards");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedRole, setSelectedRole] = useState<string>("ALL");
  const [expandedStandardId, setExpandedStandardId] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const PAGE_SIZE = 6;

  // Reset page on filter or tab change
  useEffect(() => {
    setCurrentPage(1);
  }, [activeTab, searchQuery, selectedRole]);

  useEffect(() => {
    async function loadCorpusData() {
      try {
        setIsLoading(true);
        setError(null);
        const res = await fetchResources();
        setData(res);
      } catch (err: any) {
        setError(err?.message || "Failed to load corpus resources.");
      } finally {
        setIsLoading(false);
      }
    }
    loadCorpusData();
  }, []);

  const standards = data?.standards || [];
  const evidence = data?.evidence || [];
  const relationships = data?.relationships || [];
  const benchmarkCases = data?.benchmark_cases || [];
  const sources = data?.sources || [];
  const summary = data?.summary || {
    standards_count: standards.length,
    evidence_count: evidence.length,
    relationships_count: relationships.length,
    benchmark_cases_count: benchmarkCases.length,
    sources_count: sources.length,
  };

  // Filtering standards
  const filteredStandards = standards.filter((std) => {
    const matchesSearch =
      std.standard_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      std.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (std.keywords && std.keywords.some((k) => k.toLowerCase().includes(searchQuery.toLowerCase()))) ||
      std.scope.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRole =
      selectedRole === "ALL" || std.standard_role === selectedRole;
    return matchesSearch && matchesRole;
  });

  // Filtering evidence
  const filteredEvidence = evidence.filter((ev) => {
    return (
      ev.evidence_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ev.source_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ev.text.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (ev.section && ev.section.toLowerCase().includes(searchQuery.toLowerCase()))
    );
  });

  // Filtering relationships
  const filteredRelationships = relationships.filter((rel) => {
    return (
      rel.from_standard.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rel.to_standard.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rel.relationship_type.toLowerCase().includes(searchQuery.toLowerCase())
    );
  });

  // Filtering benchmark cases
  const filteredCases = benchmarkCases.filter((c) => {
    return (
      c.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.query.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.notes.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.expected_contains && c.expected_contains.some((s) => s.toLowerCase().includes(searchQuery.toLowerCase())))
    );
  });

  // Filtering sources
  const filteredSources = sources.filter((src) => {
    return (
      src.source_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      src.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      src.publisher.toLowerCase().includes(searchQuery.toLowerCase()) ||
      src.notes.toLowerCase().includes(searchQuery.toLowerCase())
    );
  });

  const getRoleLabel = (role: string) => {
    switch (role) {
      case "PRIMARY_PRODUCT_STANDARD":
        return "Primary Product Standard";
      case "CODE_OF_PRACTICE":
        return "Code of Practice";
      case "TEST_METHOD":
        return "Test Method";
      case "RELATED_STANDARD":
        return "Related Specification";
      default:
        return role.replace(/_/g, " ");
    }
  };

  const getRoleBadge = (role: string) => {
    switch (role) {
      case "PRIMARY_PRODUCT_STANDARD":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "CODE_OF_PRACTICE":
        return "bg-purple-100 text-purple-800 border-purple-200";
      case "TEST_METHOD":
        return "bg-amber-100 text-amber-800 border-amber-200";
      case "RELATED_STANDARD":
        return "bg-emerald-100 text-emerald-800 border-emerald-200";
      default:
        return "bg-slate-100 text-slate-800 border-slate-200";
    }
  };

  const getRelatedForStandard = (stdId: string) => {
    return relationships
      .filter((r) => r.from_standard === stdId || r.to_standard === stdId)
      .map((r) => (r.from_standard === stdId ? r.to_standard : r.from_standard));
  };

  const paginate = <T,>(items: T[]) => {
    const totalPages = Math.ceil(items.length / PAGE_SIZE) || 1;
    const startIndex = (currentPage - 1) * PAGE_SIZE;
    return {
      items: items.slice(startIndex, startIndex + PAGE_SIZE),
      totalPages,
      totalCount: items.length,
    };
  };

  const renderPagination = (totalPages: number, totalCount: number) => {
    if (totalPages <= 1) return null;
    return (
      <div className="mt-8 pt-4 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
        <span className="text-slate-500 font-medium">
          Showing page <strong className="text-slate-800">{currentPage}</strong> of <strong className="text-slate-800">{totalPages}</strong> ({totalCount} total items)
        </span>
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="px-3 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 disabled:opacity-40 disabled:hover:bg-white text-slate-700 font-semibold transition-colors cursor-pointer"
          >
            Previous
          </button>
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNum) => (
            <button
              key={pageNum}
              type="button"
              onClick={() => setCurrentPage(pageNum)}
              className={`w-8 h-8 rounded-lg text-xs font-bold transition-colors cursor-pointer ${
                currentPage === pageNum
                  ? "bg-[#0A3871] text-white shadow-xs"
                  : "bg-white border border-slate-200 text-slate-700 hover:bg-slate-100"
              }`}
            >
              {pageNum}
            </button>
          ))}
          <button
            type="button"
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className="px-3 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 disabled:opacity-40 disabled:hover:bg-white text-slate-700 font-semibold transition-colors cursor-pointer"
          >
            Next
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      <Navbar onAboutClick={() => setIsAboutModalOpen(true)} />

      <main className="flex-1">
        {/* Header Hero */}
        <section className="bg-gradient-to-b from-white to-slate-100 border-b border-slate-200 pt-8 pb-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-xs font-semibold text-[#0B57D0] mb-3">
                  <Database className="w-3.5 h-3.5" />
                  <span>SpecWise Knowledge Base & Corpus Explorer</span>
                </div>
                <h1 className="text-3xl sm:text-4xl font-extrabold text-[#0A3871] tracking-tight">
                  Corpus Resources & Provenance
                </h1>
                <p className="mt-2 text-sm sm:text-base text-slate-600 max-w-2xl leading-relaxed">
                  Transparent repository of verified standards, evidence citations, normative relationships, and benchmark evaluation cases loaded live from the backend engine.
                </p>
              </div>

              {/* Dynamic Live Metrics Card */}
              <div className="grid grid-cols-3 sm:grid-cols-5 gap-2.5 bg-white p-3.5 rounded-2xl border border-slate-200 shadow-sm text-center">
                <div className="px-2 py-1">
                  <span className="block text-xl sm:text-2xl font-black text-[#0A3871]">
                    {isLoading ? "…" : summary.standards_count}
                  </span>
                  <span className="text-[11px] font-semibold text-slate-500">Standards</span>
                </div>
                <div className="px-2 py-1 border-l border-slate-100">
                  <span className="block text-xl sm:text-2xl font-black text-emerald-600">
                    {isLoading ? "…" : summary.evidence_count}
                  </span>
                  <span className="text-[11px] font-semibold text-slate-500">Evidence</span>
                </div>
                <div className="px-2 py-1 border-l border-slate-100">
                  <span className="block text-xl sm:text-2xl font-black text-indigo-600">
                    {isLoading ? "…" : summary.relationships_count}
                  </span>
                  <span className="text-[11px] font-semibold text-slate-500">Links</span>
                </div>
                <div className="px-2 py-1 border-l border-slate-100">
                  <span className="block text-xl sm:text-2xl font-black text-purple-600">
                    {isLoading ? "…" : summary.benchmark_cases_count}
                  </span>
                  <span className="text-[11px] font-semibold text-slate-500">Benchmarks</span>
                </div>
                <div className="px-2 py-1 border-l border-slate-100">
                  <span className="block text-xl sm:text-2xl font-black text-amber-600">
                    {isLoading ? "…" : summary.sources_count}
                  </span>
                  <span className="text-[11px] font-semibold text-slate-500">Sources</span>
                </div>
              </div>
            </div>

            {/* Mandatory Prototype Scope Notice */}
            <div className="mt-6 p-4 rounded-xl bg-amber-50/80 border border-amber-200 text-amber-900 flex items-start gap-3 shadow-xs">
              <Info className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
              <div className="text-xs sm:text-sm">
                <div className="font-bold flex items-center gap-2">
                  <span>Prototype corpus — currently 7 verified standards</span>
                  <span className="inline-block px-2 py-0.5 rounded bg-amber-200/80 text-amber-900 text-[10px] uppercase font-mono font-bold">
                    Not the full BIS catalogue
                  </span>
                </div>
                <p className="mt-1 text-amber-800 leading-relaxed text-xs">
                  This knowledge base is a curated prototype corpus covering mechanical pumps and irrigation equipment under BIS Technical Committee MED 20. It demonstrates evidence grounding and deterministic traceability. It does not claim live BIS database access or access to all 20,000+ national standards.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Content Section */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          
          {error && (
            <div className="p-4 mb-6 rounded-xl bg-red-50 border border-red-200 text-red-800 flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
              <div>
                <h4 className="font-bold text-sm">Failed to Load Corpus Resources</h4>
                <p className="text-xs mt-0.5">{error}</p>
              </div>
            </div>
          )}

          {/* Controls Bar: Tabs & Search Input */}
          <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4 pb-6 border-b border-slate-200">
            {/* Tabs */}
            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={() => setActiveTab("standards")}
                className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all cursor-pointer ${
                  activeTab === "standards"
                    ? "bg-[#0A3871] text-white shadow-sm"
                    : "bg-white text-slate-700 hover:bg-slate-100 border border-slate-200"
                }`}
              >
                <BookOpen className="w-4 h-4" />
                <span>Verified Standards ({isLoading ? "…" : summary.standards_count})</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveTab("evidence")}
                className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all cursor-pointer ${
                  activeTab === "evidence"
                    ? "bg-[#0A3871] text-white shadow-sm"
                    : "bg-white text-slate-700 hover:bg-slate-100 border border-slate-200"
                }`}
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Evidence Records ({isLoading ? "…" : summary.evidence_count})</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveTab("relationships")}
                className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all cursor-pointer ${
                  activeTab === "relationships"
                    ? "bg-[#0A3871] text-white shadow-sm"
                    : "bg-white text-slate-700 hover:bg-slate-100 border border-slate-200"
                }`}
              >
                <Link2 className="w-4 h-4" />
                <span>Relationships ({isLoading ? "…" : summary.relationships_count})</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveTab("benchmark")}
                className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all cursor-pointer ${
                  activeTab === "benchmark"
                    ? "bg-[#0A3871] text-white shadow-sm"
                    : "bg-white text-slate-700 hover:bg-slate-100 border border-slate-200"
                }`}
              >
                <FileCheck className="w-4 h-4" />
                <span>Benchmark Cases ({isLoading ? "…" : summary.benchmark_cases_count})</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveTab("sources")}
                className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all cursor-pointer ${
                  activeTab === "sources"
                    ? "bg-[#0A3871] text-white shadow-sm"
                    : "bg-white text-slate-700 hover:bg-slate-100 border border-slate-200"
                }`}
              >
                <Building className="w-4 h-4" />
                <span>Source Provenance ({isLoading ? "…" : summary.sources_count})</span>
              </button>
            </div>

            {/* Filter / Search input */}
            <div className="relative w-full lg:w-72">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={`Search in ${activeTab}...`}
                className="w-full pl-9 pr-3 py-2 bg-white border border-slate-300 rounded-xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-[#0B57D0]"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-400 hover:text-slate-600"
                >
                  Clear
                </button>
              )}
            </div>
          </div>

          {isLoading && (
            <div className="py-20 flex flex-col items-center justify-center text-center">
              <Loader2 className="w-8 h-8 text-[#0B57D0] animate-spin mb-3" />
              <p className="text-sm font-semibold text-slate-700">Loading verified corpus data from backend...</p>
            </div>
          )}

          {/* TAB 1: STANDARDS */}
          {!isLoading && activeTab === "standards" && (
            <div className="mt-6 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-slate-900">
                  Verified Indian Standards ({filteredStandards.length} of {summary.standards_count})
                </h2>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-500 font-medium hidden sm:inline">Role Filter:</span>
                  <select
                    value={selectedRole}
                    onChange={(e) => setSelectedRole(e.target.value)}
                    className="text-xs font-semibold bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-slate-700 focus:outline-none"
                  >
                    <option value="ALL">All Standard Types</option>
                    <option value="PRIMARY_PRODUCT_STANDARD">Primary Product Standard</option>
                    <option value="CODE_OF_PRACTICE">Code of Practice</option>
                    <option value="TEST_METHOD">Test Method</option>
                    <option value="RELATED_STANDARD">Related Specification</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {filteredStandards.map((std) => {
                  const relatedList = getRelatedForStandard(std.standard_id);
                  const isExpanded = expandedStandardId === std.standard_id;
                  const lifecycleText =
                    std.lifecycle_events && std.lifecycle_events.length > 0
                      ? std.lifecycle_events.map((e) => `${e.event.replace(/_/g, " ")} (${e.date})`).join(", ")
                      : "Active (In Force)";

                  return (
                    <div
                      key={std.standard_id}
                      className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs hover:border-blue-400 transition-all flex flex-col justify-between"
                    >
                      <div>
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <span className="font-mono text-base font-extrabold text-[#0A3871]">
                              {std.standard_id}
                            </span>
                            <h3 className="text-sm font-bold text-slate-900 mt-1 leading-snug">
                              {std.title}
                            </h3>
                          </div>
                          <span
                            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${getRoleBadge(
                              std.standard_role
                            )}`}
                          >
                            {getRoleLabel(std.standard_role)}
                          </span>
                        </div>

                        <p className="mt-3 text-xs text-slate-600 leading-relaxed">
                          {std.scope}
                        </p>

                        {/* Expandable Technical Details */}
                        {isExpanded && (
                          <div className="mt-4 pt-3 border-t border-slate-100 space-y-2.5 text-xs animate-in fade-in duration-150">
                            {std.product_terms && std.product_terms.length > 0 && (
                              <div>
                                <span className="font-semibold text-slate-700">Product Terms: </span>
                                <span className="font-mono text-slate-600">{std.product_terms.join(", ")}</span>
                              </div>
                            )}
                            {std.application_terms && std.application_terms.length > 0 && (
                              <div>
                                <span className="font-semibold text-slate-700">Application Terms: </span>
                                <span className="font-mono text-slate-600">{std.application_terms.join(", ")}</span>
                              </div>
                            )}
                            {std.exclusion_terms && std.exclusion_terms.length > 0 && (
                              <div>
                                <span className="font-semibold text-slate-700">Exclusion Terms: </span>
                                <span className="font-mono text-red-700">{std.exclusion_terms.join(", ")}</span>
                              </div>
                            )}
                            <div>
                              <span className="font-semibold text-slate-700">Versions: </span>
                              <span className="font-mono text-slate-600">{std.versions.join(", ")}</span>
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Metadata Footer */}
                      <div className="mt-4 pt-3 border-t border-slate-100 space-y-2 text-xs">
                        <div className="flex items-center justify-between text-slate-500">
                          <span className="font-medium">Lifecycle / Status:</span>
                          <span className="text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                            {lifecycleText}
                          </span>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className="text-slate-500 font-medium">Linked Evidence:</span>
                          <span className="font-bold text-[#0A3871] bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                            {std.evidence_ids.length} verified record{std.evidence_ids.length > 1 ? "s" : ""}
                          </span>
                        </div>

                        <div className="flex items-start justify-between">
                          <span className="text-slate-500 font-medium">Related Standards ({relatedList.length}):</span>
                          <span className="font-mono text-slate-700 font-semibold text-right max-w-[60%] truncate">
                            {relatedList.length > 0 ? relatedList.join(", ") : "Standalone"}
                          </span>
                        </div>

                        <button
                          type="button"
                          onClick={() => setExpandedStandardId(isExpanded ? null : std.standard_id)}
                          className="w-full mt-2 inline-flex items-center justify-center gap-1 text-[11px] font-bold text-[#0B57D0] hover:text-[#0A47A8] py-1 bg-slate-50 hover:bg-blue-50/50 rounded-lg transition-colors cursor-pointer"
                        >
                          <span>{isExpanded ? "Hide Technical Details" : "View Full Parameters & Provenance"}</span>
                          {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 2: EVIDENCE RECORDS */}
          {!isLoading && activeTab === "evidence" && (
            <div className="mt-6 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-slate-900">
                  Grounded Evidence Records ({filteredEvidence.length} of {summary.evidence_count})
                </h2>
                <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                  Official BIS Publications & Guidelines
                </span>
              </div>

              <div className="space-y-3.5">
                {filteredEvidence.map((ev) => {
                  const linkedStds = standards
                    .filter((s) => s.evidence_ids.includes(ev.evidence_id))
                    .map((s) => s.standard_id);

                  return (
                    <div
                      key={ev.evidence_id}
                      className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs hover:border-slate-300 transition-all"
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-bold text-slate-900 bg-slate-100 px-2.5 py-1 rounded-md">
                            {ev.evidence_id}
                          </span>
                          {ev.verified ? (
                            <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              <span>Verified Official BIS</span>
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-700 bg-amber-50 px-2.5 py-0.5 rounded-full border border-amber-200">
                              <ShieldAlert className="w-3.5 h-3.5" />
                              <span>Secondary Search Record</span>
                            </span>
                          )}
                        </div>

                        <span className="text-xs font-mono text-slate-500">
                          Source ID: {ev.source_id}
                        </span>
                      </div>

                      <div className="mt-3">
                        <h4 className="text-sm font-bold text-slate-900">
                          {ev.source_name}
                        </h4>
                        <p className="mt-2 text-xs text-slate-700 leading-relaxed bg-slate-50 p-3.5 rounded-xl border border-slate-200 font-serif">
                          "{ev.text}"
                        </p>
                      </div>

                      <div className="mt-3 pt-3 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                        <div className="flex items-center gap-1.5">
                          <span className="text-slate-500 font-medium">Linked Standard(s):</span>
                          <div className="flex items-center gap-1">
                            {linkedStds.length > 0 ? (
                              linkedStds.map((stdId, idx) => (
                                <span
                                  key={idx}
                                  className="font-mono font-bold text-slate-800 bg-slate-100 px-2 py-0.5 rounded text-[11px]"
                                >
                                  {stdId}
                                </span>
                              ))
                            ) : (
                              <span className="font-mono text-slate-500 text-[11px]">General Corpus</span>
                            )}
                          </div>
                        </div>

                        <a
                          href={ev.url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-[#0B57D0] hover:underline font-mono text-[11px] font-semibold"
                        >
                          <span>Official Source Link</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 3: RELATIONSHIPS */}
          {!isLoading && activeTab === "relationships" && (
            <div className="mt-6 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-slate-900">
                  Standard Relationship Graph ({filteredRelationships.length} of {summary.relationships_count})
                </h2>
                <span className="text-xs font-semibold text-slate-500">
                  Normative references, test acceptance codes, and codes of practice
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredRelationships.map((rel, idx) => (
                  <div
                    key={idx}
                    className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs hover:border-indigo-400 transition-all flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between gap-2">
                        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-indigo-50 text-indigo-700 border border-indigo-200">
                          {rel.relationship_type.replace(/_/g, " ")}
                        </span>
                        <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                          Verified Link
                        </span>
                      </div>

                      {/* Source -> Target standard visual */}
                      <div className="mt-4 flex items-center justify-between bg-slate-50 p-4 rounded-xl border border-slate-200">
                        <div>
                          <span className="text-[10px] text-slate-400 uppercase font-bold block">
                            Source Standard
                          </span>
                          <span className="font-mono text-sm font-extrabold text-[#0A3871]">
                            {rel.from_standard}
                          </span>
                        </div>

                        <div className="w-8 h-8 rounded-full bg-white border border-slate-200 flex items-center justify-center shadow-xs">
                          <ArrowRight className="w-4 h-4 text-indigo-600" />
                        </div>

                        <div className="text-right">
                          <span className="text-[10px] text-slate-400 uppercase font-bold block">
                            Target Standard
                          </span>
                          <span className="font-mono text-sm font-extrabold text-indigo-700">
                            {rel.to_standard}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                      <span className="text-slate-500 font-medium">Evidence Proof:</span>
                      <span className="font-mono text-[11px] font-bold text-slate-800">
                        {rel.evidence_ids.join(", ")}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: BENCHMARK CASES */}
          {!isLoading && activeTab === "benchmark" && (
            <div className="mt-6 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold text-slate-900">
                    Evaluation & Regression Benchmark Suite ({filteredCases.length} of {summary.benchmark_cases_count})
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Internal regression benchmark test cases (tests reproducibility against the frozen corpus)
                  </p>
                </div>
                <span className="text-xs font-semibold text-purple-700 bg-purple-50 px-2.5 py-1 rounded-full border border-purple-200">
                  Internal Regression Benchmark
                </span>
              </div>

              <div className="space-y-3.5">
                {filteredCases.map((c) => (
                  <div
                    key={c.id}
                    className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs hover:border-slate-300 transition-all"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-[#0A3871] bg-blue-50 px-2.5 py-1 rounded-md border border-blue-100">
                          {c.id}
                        </span>
                        {c.expected_decision && (
                          <span
                            className={`text-[10px] uppercase font-extrabold px-2.5 py-0.5 rounded-full ${
                              c.expected_decision === "RECOMMEND"
                                ? "bg-emerald-100 text-emerald-800"
                                : c.expected_decision === "OUT_OF_CORPUS"
                                ? "bg-purple-100 text-purple-800"
                                : "bg-amber-100 text-amber-800"
                            }`}
                          >
                            Expected: {c.expected_decision}
                          </span>
                        )}
                      </div>

                      <div className="flex items-center gap-1.5 text-xs text-slate-500">
                        <span className="font-medium">Target Standards:</span>
                        <span className="font-mono font-bold text-slate-800">
                          {c.expected_contains && c.expected_contains.length > 0
                            ? c.expected_contains.join(", ")
                            : "None (Out of Corpus)"}
                        </span>
                      </div>
                    </div>

                    <div className="mt-3">
                      <span className="text-[11px] uppercase font-bold text-slate-400 tracking-wider">
                        Evaluation Query
                      </span>
                      <p className="text-xs font-semibold text-slate-900 mt-0.5 bg-slate-50 p-2.5 rounded-lg border border-slate-200 font-mono">
                        "{c.query}"
                      </p>
                    </div>

                    <p className="mt-2.5 text-xs text-slate-600 leading-relaxed">
                      <strong className="text-slate-700">Assertion Rationale:</strong> {c.notes}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: SOURCE PROVENANCE */}
          {!isLoading && activeTab === "sources" && (
            <div className="mt-6 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-slate-900">
                  Verified BIS Source Documents & Provenance ({filteredSources.length} of {summary.sources_count})
                </h2>
                <span className="text-xs font-semibold text-slate-500">
                  Official Bureau of Indian Standards Publications
                </span>
              </div>

              <div className="space-y-4">
                {filteredSources.map((src) => (
                  <div
                    key={src.source_id}
                    className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs hover:border-slate-300 transition-all flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-bold text-slate-900 bg-slate-100 px-2.5 py-1 rounded-md">
                            {src.source_id}
                          </span>
                          <span className="text-[11px] font-bold text-[#0A3871] bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-200">
                            {src.publisher}
                          </span>
                        </div>

                        <div className="flex items-center gap-1.5 text-xs text-slate-500">
                          <Calendar className="w-3.5 h-3.5" />
                          <span>Retrieved: {src.retrieved_at}</span>
                        </div>
                      </div>

                      <h3 className="text-sm sm:text-base font-bold text-slate-900 mt-3">
                        {src.name}
                      </h3>

                      <p className="mt-2 text-xs text-slate-600 leading-relaxed">
                        {src.notes}
                      </p>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                      <span className="text-slate-400 font-mono text-[11px]">
                        Type: {src.source_type}
                      </span>
                      <a
                        href={src.url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-[#0B57D0] hover:underline font-mono text-[11px] font-semibold"
                      >
                        <span>Open Official Document</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Quick Action to Main Search */}
          <div className="mt-12 p-6 rounded-2xl bg-gradient-to-r from-[#0A3871] to-[#124B8A] text-white flex flex-col sm:flex-row items-center justify-between gap-4 shadow-md">
            <div>
              <h3 className="text-base font-bold">
                Ready to evaluate a procurement specification?
              </h3>
              <p className="text-xs text-blue-100/90 mt-1">
                Enter your product requirements or upload technical tender documents on the main evaluation engine.
              </p>
            </div>
            <Link
              href="/"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white hover:bg-slate-50 text-[#0A3871] text-xs sm:text-sm font-bold shadow-sm transition-all flex-shrink-0"
            >
              <span>Back to SpecWise Search</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </section>
      </main>

      <AboutModal
        isOpen={isAboutModalOpen}
        onClose={() => setIsAboutModalOpen(false)}
      />
      <Footer />
    </div>
  );
}
