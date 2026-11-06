"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Header } from "@/components/Header";
import { DecisionTimeline } from "@/components/DecisionTimeline";
import { ExecutiveBriefing } from "@/components/ExecutiveBriefing";
import { OnboardingKanban } from "@/components/OnboardingKanban";
import { CitationDrawer } from "@/components/CitationDrawer";
import { LeaverReviewModal } from "@/components/LeaverReviewModal";
import {
  fetchWorkspace,
  fetchQuestions,
  submitReview,
  resetSyntheticPlayground,
  fetchGraph
} from "@/lib/api";
import {
  HandoverWorkspace,
  CitationSource,
  LeaverQuestion,
  LeaverReviewSubmission,
  DAGGraph
} from "@/types";
import { Loader2 } from "lucide-react";

export default function Home() {
  const [role, setRole] = useState<"JUNIOR_SUCCESSOR" | "ADMIN">("JUNIOR_SUCCESSOR");
  const [workspace, setWorkspace] = useState<HandoverWorkspace | null>(null);
  const [questions, setQuestions] = useState<LeaverQuestion[]>([]);
  const [graphData, setGraphData] = useState<DAGGraph | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedCitation, setSelectedCitation] = useState<CitationSource | null>(null);
  const [isLeaverModalOpen, setIsLeaverModalOpen] = useState<boolean>(false);
  const [isResetting, setIsResetting] = useState<boolean>(false);
  const [isSubmittingReview, setIsSubmittingReview] = useState<boolean>(false);
  const [leaverApproved, setLeaverApproved] = useState<boolean>(false);
  const [signature, setSignature] = useState<string | undefined>(undefined);

  // Load Workspace & Graph data
  const loadData = useCallback(async (currentRole: "JUNIOR_SUCCESSOR" | "ADMIN") => {
    setLoading(true);
    const controller = new AbortController();
    try {
      const [ws, qs, g] = await Promise.all([
        fetchWorkspace(currentRole, controller.signal),
        fetchQuestions(controller.signal),
        fetchGraph(controller.signal)
      ]);
      setWorkspace(ws);
      setQuestions(qs);
      setGraphData(g);
      setLeaverApproved(Boolean(ws.stats?.leaver_review_completed));
      setSignature(ws.stats?.digital_signature);
    } catch (err: unknown) {
      if (err instanceof Error && err.name !== "AbortError") {
        console.error("Error loading workspace:", err);
      }
    } finally {
      setLoading(false);
    }
    return () => controller.abort();
  }, []);

  useEffect(() => {
    loadData(role);
  }, [role, loadData]);

  // Handle Citation Selection
  const handleSelectCitation = (citationId: string) => {
    if (!workspace) return;
    let foundCit: CitationSource | undefined;

    for (const dec of workspace.decisions) {
      const match = dec.citations.find((c) => c.id === citationId);
      if (match) {
        foundCit = match;
        break;
      }
    }

    if (!foundCit) {
      for (const contra of workspace.contradictions) {
        if (contra.source_a.id === citationId) foundCit = contra.source_a;
        if (contra.source_b.id === citationId) foundCit = contra.source_b;
      }
    }

    if (foundCit) {
      setSelectedCitation(foundCit);
    } else {
      setSelectedCitation({
        id: citationId,
        source_type: "commit",
        uri: `git://repo/commits/${citationId.replace("cit-commit-", "")}`,
        title: `Source Record: ${citationId}`,
        timestamp: "2026-02-18T16:45:00Z",
        author: "Acme Contributor",
        snippet: "// Source reference loaded from repository index."
      });
    }
  };

  // Handle 1-Click Playground Reset
  const handleResetPlayground = async () => {
    setIsResetting(true);
    try {
      await resetSyntheticPlayground();
      await loadData(role);
    } finally {
      setIsResetting(false);
    }
  };

  // Handle 60-Second Leaver Review Submit
  const handleSubmitReview = async (submission: LeaverReviewSubmission) => {
    setIsSubmittingReview(true);
    try {
      const res = await submitReview(submission);
      setLeaverApproved(true);
      setSignature(res.signature);
      setIsLeaverModalOpen(false);
      await loadData(role);
    } finally {
      setIsSubmittingReview(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <Header
        role={role}
        onRoleChange={setRole}
        onOpenLeaverModal={() => setIsLeaverModalOpen(true)}
        onResetPlayground={handleResetPlayground}
        isResetting={isResetting}
        leaverApproved={leaverApproved}
        signature={signature}
      />

      <main className="flex-1 p-4 md:p-6 max-w-7xl w-full mx-auto">
        {loading || !workspace ? (
          <div className="flex flex-col items-center justify-center min-h-[500px] text-slate-500 gap-3">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            <p className="text-xs font-semibold">Synthesizing project handover traces...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
            {/* Column 1: Left - Temporal Decision DAG (4 cols on lg) */}
            <div className="lg:col-span-4 h-full">
              <DecisionTimeline
                graphData={graphData}
                onSelectCitation={handleSelectCitation}
              />
            </div>

            {/* Column 2: Center - Executive Briefing & Decisions (4 cols on lg) */}
            <div className="lg:col-span-4 h-full">
              <ExecutiveBriefing
                workspace={workspace}
                onSelectCitation={handleSelectCitation}
                onOpenLeaverModal={() => setIsLeaverModalOpen(true)}
              />
            </div>

            {/* Column 3: Right - Onboarding Kanban (4 cols on lg) */}
            <div className="lg:col-span-4 h-full">
              <OnboardingKanban
                tasks={workspace.kanban_tasks}
                onSelectCitation={handleSelectCitation}
              />
            </div>
          </div>
        )}
      </main>

      {/* NotebookLM Citation Sidecar Drawer */}
      <CitationDrawer
        citation={selectedCitation}
        onClose={() => setSelectedCitation(null)}
      />

      {/* 60-Second Leaver Review Modal */}
      <LeaverReviewModal
        isOpen={isLeaverModalOpen}
        onClose={() => setIsLeaverModalOpen(false)}
        questions={questions}
        onSubmitReview={handleSubmitReview}
        isSubmitting={isSubmittingReview}
      />
    </div>
  );
}
