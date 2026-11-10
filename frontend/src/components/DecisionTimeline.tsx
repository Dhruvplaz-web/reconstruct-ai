"use client";

import React, { useState, useMemo } from "react";
import {
  Compass,
  ArrowRight,
  Network,
  List,
  ExternalLink,
  Download,
  Search
} from "lucide-react";
import { DAGGraph, DecisionNode, CommitEvent, DiscussionMessage } from "@/types";
import { API_BASE } from "@/lib/api";
import { DAGVisualizer } from "./DAGVisualizer";

interface TimelineEvent {
  id: string;
  type: "commit" | "discussion" | "decision";
  date: string;
  title: string;
  author: string;
  badge: string;
  citationId?: string;
  hasConflict?: boolean;
  rawTimestamp?: string;
}

const STATIC_EVENTS: TimelineEvent[] = [
  {
    id: "ev-1",
    type: "commit",
    date: "Jan 10, 2026",
    title: "feat(ledger): Double-entry ledger with sorted lock ordering",
    author: "Alice Vance",
    badge: "Git Commit",
    citationId: "cit-commit-a1b2c3d"
  },
  {
    id: "ev-2",
    type: "commit",
    date: "Jan 28, 2026",
    title: "feat(idempotency): Experiment with Redis cluster cache",
    author: "Alice Vance",
    badge: "Git Commit"
  },
  {
    id: "ev-3",
    type: "discussion",
    date: "Feb 12, 2026",
    title: "Architecture sync: Decided 24h Redis TTL for Black Friday spikes",
    author: "Alice Vance",
    badge: "Slack Discussion",
    citationId: "cit-slack-001",
    hasConflict: true
  },
  {
    id: "ev-4",
    type: "commit",
    date: "Feb 18, 2026",
    title: "revert: Rollback Redis; restore PostgreSQL SELECT FOR UPDATE",
    author: "Bob Martin",
    badge: "Git Rollback",
    citationId: "cit-commit-c8f192b",
    hasConflict: true
  },
  {
    id: "ev-5",
    type: "decision",
    date: "Feb 18, 2026",
    title: "DEC-01: PostgreSQL Idempotency Locking over Redis",
    author: "Bob & Alice",
    badge: "Active Decision",
    hasConflict: true
  },
  {
    id: "ev-6",
    type: "commit",
    date: "Feb 22, 2026",
    title: "feat(webhooks): Async dispatcher with exponential jitter backoff",
    author: "Charlie Day",
    badge: "Git Commit"
  },
  {
    id: "ev-7",
    type: "commit",
    date: "Mar 01, 2026",
    title: "security(infra): Configure production payment gateway secrets",
    author: "Alice Vance",
    badge: "Infra Secret"
  }
];

function formatDate(ts?: string): string {
  if (!ts) return "Recent";
  try {
    const d = new Date(ts);
    if (isNaN(d.getTime())) return ts.slice(0, 10);
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  } catch {
    return ts.slice(0, 10);
  }
}

interface DecisionTimelineProps {
  graphData?: DAGGraph | null;
  decisions?: DecisionNode[];
  commits?: CommitEvent[];
  discussions?: DiscussionMessage[];
  onSelectCitation: (citationId: string) => void;
  fullWidthMode?: boolean;
}

