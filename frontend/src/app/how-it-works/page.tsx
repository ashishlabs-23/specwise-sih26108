"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { AboutModal } from "@/components/AboutModal";
import { useLanguage } from "@/context/LanguageContext";
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
  const { t } = useLanguage();

  const pipelineSteps = [
    {
      step: "01",
      title: t.stage01Title,
      icon: Upload,
      category: t.stage01Category,
      desc: t.stage01Desc,
    },
    {
      step: "02",
      title: t.stage02Title,
      icon: Cpu,
      category: t.stage02Category,
      desc: t.stage02Desc,
    },
    {
      step: "03",
      title: t.stage03Title,
      icon: Search,
      category: t.stage03Category,
      desc: t.stage03Desc,
    },
    {
      step: "04",
      title: t.stage04Title,
      icon: CheckCircle2,
      category: t.stage04Category,
      desc: t.stage04Desc,
    },
    {
      step: "05",
      title: t.stage05Title,
      icon: ShieldCheck,
      category: t.stage05Category,
      desc: t.stage05Desc,
    },
    {
      step: "06",
      title: t.stage06Title,
      icon: GitFork,
      category: t.stage06Category,
      desc: t.stage06Desc,
    },
    {
      step: "07",
      title: t.stage07Title,
      icon: Award,
      category: t.stage07Category,
      desc: t.stage07Desc,
    },
    {
      step: "08",
      title: t.stage08Title,
      icon: Layers,
      category: t.stage08Category,
      desc: t.stage08Desc,
    },
    {
      step: "09",
      title: t.stage09Title,
      icon: FileCheck,
      category: t.stage09Category,
      desc: t.stage09Desc,
    },
  ];

  const decisionStates = [
    {
      state: "RECOMMEND",
      label: t.decisionRecommendLabel,
      badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-300",
      icon: CheckCircle2,
      iconColor: "text-emerald-600",
      desc: t.decisionRecommendDesc,
    },
    {
      state: "REVIEW",
      label: t.decisionReviewLabel,
      badgeColor: "bg-amber-100 text-amber-800 border-amber-300",
      icon: AlertTriangle,
      iconColor: "text-amber-600",
      desc: t.decisionReviewDesc,
    },
    {
      state: "ABSTAIN",
      label: t.decisionAbstainLabel,
      badgeColor: "bg-slate-100 text-slate-800 border-slate-300",
      icon: HelpCircle,
      iconColor: "text-slate-600",
      desc: t.decisionAbstainDesc,
    },
    {
      state: "OUT_OF_CORPUS",
      label: t.decisionOutOfCorpusLabel,
      badgeColor: "bg-purple-100 text-purple-800 border-purple-300",
      icon: ShieldAlert,
      iconColor: "text-purple-600",
      desc: t.decisionOutOfCorpusDesc,
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
              <span>{t.howItWorksPageBadge}</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-[#0A3871] tracking-tight">
              {t.howItWorksH1}
            </h1>
            <p className="mt-2 text-sm sm:text-base text-slate-600 max-w-3xl leading-relaxed">
              {t.howItWorksDesc}
            </p>

            {/* Core Architectural Principle Banner */}
            <div className="mt-6 p-5 rounded-2xl bg-white border border-slate-200 shadow-xs grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
              <div className="flex items-start gap-3.5">
                <div className="w-10 h-10 rounded-xl bg-blue-50 text-[#0B57D0] flex items-center justify-center flex-shrink-0 mt-0.5 border border-blue-200">
                  <Cpu className="w-5 h-5" />
                </div>
                <div>
                   <h3 className="text-sm font-bold text-slate-900">
                    {t.aiLanguageTitle}
                  </h3>
                  <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                    {t.aiLanguageDesc}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3.5 md:border-l md:border-slate-100 md:pl-6">
                <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center flex-shrink-0 mt-0.5 border border-emerald-200">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">
                    {t.deterministicTitle}
                  </h3>
                  <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                    {t.deterministicDesc}
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
              {t.pipelineH2}
            </h2>
            <p className="text-xs sm:text-sm text-slate-500 mt-1">
              {t.pipelineDesc}
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
                          {t.stageLabel} {step.step}
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
                {t.decisionOutcomesH2}
              </h2>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                {t.decisionOutcomesDesc}
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
              <span>{t.prototypeCorpusH3}</span>
            </h3>
            <p className="text-xs sm:text-sm text-amber-800 mt-2 leading-relaxed">
              {t.prototypeCorpusDesc}
            </p>

            <div className="mt-4 flex flex-wrap items-center gap-3">
              <Link
                href="/resources"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-amber-200/80 hover:bg-amber-300/80 text-amber-900 text-xs font-bold transition-colors"
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span>{t.exploreCorpus}</span>
              </Link>

              <Link
                href="/"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#0A3871] hover:bg-[#082a57] text-white text-xs font-bold transition-colors"
              >
                <span>{t.trySearch}</span>
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
