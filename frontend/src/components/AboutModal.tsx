"use client";

import React from "react";
import { X, ShieldCheck, CheckCircle2, Layers, Cpu, Award } from "lucide-react";

interface AboutModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AboutModal({ isOpen, onClose }: AboutModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-2 sm:p-4">
      <div className="bg-white rounded-2xl max-w-xl w-full p-4 sm:p-6 shadow-2xl border border-slate-200 relative animate-in fade-in zoom-in-95 duration-150 overflow-hidden">
        <button
          onClick={onClose}
          className="absolute top-3.5 right-3.5 text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 cursor-pointer z-10"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 pb-4 border-b border-slate-100 pr-8 min-w-0">
          <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-blue-50 text-[#0B57D0] flex items-center justify-center border border-blue-200 flex-shrink-0">
            <Award className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <h3 className="text-sm sm:text-base font-bold text-slate-900 truncate">
              About SpecWise (SIH26108)
            </h3>
            <p className="text-[11px] sm:text-xs text-slate-500 font-medium truncate">
              Smart Procurement Indian Standards Recommendation & Assurance
            </p>
          </div>
        </div>

        <div className="mt-4 space-y-3.5 text-xs sm:text-sm text-slate-600 leading-relaxed">
          <div className="p-3 bg-blue-50/70 border border-blue-200 rounded-xl text-xs text-[#0A3871]">
            <strong>Objective:</strong> Help government buyers, MSMEs, and citizens identify the exact applicable Indian Standards (BIS) from unstructured descriptions, avoiding tender non-compliance.
          </div>

          <div>
            <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider mb-1">
              Key Engineering Principles
            </h4>
            <ul className="space-y-1.5 text-xs">
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span><strong>Retrieval is not Applicability:</strong> Search candidates are verified through deterministic policy gates and evidence citations.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span><strong>No Hallucinated Standards:</strong> Every recommendation links directly to verified BIS committee evidence and guidelines.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span><strong>Normative Graph Expansion:</strong> Identifies mandatory component standards (e.g. motors) and Codes of Practice (CoP).</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span><strong>Four-State Routing:</strong> RECOMMEND, REVIEW, ABSTAIN, OUT_OF_CORPUS.</span>
              </li>
            </ul>
          </div>

          <div className="pt-2 border-t border-slate-100 text-[11px] text-slate-400">
            Smart India Hackathon 2024 / 2026 Prototype • Developed for Bureau of Indian Standards assurance workflow.
          </div>
        </div>

        <div className="mt-5 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-slate-900 text-white hover:bg-slate-800 cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
