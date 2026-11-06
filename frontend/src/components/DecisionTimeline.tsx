"use client";

import React, { useState } from "react";
import { Compass, ArrowRight } from "lucide-react";

interface TimelineEvent {
  id: string;
  type: "commit" | "discussion" | "decision";
  date: string;
  title: string;
  author: string;
  badge: string;
  citationId?: string;
  hasConflict?: boolean;
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

interface DecisionTimelineProps {
  onSelectCitation: (citationId: string) => void;
}

export function DecisionTimeline({ onSelectCitation }: DecisionTimelineProps) {
  const [filter, setFilter] = useState<string>("");

  const filteredEvents = STATIC_EVENTS.filter((e) =>
    e.title.toLowerCase().includes(filter.toLowerCase()) ||
    e.author.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex flex-col h-full">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div>
          <h2 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-1.5">
            <Compass className="w-4 h-4 text-blue-600" />
            Temporal Decision DAG
          </h2>
          <p className="text-[11px] text-slate-500">Cross-source chronological traces</p>
        </div>
        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 tabular-nums">
          {filteredEvents.length} events
        </span>
      </div>

      {/* Filter search */}
      <div className="pt-3 pb-2">
        <input
          type="text"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Filter timeline (e.g. redis, alice)..."
          className="w-full text-xs px-2.5 py-1.5 rounded-md border border-slate-200 bg-slate-50 focus:bg-white text-slate-800 placeholder-slate-400 transition"
        />
      </div>

      {/* Timeline item list */}
      <div className="space-y-3 overflow-y-auto pr-1 flex-1 max-h-[720px]">
        {filteredEvents.map((event) => (
          <div
            key={event.id}
            onClick={() => event.citationId && onSelectCitation(event.citationId)}
            className={`p-2.5 rounded-lg border text-xs transition cursor-pointer ${
              event.hasConflict
                ? "border-amber-200 bg-amber-50/50 hover:bg-amber-50"
                : "border-slate-100 bg-slate-50/60 hover:bg-slate-100/70"
            }`}
          >
            <div className="flex items-center justify-between gap-1 mb-1">
              <span className="text-[10px] text-slate-400 font-mono tabular-nums">{event.date}</span>
              <span
                className={`text-[9px] font-semibold px-1.5 py-0.2 rounded uppercase tracking-wider ${
                  event.badge === "Git Rollback"
                    ? "bg-rose-100 text-rose-700 font-bold"
                    : event.badge === "Active Decision"
                    ? "bg-blue-100 text-blue-700 font-bold"
                    : event.badge === "Slack Discussion"
                    ? "bg-purple-100 text-purple-700"
                    : "bg-slate-200 text-slate-700"
                }`}
              >
                {event.badge}
              </span>
            </div>

            <p className="font-medium text-slate-800 leading-snug">{event.title}</p>

            <div className="flex items-center justify-between mt-1.5 pt-1.5 border-t border-slate-200/50 text-[11px] text-slate-500">
              <span>Author: <strong className="text-slate-700">{event.author}</strong></span>
              {event.citationId && (
                <span className="text-blue-600 font-medium flex items-center gap-0.5 hover:underline">
                  View Source <ArrowRight className="w-3 h-3" />
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
