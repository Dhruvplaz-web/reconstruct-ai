"use client";

import React, { useState } from "react";
import {
  X,
  FolderGit2,
  GitBranch,
  MessageSquare,
  Upload,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Sparkles,
  FileCode2
} from "lucide-react";
import { IngestRepoOptions } from "@/lib/api";

interface IngestModalProps {
  isOpen: boolean;
  onClose: () => void;
  onIngest: (options: IngestRepoOptions) => Promise<void>;
  isIngesting: boolean;
}

export function IngestModal({ isOpen, onClose, onIngest, isIngesting }: IngestModalProps) {
  const [sourceType, setSourceType] = useState<"LOCAL" | "REMOTE">("LOCAL");
  const [repoPath, setRepoPath] = useState<string>(".");
  const [gitUrl, setGitUrl] = useState<string>("");
  const [discussionOption, setDiscussionOption] = useState<"SAMPLE" | "CUSTOM" | "NONE">("SAMPLE");
  const [discussionsRaw, setDiscussionsRaw] = useState<string>("");
  const [uploadedFileName, setUploadedFileName] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadedFileName(file.name);
    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      setDiscussionsRaw(content);
    };
    reader.readAsText(file);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    const options: IngestRepoOptions = {
      repoPath: sourceType === "LOCAL" ? repoPath.trim() : undefined,
      gitUrl: sourceType === "REMOTE" ? gitUrl.trim() : undefined,
      pairSampleDiscussions: discussionOption === "SAMPLE",
      discussionsRaw: discussionOption === "CUSTOM" ? discussionsRaw.trim() : undefined
    };

    if (sourceType === "REMOTE" && !gitUrl.trim()) {
      setErrorMessage("Please enter a valid remote Git URL (e.g. https://github.com/owner/repo.git).");
      return;
    }

    try {
      await onIngest(options);
      onClose();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to ingest codebase and discussion sources.");
      }
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 backdrop-blur-sm p-4 animate-in fade-in duration-150">
      <div className="w-full max-w-xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[92vh]">
        {/* Modal Header */}
        <div className="bg-slate-900 text-white p-4.5 px-6 flex items-center justify-between border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white">
              <FolderGit2 className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
                Multi-Source Ingestion Pipeline
                <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
                  OpenLineage Standard
                </span>
              </h2>
              <p className="text-[11px] text-slate-400">
                Mine real-time Git history, line blame, and pair Slack/Discord conversations
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

        {/* Modal Body Form */}
        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto space-y-5 text-xs flex-1">
          {errorMessage && (
            <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <div className="text-xs leading-relaxed">{errorMessage}</div>
            </div>
          )}

          {/* Section 1: Codebase Repository Source */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                <GitBranch className="w-3.5 h-3.5 text-blue-600" />
                1. Git Repository Source
              </label>
              <div className="flex items-center bg-slate-100 rounded-lg p-0.5 border border-slate-200">
                <button
                  type="button"
                  onClick={() => setSourceType("LOCAL")}
                  className={`px-2.5 py-1 rounded text-[11px] font-semibold transition ${
                    sourceType === "LOCAL"
                      ? "bg-white text-slate-900 shadow-sm"
                      : "text-slate-500 hover:text-slate-900"
                  }`}
                >
                  Local Directory
                </button>
                <button
                  type="button"
                  onClick={() => setSourceType("REMOTE")}
                  className={`px-2.5 py-1 rounded text-[11px] font-semibold transition ${
                    sourceType === "REMOTE"
                      ? "bg-white text-blue-600 shadow-sm"
                      : "text-slate-500 hover:text-slate-900"
                  }`}
                >
                  Remote Git Clone
                </button>
              </div>
            </div>

            {sourceType === "LOCAL" ? (
              <div className="space-y-2">
                <input
                  type="text"
                  value={repoPath}
                  onChange={(e) => setRepoPath(e.target.value)}
                  placeholder="e.g. . (current directory) or E:\Software\MyMicroservice"
                  className="w-full text-xs font-mono px-3 py-2 rounded-lg border border-slate-200 bg-slate-50 focus:bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                />
                <div className="flex items-center gap-2 text-[10px] text-slate-500">
                  <span>Presets:</span>
                  <button
                    type="button"
                    onClick={() => setRepoPath(".")}
                    className="px-2 py-0.5 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-mono transition"
                  >
                    . (Current Project)
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <input
                  type="text"
                  value={gitUrl}
                  onChange={(e) => setGitUrl(e.target.value)}
                  placeholder="https://github.com/pallets/flask.git"
                  className="w-full text-xs font-mono px-3 py-2 rounded-lg border border-slate-200 bg-slate-50 focus:bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                />
                <p className="text-[10px] text-slate-500">
                  Shallow clones `--depth 25` into a secure isolated sandbox to extract author blame and commit graph.
                </p>
              </div>
            )}
          </div>

          <hr className="border-slate-100" />

          {/* Section 2: Discussion Traces for NLI Contradiction Radar */}
          <div className="space-y-3">
            <label className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
              <MessageSquare className="w-3.5 h-3.5 text-purple-600" />
              2. Discussion Traces (Enables Epistemic Contradiction Radar)
            </label>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => setDiscussionOption("SAMPLE")}
                className={`p-3 rounded-xl border text-left transition flex flex-col justify-between ${
                  discussionOption === "SAMPLE"
                    ? "bg-purple-50/70 border-purple-400 text-purple-950 font-medium"
                    : "bg-white border-slate-200 text-slate-700 hover:bg-slate-50"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[11px] font-bold">Pair Sample Slack</span>
                  <Sparkles className="w-3.5 h-3.5 text-purple-600" />
                </div>
                <p className="text-[10px] text-slate-500 leading-normal">
                  Pairs engineering Slack sync traces to demonstrate DeBERTa NLI contradiction detection.
                </p>
              </button>

              <button
                type="button"
                onClick={() => setDiscussionOption("CUSTOM")}
                className={`p-3 rounded-xl border text-left transition flex flex-col justify-between ${
                  discussionOption === "CUSTOM"
                    ? "bg-blue-50/70 border-blue-400 text-blue-950 font-medium"
                    : "bg-white border-slate-200 text-slate-700 hover:bg-slate-50"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[11px] font-bold">Upload Slack/Discord</span>
                  <Upload className="w-3.5 h-3.5 text-blue-600" />
                </div>
                <p className="text-[10px] text-slate-500 leading-normal">
                  Drop a standard Slack export `messages.json` or paste channel text logs.
                </p>
              </button>

              <button
                type="button"
                onClick={() => setDiscussionOption("NONE")}
                className={`p-3 rounded-xl border text-left transition flex flex-col justify-between ${
                  discussionOption === "NONE"
                    ? "bg-slate-100 border-slate-400 text-slate-900 font-medium"
                    : "bg-white border-slate-200 text-slate-700 hover:bg-slate-50"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[11px] font-bold">Git Commits Only</span>
                  <FileCode2 className="w-3.5 h-3.5 text-slate-400" />
                </div>
                <p className="text-[10px] text-slate-500 leading-normal">
                  Analyzes code and line authorship without pairing external team discussions.
                </p>
              </button>
            </div>

            {discussionOption === "CUSTOM" && (
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-2 mt-2">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-semibold text-slate-700">Drop messages.json:</span>
                  <label className="cursor-pointer text-xs font-semibold text-blue-600 hover:underline flex items-center gap-1">
                    <Upload className="w-3 h-3" />
                    <span>Choose JSON File</span>
                    <input
                      type="file"
                      accept=".json,.txt"
                      onChange={handleFileUpload}
                      className="hidden"
                    />
                  </label>
                </div>
                {uploadedFileName && (
                  <div className="flex items-center gap-1.5 text-[11px] text-emerald-700 font-medium">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Loaded: {uploadedFileName}</span>
                  </div>
                )}
                <textarea
                  value={discussionsRaw}
                  onChange={(e) => setDiscussionsRaw(e.target.value)}
                  rows={3}
                  placeholder='Paste Slack JSON e.g. [{"text": "...", "user": "..."}] or plain text logs...'
                  className="w-full text-[11px] font-mono p-2 rounded-lg border border-slate-200 bg-white text-slate-800"
                />
              </div>
            )}
          </div>

          {/* Action Footer */}
          <div className="pt-3 border-t border-slate-200 flex items-center justify-end gap-2.5">
            <button
              type="button"
              onClick={onClose}
              disabled={isIngesting}
              className="px-3.5 py-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-100 font-semibold transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isIngesting}
              className="flex items-center gap-2 px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold transition shadow-sm disabled:opacity-50"
            >
              {isIngesting ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Mining Repository Traces...</span>
                </>
              ) : (
                <>
                  <FolderGit2 className="w-3.5 h-3.5" />
                  <span>Synthesize Knowledge Handover</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