export function DecisionTimeline({
  graphData,
  decisions,
  commits,
  discussions,
  onSelectCitation,
  fullWidthMode = false
}: DecisionTimelineProps) {
  const [filter, setFilter] = useState<string>("");
  const [viewMode, setViewMode] = useState<"graph" | "list">(fullWidthMode ? "graph" : "list");

  // Dynamically derive events from live sources if provided, or fallback to default
  const events = useMemo<TimelineEvent[]>(() => {
    const list: TimelineEvent[] = [];

    if (commits && commits.length > 0) {
      commits.forEach((c) => {
        const isRevert =
          c.message.toLowerCase().includes("revert") ||
          c.message.toLowerCase().includes("rollback");
        list.push({
          id: `ev-commit-${c.sha}`,
          type: "commit",
          date: formatDate(c.timestamp),
          title: c.message.split("\n")[0],
          author: c.author,
          badge: isRevert ? "Git Rollback" : "Git Commit",
          citationId: `cit-commit-${c.sha}`,
          hasConflict: isRevert,
          rawTimestamp: c.timestamp
        });
      });
    }

    if (discussions && discussions.length > 0) {
      discussions.forEach((d) => {
        list.push({
          id: `ev-disc-${d.id}`,
          type: "discussion",
          date: formatDate(d.timestamp),
          title: d.text.length > 85 ? d.text.slice(0, 85) + "..." : d.text,
          author: d.author,
          badge: `Slack #${d.channel}`,
          citationId: `cit-${d.id}`,
          rawTimestamp: d.timestamp
        });
      });
    }

    if (decisions && decisions.length > 0) {
      decisions.forEach((dec) => {
        list.push({
          id: `ev-dec-${dec.id}`,
          type: "decision",
          date: formatDate(dec.timestamp),
          title: dec.title,
          author: dec.authors.join(", "),
          badge: dec.status === "ACTIVE" ? "Active Decision" : "Reverted",
          citationId: dec.citations?.[0]?.id,
          hasConflict: dec.has_contradiction || dec.status === "REVERTED",
          rawTimestamp: dec.timestamp
        });
      });
    }

    if (list.length === 0) {
      return STATIC_EVENTS;
    }

    return list.sort((a, b) => {
      const ta = new Date(a.rawTimestamp || 0).getTime();
      const tb = new Date(b.rawTimestamp || 0).getTime();
      return ta - tb;
    });
  }, [commits, discussions, decisions]);

  const filteredEvents = events.filter(
    (e) =>
      e.title.toLowerCase().includes(filter.toLowerCase()) ||
      e.author.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 p-4 sm:p-5 shadow-xs flex flex-col h-full">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2">
            <Compass className="w-5 h-5 text-blue-600" />
            <h2 className="text-sm sm:text-base font-bold text-slate-900 tracking-tight">
              Temporal Decision DAG & Lineage
            </h2>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
              W3C PROV-DM
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Ingested provenance DAG connecting Git rollbacks, Slack architectural debates, and ADRs.
          </p>
        </div>

        {/* View Toggle */}
        <div className="flex items-center bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs shrink-0">
          <button
            onClick={() => setViewMode("graph")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition text-xs font-semibold ${
              viewMode === "graph"
                ? "bg-white text-blue-600 shadow-xs"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <Network className="w-3.5 h-3.5" />
            <span>Interactive Graph</span>
          </button>
          <button
            onClick={() => setViewMode("list")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition text-xs font-semibold ${
              viewMode === "list"
                ? "bg-white text-slate-900 shadow-xs"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <List className="w-3.5 h-3.5" />
            <span>Timeline List ({filteredEvents.length})</span>
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      {viewMode === "graph" && graphData ? (
        <div className="pt-3">
          <DAGVisualizer
            nodes={graphData.nodes}
            edges={graphData.edges}
            onSelectCitation={onSelectCitation}
            heightClass={fullWidthMode ? "h-[640px]" : "h-[540px]"}
          />
        </div>
      ) : (
        <div className="flex-1 flex flex-col pt-3">
          {/* Filter search */}
          <div className="relative pb-3">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              placeholder="Search timeline events by keyword, author, or technology (e.g. redis, alice)..."
              className="w-full text-xs pl-8 pr-3 py-2 rounded-lg border border-slate-200 bg-slate-50 focus:bg-white focus:border-blue-500 text-slate-800 placeholder-slate-400 transition"
            />
          </div>

          {/* Timeline item list */}
          <div className="space-y-3 overflow-y-auto pr-1 flex-1 max-h-[640px]">
            {filteredEvents.map((event) => (
              <div
                key={event.id}
                onClick={() => event.citationId && onSelectCitation(event.citationId)}
                className={`p-3.5 rounded-xl border text-xs transition cursor-pointer ${
                  event.hasConflict
                    ? "border-amber-200 bg-amber-50/50 hover:bg-amber-50 hover:border-amber-300"
                    : "border-slate-100 bg-slate-50/70 hover:bg-white hover:border-slate-300 hover:shadow-xs"
                }`}
              >
                <div className="flex items-center justify-between gap-1 mb-1.5">
                  <span className="text-[11px] text-slate-500 font-mono tabular-nums">
                    {event.date}
                  </span>
                  <span
                    className={`text-[9px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                      event.badge === "Git Rollback" || event.badge === "Reverted"
                        ? "bg-rose-100 text-rose-800 font-extrabold"
                        : event.badge === "Active Decision"
                        ? "bg-blue-100 text-blue-800 font-extrabold"
                        : event.badge.includes("Slack")
                        ? "bg-purple-100 text-purple-800"
                        : "bg-slate-200 text-slate-800"
                    }`}
                  >
                    {event.badge}
                  </span>
                </div>

                <p className="font-semibold text-slate-900 leading-snug text-xs sm:text-[13px]">
                  {event.title}
                </p>

                <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-200/60 text-[11px] text-slate-500">
                  <span>
                    Author: <strong className="text-slate-800">{event.author}</strong>
                  </span>
                  {event.citationId && (
                    <span className="text-blue-600 font-semibold flex items-center gap-1 hover:underline">
                      Inspect Grounded Diff <ArrowRight className="w-3 h-3" />
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Export W3C & ADR footer */}
      <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-400">
        <div className="flex items-center gap-4">
          <a
            href={`${API_BASE}/export/w3c-prov`}
            target="_blank"
            rel="noreferrer"
            className="text-blue-600 font-semibold hover:underline flex items-center gap-1"
          >
            <Download className="w-3 h-3" /> Export W3C PROV-JSON
          </a>
          <a
            href={`${API_BASE}/export/adr`}
            target="_blank"
            rel="noreferrer"
            className="text-slate-700 font-semibold hover:underline flex items-center gap-1"
          >
            <ExternalLink className="w-3 h-3" /> Export Architecture ADRs
          </a>
        </div>
        <span className="text-[11px] text-slate-400">
          W3C PROV-DM 2.0 Compliant
        </span>
      </div>
    </div>
  );
}
