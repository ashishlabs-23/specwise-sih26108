"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "@/components/Navbar";
import { HeroSearch } from "@/components/HeroSearch";
import { DecisionBanner } from "@/components/DecisionBanner";
import { KeyDetailsCard } from "@/components/KeyDetailsCard";
import { RelatedStandardsCard } from "@/components/RelatedStandardsCard";
import { EvidenceSourcesCard } from "@/components/EvidenceSourcesCard";
import { CertificationBanner } from "@/components/CertificationBanner";
import { AdvancedDetailsAccordion } from "@/components/AdvancedDetailsAccordion";
import { PdfUploadModal } from "@/components/PdfUploadModal";
import { ReportViewModal } from "@/components/ReportViewModal";
import { AllSourcesModal } from "@/components/AllSourcesModal";
import { AboutModal } from "@/components/AboutModal";
import { Footer } from "@/components/Footer";
import { AnalysisResponse, StandardRecord } from "@/types/api";
import { analyzeProduct, fetchStandardDetails, startRenderKeepAlive } from "@/lib/api";
import { AlertCircle, Loader2, Sparkles, RefreshCw, XCircle } from "lucide-react";

export default function HomePage() {
  const [inputText, setInputText] = useState<string>(
    "openwell submersible pumpset for agricultural irrigation"
  );
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<AnalysisResponse | null>(null);
  const [primaryStandard, setPrimaryStandard] = useState<StandardRecord | null>(null);
  const [recentQueries, setRecentQueries] = useState<string[]>([]);

  // Modals state
  const [isPdfModalOpen, setIsPdfModalOpen] = useState(false);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [isSourcesModalOpen, setIsSourcesModalOpen] = useState(false);
  const [isAboutModalOpen, setIsAboutModalOpen] = useState(false);

  // Load recent queries from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem("specwise_recent_queries");
      if (saved) {
        setRecentQueries(JSON.parse(saved));
      }
    } catch {
      // ignore
    }
  }, []);

  const saveRecentQuery = (query: string) => {
    try {
      const updated = [query, ...recentQueries.filter((q) => q.toLowerCase() !== query.toLowerCase())].slice(0, 5);
      setRecentQueries(updated);
      localStorage.setItem("specwise_recent_queries", JSON.stringify(updated));
    } catch {
      // ignore
    }
  };

  const handleClearRecentQueries = () => {
    setRecentQueries([]);
    try {
      localStorage.removeItem("specwise_recent_queries");
    } catch {
      // ignore
    }
  };

  // Search handler
  const handleSearch = async (text: string) => {
    if (!text.trim()) return;
    setIsLoading(true);
    setError(null);

    // Sync query parameter to URL for deep linking
    try {
      if (typeof window !== "undefined") {
        const newUrl = new URL(window.location.href);
        newUrl.searchParams.set("q", text.trim());
        window.history.replaceState({}, "", newUrl.toString());
      }
    } catch {
      // ignore
    }

    try {
      const data = await analyzeProduct({ text: text.trim() });
      setResponse(data);
      saveRecentQuery(text.trim());

      // Save latest session cache
      try {
        localStorage.setItem("specwise_last_query", text.trim());
        localStorage.setItem("specwise_last_result", JSON.stringify(data));
      } catch {
        // ignore
      }

      // Fetch primary standard details if strong recommendation exists
      const strongApp = data.applicability.find((a) => a.result === "strong");
      const targetId = strongApp?.standard_id || data.candidates[0]?.standard_id;

      if (targetId && data.decision !== "OUT_OF_CORPUS") {
        try {
          const stdData = await fetchStandardDetails(targetId);
          setPrimaryStandard(stdData.standard);
        } catch {
          setPrimaryStandard(null);
        }
      } else {
        setPrimaryStandard(null);
      }

      // Smooth scroll to results
      setTimeout(() => {
        const resEl = document.getElementById("results-section");
        if (resEl) {
          resEl.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      }, 100);
    } catch (err: any) {
      setError(
        err.message ||
          "Unable to connect to the BIS recommendation API. Please ensure the backend engine is running on http://127.0.0.1:8000."
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Reset search and results
  const handleResetSearch = () => {
    setInputText("");
    setResponse(null);
    setPrimaryStandard(null);
    setError(null);
    try {
      localStorage.removeItem("specwise_last_result");
      const newUrl = new URL(window.location.href);
      newUrl.searchParams.delete("q");
      window.history.replaceState({}, "", newUrl.toString());
    } catch {
      // ignore
    }
  };

  // Initial load: start Render keep-alive, check URL params, then session cache, then default demo query
  useEffect(() => {
    if (typeof window === "undefined") return;

    // Start 14-min keep-alive ping to prevent Render free instance sleep
    startRenderKeepAlive();

    const urlParams = new URLSearchParams(window.location.search);
    const queryParam = urlParams.get("q");

    if (queryParam && queryParam.trim()) {
      setInputText(queryParam.trim());
      handleSearch(queryParam.trim());
      return;
    }

    try {
      const cachedResult = localStorage.getItem("specwise_last_result");
      const cachedQuery = localStorage.getItem("specwise_last_query");
      if (cachedResult && cachedQuery) {
        const parsed = JSON.parse(cachedResult);
        setInputText(cachedQuery);
        setResponse(parsed);
        const strongApp = parsed.applicability?.find((a: any) => a.result === "strong");
        const targetId = strongApp?.standard_id || parsed.candidates?.[0]?.standard_id;
        if (targetId && parsed.decision !== "OUT_OF_CORPUS") {
          fetchStandardDetails(targetId)
            .then((res) => setPrimaryStandard(res.standard))
            .catch(() => setPrimaryStandard(null));
        }
        return;
      }
    } catch {
      // ignore cache parsing error
    }

    // Default initial demonstration search
    handleSearch("openwell submersible pumpset for agricultural irrigation");
  }, []);

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar onAboutClick={() => setIsAboutModalOpen(true)} />

      <main className="flex-1">
        {/* Hero & Search Section */}
        <HeroSearch
          inputText={inputText}
          setInputText={setInputText}
          onSearch={handleSearch}
          isLoading={isLoading}
          onOpenPdfModal={() => setIsPdfModalOpen(true)}
          recentQueries={recentQueries}
          onClearRecentQueries={handleClearRecentQueries}
        />

        {/* Results Section */}
        <section id="results-section" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 pb-12">
          {error && (
            <div className="p-4 mb-6 rounded-xl bg-red-50 border border-red-200 text-red-800 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-bold text-sm">Connection / API Error</h4>
                <p className="text-xs mt-1 leading-relaxed">{error}</p>
                <button
                  onClick={() => handleSearch(inputText)}
                  className="mt-3 inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-red-100 hover:bg-red-200 text-red-900 text-xs font-semibold"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>Retry Analysis</span>
                </button>
              </div>
            </div>
          )}

          {isLoading && !response && (
            <div className="py-20 flex flex-col items-center justify-center text-center">
              <Loader2 className="w-10 h-10 text-[#0B57D0] animate-spin mb-4" />
              <h3 className="text-base font-bold text-slate-800">
                Evaluating Applicable Indian Standards...
              </h3>
              <p className="text-xs text-slate-500 mt-1 max-w-sm">
                Running requirement extraction, BM25 retrieval, deterministic applicability gates, and graph traversal.
              </p>
            </div>
          )}

          {response && (
            <div className="space-y-6 animate-in fade-in duration-300">
              {/* Decision Card */}
              <DecisionBanner
                response={response}
                primaryStandard={primaryStandard}
                onNewSearch={() => {
                  window.scrollTo({ top: 0, behavior: "smooth" });
                }}
                onDownloadReport={() => setIsReportModalOpen(true)}
              />

              {/* 3-Column Core Breakdown Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <KeyDetailsCard
                  response={response}
                  primaryStandard={primaryStandard}
                />
                <RelatedStandardsCard
                  response={response}
                  onSelectStandard={(stdId) => {
                    setInputText(`procurement compliance as per ${stdId}`);
                    handleSearch(`procurement compliance as per ${stdId}`);
                  }}
                  onViewAll={() => {
                    const accEl = document.getElementById("advanced-accordion");
                    if (accEl) accEl.scrollIntoView({ behavior: "smooth" });
                  }}
                />
                <EvidenceSourcesCard
                  response={response}
                  onViewAllSources={() => setIsSourcesModalOpen(true)}
                />
              </div>

              {/* Certification / QCO Status Banner */}
              <CertificationBanner response={response} />

              {/* Progressive Disclosure: Advanced Details Accordion */}
              <div id="advanced-accordion" className="pt-2">
                <AdvancedDetailsAccordion
                  response={response}
                  onOpenReportModal={() => setIsReportModalOpen(true)}
                />
              </div>
            </div>
          )}
        </section>
      </main>

      {/* Modals */}
      <PdfUploadModal
        isOpen={isPdfModalOpen}
        onClose={() => setIsPdfModalOpen(false)}
        onAnalysisComplete={async (data) => {
          setResponse(data);
          setError(null);
          const strongApp = data.applicability.find((a) => a.result === "strong");
          const targetId = strongApp?.standard_id || data.candidates[0]?.standard_id;
          if (targetId && data.decision !== "OUT_OF_CORPUS") {
            try {
              const stdData = await fetchStandardDetails(targetId);
              setPrimaryStandard(stdData.standard);
            } catch {
              setPrimaryStandard(null);
            }
          } else {
            setPrimaryStandard(null);
          }
          setTimeout(() => {
            const resEl = document.getElementById("results-section");
            if (resEl) {
              resEl.scrollIntoView({ behavior: "smooth", block: "start" });
            }
          }, 100);
        }}
      />

      {response && (
        <ReportViewModal
          isOpen={isReportModalOpen}
          onClose={() => setIsReportModalOpen(false)}
          response={response}
        />
      )}

      {response && (
        <AllSourcesModal
          isOpen={isSourcesModalOpen}
          onClose={() => setIsSourcesModalOpen(false)}
          evidence={response.evidence}
        />
      )}

      <AboutModal
        isOpen={isAboutModalOpen}
        onClose={() => setIsAboutModalOpen(false)}
      />

      <Footer />
    </div>
  );
}
