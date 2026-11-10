"use client";

import React from "react";
import {
  RotateCcw,
  Shield,
  CheckCircle2,
  AlertTriangle,
  FolderGit2,
  Loader2
} from "lucide-react";

interface HeaderProps {
  role: "JUNIOR_SUCCESSOR" | "ADMIN";
  onRoleChange: (newRole: "JUNIOR_SUCCESSOR" | "ADMIN") => void;
  onOpenLeaverModal: () => void;
  onOpenIngestModal: () => void;
  onResetPlayground: () => void;
  isResetting: boolean;
  isAnalyzingLive: boolean;
  leaverApproved: boolean;
  signature?: string;
  projectName?: string;
  leaverName?: string;
}

export function Header({
  role,
  onRoleChange,
  onOpenLeaverModal,
  onOpenIngestModal,
  onResetPlayground,
  isResetting,
  isAnalyzingLive,
  leaverApproved,
  signature,
  projectName = "Acme Payments Microservice",
  leaverName = "Alice Vance"
}: HeaderProps) {
  return (
    <header className="sticky top-0 z-30 bg-slate-900/95 backdrop-blur-md text-white border-b border-slate-800 px-4 md:px-8 py-3 shadow-md">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        {/* Brand & Project Info */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-700 to-indigo-500 flex items-center justify-center font-black text-white text-lg tracking-wider shadow-sm ring-1 ring-white/20">
            R
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold tracking-tight text-base text-white">RECONSTRUCT.AI</span>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-500/30">
                TEAM DOMINATOR
              </span>
              <span className="hidden sm:inline-block px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-400 border border-slate-700">
                JSPM RSCOE
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              <span className="text-slate-200 font-semibold">{projectName}</span> &bull; Departing Maintainer:{" "}
              <span className="text-slate-300 font-medium">{leaverName}</span>
            </p>
          </div>
        </div>

        {/* Global Controls & Actions */}
        <div className="flex flex-wrap items-center gap-2 sm:gap-2.5">
          {/* Multi-Source Real-Time Ingestion Trigger */}
          <button
            onClick={onOpenIngestModal}
            disabled={isAnalyzingLive}
            title="Ingest local repo, remote Git clone, or team Slack/Discord traces"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 text-xs font-semibold border border-emerald-500/40 transition active:scale-95"
          >
            {isAnalyzingLive ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <FolderGit2 className="w-3.5 h-3.5 text-emerald-400" />
            )}
            <span>Ingest Sources</span>
          </button>

          {/* 1-Click Synthetic Playground Reset */}
          <button
            onClick={onResetPlayground}
            disabled={isResetting}
            title="Reset to clean benchmark state (Acme Payments Microservice)"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition active:scale-95"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${isResetting ? "animate-spin" : ""}`} />
            <span>Benchmark Demo</span>
          </button>

          {/* 60-Second Leaver Review Trigger */}
          {leaverApproved ? (
            <div
              title={`RFC 8032 Ed25519 Cryptographically Verified Signature: ${signature}`}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-300 text-xs font-semibold border border-emerald-500/40 cursor-help"
            >
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Ed25519 Signed ({signature ? signature.replace("ed25519:", "").slice(0, 8) + "..." : "Verified"})</span>
            </div>
          ) : (
            <button
              onClick={onOpenLeaverModal}
              title="Resolve 2-week notice paradox with 60-sec micro-review"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 text-xs font-semibold border border-amber-500/40 transition active:scale-95"
            >
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
              <span>60-Sec Leaver Review</span>
            </button>
          )}

          {/* Role Switcher (ABAC Clearance Boundary) */}
          <div className="flex items-center bg-slate-800 rounded-lg p-0.5 border border-slate-700 text-xs font-medium">
            <span className="px-2 text-slate-400 flex items-center gap-1 text-[11px]">
              <Shield className="w-3 h-3 text-slate-400" />
              Role:
            </span>
            <button
              onClick={() => onRoleChange("JUNIOR_SUCCESSOR")}
              title="NIST SP 800-162 ABAC Filter Active: Sensitive secrets and production credentials redacted"
              className={`px-2.5 py-1 rounded-md transition text-xs ${
                role === "JUNIOR_SUCCESSOR"
                  ? "bg-blue-600 text-white font-semibold shadow-xs"
                  : "text-slate-300 hover:text-white"
              }`}
            >
              Junior
            </button>
            <button
              onClick={() => onRoleChange("ADMIN")}
              title="Unrestricted Admin/Auditor Clearance: All architectural traces and secrets visible"
              className={`px-2.5 py-1 rounded-md transition text-xs ${
                role === "ADMIN"
                  ? "bg-purple-600 text-white font-semibold shadow-xs"
                  : "text-slate-300 hover:text-white"
              }`}
            >
              Admin
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
