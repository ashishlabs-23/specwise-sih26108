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
import { analyzeProduct, fetchStandardDetails } from "@/lib/api";
import { AlertCircle, Loader2, Sparkles, RefreshCw } from "lucide-react";

export default function HomePage() {
  const [inputText, setInputText] = useState<string>(
    "openwell submersible pumpset for agricultural irrigation"
  );
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<AnalysisResponse | null>(null);
  const [primaryStandard, setPrimaryStandard] = useState<StandardRecord | null>(null);

  // Modals state
  const [isPdfModalOpen, setIsPdfModalOpen] = useState(false);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [isSourcesModalOpen, setIsSourcesModalOpen] = useState(false);
  const [isAboutModalOpen, setIsAboutModalOpen] = useState(false);

  // Search handler
  const handleSearch = async (text: string) => {
    if (!text.trim()) return;
    setIsLoading(true);
    setError(null);

    try {
      const data = await analyzeProduct({ text: text.trim() });
      setResponse(data);

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

  // Perform initial search on mount with default query to match demo state
  useEffect(() => {
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
