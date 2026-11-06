"use client";

import React, { useEffect } from "react";
import { X, ShieldAlert, Code2, MessageSquare, FileText } from "lucide-react";
import { CitationSource } from "@/types";

interface CitationDrawerProps {
  citation: CitationSource | null;
  onClose: () => void;
}

export function CitationDrawer({ citation, onClose }: CitationDrawerProps) {
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

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-900/40 backdrop-blur-sm transition-opacity">
      {/* Click outside to close */}
      <div className="flex-1" onClick={onClose} />

      {/* Drawer content */}
      <div className="w-full max-w-lg bg-white h-full shadow-2xl flex flex-col border-l border-slate-200 animate-in slide-in-from-right duration-200">
        {/* Drawer Header */}
        <div className="p-4 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800">
          <div className="flex items-center gap-2">
            {citation.source_type === "commit" ? (
              <Code2 className="w-4 h-4 text-blue-400" />
            ) : citation.source_type === "discussion" ? (
              <MessageSquare className="w-4 h-4 text-purple-400" />
            ) : (
              <FileText className="w-4 h-4 text-emerald-400" />
            )}
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                NotebookLM Grounded Citation
              </span>
              <h3 className="text-xs font-bold text-white truncate max-w-xs">{citation.title}</h3>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Metadata section */}
        <div className="p-4 bg-slate-50 border-b border-slate-200 text-xs space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-slate-500 font-medium">Source URI:</span>
            <code className="text-[11px] font-mono text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-100">
              {citation.uri}
            </code>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-500 font-medium">Author:</span>
            <strong className="text-slate-800">{citation.author}</strong>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-500 font-medium">Recorded Timestamp:</span>
            <span className="font-mono text-slate-600 tabular-nums">{citation.timestamp}</span>
          </div>
        </div>

        {/* Snippet / Code Diff Body */}
        <div className="p-4 flex-1 overflow-y-auto">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-xs font-bold text-slate-900 tracking-tight">Verifiable Source Traces</h4>
            <span className="text-[10px] font-semibold text-slate-400">Cryptographically Grounded</span>
          </div>

          {isRedacted ? (
            <div className="p-4 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 space-y-2">
              <div className="flex items-center gap-2 font-bold text-xs text-rose-900">
                <ShieldAlert className="w-4 h-4 text-rose-600" />
                <span>Restricted Cryptographic Token</span>
              </div>
              <p className="text-xs leading-relaxed">
                This source contains production credentials or confidential HR records. It has been stripped server-side
                in accordance with Attribute-Based Access Control (ABAC) policies.
              </p>
              <div className="p-2 rounded bg-rose-100 font-mono text-[11px] text-rose-900">
                {citation.snippet}
              </div>
            </div>
          ) : (
            <div className="rounded-lg bg-slate-950 p-3 font-mono text-xs text-slate-200 leading-relaxed overflow-x-auto border border-slate-800 shadow-inner">
              <pre className="whitespace-pre-wrap">{citation.snippet}</pre>
            </div>
          )}

          <div className="mt-4 p-3 rounded-lg bg-blue-50 border border-blue-200 text-xs text-blue-900">
            <p className="font-semibold mb-1">W3C PROV-DM Alignment:</p>
            <p className="text-[11px] text-blue-800 leading-normal">
              This evidence node is registered under the W3C PROV data model as <code>prov:wasDerivedFrom</code>. Every claim in the Continuation Hub can be verified directly back to this exact trace.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 bg-slate-100 border-t border-slate-200 flex items-center justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-md bg-slate-900 text-white text-xs font-medium hover:bg-slate-800 transition"
          >
            Close Sidecar
          </button>
        </div>
      </div>
    </div>
  );
}
