"use client";

import React from "react";
import {
  LayoutDashboard,
  Compass,
  AlertOctagon,
  CalendarCheck2,
  ShieldCheck,
  Columns3
} from "lucide-react";

export type TabId = "overview" | "dag" | "risks" | "onboarding" | "audit" | "split";

interface NavigationTabsProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
  badgeCounts: {
    risks?: number;
    tasksRemaining?: number;
    decisions?: number;
  };
}

export function NavigationTabs({
  activeTab,
  onTabChange,
  badgeCounts
}: NavigationTabsProps) {
  const tabs = [
    {
      id: "overview" as TabId,
      label: "Executive Overview",
      icon: LayoutDashboard,
      badge: null
    },
    {
      id: "dag" as TabId,
      label: "Decision DAG & Lineage",
      icon: Compass,
      badge: badgeCounts.decisions ? `${badgeCounts.decisions}` : null,
      badgeColor: "bg-blue-100 text-blue-800"
    },
    {
      id: "risks" as TabId,
      label: "Bus Factor & Radar",
      icon: AlertOctagon,
      badge: badgeCounts.risks ? `${badgeCounts.risks} alerts` : null,
      badgeColor: "bg-amber-100 text-amber-800"
    },
    {
      id: "onboarding" as TabId,
      label: "Onboarding Roadmap",
      icon: CalendarCheck2,
      badge: badgeCounts.tasksRemaining ? `${badgeCounts.tasksRemaining} left` : null,
      badgeColor: "bg-emerald-100 text-emerald-800"
    },
    {
      id: "audit" as TabId,
      label: "Traces & Audit Vault",
      icon: ShieldCheck,
      badge: null
    },
    {
      id: "split" as TabId,
      label: "Multi-Panel View",
      icon: Columns3,
      badge: null
    }
  ];

  return (
    <div className="flex items-center justify-between border-b border-slate-200/90 mb-6 bg-white px-3 sm:px-4 rounded-xl shadow-xs overflow-x-auto">
      <div className="flex items-center gap-1 sm:gap-2 py-2 min-w-max">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all select-none ${
                isActive
                  ? "bg-slate-900 text-white shadow-xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-blue-400" : "text-slate-400"}`} />
              <span>{tab.label}</span>
              {tab.badge && (
                <span
                  className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${
                    isActive ? "bg-white/20 text-white" : tab.badgeColor || "bg-slate-100 text-slate-700"
                  }`}
                >
                  {tab.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

