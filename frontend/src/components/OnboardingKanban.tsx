"use client";

import React, { useState, useEffect } from "react";
import {
  CheckSquare,
  Square,
  Calendar,
  FileCode,
  Link2
} from "lucide-react";
import { KanbanTask } from "@/types";

interface OnboardingKanbanProps {
  tasks: KanbanTask[];
  onSelectCitation: (citationId: string) => void;
  fullWidthMode?: boolean;
}

export function OnboardingKanban({
  tasks: initialTasks,
  onSelectCitation,
  fullWidthMode = false
}: OnboardingKanbanProps) {
  const [tasks, setTasks] = useState<KanbanTask[]>(initialTasks);
  const [activeTab, setActiveTab] = useState<"ALL" | "DAY_1" | "DAY_7" | "DAY_30">("ALL");

  useEffect(() => {
    setTasks(initialTasks);
  }, [initialTasks]);

  const toggleTask = (taskId: string) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, completed: !t.completed } : t))
    );
  };

  const filteredTasks = tasks.filter((t) => (activeTab === "ALL" ? true : t.stage === activeTab));
  const completedCount = tasks.filter((t) => t.completed).length;
  const progressPercent = tasks.length > 0 ? Math.round((completedCount / tasks.length) * 100) : 0;

  const day1Tasks = tasks.filter((t) => t.stage === "DAY_1");
  const day7Tasks = tasks.filter((t) => t.stage === "DAY_7");
  const day30Tasks = tasks.filter((t) => t.stage === "DAY_30");

  const renderTaskCard = (task: KanbanTask) => (
    <div
      key={task.id}
      className={`p-3.5 rounded-xl border text-xs transition-all ${
        task.completed
          ? "bg-slate-50/80 border-slate-200 opacity-70"
          : "bg-white border-slate-200/90 hover:border-blue-400 hover:shadow-xs"
      }`}
    >
      <div className="flex items-start gap-2.5">
        <button
          onClick={() => toggleTask(task.id)}
          className="mt-0.5 text-slate-400 hover:text-blue-600 transition shrink-0"
        >
          {task.completed ? (
            <CheckSquare className="w-4 h-4 text-emerald-600" />
          ) : (
            <Square className="w-4 h-4" />
          )}
        </button>

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-1 mb-1">
            <span
              className={`text-[9px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                task.stage === "DAY_1"
                  ? "bg-rose-100 text-rose-800"
                  : task.stage === "DAY_7"
                  ? "bg-amber-100 text-amber-800"
                  : "bg-blue-100 text-blue-800"
              }`}
            >
              {task.stage.replace("_", " ")}
            </span>

            <div className="flex items-center gap-1.5">
              {task.category && (
                <span className="text-[9px] font-semibold text-slate-400 uppercase">
                  {task.category.replace("_", " ")}
                </span>
              )}
              <span
                className={`text-[9px] font-bold px-1.5 py-0.5 rounded uppercase ${
                  task.priority === "URGENT"
                    ? "bg-red-50 text-red-700 border border-red-200 font-extrabold"
                    : task.priority === "HIGH"
                    ? "bg-amber-50 text-amber-700 border border-amber-200"
                    : "bg-slate-100 text-slate-600"
                }`}
              >
                {task.priority}
              </span>
            </div>
          </div>

          <p
            className={`font-semibold leading-snug text-xs sm:text-[13px] ${
              task.completed ? "line-through text-slate-400" : "text-slate-900"
            }`}
          >
            {task.title}
          </p>

          <p className="text-xs text-slate-600 mt-1 leading-relaxed">{task.description}</p>

          {/* Linked File / PR citation */}
          <div className="flex flex-wrap items-center justify-between gap-2 mt-2.5 pt-2 border-t border-slate-100 text-[11px]">
            {task.linked_file ? (
              <span className="flex items-center gap-1 font-mono text-slate-600 bg-slate-100 px-2 py-0.5 rounded text-[10px] truncate max-w-[200px]">
                <FileCode className="w-3 h-3 text-slate-400 shrink-0" />
                {task.linked_file}
              </span>
            ) : (
              <span />
            )}
            {task.citation_id && (
              <button
                onClick={() => onSelectCitation(task.citation_id!)}
                className="text-blue-600 font-semibold hover:underline inline-flex items-center gap-1"
              >
                <Link2 className="w-3 h-3" />
                <span>Inspect Trace &rarr;</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 p-4 sm:p-5 shadow-xs flex flex-col h-full">
      {/* Header with Progress bar */}
      <div className="pb-3 border-b border-slate-100">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
          <div>
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-emerald-600" />
              <h2 className="text-sm sm:text-base font-bold text-slate-900 tracking-tight">
                Day 1–30 Onboarding Roadmap
              </h2>
            </div>
            <p className="text-xs text-slate-500">
              Role-tailored successor action items derived from Bus Factor risks and ADR contracts
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 tabular-nums">
              {completedCount} of {tasks.length} Done ({progressPercent}%)
            </span>
          </div>
        </div>

        {/* Progress bar */}
        <div className="w-full bg-slate-100 rounded-full h-2 mt-2 overflow-hidden">
          <div
            className="bg-emerald-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {fullWidthMode ? (
        /* 3-Column Kanban Board for dedicated view */
        <div className="pt-4 grid grid-cols-1 md:grid-cols-3 gap-4 flex-1">
          {/* Column 1: Day 1 (Immediate Setup) */}
          <div className="bg-slate-50/70 p-3.5 rounded-xl border border-slate-200 flex flex-col">
            <div className="flex items-center justify-between pb-2.5 mb-3 border-b border-slate-200">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Day 1: Setup & Auth
                </h3>
              </div>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-100 text-rose-800">
                {day1Tasks.filter((t) => t.completed).length}/{day1Tasks.length}
              </span>
            </div>
            <div className="space-y-3 flex-1 overflow-y-auto">
              {day1Tasks.map((t) => renderTaskCard(t))}
            </div>
          </div>

          {/* Column 2: Day 7 (Architecture & High-Risk Files) */}
          <div className="bg-slate-50/70 p-3.5 rounded-xl border border-slate-200 flex flex-col">
            <div className="flex items-center justify-between pb-2.5 mb-3 border-b border-slate-200">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Day 7: Architecture
                </h3>
              </div>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-800">
                {day7Tasks.filter((t) => t.completed).length}/{day7Tasks.length}
              </span>
            </div>
            <div className="space-y-3 flex-1 overflow-y-auto">
              {day7Tasks.map((t) => renderTaskCard(t))}
            </div>
          </div>

          {/* Column 3: Day 30 (Feature Ownership) */}
          <div className="bg-slate-50/70 p-3.5 rounded-xl border border-slate-200 flex flex-col">
            <div className="flex items-center justify-between pb-2.5 mb-3 border-b border-slate-200">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-500" />
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Day 30: Feature Ownership
                </h3>
              </div>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-800">
                {day30Tasks.filter((t) => t.completed).length}/{day30Tasks.length}
              </span>
            </div>
            <div className="space-y-3 flex-1 overflow-y-auto">
              {day30Tasks.map((t) => renderTaskCard(t))}
            </div>
          </div>
        </div>
      ) : (
        /* Filterable list for column/split view */
        <div className="flex-1 flex flex-col pt-3">
          {/* Stage Filter Tabs */}
          <div className="flex items-center gap-1.5 pb-3 border-b border-slate-100 text-xs">
            {(["ALL", "DAY_1", "DAY_7", "DAY_30"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-2.5 py-1 rounded-md text-xs font-semibold transition ${
                  activeTab === tab
                    ? "bg-slate-900 text-white shadow-xs"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {tab === "ALL"
                  ? `All (${tasks.length})`
                  : tab === "DAY_1"
                  ? `Day 1 (${day1Tasks.length})`
                  : tab === "DAY_7"
                  ? `Day 7 (${day7Tasks.length})`
                  : `Day 30 (${day30Tasks.length})`}
              </button>
            ))}
          </div>

          {/* Task Cards list */}
          <div className="space-y-3 overflow-y-auto pr-1 flex-1 pt-3 max-h-[640px]">
            {filteredTasks.map((task) => renderTaskCard(task))}
          </div>
        </div>
      )}
    </div>
  );
}
