"use client";

import React, { useEffect, useState } from "react";
import { X, ShieldAlert, Code2, MessageSquare, FileText, Copy, Check } from "lucide-react";
import { CitationSource } from "@/types";

interface CitationDrawerProps {
  citation: CitationSource | null;
  onClose: () => void;
}

export function CitationDrawer({ citation, onClose }: CitationDrawerProps) {
  const [copied, setCopied] = useState<boolean>(false);

  // Listen for Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  if (!citation) return null;

  const isRedacted = citation.snippet.includes("[REDACTED");

  const handleCopy = () => {
    navigator.clipboard.writeText(citation.snippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-900/50 backdrop-blur-xs transition-opacity">
      {/* Click outside to close */}
      <div className="flex-1" onClick={onClose} />

      {/* Drawer content */}
      <div className="w-full max-w-xl bg-white h-full shadow-2xl flex flex-col border-l border-slate-200 animate-in slide-in-from-right duration-200">
        {/* Drawer Header */}
        <div className="p-4 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center shrink-0">
              {citation.source_type === "commit" ? (
                <Code2 className="w-4 h-4 text-blue-400" />
              ) : citation.source_type === "discussion" ? (
                <MessageSquare className="w-4 h-4 text-purple-400" />
              ) : (
                <FileText className="w-4 h-4 text-emerald-400" />
              )}
            </div>
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                NotebookLM Grounded Citation &bull; {citation.source_type.toUpperCase()}
              </span>
              <h3 className="text-xs font-bold text-white truncate max-w-sm">{citation.title}</h3>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Metadata section */}
        <div className="p-4 bg-slate-50 border-b border-slate-200 text-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-slate-500 font-medium">Source URI:</span>
            <code className="text-[11px] font-mono text-blue-600 bg-blue-50 px-2.5 py-0.5 rounded border border-blue-200 truncate max-w-[280px]">
              {citation.uri}
            </code>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-500 font-medium">Author / Contributor:</span>
            <strong className="text-slate-800">{citation.author}</strong>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-500 font-medium">Timestamp:</span>
            <span className="font-mono text-slate-600 tabular-nums">{citation.timestamp}</span>
          </div>
        </div>

        {/* Snippet / Code Diff Body */}
        <div className="p-4 flex-1 overflow-y-auto space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold text-slate-900 tracking-tight">Verifiable Source Traces</h4>
            <button
              onClick={handleCopy}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-semibold text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 transition"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? "Copied" : "Copy Snippet"}</span>
            </button>
          </div>

          {isRedacted ? (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 space-y-2">
              <div className="flex items-center gap-2 font-bold text-xs text-rose-900">
                <ShieldAlert className="w-4 h-4 text-rose-600" />
                <span>Restricted Cryptographic Token / Secret Redacted</span>
              </div>
              <p className="text-xs leading-relaxed">
                This source contains production credentials or confidential records. It has been stripped server-side
                in accordance with NIST SP 800-162 Attribute-Based Access Control (ABAC) policies.
              </p>
              <div className="p-3 rounded-lg bg-rose-100/80 font-mono text-xs text-rose-950 whitespace-pre-wrap break-all">
                {citation.snippet}
              </div>
            </div>
          ) : (
            <div className="rounded-xl bg-slate-950 p-4 font-mono text-xs text-slate-200 leading-relaxed overflow-x-auto border border-slate-800 shadow-inner">
              <pre className="whitespace-pre-wrap font-mono">{citation.snippet}</pre>
            </div>
          )}

          <div className="p-3.5 rounded-xl bg-blue-50 border border-blue-200 text-xs text-blue-900">
            <p className="font-bold mb-1">W3C PROV-DM Alignment:</p>
            <p className="text-[11px] text-blue-800 leading-normal">
              This evidence node is registered under the W3C PROV specification as <code>prov:wasDerivedFrom</code>. Every decision in the Continuation Hub can be verified directly back to this exact trace.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="p-3.5 bg-slate-100 border-t border-slate-200 flex items-center justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800 transition"
          >
            Close Sidecar
          </button>
        </div>
      </div>
    </div>
  );
}
