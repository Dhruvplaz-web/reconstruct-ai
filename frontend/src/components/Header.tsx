"use client";

import React from "react";
import { RotateCcw, Shield, CheckCircle2, AlertTriangle } from "lucide-react";

interface HeaderProps {
  role: "JUNIOR_SUCCESSOR" | "ADMIN";
  onRoleChange: (newRole: "JUNIOR_SUCCESSOR" | "ADMIN") => void;
  onOpenLeaverModal: () => void;
  onResetPlayground: () => void;
  isResetting: boolean;
  leaverApproved: boolean;
  signature?: string;
}

export function Header({
  role,
  onRoleChange,
  onOpenLeaverModal,
  onResetPlayground,
  isResetting,
  leaverApproved,
  signature
}: HeaderProps) {
  return (
    <header className="sticky top-0 z-30 bg-slate-900 text-white border-b border-slate-800 px-4 md:px-8 py-3">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        {/* Brand & Project Info */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center font-black text-white text-lg tracking-wider shadow-sm">
            R
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold tracking-tight text-base text-white">RECONSTRUCT.AI</span>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-500/30">
                TEAM DOMINATOR
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Acme Payments Microservice &bull; Offboarding: <span className="text-slate-200 font-medium">Alice Vance</span>
            </p>
          </div>
        </div>

        {/* Global Controls & Actions */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* 1-Click Playground Reset */}
          <button
            onClick={onResetPlayground}
            disabled={isResetting}
            title="Reset to clean benchmark state"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${isResetting ? "animate-spin" : ""}`} />
            <span>1-Click Playground</span>
          </button>

          {/* 60-Second Leaver Review Trigger */}
          {leaverApproved ? (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-emerald-500/20 text-emerald-300 text-xs font-medium border border-emerald-500/40">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Signed ({signature ? signature.slice(0, 16) : "Approved"})</span>
            </div>
          ) : (
            <button
              onClick={onOpenLeaverModal}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 text-xs font-semibold border border-amber-500/40 transition"
            >
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
              <span>60-Sec Leaver Review</span>
            </button>
          )}

          {/* Role Switcher (ABAC Clearance Boundary) */}
          <div className="flex items-center bg-slate-800 rounded-md p-0.5 border border-slate-700 text-xs font-medium">
            <span className="px-2 text-slate-400 flex items-center gap-1">
              <Shield className="w-3 h-3" />
              Role:
            </span>
            <button
              onClick={() => onRoleChange("JUNIOR_SUCCESSOR")}
              className={`px-2.5 py-1 rounded transition ${
                role === "JUNIOR_SUCCESSOR"
                  ? "bg-blue-600 text-white font-semibold shadow-sm"
                  : "text-slate-300 hover:text-white"
              }`}
            >
              Junior Successor
            </button>
            <button
              onClick={() => onRoleChange("ADMIN")}
              className={`px-2.5 py-1 rounded transition ${
                role === "ADMIN"
                  ? "bg-purple-600 text-white font-semibold shadow-sm"
                  : "text-slate-300 hover:text-white"
              }`}
            >
              Admin / Lead
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
