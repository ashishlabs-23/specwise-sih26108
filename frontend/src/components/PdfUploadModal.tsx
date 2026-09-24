"use client";

import React, { useState } from "react";
import { Upload, X, FileText, AlertCircle, CheckCircle2, Shield } from "lucide-react";
import { uploadPdf } from "@/lib/api";
import type { AnalysisResponse } from "@/types/api";

interface PdfUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onTextExtracted?: (text: string) => void;
  onAnalysisComplete?: (analysis: AnalysisResponse) => void;
}

export function PdfUploadModal({ isOpen, onClose, onAnalysisComplete }: PdfUploadModalProps) {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-2 sm:p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full p-4 sm:p-6 shadow-2xl border border-slate-200 relative animate-in fade-in zoom-in-95 duration-150 overflow-hidden">
        <button
          onClick={onClose}
          className="absolute top-3.5 right-3.5 text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 cursor-pointer z-10"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 pb-4 border-b border-slate-100 pr-8 min-w-0">
          <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-blue-50 text-[#0B57D0] flex items-center justify-center border border-blue-200 flex-shrink-0">
            <Upload className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <h3 className="text-sm sm:text-base font-bold text-slate-900 truncate">
              Upload Tender Document (PDF)
            </h3>
            <p className="text-[11px] sm:text-xs text-slate-500 font-medium truncate">
              Extract product requirements from technical documents
            </p>
          </div>
        </div>

        {/* Drag & Drop Area */}
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            if (e.dataTransfer.files?.[0]) {
              setSelectedFile(e.dataTransfer.files[0]);
            }
          }}
          className={`mt-5 border-2 border-dashed rounded-xl p-8 text-center transition-all ${
            dragOver
              ? "border-blue-500 bg-blue-50/50"
              : "border-slate-300 bg-slate-50/60 hover:bg-slate-50"
          }`}
        >
          <div className="w-12 h-12 rounded-full bg-blue-100 text-[#0B57D0] flex items-center justify-center mx-auto mb-3">
            <FileText className="w-6 h-6" />
          </div>

          <h4 className="text-xs sm:text-sm font-semibold text-slate-800">
            {selectedFile ? selectedFile.name : "Drag & drop tender PDF here"}
          </h4>
          <p className="text-xs text-slate-500 mt-1">
            Supports technical specifications, RFP documents, schedule of requirements (.pdf up to 25MB)
          </p>

          <label className="mt-4 inline-block">
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={(e) => {
                if (e.target.files?.[0]) {
                  setSelectedFile(e.target.files[0]);
                }
              }}
            />
            <span className="px-4 py-2 rounded-lg bg-white border border-slate-300 hover:bg-slate-50 text-xs font-semibold text-slate-700 shadow-xs cursor-pointer inline-block">
              Browse Files
            </span>
          </label>
        </div>

        {/* Informative Security & Workflow Notice */}
        <div className="mt-4 p-3 rounded-xl bg-slate-100 border border-slate-200 text-xs text-slate-600 space-y-1.5">
          <div className="flex items-center gap-1.5 font-bold text-slate-800">
            <Shield className="w-3.5 h-3.5 text-[#0A3871]" />
            <span>Document Extraction Workflow</span>
          </div>
          <p>
            The backend engine extracts text layers using PyMuPDF and isolates technical requirements (power ratings, discharge capacity, application domain).
          </p>
          <p className="text-[11px] text-slate-500">
            The backend will extract the PDF text layers and run the same analysis pipeline used for text input.
          </p>
        </div>

        {/* Modal Buttons */}
        <div className="mt-5 flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 cursor-pointer"
          >
            Cancel
          </button>
          <div className="flex items-center gap-2">
            {error ? (
              <div className="text-sm text-red-600">{error}</div>
            ) : null}
            <button
              type="button"
              disabled={!selectedFile || loading}
              onClick={async () => {
                if (!selectedFile) return;
                setError(null);
                setLoading(true);
                try {
                  const analysis = await uploadPdf(selectedFile);
                  if (onAnalysisComplete) onAnalysisComplete(analysis);
                  onClose();
                } catch (err: any) {
                  setError(err?.message || "Upload failed.");
                } finally {
                  setLoading(false);
                }
              }}
              className="px-4 py-2 text-xs font-semibold rounded-lg bg-[#0B57D0] disabled:bg-slate-300 text-white hover:bg-[#0A47A8] cursor-pointer"
            >
              {loading ? "Processing…" : "Process Document"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
