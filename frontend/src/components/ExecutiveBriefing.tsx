"use client";

import React from "react";
import { GitBranch, AlertOctagon, Link2, BookOpen } from "lucide-react";
import { HandoverWorkspace } from "@/types";

interface ExecutiveBriefingProps {
  workspace: HandoverWorkspace;
  onSelectCitation: (citationId: string) => void;
  onOpenLeaverModal: () => void;
}

export function ExecutiveBriefing({
  workspace,
  onSelectCitation,
  onOpenLeaverModal
}: ExecutiveBriefingProps) {
  const primaryOrphan = workspace.orphan_risk_files.find((f) => f.bus_factor_risk === "CRITICAL") || workspace.orphan_risk_files[0];
  const primaryContra = workspace.contradictions[0];

  return (
    <div className="space-y-4">
      {/* Executive Summary Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
        <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-blue-600" />
            <h1 className="text-sm font-bold text-slate-900 tracking-tight">Executive Continuity Briefing</h1>
          </div>
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
            JSPM RSCOE &bull; We Code Coders
          </span>
        </div>
        <p className="text-xs text-slate-600 leading-relaxed text-justify">
          {workspace.executive_summary}
        </p>
      </div>

      {/* Bus Factor = 1 Warning Banner */}
      {primaryOrphan && (
        <div className="bg-gradient-to-r from-rose-50 to-amber-50 rounded-xl border border-rose-200 p-4 shadow-sm">
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-rose-600 text-white flex items-center justify-center font-bold text-xs">
                !
              </div>
              <div>
                <h3 className="text-xs font-bold text-rose-950 flex items-center gap-1.5">
                  Single-Author Continuity Warning (Bus Factor = 1)
                  <span className="text-[9px] uppercase px-1.5 py-0.2 rounded font-black bg-rose-200 text-rose-800">
                    {primaryOrphan.bus_factor_risk}
                  </span>
                </h3>
                <p className="text-[11px] font-mono text-slate-700">{primaryOrphan.file_path}</p>
              </div>
            </div>
            <div className="text-right">
              <span className="text-base font-extrabold text-rose-700 tabular-nums">
                {primaryOrphan.blame_percentage}%
              </span>
              <p className="text-[10px] text-slate-500 font-medium">Single-Author Blame</p>
            </div>
          </div>

          <p className="mt-2 text-xs text-slate-700 leading-normal bg-white/70 p-2.5 rounded-lg border border-rose-100">
            {primaryOrphan.risk_rationale}
          </p>

          <div className="mt-2.5 flex items-center justify-between text-[11px]">
            <span className="text-slate-600">
              Primary Contributor: <strong className="text-slate-900">{primaryOrphan.primary_author}</strong>
            </span>
            <button
              onClick={onOpenLeaverModal}
              className="font-semibold text-rose-700 hover:text-rose-800 hover:underline flex items-center gap-1"
            >
              Verify Edge-Case in 60-Sec Review &rarr;
            </button>
          </div>
        </div>
      )}

      {/* DeBERTa-v3 Contradiction Radar Card */}
      {primaryContra && (
        <div className="bg-white rounded-xl border border-amber-300 p-4 shadow-sm">
          <div className="flex items-center justify-between pb-2 mb-2.5 border-b border-amber-100">
            <div className="flex items-center gap-2">
              <AlertOctagon className="w-4 h-4 text-amber-600" />
              <h3 className="text-xs font-bold text-slate-900 tracking-tight">
                DeBERTa-v3 Contradiction Radar
              </h3>
            </div>
            <span
              className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                primaryContra.status === "RESOLVED_BY_LEAVER"
                  ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                  : "bg-amber-100 text-amber-800 border border-amber-300 animate-pulse"
              }`}
            >
              {primaryContra.status === "RESOLVED_BY_LEAVER" ? "Resolved by Leaver" : "Unresolved Contradiction"}
            </span>
          </div>

          <div className="text-xs text-slate-600 mb-2">
            <p className="font-semibold text-slate-800">{primaryContra.topic}</p>
            <p className="text-[11px] text-slate-500 mt-0.5">{primaryContra.explanation}</p>
          </div>

          {/* Side-by-Side Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 my-2.5 text-xs">
            <div
              onClick={() => onSelectCitation(primaryContra.source_a.id)}
              className="p-2.5 rounded-lg border border-purple-200 bg-purple-50/50 hover:bg-purple-50 cursor-pointer transition"
            >
              <div className="flex items-center justify-between text-[10px] text-purple-700 font-semibold mb-1">
                <span>Source A (Discussion)</span>
                <span className="font-mono">Feb 12</span>
              </div>
              <p className="text-slate-800 font-medium leading-snug">{primaryContra.claim_a}</p>
              <span className="mt-1.5 inline-flex items-center gap-1 text-[10px] text-purple-700 font-bold hover:underline">
                <Link2 className="w-2.5 h-2.5" /> Inspect Slack Diff
              </span>
            </div>

            <div
              onClick={() => onSelectCitation(primaryContra.source_b.id)}
              className="p-2.5 rounded-lg border border-blue-200 bg-blue-50/50 hover:bg-blue-50 cursor-pointer transition"
            >
              <div className="flex items-center justify-between text-[10px] text-blue-700 font-semibold mb-1">
                <span>Source B (Git Revert)</span>
                <span className="font-mono">Feb 18</span>
              </div>
              <p className="text-slate-800 font-medium leading-snug">{primaryContra.claim_b}</p>
              <span className="mt-1.5 inline-flex items-center gap-1 text-[10px] text-blue-700 font-bold hover:underline">
                <Link2 className="w-2.5 h-2.5" /> Inspect Git Diff
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
            <span>
              Contradiction Probability: <strong className="text-amber-700 tabular-nums">{(primaryContra.contradiction_score * 100).toFixed(1)}%</strong>
            </span>
            {primaryContra.status !== "RESOLVED_BY_LEAVER" && (
              <button
                onClick={onOpenLeaverModal}
                className="text-xs font-semibold text-blue-600 hover:text-blue-700 hover:underline"
              >
                Resolve via 60-Sec Review &rarr;
              </button>
            )}
          </div>
        </div>
      )}

      {/* Core Decisions List */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
        <div className="flex items-center justify-between pb-2 mb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <GitBranch className="w-4 h-4 text-blue-600" />
            <h3 className="text-xs font-bold text-slate-900 tracking-tight">Verified Architecture Decisions</h3>
          </div>
          <span className="text-[10px] text-slate-500 font-medium tabular-nums">
            {workspace.decisions.length} Active Contracts
          </span>
        </div>

        <div className="space-y-3">
          {workspace.decisions.map((dec) => (
            <div key={dec.id} className="p-3 rounded-lg border border-slate-100 bg-slate-50/50 text-xs">
              <div className="flex items-start justify-between gap-2 mb-1">
                <span className="font-bold text-slate-900 leading-snug">{dec.title}</span>
                <div className="flex items-center gap-1 shrink-0">
                  <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-emerald-100 text-emerald-800 border border-emerald-200 tabular-nums">
                    G(A): {(dec.grounding_score * 100).toFixed(0)}%
                  </span>
                  <span className="text-[9px] font-semibold px-1.5 py-0.2 rounded bg-slate-200 text-slate-700 uppercase">
                    {dec.status}
                  </span>
                </div>
              </div>

              <p className="text-slate-600 text-[11px] leading-relaxed my-1.5">{dec.summary}</p>

              <div className="bg-white p-2 rounded border border-slate-200/60 text-[11px] text-slate-700 mb-2">
                <strong>Why:</strong> {dec.rationale}
              </div>

              {/* Clickable Citation Chips */}
              <div className="flex flex-wrap items-center gap-1.5 pt-1 border-t border-slate-200/50">
                <span className="text-[10px] font-semibold text-slate-400">Sources:</span>
                {dec.citations.map((cit) => (
                  <button
                    key={cit.id}
                    onClick={() => onSelectCitation(cit.id)}
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 transition"
                  >
                    <Link2 className="w-2.5 h-2.5" />
                    <span>{cit.title}</span>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
