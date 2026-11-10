"use client";

import React, { useState } from "react";
import {
  AlertOctagon,
  AlertTriangle,
  Link2,
  CheckCircle2,
  FileCode,
  Flame,
  ArrowRight,
  Sparkles
} from "lucide-react";
import { HandoverWorkspace } from "@/types";

interface RiskRadarViewProps {
  workspace: HandoverWorkspace;
  onSelectCitation: (citationId: string) => void;
  onOpenLeaverModal: () => void;
}

export function RiskRadarView({
  workspace,
  onSelectCitation,
  onOpenLeaverModal
}: RiskRadarViewProps) {
  const [activeTab, setActiveTab] = useState<"ALL" | "ORPHANS" | "CONTRADICTIONS">("ALL");

  const orphanFiles = workspace.orphan_risk_files || [];
  const contradictions = workspace.contradictions || [];

  const filteredOrphans = orphanFiles;
  const filteredContradictions = contradictions;

  return (
    <div className="space-y-6">
      {/* Top Banner & Control Bar */}
      <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-600 flex items-center justify-center font-bold">
                <AlertOctagon className="w-5 h-5" />
              </span>
              <h2 className="text-base font-bold text-slate-900 tracking-tight">
                Continuity Risk Radar & Code Ownership
              </h2>
            </div>
            <p className="text-xs text-slate-500 max-w-2xl leading-relaxed">
              Detects single-developer architectural silos using the academic ICSE Degree of Authorship (DOA) metric and identifies pairwise architectural contradictions using local HuggingFace NLI cross-encoders.
            </p>
          </div>

          {/* Quick Filters */}
          <div className="flex items-center gap-2 shrink-0">
            <div className="flex items-center bg-slate-100 p-1 rounded-lg text-xs font-semibold">
              <button
                onClick={() => setActiveTab("ALL")}
                className={`px-3 py-1 rounded transition ${
                  activeTab === "ALL" ? "bg-white text-slate-900 shadow-xs" : "text-slate-500 hover:text-slate-900"
                }`}
              >
                All ({orphanFiles.length + contradictions.length})
              </button>
              <button
                onClick={() => setActiveTab("ORPHANS")}
                className={`px-3 py-1 rounded transition ${
                  activeTab === "ORPHANS" ? "bg-white text-rose-700 shadow-xs" : "text-slate-500 hover:text-slate-900"
                }`}
              >
                Orphan Files ({orphanFiles.length})
              </button>
              <button
                onClick={() => setActiveTab("CONTRADICTIONS")}
                className={`px-3 py-1 rounded transition ${
                  activeTab === "CONTRADICTIONS" ? "bg-white text-amber-700 shadow-xs" : "text-slate-500 hover:text-slate-900"
                }`}
              >
                Contradictions ({contradictions.length})
              </button>
            </div>
          </div>
        </div>

        {/* Methodology Explainer Pill */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs bg-slate-50 p-3.5 rounded-xl border border-slate-100">
          <div className="flex items-start gap-2.5">
            <Flame className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-900 block font-semibold">ICSE Degree of Authorship (DOA) Formula</strong>
              <span className="text-[11px] text-slate-600 font-mono">
                DOA = 3.293 + 1.098·FA + 0.164·DL - 0.321·ln(1 + AC)
              </span>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Filters noise from formatting/whitespace commits to compute pure semantic author ownership.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-2.5">
            <Sparkles className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-900 block font-semibold">HuggingFace NLI Radar Engine</strong>
              <span className="text-[11px] text-slate-600 font-mono">
                all-MiniLM-L6-v2 Cross-Encoder &bull; Δt Temporal Decay
              </span>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Surfaces conflicting architecture choices (e.g. Redis cache vs PostgreSQL locks) under 50ms locally.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* SECTION 1: Bus Factor = 1 Orphan Risk Files */}
      {(activeTab === "ALL" || activeTab === "ORPHANS") && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-600" />
              <h3 className="text-sm font-bold text-slate-900 tracking-tight">
                Single-Author Orphan Files (Bus Factor = 1)
              </h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-100 text-rose-800">
                {filteredOrphans.length} High-Risk Targets
              </span>
            </div>
            <button
              onClick={onOpenLeaverModal}
              className="text-xs font-semibold text-rose-700 hover:text-rose-800 hover:underline flex items-center gap-1"
            >
              Verify All in 60-Sec Review &rarr;
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredOrphans.map((file, idx) => (
              <div
                key={file.file_path || idx}
                className="bg-white rounded-xl border border-rose-200/90 p-4 shadow-xs hover:border-rose-400 hover:shadow-sm transition flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2 min-w-0">
                      <FileCode className="w-4 h-4 text-rose-600 shrink-0" />
                      <span className="font-mono text-xs font-bold text-slate-900 truncate">
                        {file.file_path}
                      </span>
                    </div>
                    <span
                      className={`text-[9px] uppercase px-2 py-0.5 rounded font-black tracking-wider shrink-0 ${
                        file.bus_factor_risk === "CRITICAL"
                          ? "bg-rose-100 text-rose-800 border border-rose-200"
                          : "bg-amber-100 text-amber-800 border border-amber-200"
                      }`}
                    >
                      {file.bus_factor_risk} RISK
                    </span>
                  </div>

                  {/* Blame Progress bar */}
                  <div className="my-2.5 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="text-slate-600 font-medium">Primary Author:</span>
                      <strong className="text-slate-900 font-semibold">{file.primary_author}</strong>
                    </div>
                    <div className="flex items-center justify-between text-xs mb-1.5">
                      <span className="text-slate-500 text-[11px]">Ownership Blame:</span>
                      <span className="font-extrabold text-rose-700 tabular-nums text-xs">
                        {file.blame_percentage}% ({file.single_author_lines}/{file.total_lines} lines)
                      </span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-rose-600 h-2 rounded-full"
                        style={{ width: `${file.blame_percentage}%` }}
                      />
                    </div>
                  </div>

                  <p className="text-xs text-slate-600 leading-relaxed bg-rose-50/40 p-2.5 rounded-lg border border-rose-100/70 mb-3">
                    {file.risk_rationale}
                  </p>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-[11px]">
                  <span className="text-slate-400">
                    Last touched: {file.last_modified_date || "Recent sprint"}
                  </span>
                  <button
                    onClick={onOpenLeaverModal}
                    className="text-xs font-semibold text-rose-700 hover:text-rose-900 flex items-center gap-1 hover:underline"
                  >
                    Resolve in 60s Review &rarr;
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SECTION 2: HuggingFace NLI Contradiction Radar */}
      {(activeTab === "ALL" || activeTab === "CONTRADICTIONS") && (
        <div className="space-y-4 pt-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-600" />
              <h3 className="text-sm font-bold text-slate-900 tracking-tight">
                Architectural Contradiction Radar
              </h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">
                {filteredContradictions.length} Semantic Conflicts
              </span>
            </div>
            <span className="text-xs text-slate-500">
              Evaluated across Git commit diffs & Slack threads
            </span>
          </div>

          <div className="space-y-4">
            {filteredContradictions.map((contra) => (
              <div
                key={contra.id}
                className="bg-white rounded-2xl border border-amber-300 p-5 shadow-xs"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 mb-3 border-b border-amber-100">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-amber-600 block mb-0.5">
                      Conflict Topic
                    </span>
                    <h4 className="text-sm font-bold text-slate-900">{contra.topic}</h4>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-xs font-bold px-2.5 py-1 rounded-md bg-amber-50 text-amber-800 border border-amber-200 tabular-nums">
                      P(conflict): {(contra.contradiction_score * 100).toFixed(1)}%
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2.5 py-1 rounded-md uppercase tracking-wider ${
                        contra.status === "RESOLVED_BY_LEAVER"
                          ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                          : "bg-amber-100 text-amber-800 border border-amber-300 animate-pulse"
                      }`}
                    >
                      {contra.status === "RESOLVED_BY_LEAVER"
                        ? "Resolved by Leaver"
                        : "Unresolved Contradiction"}
                    </span>
                  </div>
                </div>

                <p className="text-xs text-slate-600 mb-3.5 leading-relaxed">
                  {contra.explanation}
                </p>

                {/* Side-by-Side Comparison Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3.5">
                  {/* Source A */}
                  <div
                    onClick={() => onSelectCitation(contra.source_a.id)}
                    className="p-3.5 rounded-xl border border-purple-200 bg-purple-50/60 hover:bg-purple-50 cursor-pointer transition flex flex-col justify-between group"
                  >
                    <div>
                      <div className="flex items-center justify-between text-[11px] text-purple-700 font-semibold mb-1.5">
                        <span className="flex items-center gap-1.5 font-bold">
                          Source A: {contra.source_a.source_type.toUpperCase()}
                        </span>
                        <span className="font-mono text-[10px] text-purple-600">
                          {contra.source_a.timestamp?.slice(0, 10)}
                        </span>
                      </div>
                      <p className="text-xs font-semibold text-slate-900 leading-snug">
                        &ldquo;{contra.claim_a}&rdquo;
                      </p>
                      <p className="text-[11px] text-slate-500 mt-1">
                        Author: <strong className="text-slate-700">{contra.source_a.author}</strong>
                      </p>
                    </div>
                    <span className="mt-2.5 inline-flex items-center gap-1 text-[11px] text-purple-700 font-bold group-hover:underline">
                      <Link2 className="w-3 h-3" /> Inspect Discussion Trace &rarr;
                    </span>
                  </div>

                  {/* Source B */}
                  <div
                    onClick={() => onSelectCitation(contra.source_b.id)}
                    className="p-3.5 rounded-xl border border-blue-200 bg-blue-50/60 hover:bg-blue-50 cursor-pointer transition flex flex-col justify-between group"
                  >
                    <div>
                      <div className="flex items-center justify-between text-[11px] text-blue-700 font-semibold mb-1.5">
                        <span className="flex items-center gap-1.5 font-bold">
                          Source B: {contra.source_b.source_type.toUpperCase()}
                        </span>
                        <span className="font-mono text-[10px] text-blue-600">
                          {contra.source_b.timestamp?.slice(0, 10)}
                        </span>
                      </div>
                      <p className="text-xs font-semibold text-slate-900 leading-snug">
                        &ldquo;{contra.claim_b}&rdquo;
                      </p>
                      <p className="text-[11px] text-slate-500 mt-1">
                        Author: <strong className="text-slate-700">{contra.source_b.author}</strong>
                      </p>
                    </div>
                    <span className="mt-2.5 inline-flex items-center gap-1 text-[11px] text-blue-700 font-bold group-hover:underline">
                      <Link2 className="w-3 h-3" /> Inspect Code Commit Diff &rarr;
                    </span>
                  </div>
                </div>

                {/* Footer Action */}
                <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs">
                  <span className="text-[11px] text-slate-500">
                    Confidence: <strong>Multi-source cross-encoder verified</strong>
                  </span>
                  {contra.status !== "RESOLVED_BY_LEAVER" ? (
                    <button
                      onClick={onOpenLeaverModal}
                      className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs transition flex items-center gap-1.5 shadow-xs"
                    >
                      <span>Resolve in 60-Sec Review</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  ) : (
                    <span className="flex items-center gap-1 text-emerald-700 font-bold text-xs">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      Resolved by Leaver Architect
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

