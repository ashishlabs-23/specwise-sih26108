"use client";

import React from "react";
import { X, Download, Printer, FileText } from "lucide-react";
import { AnalysisResponse } from "@/types/api";
import { useLanguage } from "@/context/LanguageContext";

interface ReportViewModalProps {
  isOpen: boolean;
  onClose: () => void;
  response: AnalysisResponse;
}

export function ReportViewModal({ isOpen, onClose, response }: ReportViewModalProps) {
  const { t } = useLanguage();
  if (!isOpen) return null;

  const htmlContent = response.report_html || `<p>${t.noReport}</p>`;

  const handleDownloadHtml = () => {
    const blob = new Blob([htmlContent], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `specwise-audit-${response.analysis_id || "report"}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    const printWindow = window.open("", "_blank");
    if (printWindow) {
      printWindow.document.write(htmlContent);
      printWindow.document.close();
      printWindow.focus();
      printWindow.print();
    }
  };

  return (
    <div className="fixed inset-0 z-50 pointer-events-none bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-2 sm:p-4">
      <div className="bg-white rounded-2xl max-w-4xl w-full h-[88vh] sm:h-[85vh] flex flex-col shadow-2xl border border-slate-200 relative z-10 pointer-events-auto animate-in fade-in zoom-in-95 duration-150 overflow-hidden">
        
        {/* Header */}
        <div className="p-3 sm:p-5 border-b border-slate-200 flex flex-wrap items-center justify-between bg-slate-50 rounded-t-2xl gap-2">
          <div className="flex items-center gap-2.5 sm:gap-3 min-w-0">
            <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-xl bg-blue-100 text-[#0A3871] flex items-center justify-center font-bold flex-shrink-0">
              <FileText className="w-4 h-4 sm:w-5 sm:h-5" />
            </div>
            <div className="min-w-0">
              <h3 className="text-xs sm:text-base font-bold text-slate-900 truncate">
                {t.reportTitle}
              </h3>
              <p className="text-[10px] sm:text-xs text-slate-500 font-mono truncate">
                ID: {response.analysis_id || "N/A"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5 sm:gap-2 ml-auto">
            <button
              onClick={handlePrint}
              className="inline-flex items-center gap-1 px-2.5 sm:px-3 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-[11px] sm:text-xs font-semibold text-slate-700 shadow-xs cursor-pointer"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>{t.print}</span>
            </button>

            <button
              onClick={handleDownloadHtml}
              className="inline-flex items-center gap-1 px-2.5 sm:px-3 py-1.5 rounded-lg bg-[#0B57D0] hover:bg-[#0A47A8] text-white text-[11px] sm:text-xs font-semibold shadow-xs cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>{t.download}</span>
            </button>

            <button
              onClick={onClose}
              className="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-200 ml-1 cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content iframe / raw renderer */}
        <div className="flex-1 p-4 overflow-hidden bg-slate-100">
          <iframe
            srcDoc={htmlContent}
            title="Audit Report"
            className="w-full h-full rounded-xl bg-white border border-slate-300 shadow-inner"
          />
        </div>
      </div>
    </div>
  );
}
