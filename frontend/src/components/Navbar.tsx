"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { User, ChevronDown, Info, ExternalLink, ShieldCheck } from "lucide-react";

export function Navbar({ onAboutClick }: { onAboutClick?: () => void }) {
  const pathname = usePathname();
  const [lang, setLang] = useState("English");
  const [showLangMenu, setShowLangMenu] = useState(false);

  return (
    <header className="w-full bg-white border-b border-slate-200 sticky top-0 z-40">
      {/* Top Government Disclaimer Banner */}
      <div className="bg-slate-900 text-slate-200 text-xs px-4 py-1.5 flex items-center justify-between">
        <div className="flex items-center gap-2 max-w-7xl mx-auto w-full">
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30">
            SIH26108 Prototype
          </span>
          <span className="text-slate-300 truncate">
            SpecWise — Smart Procurement Standards Engine. Not an official BIS portal.
          </span>
          <a
            href="https://www.bis.gov.in"
            target="_blank"
            rel="noreferrer"
            className="ml-auto flex items-center gap-1 text-slate-400 hover:text-white transition-colors"
          >
            <span>Official Portal</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>

        {/* Main Header */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Left: BIS Emblem + SpecWise Brand */}
        <div className="flex items-center gap-4 lg:gap-6">
          {/* BIS Emblem Logo (icon only) */}
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-lg bg-[#0A3871] text-white flex items-center justify-center p-1 shadow-sm flex-shrink-0" aria-hidden>
              <div className="w-6 h-6 border-2 border-white rounded-sm flex items-center justify-center relative">
                <div className="w-3 h-3 bg-amber-400 rotate-45" />
              </div>
            </div>
          </div>

          {/* SpecWise Brand */}
          <div className="flex flex-col">
            <div className="flex items-center gap-3">
              <span className="text-2xl font-bold tracking-tight text-[#0A3871] whitespace-nowrap">
                Spec<span className="text-[#0B57D0]">Wise</span>
              </span>
              <span className="inline-flex items-center text-xs font-medium text-slate-600 bg-slate-50 px-2 py-0.5 rounded border border-slate-200">
                SIH26108 Prototype
              </span>
            </div>
            <span className="text-sm text-slate-500 font-medium hidden md:inline whitespace-nowrap">
              Right Standards. Safer Procurement.
            </span>
          </div>
        </div>

        {/* Center & Right Navigation */}
        <div className="flex items-center gap-6">
          <nav className="hidden lg:flex items-center gap-8 text-sm font-medium text-slate-700 whitespace-nowrap">
            <Link
              href="/"
              className={`transition-colors ${
                pathname === "/"
                  ? "text-[#0B57D0] font-semibold"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Home
            </Link>
            <Link
              href="/how-it-works"
              className={`transition-colors ${
                pathname === "/how-it-works"
                  ? "text-[#0B57D0] font-semibold"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              How it works
            </Link>
            <Link
              href="/resources"
              className={`transition-colors ${
                pathname === "/resources"
                  ? "text-[#0B57D0] font-semibold"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Resources
            </Link>
            <button
              onClick={onAboutClick}
              className="text-slate-600 hover:text-slate-900 transition-colors cursor-pointer"
            >
              About
            </button>
          </nav>

          <div className="flex items-center gap-3 pl-2 sm:border-l sm:border-slate-200">
            {/* Language Selector */}
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowLangMenu(!showLangMenu)}
                className="flex items-center gap-1.5 text-xs font-medium text-slate-700 bg-slate-50 hover:bg-slate-100 px-2.5 py-1.5 rounded-md border border-slate-200 transition-colors"
              >
                <span>{lang}</span>
                <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
              </button>
              {showLangMenu && (
                <div className="absolute right-0 mt-1 w-32 bg-white rounded-md shadow-lg border border-slate-200 py-1 text-xs z-50">
                  {["English", "हिन्दी", "தமிழ்", "తెలుగు", "मराठी"].map((l) => (
                    <button
                      key={l}
                      onClick={() => {
                        setLang(l);
                        setShowLangMenu(false);
                      }}
                      className="w-full text-left px-3 py-1.5 hover:bg-slate-50 text-slate-700"
                    >
                      {l}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* User Icon */}
            <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-600 border border-slate-200">
              <User className="w-4 h-4" />
            </div>

            {/* Atmanirbhar Bharat Logo */}
            <div className="hidden xl:flex items-center gap-2 pl-3 border-l border-slate-200">
              <div className="flex flex-col text-right">
                <span className="text-[13px] font-bold text-slate-800 leading-tight tracking-wide">
                  आत्मनिर्भर भारत
                </span>
                <span className="text-[9px] text-slate-500 leading-none">
                  Safer, Stronger, Self-reliant India
                </span>
              </div>
              <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-orange-500 via-white to-green-600 p-[1.5px] shadow-sm">
                <div className="w-full h-full rounded-full bg-white flex items-center justify-center">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#0A3871]" />
                </div>
              </div>
            </div>
          </div>
        </div>
        </div>

      {/* Subtle prototype disclosure below header */}
      <div className="bg-white border-t border-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-1 text-center text-xs text-slate-500">
          SIH26108 Prototype · Not an official BIS portal
        </div>
      </div>
    </header>
  );
}
