"use client";

import React, { useState } from "react";
import { Search, FileText, Upload, ShieldCheck, FileCheck, Users, Sparkles, Loader2 } from "lucide-react";

interface HeroSearchProps {
  inputText: string;
  setInputText: (val: string) => void;
  onSearch: (text: string) => void;
  isLoading: boolean;
  onOpenPdfModal: () => void;
}

export function HeroSearch({
  inputText,
  setInputText,
  onSearch,
  isLoading,
  onOpenPdfModal,
}: HeroSearchProps) {
  const [activeTab, setActiveTab] = useState<"text" | "pdf">("text");

  const sampleQueries = [
    { label: "openwell submersible pumpset", text: "openwell submersible pumpset for agricultural irrigation" },
    { label: "borewell submersible", text: "submersible pumpset for a borewell supplying agricultural water" },
    { label: "monoset pump", text: "monoset pump for clear cold water for agriculture" },
    { label: "out of corpus query", text: "advanced underwater robotic mining vehicle" },
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputText.trim()) {
      onSearch(inputText.trim());
    }
  };

  return (
    <div className="relative bg-gradient-to-b from-slate-50 to-white pt-8 pb-12 border-b border-slate-200 overflow-hidden">
      {/* Subtle Background Elements */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-blue-100/40 rounded-full blur-3xl -z-10 pointer-events-none" />
      <div className="absolute bottom-0 left-10 w-80 h-80 bg-emerald-50/50 rounded-full blur-2xl -z-10 pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          
          {/* Left Column: Heading, Tabs, Input Form */}
          <div className="lg:col-span-7 flex flex-col justify-center">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200/60 text-xs font-semibold text-[#0B57D0] w-fit mb-3">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Evidence-Grounded BIS Decision Support</span>
            </div>

            <h1 className="text-3xl sm:text-4xl lg:text-[40px] font-extrabold text-[#0A3871] tracking-tight leading-[1.2]">
              Not sure which <br />
              <span className="text-[#0B57D0]">Indian Standard</span> applies?
            </h1>

            <p className="mt-3 text-sm sm:text-base text-slate-600 max-w-xl leading-relaxed">
              Describe your product or paste tender specifications. SpecWise helps you find the most relevant BIS standards with clear guidance and trusted sources.
            </p>

            {/* Input Method Tabs */}
            <div className="mt-6 flex items-center gap-3">
              <button
                type="button"
                onClick={() => setActiveTab("text")}
                className={`inline-flex items-center gap-2 px-4 py-2 text-xs sm:text-sm font-semibold rounded-lg border transition-all ${
                  activeTab === "text"
                    ? "bg-white text-[#0A3871] border-blue-500 shadow-sm ring-2 ring-blue-500/10"
                    : "bg-slate-100 text-slate-600 border-slate-200 hover:bg-slate-200/70"
                }`}
              >
                <FileText className="w-4 h-4 text-[#0B57D0]" />
                <span>Enter Description</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  setActiveTab("pdf");
                  onOpenPdfModal();
                }}
                className={`inline-flex items-center gap-2 px-4 py-2 text-xs sm:text-sm font-semibold rounded-lg border transition-all ${
                  activeTab === "pdf"
                    ? "bg-white text-[#0A3871] border-blue-500 shadow-sm"
                    : "bg-slate-100 text-slate-600 border-slate-200 hover:bg-slate-200/70"
                }`}
              >
                <Upload className="w-4 h-4 text-slate-500" />
                <span>Upload Document (PDF)</span>
              </button>
            </div>

            {/* Input Form Box */}
            <form onSubmit={handleSubmit} className="mt-4">
              <div className="relative rounded-xl border border-slate-300 bg-white shadow-md focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 transition-all p-3">
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="e.g. openwell submersible pumpset for agricultural irrigation"
                  rows={3}
                  maxLength={2000}
                  className="w-full text-slate-800 placeholder-slate-400 text-sm sm:text-base outline-none resize-none pr-3"
                />

                <div className="flex items-center justify-between pt-2 border-t border-slate-100 mt-1">
                  <span className="text-[11px] text-slate-400 font-mono">
                    {inputText.length}/2000
                  </span>

                  <button
                    type="submit"
                    disabled={isLoading || !inputText.trim()}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[#0B57D0] hover:bg-[#0A47A8] disabled:bg-slate-300 text-white font-medium text-xs sm:text-sm shadow-sm transition-all cursor-pointer"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Analyzing Standards...</span>
                      </>
                    ) : (
                      <>
                        <Search className="w-4 h-4" />
                        <span>Find Applicable Standards</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </form>

            {/* Example Queries */}
            <div className="mt-3 flex flex-wrap items-center gap-1.5 text-xs text-slate-500">
              <span className="font-medium text-slate-600">Examples:</span>
              {sampleQueries.map((ex, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setInputText(ex.text);
                    onSearch(ex.text);
                  }}
                  className="px-2 py-0.5 rounded bg-slate-100 hover:bg-blue-50 hover:text-[#0B57D0] border border-slate-200 text-[11px] text-slate-700 transition-colors"
                >
                  "{ex.label}"
                </button>
              ))}
            </div>
          </div>

          {/* Right Column: Hero Graphic Card with Real Field Theme */}
          <div className="lg:col-span-5 flex justify-center">
            <div className="w-full max-w-md relative rounded-2xl overflow-hidden shadow-xl border border-slate-200 bg-gradient-to-br from-[#0F3968] via-[#124B8A] to-[#1A62B8] text-white p-6 sm:p-8 flex flex-col justify-between min-h-[360px]">
              
              {/* Agricultural Water Pump Graphic Backdrop */}
              <div className="absolute inset-0 opacity-15 mix-blend-overlay pointer-events-none bg-[radial-gradient(#fff_1px,transparent_1px)] [background-size:16px_16px]" />
              
              {/* Top Water Pump Flow Visual */}
              <div className="relative z-10 flex items-center justify-between pb-4 border-b border-white/15">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-white/20 backdrop-blur-md flex items-center justify-center">
                    <ShieldCheck className="w-5 h-5 text-emerald-300" />
                  </div>
                  <span className="text-xs font-semibold tracking-wide uppercase text-blue-100">
                    BIS Standards Engine
                  </span>
                </div>
                <span className="text-[11px] px-2 py-0.5 rounded bg-emerald-400/20 text-emerald-200 border border-emerald-400/30 font-medium">
                  Verified Data
                </span>
              </div>

              {/* 3 Value Pillars */}
              <div className="relative z-10 my-6 space-y-4">
                <div className="flex items-start gap-3.5">
                  <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <ShieldCheck className="w-4 h-4 text-emerald-300" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white">
                      Make informed procurement decisions
                    </h4>
                    <p className="text-xs text-blue-100/80 mt-0.5 leading-normal">
                      Avoid incorrect standard citations in tender documents and purchase orders.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3.5">
                  <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <FileCheck className="w-4 h-4 text-blue-300" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white">
                      Based on Indian Standards & official sources
                    </h4>
                    <p className="text-xs text-blue-100/80 mt-0.5 leading-normal">
                      Every result is grounded in BIS committee evidence, guidelines, and published standards.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3.5">
                  <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Users className="w-4 h-4 text-amber-300" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white">
                      Designed for citizens, buyers and government users
                    </h4>
                    <p className="text-xs text-blue-100/80 mt-0.5 leading-normal">
                      Plain-language summaries backed by deep technical compliance traceability.
                    </p>
                  </div>
                </div>
              </div>

              {/* Quality builds a better tomorrow cursive banner */}
              <div className="relative z-10 pt-4 border-t border-white/15 flex items-center justify-between">
                <span className="text-base sm:text-lg font-serif italic text-amber-200 tracking-wide">
                  "Quality builds a better tomorrow"
                </span>
                <span className="text-[10px] text-blue-200 uppercase tracking-widest font-bold">
                  BIS • मानक
                </span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
