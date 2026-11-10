"use client";

import React from "react";
import {
  AlertTriangle,
  GitBranch,
  ShieldAlert,
  CalendarCheck,
  ShieldCheck,
  CheckCircle2,
  Lock,
  Unlock
} from "lucide-react";
import { HandoverWorkspace } from "@/types";

interface MetricsRibbonProps {
  workspace: HandoverWorkspace;
  role: "JUNIOR_SUCCESSOR" | "ADMIN";
  leaverApproved: boolean;
  signature?: string;
  onOpenLeaverModal: () => void;
  onTabSelect?: (tabId: string) => void;
}

export function MetricsRibbon({
  workspace,
  role,
  leaverApproved,
  signature,
  onOpenLeaverModal,
  onTabSelect
}: MetricsRibbonProps) {
  const orphanCount = workspace.orphan_risk_files.length;
  const criticalOrphan = workspace.orphan_risk_files.find((f) => f.bus_factor_risk === "CRITICAL") || workspace.orphan_risk_files[0];
  const maxBlame = criticalOrphan ? criticalOrphan.blame_percentage : 0;

  const decisionsCount = workspace.decisions.length;
  const avgGrounding =
    decisionsCount > 0
      ? (
          workspace.decisions.reduce((acc, d) => acc + (d.grounding_score || 0), 0) /
          decisionsCount
        ) * 100
      : 95;

  const totalContra = workspace.contradictions.length;
  const openContra = workspace.contradictions.filter(
    (c) => c.status !== "RESOLVED_BY_LEAVER"
  ).length;

  const totalTasks = workspace.kanban_tasks.length;
  const doneTasks = workspace.kanban_tasks.filter((t) => t.completed).length;
  const progressPercent = totalTasks > 0 ? Math.round((doneTasks / totalTasks) * 100) : 0;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 mb-6">
      {/* 1. Bus Factor / Code Ownership */}
      <div
        onClick={() => onTabSelect && onTabSelect("risks")}
        className="bg-white rounded-xl border border-slate-200/80 p-3.5 shadow-sm hover:border-rose-300 hover:shadow transition cursor-pointer group"
      >
        <div className="flex items-center justify-between text-xs mb-1.5">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-rose-500" />
            Bus Factor Risk
          </span>
          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200">
            DOA = 1
          </span>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-xl font-extrabold text-slate-900 group-hover:text-rose-600 transition tabular-nums">
            {orphanCount} {orphanCount === 1 ? "File" : "Files"}
          </span>
          <span className="text-xs text-rose-600 font-semibold tabular-nums">
            {maxBlame}% solo
          </span>
        </div>
        <p className="text-[11px] text-slate-500 mt-1 truncate">
          {criticalOrphan ? criticalOrphan.file_path.split("/").pop() : "No critical orphans"}
        </p>
      </div>

      {/* 2. Decisions & Grounding */}
      <div
        onClick={() => onTabSelect && onTabSelect("dag")}
        className="bg-white rounded-xl border border-slate-200/80 p-3.5 shadow-sm hover:border-blue-300 hover:shadow transition cursor-pointer group"
      >
        <div className="flex items-center justify-between text-xs mb-1.5">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
            <GitBranch className="w-3.5 h-3.5 text-blue-500" />
            Architecture Decisions
          </span>
          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
            W3C PROV
          </span>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-xl font-extrabold text-slate-900 group-hover:text-blue-600 transition tabular-nums">
            {decisionsCount} Active
          </span>
          <span className="text-xs text-emerald-600 font-bold tabular-nums">
            {avgGrounding.toFixed(0)}% G(A)
          </span>
        </div>
        <p className="text-[11px] text-slate-500 mt-1 truncate">
          Prov-DM Lineage & DAG validated
        </p>
      </div>

      {/* 3. Contradiction Radar */}
      <div
        onClick={() => onTabSelect && onTabSelect("risks")}
        className="bg-white rounded-xl border border-slate-200/80 p-3.5 shadow-sm hover:border-amber-300 hover:shadow transition cursor-pointer group"
      >
        <div className="flex items-center justify-between text-xs mb-1.5">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
            <ShieldAlert className="w-3.5 h-3.5 text-amber-500" />
            NLI Contradictions
          </span>
          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${
            openContra > 0
              ? "bg-amber-50 text-amber-800 border-amber-200 animate-pulse"
              : "bg-emerald-50 text-emerald-800 border-emerald-200"
          }`}>
            {openContra > 0 ? "Radar Alert" : "Clean"}
          </span>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-xl font-extrabold text-slate-900 group-hover:text-amber-600 transition tabular-nums">
            {totalContra} Detected
          </span>
          <span className="text-xs text-amber-600 font-semibold">
            {openContra} open
          </span>
        </div>
        <p className="text-[11px] text-slate-500 mt-1 truncate">
          DeBERTa-v3 semantic conflict radar
        </p>
      </div>

      {/* 4. Successor Onboarding */}
      <div
        onClick={() => onTabSelect && onTabSelect("onboarding")}
        className="bg-white rounded-xl border border-slate-200/80 p-3.5 shadow-sm hover:border-emerald-300 hover:shadow transition cursor-pointer group"
      >
        <div className="flex items-center justify-between text-xs mb-1.5">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
            <CalendarCheck className="w-3.5 h-3.5 text-emerald-500" />
            Onboarding Roadmap
          </span>
          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 tabular-nums">
            {progressPercent}%
          </span>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-xl font-extrabold text-slate-900 group-hover:text-emerald-600 transition tabular-nums">
            {doneTasks}/{totalTasks}
          </span>
          <span className="text-xs text-slate-500 font-medium">Tasks done</span>
        </div>
        {/* Mini progress bar */}
        <div className="w-full bg-slate-100 rounded-full h-1.5 mt-2 overflow-hidden">
          <div
            className="bg-emerald-500 h-1.5 rounded-full transition-all duration-300"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* 5. Cryptographic Integrity & ABAC */}
      <div
        title={signature ? `Ed25519 Signature: ${signature}` : "Review pending"}
        onClick={() => {
          if (!leaverApproved) onOpenLeaverModal();
          else if (onTabSelect) onTabSelect("audit");
        }}
        className="col-span-2 md:col-span-1 bg-white rounded-xl border border-slate-200/80 p-3.5 shadow-sm hover:border-purple-300 hover:shadow transition cursor-pointer group"
      >
        <div className="flex items-center justify-between text-xs mb-1.5">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-purple-500" />
            Ed25519 & ABAC
          </span>
          <span
            className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${
              role === "ADMIN"
                ? "bg-purple-50 text-purple-700 border-purple-200"
                : "bg-blue-50 text-blue-700 border-blue-200"
            }`}
          >
            {role === "ADMIN" ? "Admin" : "Junior"}
          </span>
        </div>
        <div className="flex items-center gap-1.5 mt-0.5">
          {leaverApproved ? (
            <div className="flex items-center gap-1 text-emerald-700">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span className="text-xs font-bold truncate">RFC 8032 Signed</span>
            </div>
          ) : (
            <div className="flex items-center gap-1 text-amber-700">
              <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
              <span className="text-xs font-bold">Review Pending</span>
            </div>
          )}
        </div>
        <div className="flex items-center gap-1 text-[10px] text-slate-500 mt-1.5">
          {role === "ADMIN" ? (
            <span className="flex items-center gap-1 text-purple-700 font-medium">
              <Unlock className="w-3 h-3" /> Unrestricted Clearance
            </span>
          ) : (
            <span className="flex items-center gap-1 text-slate-500">
              <Lock className="w-3 h-3" /> Secrets Redacted (NIST)
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

