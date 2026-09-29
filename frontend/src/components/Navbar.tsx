"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { User, ChevronDown, ExternalLink } from "lucide-react";
import { useLanguage, Language } from "@/context/LanguageContext";

export function Navbar({ onAboutClick }: { onAboutClick?: () => void }) {
  const pathname = usePathname();
  const { language, setLanguage, t } = useLanguage();
  const [showLangMenu, setShowLangMenu] = useState(false);
  const langMenuRef = useRef<HTMLDivElement>(null);

  const langLabels: Record<Language, string> = {
    en: "English",
    hi: "हिन्दी",
    kn: "ಕನ್ನಡ",
    ta: "தமிழ்",
    te: "తెలుగు",
  };

  const languageList: Array<{ code: Language; label: string }> = [
    { code: "en", label: "English" },
    { code: "hi", label: "हिन्दी" },
    { code: "kn", label: "ಕನ್ನಡ" },
    { code: "ta", label: "தமிழ்" },
    { code: "te", label: "తెలుగు" },
  ];

  // Close dropdown on click outside or Escape key
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (langMenuRef.current && !langMenuRef.current.contains(event.target as Node)) {
        setShowLangMenu(false);
      }
    }
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setShowLangMenu(false);
      }
    }

    if (showLangMenu) {
      document.addEventListener("mousedown", handleClickOutside);
      document.addEventListener("keydown", handleKeyDown);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [showLangMenu]);

  return (
    <header className="w-full bg-white border-b border-slate-200 sticky top-0 z-40 overflow-hidden">
      {/* Top Government Disclaimer Banner */}
      <div className="bg-slate-900 text-slate-200 text-xs px-3 sm:px-4 py-1.5 flex items-center justify-between">
        <div className="flex items-center gap-2 max-w-7xl mx-auto w-full min-w-0">
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex-shrink-0">
            SIH26108
          </span>
          <span className="text-slate-300 truncate text-[11px] sm:text-xs flex-1">
            {t.siteTitle} — {t.tagline}
          </span>
          <a
            href="https://www.bis.gov.in"
            target="_blank"
            rel="noreferrer"
            className="ml-auto flex items-center gap-1 text-slate-400 hover:text-white transition-colors flex-shrink-0 text-[11px]"
          >
            <span className="hidden sm:inline">{t.officialPortal}</span>
            <span className="sm:hidden">BIS</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>

      {/* Main Header */}
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 h-16 sm:h-20 flex items-center justify-between gap-2">
        {/* Left: BIS Emblem + SpecWise Brand */}
        <div className="flex items-center gap-2.5 sm:gap-4 lg:gap-6 min-w-0">
          {/* BIS Emblem Logo (icon only) */}
          <div className="flex items-center gap-3 flex-shrink-0">
            <div className="w-9 h-9 sm:w-11 sm:h-11 rounded-lg bg-[#0A3871] text-white flex items-center justify-center p-1 shadow-sm flex-shrink-0" aria-hidden>
              <div className="w-5 h-5 sm:w-6 sm:h-6 border-2 border-white rounded-sm flex items-center justify-center relative">
                <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 bg-amber-400 rotate-45" />
              </div>
            </div>
          </div>

          {/* SpecWise Brand */}
          <div className="flex flex-col min-w-0">
            <Link href="/" className="group flex items-center gap-1.5 focus:outline-none">
              <span className="text-xl sm:text-2xl font-black tracking-tight text-[#0A3871] group-hover:text-[#0B57D0] transition-colors truncate">
                {t.siteTitle}
              </span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue-100 text-[#0B57D0] tracking-wider uppercase flex-shrink-0 hidden xs:inline-block">
                BIS
              </span>
            </Link>
            <span className="text-[10px] sm:text-xs text-slate-500 font-medium tracking-tight truncate hidden md:inline-block">
              {t.tagline}
            </span>
          </div>
        </div>

        {/* Right Side: Navigation & Actions */}
        <div className="flex items-center gap-2 sm:gap-6 flex-shrink-0">
          <nav className="hidden md:flex items-center gap-5 text-sm font-medium">
            <Link
              href="/"
              className={`transition-colors ${
                pathname === "/"
                  ? "text-[#0B57D0] font-semibold"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              {t.home}
            </Link>
            <Link
              href="/how-it-works"
              className={`transition-colors ${
                pathname === "/how-it-works"
                  ? "text-[#0B57D0] font-semibold"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              {t.howItWorks}
            </Link>
            <Link
              href="/resources"
              className={`transition-colors ${
                pathname === "/resources"
                  ? "text-[#0B57D0] font-semibold"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              {t.resources}
            </Link>
            <button
              onClick={onAboutClick}
              className="text-slate-600 hover:text-slate-900 transition-colors cursor-pointer"
            >
              {t.about}
            </button>
          </nav>

          <div className="flex items-center gap-3 pl-2 sm:border-l sm:border-slate-200">
            {/* Language Selector */}
            <div className="relative" ref={langMenuRef}>
              <button
                type="button"
                id="language-menu-button"
                aria-haspopup="listbox"
                aria-expanded={showLangMenu}
                aria-label={t.language || "Select Language"}
                onClick={() => setShowLangMenu(!showLangMenu)}
                className="flex items-center gap-1.5 text-xs font-medium text-slate-700 bg-slate-50 hover:bg-slate-100 px-2.5 py-1.5 rounded-md border border-slate-200 transition-colors cursor-pointer"
              >
                <span>{langLabels[language] || "English"}</span>
                <ChevronDown className={`w-3.5 h-3.5 text-slate-500 transition-transform ${showLangMenu ? "rotate-180" : ""}`} />
              </button>
              {showLangMenu && (
                <div
                  role="listbox"
                  aria-labelledby="language-menu-button"
                  className="absolute right-0 mt-1 w-32 bg-white rounded-md shadow-lg border border-slate-200 py-1 text-xs z-50 animate-in fade-in zoom-in-95 duration-100"
                >
                  {languageList.map((item) => {
                    const isSelected = language === item.code;
                    return (
                      <button
                        key={item.code}
                        role="option"
                        aria-selected={isSelected}
                        onClick={() => {
                          setLanguage(item.code);
                          setShowLangMenu(false);
                        }}
                        className={`w-full text-left px-3 py-1.5 hover:bg-slate-50 transition-colors cursor-pointer ${
                          isSelected ? "font-bold text-[#0B57D0] bg-blue-50/50" : "text-slate-700"
                        }`}
                      >
                        {item.label}
                      </button>
                    );
                  })}
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
          SIH26108 {t.prototypeNotice}
        </div>
      </div>
    </header>
  );
}
