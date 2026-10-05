"use client";

import React, { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { Upload, X, FileText, AlertCircle, CheckCircle2, Shield, Loader2 } from "lucide-react";
import { uploadPdf } from "@/lib/api";
import type { AnalysisResponse } from "@/types/api";
import { useLanguage } from "@/context/LanguageContext";

interface PdfUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAnalysisStart?: () => void;
  onTextExtracted?: (text: string) => void;
  onAnalysisComplete?: (analysis: AnalysisResponse) => void;
}

export function PdfUploadModal({ isOpen, onClose, onAnalysisStart, onAnalysisComplete }: PdfUploadModalProps) {
  const { t } = useLanguage();
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [currentProgressStep, setCurrentProgressStep] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const dialogRef = useRef<HTMLDialogElement>(null);
  const timersRef = useRef<NodeJS.Timeout[]>([]);

  const clearProgressTimers = () => {
    timersRef.current.forEach((t) => clearTimeout(t));
    timersRef.current = [];
  };

  useEffect(() => {
    if (!isOpen) {
      setError(null);
      setSelectedFile(null);
      setDragOver(false);
      setLoading(false);
      setCurrentProgressStep(0);
      clearProgressTimers();
    }
  }, [isOpen]);

  useEffect(() => {
    return () => {
      clearProgressTimers();
    };
  }, []);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (isOpen && dialog && !dialog.open) dialog.showModal();
    if (!isOpen && dialog?.open) dialog.close();
    return () => {
      if (dialog?.open) dialog.close();
    };
  }, [isOpen]);

  // Progressive status message sequence based on elapsed time
  const getProgressMessage = (step: number) => {
    switch (step) {
      case 0:
        return t.ocrUploadingDoc;
      case 1:
        return t.ocrScannedDetected;
      case 2:
        return t.ocrRecoveringText;
      case 3:
        return t.ocrValidating;
      case 4:
        return t.ocrAnalyzing;
      default:
        return t.ocrAnalyzing;
    }
  };

  const mapBackendError = (rawMsg: string): string => {
    const msg = (rawMsg || "").toLowerCase();
    if (msg.includes("contains no readable text") || msg.includes("blank")) {
      return t.ocrNoReadableText;
    }
    if (msg.includes("sufficient quality") || msg.includes("confidence:") || msg.includes("low confidence")) {
      return t.ocrQualityTooLow;
    }
    if (msg.includes("unavailable on this server") || msg.includes("ocr integration is required")) {
      return t.ocrRuntimeUnavailable;
    }
    if (msg.includes("unsupported file type")) {
      return t.pdfUnsupportedType;
    }
    if (msg.includes("size limit") || msg.includes("25 mb")) {
      return t.pdfSizeLimit;
    }
    if (msg.includes("could not read this pdf") || msg.includes("unprotected pdf") || msg.includes("corrupt")) {
      return t.pdfCorrupt;
    }
    return rawMsg || t.pdfGeneralError;
  };

  const handleProcessDocument = async () => {
    if (!selectedFile || loading) return;
    setError(null);
    setLoading(true);
    setCurrentProgressStep(0);
    clearProgressTimers();

    // Start progressive status timer progression
    timersRef.current.push(setTimeout(() => setCurrentProgressStep(1), 1500));
    timersRef.current.push(setTimeout(() => setCurrentProgressStep(2), 4000));
    timersRef.current.push(setTimeout(() => setCurrentProgressStep(3), 6500));
    timersRef.current.push(setTimeout(() => setCurrentProgressStep(4), 9000));

    onAnalysisStart?.();
    try {
      const analysis = await uploadPdf(selectedFile);
      clearProgressTimers();
      if (onAnalysisComplete) onAnalysisComplete(analysis);
      onClose();
    } catch (err: any) {
      clearProgressTimers();
      setError(mapBackendError(err?.message || ""));
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return createPortal(
    <dialog
      ref={dialogRef}
      role="dialog"
      aria-modal="true"
      aria-labelledby="pdf-modal-title"
      className="fixed inset-0 z-[2147483647] m-0 flex h-screen w-screen max-h-none max-w-none items-center justify-center border-0 bg-slate-900/60 p-2 sm:p-4 backdrop-blur-xs"
      style={{ zIndex: 2147483647 }}
      onCancel={(event) => {
        event.preventDefault();
        if (!loading) onClose();
      }}
    >
      <div
        className="bg-white rounded-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto p-4 sm:p-6 shadow-2xl border border-slate-200 relative z-[2147483647] pointer-events-auto animate-in fade-in zoom-in-95 duration-150"
        style={{ zIndex: 2147483647, pointerEvents: "auto", position: "relative" }}
      >
        <button
          onClick={onClose}
          disabled={loading}
          aria-label={t.close}
          className="absolute top-3.5 right-3.5 text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 cursor-pointer z-10 disabled:opacity-50"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 pb-4 border-b border-slate-100 pr-8 min-w-0">
          <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-blue-50 text-[#0B57D0] flex items-center justify-center border border-blue-200 flex-shrink-0">
            <Upload className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <h3 id="pdf-modal-title" className="text-sm sm:text-base font-bold text-slate-900 truncate">
              {t.uploadTender}
            </h3>
            <p className="text-[11px] sm:text-xs text-slate-500 font-medium truncate">
              {t.pdfSupport}
            </p>
          </div>
        </div>

        {/* Drag & Drop Area */}
        <div
          onDragOver={(e) => {
            e.preventDefault();
            if (!loading) setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            if (!loading && e.dataTransfer.files?.[0]) {
              setSelectedFile(e.dataTransfer.files[0]);
              setError(null);
            }
          }}
          className={`mt-5 border-2 border-dashed rounded-xl p-6 sm:p-8 text-center transition-all ${
            dragOver
              ? "border-blue-500 bg-blue-50/50"
              : "border-slate-300 bg-slate-50/60 hover:bg-slate-50"
          } ${loading ? "opacity-75 pointer-events-none" : ""}`}
        >
          <div className="w-12 h-12 rounded-full bg-blue-100 text-[#0B57D0] flex items-center justify-center mx-auto mb-3">
            <FileText className="w-6 h-6" />
          </div>

          <h4 className="text-xs sm:text-sm font-semibold text-slate-800 break-words max-w-full">
            {selectedFile ? selectedFile.name : t.dragDrop}
          </h4>
          <p className="text-xs text-slate-500 mt-1">
            {t.pdfSupport}
          </p>

          {!loading && (
            <label className="mt-4 inline-block">
              <input
                type="file"
                accept=".pdf,application/pdf"
                className="hidden"
                disabled={loading}
                onChange={(e) => {
                  if (e.target.files?.[0]) {
                    setSelectedFile(e.target.files[0]);
                    setError(null);
                  }
                }}
              />
              <span className="px-4 py-2 rounded-lg bg-white border border-slate-300 hover:bg-slate-50 text-xs font-semibold text-slate-700 shadow-xs cursor-pointer inline-block">
                {t.browseFiles}
              </span>
            </label>
          )}
        </div>

        {/* Live Processing State with Progressive Status */}
        {loading && (
          <div
            role="status"
            aria-live="polite"
            className="mt-4 p-4 rounded-xl bg-blue-50 border border-blue-200 flex items-center gap-3 animate-in fade-in duration-200"
          >
            <Loader2 className="w-5 h-5 text-[#0B57D0] animate-spin flex-shrink-0" />
            <div className="min-w-0 flex-1">
              <div className="text-xs font-bold text-slate-900">
                {getProgressMessage(currentProgressStep)}
              </div>
              <div className="w-full bg-blue-200/70 h-1.5 rounded-full mt-2 overflow-hidden">
                <div
                  className="bg-[#0B57D0] h-full rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(20 + currentProgressStep * 20, 95)}%` }}
                />
              </div>
            </div>
          </div>
        )}

        {/* Error Banner */}
        {error && (
          <div
            role="alert"
            aria-live="assertive"
            className="mt-4 p-3.5 rounded-xl bg-red-50 border border-red-200 text-xs text-red-800 flex items-start gap-2.5 animate-in fade-in duration-150"
          >
            <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="min-w-0 flex-1">
              <span className="font-bold block text-red-900">{t.connectionError}</span>
              <p className="mt-0.5 leading-relaxed text-red-700 break-words">{error}</p>
            </div>
          </div>
        )}

        {/* Informative Workflow Notice */}
        <div className="mt-4 p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600 space-y-1.5">
          <div className="flex items-center gap-1.5 font-bold text-slate-800">
            <Shield className="w-3.5 h-3.5 text-[#0A3871]" />
            <span>{t.extractionWorkflow}</span>
          </div>
          <p className="leading-relaxed">
            {t.pdfModalWorkflowNotice}
          </p>
          <p className="text-[11px] text-slate-500">
            {t.pdfModalSecondaryNotice}
          </p>
        </div>

        {/* Modal Action Buttons */}
        <div className="mt-5 flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2 text-xs font-semibold rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 disabled:opacity-50 cursor-pointer"
          >
            {t.cancel}
          </button>
          <button
            type="button"
            disabled={!selectedFile || loading}
            onClick={handleProcessDocument}
            className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-lg bg-[#0B57D0] disabled:bg-slate-300 text-white hover:bg-[#0A47A8] disabled:cursor-not-allowed cursor-pointer transition-colors shadow-xs"
          >
            {loading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>{t.processing}</span>
              </>
            ) : (
              <span>{t.processDocument}</span>
            )}
          </button>
        </div>
      </div>
    </dialog>,
    document.body
  );
}
