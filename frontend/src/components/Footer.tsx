"use client";

import React from "react";

export function Footer() {
  return (
    <footer className="w-full bg-white border-t border-slate-200 py-6 mt-16 text-xs text-slate-500">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        
        {/* Copyright & Disclaimer */}
        <div className="flex flex-col sm:flex-row items-center gap-1 sm:gap-2 text-center sm:text-left">
          <span>© 2025 Bureau of Indian Standards</span>
          <span className="hidden sm:inline text-slate-300">|</span>
          <span className="text-slate-600 font-medium">
            SpecWise (Prototype for SIH26108 — Not an official BIS portal)
          </span>
        </div>

        {/* Footer Links */}
        <div className="flex items-center gap-4 text-slate-500">
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              alert("SpecWise Prototype: Privacy Policy strictly protects tender specification data locally without transmitting to external clouds.");
            }}
            className="hover:text-slate-800 transition-colors"
          >
            Privacy
          </a>
          <span className="text-slate-300">|</span>
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              alert("SpecWise Prototype: Terms of Use — Decision support system for procurement guidance.");
            }}
            className="hover:text-slate-800 transition-colors"
          >
            Terms
          </a>
          <span className="text-slate-300">|</span>
          <a
            href="https://www.bis.gov.in"
            target="_blank"
            rel="noreferrer"
            className="hover:text-slate-800 transition-colors"
          >
            Contact BIS
          </a>
        </div>

      </div>
    </footer>
  );
}
