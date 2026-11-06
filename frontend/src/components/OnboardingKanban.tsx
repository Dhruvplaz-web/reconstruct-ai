"use client";

import React, { useState, useEffect } from "react";
import { CheckSquare, Square, Calendar, FileCode } from "lucide-react";
import { KanbanTask } from "@/types";

interface OnboardingKanbanProps {
  tasks: KanbanTask[];
  onSelectCitation: (citationId: string) => void;
}

export function OnboardingKanban({ tasks: initialTasks, onSelectCitation }: OnboardingKanbanProps) {
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

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex flex-col h-full">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div>
          <h2 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-1.5">
            <Calendar className="w-4 h-4 text-blue-600" />
            Day 1–30 Onboarding Kanban
          </h2>
          <p className="text-[11px] text-slate-500">Actionable successor roadmap</p>
        </div>
        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 tabular-nums">
          {completedCount}/{tasks.length} done
        </span>
      </div>

      {/* Stage Filter Tabs */}
      <div className="flex items-center gap-1 py-2.5 border-b border-slate-100 text-xs">
        {(["ALL", "DAY_1", "DAY_7", "DAY_30"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-2 py-1 rounded text-[11px] font-medium transition ${
              activeTab === tab
                ? "bg-slate-900 text-white font-bold"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            {tab === "ALL" ? "All" : tab === "DAY_1" ? "Day 1" : tab === "DAY_7" ? "Day 7" : "Day 30"}
          </button>
        ))}
      </div>

      {/* Task Cards */}
      <div className="space-y-2.5 overflow-y-auto pr-1 flex-1 pt-3 max-h-[720px]">
        {filteredTasks.map((task) => (
          <div
            key={task.id}
            className={`p-3 rounded-lg border text-xs transition ${
              task.completed
                ? "bg-slate-50 border-slate-200 opacity-60"
                : "bg-white border-slate-200 hover:border-slate-300 shadow-sm"
            }`}
          >
            <div className="flex items-start gap-2">
              <button
                onClick={() => toggleTask(task.id)}
                className="mt-0.5 text-slate-400 hover:text-blue-600 transition"
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
                    className={`text-[9px] font-bold px-1.5 py-0.2 rounded uppercase ${
                      task.stage === "DAY_1"
                        ? "bg-rose-100 text-rose-700"
                        : task.stage === "DAY_7"
                        ? "bg-amber-100 text-amber-700"
                        : "bg-blue-100 text-blue-700"
                    }`}
                  >
                    {task.stage.replace("_", " ")}
                  </span>

                  <span
                    className={`text-[9px] font-semibold px-1.5 py-0.2 rounded uppercase ${
                      task.priority === "URGENT"
                        ? "bg-red-50 text-red-600 border border-red-200"
                        : "bg-slate-100 text-slate-600"
                    }`}
                  >
                    {task.priority}
                  </span>
                </div>

                <p
                  className={`font-semibold leading-snug ${
                    task.completed ? "line-through text-slate-400" : "text-slate-900"
                  }`}
                >
                  {task.title}
                </p>

                <p className="text-[11px] text-slate-500 mt-1 leading-normal">{task.description}</p>

                {/* Linked File / PR badge */}
                <div className="flex flex-wrap items-center gap-1.5 mt-2 pt-1.5 border-t border-slate-100 text-[10px]">
                  {task.linked_file && (
                    <span className="flex items-center gap-1 font-mono text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded">
                      <FileCode className="w-3 h-3 text-slate-400" />
                      {task.linked_file}
                    </span>
                  )}
                  {task.citation_id && (
                    <button
                      onClick={() => onSelectCitation(task.citation_id!)}
                      className="text-blue-600 font-medium hover:underline ml-auto"
                    >
                      Inspect Diff &rarr;
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
