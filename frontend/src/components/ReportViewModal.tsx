"use client";

import React from "react";
import { X, Download, Printer, FileText } from "lucide-react";
import { AnalysisResponse } from "@/types/api";

interface ReportViewModalProps {
  isOpen: boolean;
  onClose: () => void;
  response: AnalysisResponse;
}

export function ReportViewModal({ isOpen, onClose, response }: ReportViewModalProps) {
  if (!isOpen) return null;

  const htmlContent = response.report_html || "<p>No report generated.</p>";

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
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-4xl w-full h-[85vh] flex flex-col shadow-2xl border border-slate-200 relative animate-in fade-in zoom-in-95 duration-150">
        
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-slate-200 flex items-center justify-between bg-slate-50 rounded-t-2xl">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-100 text-[#0A3871] flex items-center justify-center font-bold">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm sm:text-base font-bold text-slate-900">
                Official SpecWise Audit Report
              </h3>
              <p className="text-xs text-slate-500 font-mono">
                Analysis ID: {response.analysis_id || "N/A"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handlePrint}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-xs font-semibold text-slate-700 shadow-xs cursor-pointer"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print</span>
            </button>

            <button
              onClick={handleDownloadHtml}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0B57D0] hover:bg-[#0A47A8] text-white text-xs font-semibold shadow-xs cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download HTML</span>
            </button>

            <button
              onClick={onClose}
              className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-200 ml-1 cursor-pointer"
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
