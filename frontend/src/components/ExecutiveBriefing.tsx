"use client";

import React from "react";
import {
  BookOpen,
  AlertTriangle,
  AlertOctagon,
  GitBranch,
  Link2,
  CheckCircle2,
  UserCheck,
  Building2,
  ArrowRight
} from "lucide-react";
import { HandoverWorkspace } from "@/types";

interface ExecutiveBriefingProps {
  workspace: HandoverWorkspace;
  onSelectCitation: (citationId: string) => void;
  onOpenLeaverModal: () => void;
  onTabSelect?: (tabId: string) => void;
}

export function ExecutiveBriefing({
  workspace,
  onSelectCitation,
  onOpenLeaverModal,
  onTabSelect
}: ExecutiveBriefingProps) {
  const primaryOrphan =
    workspace.orphan_risk_files.find((f) => f.bus_factor_risk === "CRITICAL") ||
    workspace.orphan_risk_files[0];
  const primaryContra = workspace.contradictions[0];

  return (
    <div className="space-y-6">
      {/* 1. Executive Summary Card */}
      <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 mb-3 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-600/10 text-blue-600 flex items-center justify-center font-bold">
              <BookOpen className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 tracking-tight">
                Executive Continuity Briefing
              </h2>
              <p className="text-xs text-slate-500">
                Automated context reconstruction for incoming maintainers
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 flex items-center gap-1">
              <Building2 className="w-3 h-3 text-blue-600" />
              RSCOE &bull; Hackathon
            </span>
          </div>
        </div>

        <p className="text-xs sm:text-[13px] text-slate-700 leading-relaxed text-justify bg-slate-50/60 p-4 rounded-xl border border-slate-100">
          {workspace.executive_summary}
        </p>

        {/* Maintainer & Handoff Context Pills */}
        <div className="mt-3.5 pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1 text-slate-700">
              <UserCheck className="w-3.5 h-3.5 text-blue-600" />
              Primary Maintainer: <strong className="text-slate-900 ml-0.5">{workspace.leaver_name}</strong>
            </span>
            <span className="text-slate-300">&bull;</span>
            <span className="text-slate-600">
              Project: <strong className="text-slate-900">{workspace.project_name}</strong>
            </span>
          </div>
          <span className="text-[11px] text-slate-400">
            Generated: {workspace.generated_at ? new Date(workspace.generated_at).toLocaleDateString() : "Live Session"}
          </span>
        </div>
      </div>

      {/* 2. Side-by-Side Highlight Grid: Bus Factor Warning & Contradiction Alert */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Bus Factor = 1 Warning Card */}
        {primaryOrphan && (
          <div className="bg-gradient-to-br from-rose-50/90 via-rose-50/40 to-white rounded-2xl border border-rose-200 p-5 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-start justify-between gap-2 mb-2.5">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-rose-600 text-white flex items-center justify-center font-bold text-sm shadow-xs">
                    <AlertTriangle className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-rose-950 flex items-center gap-1.5">
                      Single-Author Continuity Warning
                    </h3>
                    <span className="text-[9px] uppercase px-1.5 py-0.5 rounded font-black bg-rose-200 text-rose-800 tracking-wider">
                      BUS FACTOR = 1 &bull; {primaryOrphan.bus_factor_risk}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-xl font-extrabold text-rose-700 tabular-nums">
                    {primaryOrphan.blame_percentage}%
                  </span>
                  <p className="text-[10px] text-slate-500 font-medium">Solo Blame</p>
                </div>
              </div>

              <div className="bg-white/80 p-2.5 rounded-lg border border-rose-100 my-2">
                <span className="text-[10px] text-slate-400 uppercase font-mono block">Target File:</span>
                <code className="text-xs font-mono font-bold text-slate-800 break-all">
                  {primaryOrphan.file_path}
                </code>
              </div>

              <p className="text-xs text-slate-700 leading-relaxed bg-white/60 p-3 rounded-lg border border-rose-100/60">
                {primaryOrphan.risk_rationale}
              </p>
            </div>

            <div className="mt-3.5 pt-3 border-t border-rose-100 flex items-center justify-between text-xs">
              <span className="text-slate-600">
                Author: <strong className="text-slate-900">{primaryOrphan.primary_author}</strong>
              </span>
              <div className="flex items-center gap-3">
                {onTabSelect && (
                  <button
                    onClick={() => onTabSelect("risks")}
                    className="text-xs font-semibold text-slate-600 hover:text-slate-900 flex items-center gap-0.5"
                  >
                    All Risks <ArrowRight className="w-3 h-3" />
                  </button>
                )}
                <button
                  onClick={onOpenLeaverModal}
                  className="font-bold text-rose-700 hover:text-rose-900 flex items-center gap-1 hover:underline"
                >
                  Verify in 60s Review &rarr;
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Contradiction Radar Card */}
        {primaryContra && (
          <div className="bg-gradient-to-br from-amber-50/90 via-amber-50/40 to-white rounded-2xl border border-amber-300 p-5 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-2 mb-2.5 border-b border-amber-100">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-700 flex items-center justify-center font-bold text-sm">
                    <AlertOctagon className="w-4 h-4 text-amber-600" />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-slate-900 tracking-tight">
                      Architectural Contradiction Radar
                    </h3>
                    <span className="text-[10px] text-amber-700 font-semibold">
                      DeBERTa-v3 Semantic Cross-Encoder
                    </span>
                  </div>
                </div>
                <span
                  className={`text-[9px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                    primaryContra.status === "RESOLVED_BY_LEAVER"
                      ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                      : "bg-amber-100 text-amber-800 border border-amber-300 animate-pulse"
                  }`}
                >
                  {primaryContra.status === "RESOLVED_BY_LEAVER" ? "Resolved" : "Unresolved"}
                </span>
              </div>

              <div className="text-xs text-slate-700 mb-2">
                <strong className="text-slate-900 block font-semibold text-xs">{primaryContra.topic}</strong>
                <p className="text-[11px] text-slate-600 mt-1">{primaryContra.explanation}</p>
              </div>

              {/* Mini side-by-side */}
              <div className="grid grid-cols-2 gap-2 my-2.5 text-xs">
                <div
                  onClick={() => onSelectCitation(primaryContra.source_a.id)}
                  className="p-2.5 rounded-lg border border-purple-200 bg-purple-50/60 hover:bg-purple-100/60 cursor-pointer transition text-[11px]"
                >
                  <span className="text-[9px] font-bold text-purple-700 uppercase block mb-1">
                    Source A (Slack)
                  </span>
                  <p className="text-slate-800 font-medium line-clamp-2">{primaryContra.claim_a}</p>
                </div>
                <div
                  onClick={() => onSelectCitation(primaryContra.source_b.id)}
                  className="p-2.5 rounded-lg border border-blue-200 bg-blue-50/60 hover:bg-blue-100/60 cursor-pointer transition text-[11px]"
                >
                  <span className="text-[9px] font-bold text-blue-700 uppercase block mb-1">
                    Source B (Git Revert)
                  </span>
                  <p className="text-slate-800 font-medium line-clamp-2">{primaryContra.claim_b}</p>
                </div>
              </div>
            </div>

            <div className="mt-2.5 pt-2 border-t border-amber-100 flex items-center justify-between text-xs">
              <span className="text-[11px] text-slate-500">
                Conflict Score: <strong className="text-amber-700">{(primaryContra.contradiction_score * 100).toFixed(0)}%</strong>
              </span>
              {primaryContra.status !== "RESOLVED_BY_LEAVER" ? (
                <button
                  onClick={onOpenLeaverModal}
                  className="text-xs font-semibold text-blue-600 hover:text-blue-700 hover:underline"
                >
                  Resolve in 60s Review &rarr;
                </button>
              ) : (
                <span className="text-emerald-700 font-bold text-xs flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Resolved
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* 3. Verified Architecture Decisions Card */}
      <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs">
        <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <GitBranch className="w-4 h-4 text-blue-600" />
            <h3 className="text-sm font-bold text-slate-900 tracking-tight">
              Verified Architecture Decisions
            </h3>
          </div>
          <span className="text-xs font-semibold text-slate-500">
            {workspace.decisions.length} Active Architecture Contracts
          </span>
        </div>

        <div className="space-y-3.5">
          {workspace.decisions.map((dec) => (
            <div
              key={dec.id}
              className="p-4 rounded-xl border border-slate-100 bg-slate-50/50 hover:bg-white hover:border-slate-300 hover:shadow-xs transition text-xs"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                <span className="font-bold text-slate-900 text-xs sm:text-[13px] leading-snug">
                  {dec.title}
                </span>
                <div className="flex items-center gap-1.5 shrink-0">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200 tabular-nums">
                    G(A): {(dec.grounding_score * 100).toFixed(0)}% Grounded
                  </span>
                  <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-slate-200 text-slate-700 uppercase">
                    {dec.status}
                  </span>
                </div>
              </div>

              <p className="text-slate-600 text-xs leading-relaxed my-2">{dec.summary}</p>

              <div className="bg-white p-2.5 rounded-lg border border-slate-200/80 text-[11px] text-slate-700 mb-2.5">
                <strong className="text-slate-900">Why (Architectural Rationale):</strong> {dec.rationale}
              </div>

              {/* Clickable Citation Chips */}
              <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-200/50">
                <span className="text-[11px] font-semibold text-slate-400">Verifiable Sources:</span>
                {dec.citations.map((cit) => (
                  <button
                    key={cit.id}
                    onClick={() => onSelectCitation(cit.id)}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-medium bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 transition"
                  >
                    <Link2 className="w-3 h-3" />
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
