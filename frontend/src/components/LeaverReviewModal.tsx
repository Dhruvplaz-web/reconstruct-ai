"use client";

import React, { useState } from "react";
import { X, CheckCircle2, ShieldCheck, Loader2 } from "lucide-react";
import { LeaverQuestion, LeaverReviewSubmission } from "@/types";

interface LeaverReviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  questions: LeaverQuestion[];
  onSubmitReview: (submission: LeaverReviewSubmission) => Promise<void>;
  isSubmitting: boolean;
}

export function LeaverReviewModal({
  isOpen,
  onClose,
  questions,
  onSubmitReview,
  isSubmitting
}: LeaverReviewModalProps) {
  // Pre-fill with recommended/suggested answers for frictionless 60-second experience
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>(() => {
    const initial: Record<string, string> = {};
    questions.forEach((q) => {
      initial[q.id] = q.suggested_answer || q.options[0];
    });
    return initial;
  });

  const [notes, setNotes] = useState<string>("All production edge-cases and rollback decisions verified.");

  if (!isOpen) return null;

  const handleSelectOption = (questionId: string, option: string) => {
    setSelectedAnswers((prev) => ({ ...prev, [questionId]: option }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmitReview({
      responses: selectedAnswers,
      additional_notes: notes,
      approved_by: "Alice Vance (Lead Architect)"
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 animate-in fade-in duration-150">
      <div className="w-full max-w-2xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="bg-slate-900 text-white p-4 flex items-center justify-between border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white tracking-tight">60-Second Leaver Review Gate</h2>
              <p className="text-[11px] text-slate-400">
                Alice Vance (Lead Architect) &bull; Confirm 3 detected knowledge gaps
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-5 overflow-y-auto space-y-4 flex-1 text-xs">
          <div className="p-3 rounded-lg bg-blue-50 border border-blue-200 text-blue-900">
            <p className="font-semibold text-xs mb-0.5">Zero-Friction Handover Philosophy:</p>
            <p className="text-[11px] leading-relaxed text-blue-800">
              Rather than writing a manual 20-page wiki, our Git Blame Miner and DeBERTa-v3 Contradiction Radar identified the 3 single-author risk areas below. Simply confirm or adjust your answers to finalize the handover.
            </p>
          </div>

          {questions.map((q, idx) => (
            <div key={q.id} className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/60 space-y-2">
              <div className="flex items-start justify-between gap-2">
                <span className="font-bold text-slate-900 leading-snug">
                  {idx + 1}. {q.question}
                </span>
                <span className="font-mono text-[10px] text-slate-500 bg-white px-2 py-0.5 rounded border border-slate-200 shrink-0">
                  {q.file_path}
                </span>
              </div>

              <p className="text-[11px] text-slate-500 italic">Context: {q.context}</p>

              <div className="space-y-1.5 pt-1">
                {q.options.map((option, optIdx) => {
                  const isSelected = selectedAnswers[q.id] === option;
                  return (
                    <div
                      key={optIdx}
                      onClick={() => handleSelectOption(q.id, option)}
                      className={`p-2.5 rounded-lg border text-xs cursor-pointer transition flex items-start gap-2 ${
                        isSelected
                          ? "bg-blue-50 border-blue-500 text-blue-950 font-medium"
                          : "bg-white border-slate-200 text-slate-700 hover:bg-slate-50"
                      }`}
                    >
                      <input
                        type="radio"
                        name={q.id}
                        checked={isSelected}
                        onChange={() => handleSelectOption(q.id, option)}
                        className="mt-0.5 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="flex-1 leading-snug">{option}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}

          {/* Notes */}
          <div className="space-y-1">
            <label className="font-semibold text-slate-700 text-[11px]">Final Handover Remarks:</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={2}
              className="w-full p-2 rounded-lg border border-slate-200 text-xs bg-slate-50 focus:bg-white text-slate-800"
            />
          </div>

          {/* Submit Action */}
          <div className="pt-2 flex items-center justify-between border-t border-slate-200">
            <span className="text-[11px] text-slate-500">
              Signs with: <strong className="text-slate-800">Alice Vance (Lead Architect)</strong>
            </span>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onClose}
                className="px-3 py-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-100 text-xs font-medium transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition shadow-sm"
              >
                {isSubmitting ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <CheckCircle2 className="w-3.5 h-3.5" />
                )}
                <span>Sign & Approve Handover</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
