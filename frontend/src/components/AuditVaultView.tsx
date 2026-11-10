"use client";

import React, { useState } from "react";
import {
  ShieldCheck,
  KeyRound,
  Lock,
  Unlock,
  Download,
  ExternalLink,
  Code2,
  MessageSquare,
  CheckCircle2,
  Copy,
  Check
} from "lucide-react";
import { HandoverWorkspace, CommitEvent, DiscussionMessage } from "@/types";
import { API_BASE } from "@/lib/api";

interface AuditVaultViewProps {
  workspace: HandoverWorkspace;
  role: "JUNIOR_SUCCESSOR" | "ADMIN";
  onRoleChange: (role: "JUNIOR_SUCCESSOR" | "ADMIN") => void;
  signature?: string;
  leaverApproved: boolean;
  onSelectCitation: (citationId: string) => void;
  onOpenLeaverModal: () => void;
}

export function AuditVaultView({
  workspace,
  role,
  onRoleChange,
  signature,
  leaverApproved,
  onSelectCitation,
  onOpenLeaverModal
}: AuditVaultViewProps) {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [activeSubTab, setActiveSubTab] = useState<"CRYPTO" | "COMMITS" | "DISCUSSIONS">("CRYPTO");

  const commits: CommitEvent[] = workspace.commits || [];
  const discussions: DiscussionMessage[] = workspace.discussions || [];

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(label);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header & Sub-Tabs */}
      <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="w-8 h-8 rounded-lg bg-purple-500/10 text-purple-600 flex items-center justify-center font-bold">
                <ShieldCheck className="w-5 h-5" />
              </span>
              <h2 className="text-base font-bold text-slate-900 tracking-tight">
                Cryptographic Audit Vault & Provenance Traces
              </h2>
            </div>
            <p className="text-xs text-slate-500 max-w-2xl leading-relaxed">
              Provides mathematical tamper-evidence via RFC 8032 Ed25519 digital signatures, NIST SP 800-162 ABAC security filtering, and raw multi-source ingestion records.
            </p>
          </div>

          {/* Sub-tab navigation */}
          <div className="flex items-center bg-slate-100 p-1 rounded-lg text-xs font-semibold shrink-0">
            <button
              onClick={() => setActiveSubTab("CRYPTO")}
              className={`px-3 py-1.5 rounded transition ${
                activeSubTab === "CRYPTO" ? "bg-white text-purple-700 shadow-xs" : "text-slate-500 hover:text-slate-900"
              }`}
            >
              Security Certificate
            </button>
            <button
              onClick={() => setActiveSubTab("COMMITS")}
              className={`px-3 py-1.5 rounded transition ${
                activeSubTab === "COMMITS" ? "bg-white text-blue-700 shadow-xs" : "text-slate-500 hover:text-slate-900"
              }`}
            >
              Git Commits ({commits.length})
            </button>
            <button
              onClick={() => setActiveSubTab("DISCUSSIONS")}
              className={`px-3 py-1.5 rounded transition ${
                activeSubTab === "DISCUSSIONS" ? "bg-white text-slate-900 shadow-xs" : "text-slate-500 hover:text-slate-900"
              }`}
            >
              Discussions ({discussions.length})
            </button>
          </div>
        </div>

        {/* Quick Action Export Buttons */}
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 pt-1">
          <div className="flex items-center gap-2">
            <a
              href={`${API_BASE}/export/w3c-prov`}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-semibold border border-blue-200 transition"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Official W3C PROV-JSON</span>
            </a>
            <a
              href={`${API_BASE}/export/adr`}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-semibold border border-slate-200 transition"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              <span>Export Architecture ADRs (Markdown)</span>
            </a>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-500">Current ABAC View:</span>
            <div className="flex items-center bg-slate-100 p-0.5 rounded-md border border-slate-200">
              <button
                onClick={() => onRoleChange("JUNIOR_SUCCESSOR")}
                className={`px-2 py-0.5 rounded text-[11px] font-semibold transition ${
                  role === "JUNIOR_SUCCESSOR" ? "bg-blue-600 text-white shadow-xs" : "text-slate-600 hover:text-slate-900"
                }`}
              >
                Junior Successor
              </button>
              <button
                onClick={() => onRoleChange("ADMIN")}
                className={`px-2 py-0.5 rounded text-[11px] font-semibold transition ${
                  role === "ADMIN" ? "bg-purple-600 text-white shadow-xs" : "text-slate-600 hover:text-slate-900"
                }`}
              >
                Admin (Auditor)
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* SUB-TAB 1: SECURITY & CRYPTOGRAPHY CERTIFICATE */}
      {activeSubTab === "CRYPTO" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Certificate Card */}
          <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <KeyRound className="w-4 h-4 text-purple-600" />
                <h3 className="text-sm font-bold text-slate-900 tracking-tight">
                  RFC 8032 Ed25519 Verification Certificate
                </h3>
              </div>
              {leaverApproved ? (
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                  VERIFIED STATE
                </span>
              ) : (
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-300">
                  SIGNATURE PENDING
                </span>
              )}
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-[11px] text-slate-500 block mb-1">State Fingerprint (SHA-256 Digest):</span>
                <div className="flex items-center justify-between bg-slate-50 p-2.5 rounded-lg border border-slate-200 font-mono text-[11px] text-slate-800 break-all">
                  <span>{signature ? signature.replace("ed25519:", "").slice(0, 32) + "..." : "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}</span>
                  <button
                    onClick={() => copyToClipboard(signature || "", "sha")}
                    className="ml-2 text-slate-400 hover:text-slate-700 shrink-0"
                    title="Copy SHA-256"
                  >
                    {copiedKey === "sha" ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              <div>
                <span className="text-[11px] text-slate-500 block mb-1">Cryptographic Ed25519 Signature:</span>
                <div className="flex items-center justify-between bg-slate-50 p-2.5 rounded-lg border border-slate-200 font-mono text-[11px] text-purple-900 break-all">
                  <span>{signature || "Pending leaver architect review sign-off."}</span>
                  {signature && (
                    <button
                      onClick={() => copyToClipboard(signature, "sig")}
                      className="ml-2 text-slate-400 hover:text-slate-700 shrink-0"
                      title="Copy Signature"
                    >
                      {copiedKey === "sig" ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                  )}
                </div>
              </div>

              <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px]">
                <span className="text-slate-500">Signing Algorithm:</span>
                <strong className="text-slate-800">Edwards-curve Digital Signature Algorithm (Ed25519)</strong>
              </div>

              <div className="flex items-center justify-between text-[11px]">
                <span className="text-slate-500">Certified Signer:</span>
                <strong className="text-slate-800">{workspace.leaver_name} (Lead Maintainer)</strong>
              </div>
            </div>

            {!leaverApproved && (
              <div className="mt-4 pt-3 border-t border-slate-100">
                <button
                  onClick={onOpenLeaverModal}
                  className="w-full py-2 rounded-lg bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold transition shadow-xs"
                >
                  Sign State via 60-Second Leaver Review
                </button>
              </div>
            )}
          </div>

          {/* NIST ABAC Security Engine Card */}
          <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                {role === "ADMIN" ? (
                  <Unlock className="w-4 h-4 text-purple-600" />
                ) : (
                  <Lock className="w-4 h-4 text-blue-600" />
                )}
                <h3 className="text-sm font-bold text-slate-900 tracking-tight">
                  NIST SP 800-162 ABAC Security Engine
                </h3>
              </div>
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                  role === "ADMIN"
                    ? "bg-purple-100 text-purple-800 border border-purple-200"
                    : "bg-blue-100 text-blue-800 border border-blue-200"
                }`}
              >
                {role === "ADMIN" ? "Level 3 Clearance (Admin)" : "Level 1 Clearance (Junior)"}
              </span>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              Enforces Attribute-Based Access Control (ABAC) server-side prior to JSON serialization. Secret credentials, production API keys, and sensitive internal HR traces are deep-scrubbed before junior successors can view them.
            </p>

            <div className="space-y-2 text-xs">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <div className="flex items-center justify-between font-semibold text-slate-800 mb-1">
                  <span>Target Sensitivity Policy:</span>
                  <span className="font-mono text-[11px] text-slate-600">CONFIDENTIAL_INFRA</span>
                </div>
                <p className="text-[11px] text-slate-500 leading-normal">
                  {role === "ADMIN"
                    ? "🟢 Unlocked: All raw production keys, Stripe test tokens, and JWT secrets are visible."
                    : "🛡️ Redacted: Sensitive tokens are stripped and replaced with [REDACTED_API_KEY] markers."}
                </p>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <div className="flex items-center justify-between font-semibold text-slate-800 mb-1">
                  <span>Enforcement Layer:</span>
                  <span className="text-[11px] text-emerald-700 font-bold">FastAPI Server-Side Filter</span>
                </div>
                <p className="text-[11px] text-slate-500 leading-normal">
                  Redaction is enforced in the Python backend pipeline before network transmission — never masked via client-side CSS.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* SUB-TAB 2: COMMITS TABLE */}
      {activeSubTab === "COMMITS" && (
        <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs">
          <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100">
            <div>
              <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
                <Code2 className="w-4 h-4 text-blue-600" />
                Ingested Git Commits ({commits.length})
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Mined commit events with author attribution, diff insertions, and ABAC classification.
              </p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 text-slate-400 font-semibold uppercase text-[10px]">
                  <th className="pb-2.5">SHA</th>
                  <th className="pb-2.5">Commit Message</th>
                  <th className="pb-2.5">Author</th>
                  <th className="pb-2.5">Changes</th>
                  <th className="pb-2.5">Security Tag</th>
                  <th className="pb-2.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {commits.map((c) => (
                  <tr key={c.sha} className="hover:bg-slate-50/70 transition">
                    <td className="py-3 font-mono text-[11px] font-bold text-blue-600">
                      {c.sha.slice(0, 7)}
                    </td>
                    <td className="py-3 font-medium text-slate-800 max-w-xs truncate pr-4">
                      {c.message.split("\n")[0]}
                    </td>
                    <td className="py-3 text-slate-600">{c.author}</td>
                    <td className="py-3 text-[11px] font-mono tabular-nums">
                      <span className="text-emerald-600 font-bold">+{c.insertions}</span>{" "}
                      <span className="text-rose-600 font-bold">-{c.deletions}</span>
                    </td>
                    <td className="py-3">
                      <span
                        className={`text-[9px] font-bold px-1.5 py-0.5 rounded uppercase ${
                          c.security_tag === "CONFIDENTIAL_INFRA"
                            ? "bg-rose-100 text-rose-700"
                            : "bg-slate-100 text-slate-700"
                        }`}
                      >
                        {c.security_tag}
                      </span>
                    </td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => onSelectCitation(`cit-commit-${c.sha}`)}
                        className="text-xs font-semibold text-blue-600 hover:text-blue-800 hover:underline inline-flex items-center gap-1"
                      >
                        Inspect Trace &rarr;
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* SUB-TAB 3: DISCUSSIONS */}
      {activeSubTab === "DISCUSSIONS" && (
        <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs">
          <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100">
            <div>
              <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-purple-600" />
                Slack & Discord Team Discussions ({discussions.length})
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Asynchronous chat traces mined for architectural intent, rationale, and consensus.
              </p>
            </div>
          </div>

          <div className="space-y-3">
            {discussions.map((d) => (
              <div
                key={d.id}
                onClick={() => onSelectCitation(`cit-${d.id}`)}
                className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/60 hover:bg-slate-100/80 cursor-pointer transition text-xs flex flex-col justify-between"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-100 text-purple-700 uppercase">
                      #{d.channel}
                    </span>
                    <strong className="text-slate-800 font-semibold">{d.author}</strong>
                  </div>
                  <span className="font-mono text-[10px] text-slate-400 tabular-nums">
                    {d.timestamp}
                  </span>
                </div>

                <p className="text-slate-700 leading-relaxed font-normal my-1">
                  &ldquo;{d.text}&rdquo;
                </p>

                <div className="flex items-center justify-between pt-2 border-t border-slate-200/60 text-[11px] text-slate-500 mt-1">
                  <span>Security: {d.security_tag}</span>
                  <span className="text-purple-700 font-semibold hover:underline">
                    Inspect Discussion Diff &rarr;
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

