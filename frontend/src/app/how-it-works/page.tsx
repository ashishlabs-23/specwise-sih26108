"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { AboutModal } from "@/components/AboutModal";
import {
  FileText,
  Upload,
  Cpu,
  Search,
  CheckCircle2,
  GitFork,
  ShieldCheck,
  Award,
  FileCheck,
  AlertTriangle,
  HelpCircle,
  ShieldAlert,
  ArrowRight,
  Database,
  Layers,
  Sparkles,
  BookOpen,
  Info,
} from "lucide-react";

export default function HowItWorksPage() {
  const [isAboutModalOpen, setIsAboutModalOpen] = useState(false);

  const pipelineSteps = [
    {
      step: "01",
      title: "Input Ingestion (Text or Tender PDF)",
      icon: Upload,
      category: "Input Layer",
      desc: "Accepts plain-text trade descriptions, procurement queries, or technical specification PDF documents (up to 25 MB). Ingested PDFs are parsed via PyMuPDF with automated text layer validation.",
    },
    {
      step: "02",
      title: "Requirement Extraction & Parameter Isolation",
      icon: Cpu,
      category: "AI & Rule Extraction",
      desc: "Extracts structured product terms (e.g. openwell, borewell, monoset), technical attributes (power ratings like 5 HP / 3.7 kW), application domain (agricultural irrigation), and cited standard references.",
    },
    {
      step: "03",
      title: "Hybrid Multi-Stage Retrieval",
      icon: Search,
      category: "Retrieval Layer",
      desc: "Combines exact IS-identifier resolution, lexical BM25 keyword matching, and dense semantic neural embeddings (SentenceTransformers), fused via Reciprocal Rank Fusion (RRF).",
    },
    {
      step: "04",
      title: "Evidence & Validity Grounding",
      icon: CheckCircle2,
      category: "Evidence Layer",
      desc: "Every candidate standard is verified against curated official BIS publications, committee programme of work documents, and implementation guidelines. No hallucinations or ungrounded claims are emitted.",
    },
    {
      step: "05",
      title: "Deterministic Applicability Gates",
      icon: ShieldCheck,
      category: "Gating Layer",
      desc: "Applies rule-based inclusion, product-term compatibility, and exclusion-term verification to classify applicability as 'strong', 'possible', or 'weak'.",
    },
    {
      step: "06",
      title: "Normative Graph Traversal",
      icon: GitFork,
      category: "Graph Layer",
      desc: "Traverses knowledge graph edges to surface referenced motor specifications (IS 9283), hydraulic test acceptance codes (IS 11346), and codes of practice (IS 14536) linked to primary product standards.",
    },
    {
      step: "07",
      title: "Certification & Regulatory Verification",
      icon: Award,
      category: "Policy Layer",
      desc: "Evaluates Quality Control Orders (QCO) and BIS certification schemes. Unconfirmed regulatory drafts are transparently flagged as not_verified_in_prototype_corpus rather than asserting ungrounded mandates.",
    },
    {
      step: "08",
      title: "Confidence & Decision Synthesis",
      icon: Layers,
      category: "Decision Engine",
      desc: "Synthesizes retrieval scores, applicability gates, and requirement coverage into one of four unambiguous decision states: RECOMMEND, REVIEW, ABSTAIN, or OUT_OF_CORPUS.",
    },
    {
      step: "09",
      title: "Audit Report Generation",
      icon: FileCheck,
      category: "Output Layer",
      desc: "Generates an auditable procurement compliance report with structured parameter coverage, gap analysis, and direct source citations exportable to standalone HTML.",
    },
  ];

  const decisionStates = [
    {
      state: "RECOMMEND",
      label: "Definitive Match",
      badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-300",
      icon: CheckCircle2,
      iconColor: "text-emerald-600",
      desc: "Assigned when the product description uniquely matches the primary scope of an active standard, satisfies all deterministic applicability gates, and has verified evidence citations.",
    },
    {
      state: "REVIEW",
      label: "Human Review Needed",
      badgeColor: "bg-amber-100 text-amber-800 border-amber-300",
      icon: AlertTriangle,
      iconColor: "text-amber-600",
      desc: "Assigned when multiple competing standards are plausible, specifications require technical confirmation, or overlapping product features require domain engineer discretion.",
    },
    {
      state: "ABSTAIN",
      label: "Insufficient Information",
      badgeColor: "bg-slate-100 text-slate-800 border-slate-300",
      icon: HelpCircle,
      iconColor: "text-slate-600",
      desc: "Assigned when the input query is too generic (e.g. 'submersible pump') to distinguish between distinct standards like openwell (IS 14220) and borewell (IS 8034). Prompts the user for specific parameters.",
    },
    {
      state: "OUT_OF_CORPUS",
      label: "Outside Prototype Corpus",
      badgeColor: "bg-purple-100 text-purple-800 border-purple-300",
      icon: ShieldAlert,
      iconColor: "text-purple-600",
      desc: "Assigned when the requested equipment is completely outside the pump-sector demonstration corpus (MED 20). Prevents false matches by declining to recommend unsupported items.",
    },
  ];

  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      <Navbar onAboutClick={() => setIsAboutModalOpen(true)} />

      <main className="flex-1">
        {/* Header Hero */}
        <section className="bg-gradient-to-b from-white to-slate-100 border-b border-slate-200 pt-8 pb-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-xs font-semibold text-[#0B57D0] mb-3">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Evidence-Grounded Recommendation Architecture</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-[#0A3871] tracking-tight">
              How SpecWise Works
            </h1>
            <p className="mt-2 text-sm sm:text-base text-slate-600 max-w-3xl leading-relaxed">
              An evidence-grounded decision support engine combining AI-powered requirement extraction with deterministic BIS standard applicability gates.
            </p>

            {/* Core Architectural Principle Banner */}
            <div className="mt-6 p-5 rounded-2xl bg-white border border-slate-200 shadow-xs grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
              <div className="flex items-start gap-3.5">
                <div className="w-10 h-10 rounded-xl bg-blue-50 text-[#0B57D0] flex items-center justify-center flex-shrink-0 mt-0.5 border border-blue-200">
                  <Cpu className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">
                    AI for Language & Requirement Understanding
                  </h3>
                  <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                    AI parses natural procurement specifications, handles trade vocabulary mismatches, and extracts structured technical parameters.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3.5 md:border-l md:border-slate-100 md:pl-6">
                <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center flex-shrink-0 mt-0.5 border border-emerald-200">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">
                    Deterministic Checks for Standard Support
                  </h3>
                  <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                    Recommendations are never fabricated by language models; they are strictly established by evidence-grounded deterministic rules and verified BIS publications.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 9-Step Pipeline Section */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <div className="pb-4 border-b border-slate-200 mb-8">
            <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight">
              The 9-Stage Recommendation Pipeline
            </h2>
            <p className="text-xs sm:text-sm text-slate-500 mt-1">
              End-to-end processing from tender input to verified procurement audit report
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {pipelineSteps.map((step) => {
              const Icon = step.icon;
              return (
                <div
                  key={step.step}
                  className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs hover:border-blue-400 transition-all flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-blue-50 text-[#0B57D0] flex items-center justify-center font-bold text-xs border border-blue-100">
                          <Icon className="w-4 h-4" />
                        </div>
                        <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                          Stage {step.step}
                        </span>
                      </div>
                      <span className="text-[10px] font-bold text-[#0A3871] bg-slate-100 px-2 py-0.5 rounded">
                        {step.category}
                      </span>
                    </div>

                    <h3 className="text-sm font-bold text-slate-900 mt-3">
                      {step.title}
                    </h3>

                    <p className="mt-2 text-xs text-slate-600 leading-relaxed">
                      {step.desc}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Four Decision States Section */}
        <section className="bg-white border-y border-slate-200 py-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="pb-4 border-b border-slate-100 mb-8">
              <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight">
                The Four Explicit Decision Outcomes
              </h2>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                SpecWise avoids false confidence by explicitly gating outcomes into four deterministic states
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {decisionStates.map((ds) => {
                const Icon = ds.icon;
                return (
                  <div
                    key={ds.state}
                    className="rounded-2xl border border-slate-200 p-6 bg-slate-50/50 hover:bg-white hover:border-slate-300 transition-all flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between gap-2 pb-3 border-b border-slate-200">
                        <div className="flex items-center gap-2.5">
                          <Icon className={`w-5 h-5 ${ds.iconColor}`} />
                          <span className="font-mono text-sm font-extrabold text-slate-900">
                            {ds.state}
                          </span>
                        </div>
                        <span
                          className={`text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full border ${ds.badgeColor}`}
                        >
                          {ds.label}
                        </span>
                      </div>

                      <p className="mt-3 text-xs sm:text-sm text-slate-600 leading-relaxed">
                        {ds.desc}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Prototype Scope Disclosure */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <div className="p-6 rounded-2xl bg-amber-50/80 border border-amber-200 text-amber-900">
            <h3 className="text-base font-bold flex items-center gap-2">
              <Info className="w-4 h-4 text-amber-600" />
              <span>Prototype Scope & Corpus Integrity</span>
            </h3>
            <p className="text-xs sm:text-sm text-amber-800 mt-2 leading-relaxed">
              SpecWise currently operates on a frozen, evidence-grounded demonstration corpus of <strong>7 verified Indian Standards</strong> under Technical Committee MED 20 (Pumps and fluid handling). It is designed to demonstrate safe procurement assistance, deterministic gating, and verifiable evidence traceability before expanding to the broader national standards database.
            </p>

            <div className="mt-4 flex flex-wrap items-center gap-3">
              <Link
                href="/resources"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-amber-200/80 hover:bg-amber-300/80 text-amber-900 text-xs font-bold transition-colors"
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span>Explore Corpus & Evidence in Resources</span>
              </Link>

              <Link
                href="/"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#0A3871] hover:bg-[#082a57] text-white text-xs font-bold transition-colors"
              >
                <span>Try Main SpecWise Search</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
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
