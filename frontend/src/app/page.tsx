"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Header } from "@/components/Header";
import { MetricsRibbon } from "@/components/MetricsRibbon";
import { NavigationTabs, TabId } from "@/components/NavigationTabs";
import { DecisionTimeline } from "@/components/DecisionTimeline";
import { ExecutiveBriefing } from "@/components/ExecutiveBriefing";
import { OnboardingKanban } from "@/components/OnboardingKanban";
import { RiskRadarView } from "@/components/RiskRadarView";
import { AuditVaultView } from "@/components/AuditVaultView";
import { CitationDrawer } from "@/components/CitationDrawer";
import { LeaverReviewModal } from "@/components/LeaverReviewModal";
import { IngestModal } from "@/components/IngestModal";
import {
  fetchWorkspace,
  fetchQuestions,
  submitReview,
  resetSyntheticPlayground,
  fetchGraph,
  ingestLiveSources,
  IngestRepoOptions
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
  const [activeTab, setActiveTab] = useState<TabId>("overview");
  const [workspace, setWorkspace] = useState<HandoverWorkspace | null>(null);
  const [questions, setQuestions] = useState<LeaverQuestion[]>([]);
  const [graphData, setGraphData] = useState<DAGGraph | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedCitation, setSelectedCitation] = useState<CitationSource | null>(null);
  const [isLeaverModalOpen, setIsLeaverModalOpen] = useState<boolean>(false);
  const [isIngestModalOpen, setIsIngestModalOpen] = useState<boolean>(false);
  const [isResetting, setIsResetting] = useState<boolean>(false);
  const [isAnalyzingLive, setIsAnalyzingLive] = useState<boolean>(false);
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

    // 1. Search in decisions
    for (const dec of workspace.decisions) {
      const match = dec.citations.find((c) => c.id === citationId);
      if (match) {
        foundCit = match;
        break;
      }
    }

    // 2. Search in contradictions
    if (!foundCit) {
      for (const contra of workspace.contradictions) {
        if (contra.source_a.id === citationId) foundCit = contra.source_a;
        if (contra.source_b.id === citationId) foundCit = contra.source_b;
      }
    }

    // 3. Search in commits
    if (!foundCit && workspace.commits) {
      const commitSha = citationId.replace("cit-commit-", "").replace("commit:", "");
      const matchedCommit = workspace.commits.find((c) => c.sha.startsWith(commitSha) || commitSha.startsWith(c.sha));
      if (matchedCommit) {
        foundCit = {
          id: citationId,
          source_type: "commit",
          uri: `git://repo/commits/${matchedCommit.sha}`,
          title: `Commit: ${matchedCommit.message.split("\n")[0]}`,
          timestamp: matchedCommit.timestamp,
          author: matchedCommit.author,
          snippet: matchedCommit.diff_snippet || matchedCommit.message,
          security_tag: matchedCommit.security_tag
        };
      }
    }

    // 4. Search in discussions
    if (!foundCit && workspace.discussions) {
      const discId = citationId.replace("cit-", "").replace("disc:", "");
      const matchedDisc = workspace.discussions.find((d) => d.id === discId);
      if (matchedDisc) {
        foundCit = {
          id: citationId,
          source_type: "discussion",
          uri: `slack://channel/${matchedDisc.channel}/${matchedDisc.id}`,
          title: `Discussion #${matchedDisc.channel}`,
          timestamp: matchedDisc.timestamp,
          author: matchedDisc.author,
          snippet: matchedDisc.text,
          security_tag: matchedDisc.security_tag
        };
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

  // Handle Multi-Source Ingestion
  const handleIngestSources = async (options: IngestRepoOptions) => {
    setIsAnalyzingLive(true);
    try {
      await ingestLiveSources(options);
      await loadData(role);
    } finally {
      setIsAnalyzingLive(false);
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
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans selection:bg-blue-100 selection:text-blue-900">
      <Header
        role={role}
        onRoleChange={setRole}
        onOpenLeaverModal={() => setIsLeaverModalOpen(true)}
        onOpenIngestModal={() => setIsIngestModalOpen(true)}
        onResetPlayground={handleResetPlayground}
        isResetting={isResetting}
        isAnalyzingLive={isAnalyzingLive}
        leaverApproved={leaverApproved}
        signature={signature}
        projectName={workspace?.project_name}
        leaverName={workspace?.leaver_name}
      />

      <main className="flex-1 p-4 md:p-6 lg:p-8 max-w-7xl w-full mx-auto">
        {loading || !workspace ? (
          <div className="flex flex-col items-center justify-center min-h-[500px] text-slate-500 gap-3">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            <p className="text-xs font-semibold tracking-wide">
              Synthesizing project handover traces & DAG lineage...
            </p>
          </div>
        ) : (
          <div>
            {/* Top Metrics Ribbon */}
            <MetricsRibbon
              workspace={workspace}
              role={role}
              leaverApproved={leaverApproved}
              signature={signature}
              onOpenLeaverModal={() => setIsLeaverModalOpen(true)}
              onTabSelect={(tab) => setActiveTab(tab as TabId)}
            />

            {/* Navigation Workspace Switcher */}
            <NavigationTabs
              activeTab={activeTab}
              onTabChange={setActiveTab}
              badgeCounts={{
                risks: (workspace.orphan_risk_files?.length || 0) + (workspace.contradictions?.length || 0),
                tasksRemaining: workspace.kanban_tasks?.filter((t) => !t.completed).length,
                decisions: workspace.decisions?.length
              }}
            />

            {/* TAB VIEW 1: EXECUTIVE OVERVIEW */}
            {activeTab === "overview" && (
              <ExecutiveBriefing
                workspace={workspace}
                onSelectCitation={handleSelectCitation}
                onOpenLeaverModal={() => setIsLeaverModalOpen(true)}
                onTabSelect={(tab) => setActiveTab(tab as TabId)}
              />
            )}

            {/* TAB VIEW 2: DECISION DAG & LINEAGE */}
            {activeTab === "dag" && (
              <DecisionTimeline
                graphData={graphData}
                decisions={workspace.decisions}
                commits={workspace.commits}
                discussions={workspace.discussions}
                onSelectCitation={handleSelectCitation}
                fullWidthMode={true}
              />
            )}

            {/* TAB VIEW 3: BUS FACTOR & CONTRADICTION RADAR */}
            {activeTab === "risks" && (
              <RiskRadarView
                workspace={workspace}
                onSelectCitation={handleSelectCitation}
                onOpenLeaverModal={() => setIsLeaverModalOpen(true)}
              />
            )}

            {/* TAB VIEW 4: ONBOARDING ROADMAP (3-COLUMN KANBAN) */}
            {activeTab === "onboarding" && (
              <OnboardingKanban
                key={workspace.project_name}
                tasks={workspace.kanban_tasks}
                onSelectCitation={handleSelectCitation}
                fullWidthMode={true}
              />
            )}

            {/* TAB VIEW 5: AUDIT VAULT & TRACES */}
            {activeTab === "audit" && (
              <AuditVaultView
                workspace={workspace}
                role={role}
                onRoleChange={setRole}
                signature={signature}
                leaverApproved={leaverApproved}
                onSelectCitation={handleSelectCitation}
                onOpenLeaverModal={() => setIsLeaverModalOpen(true)}
              />
            )}

            {/* TAB VIEW 6: CLASSIC MULTI-PANEL SPLIT VIEW */}
            {activeTab === "split" && (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
                <div className="lg:col-span-4 h-full">
                  <DecisionTimeline
                    graphData={graphData}
                    decisions={workspace.decisions}
                    commits={workspace.commits}
                    discussions={workspace.discussions}
                    onSelectCitation={handleSelectCitation}
                    fullWidthMode={false}
                  />
                </div>
                <div className="lg:col-span-4 h-full">
                  <ExecutiveBriefing
                    workspace={workspace}
                    onSelectCitation={handleSelectCitation}
                    onOpenLeaverModal={() => setIsLeaverModalOpen(true)}
                    onTabSelect={(tab) => setActiveTab(tab as TabId)}
                  />
                </div>
                <div className="lg:col-span-4 h-full">
                  <OnboardingKanban
                    key={`split-${workspace.project_name}`}
                    tasks={workspace.kanban_tasks}
                    onSelectCitation={handleSelectCitation}
                    fullWidthMode={false}
                  />
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* NotebookLM Citation Sidecar Drawer */}
      <CitationDrawer
        citation={selectedCitation}
        onClose={() => setSelectedCitation(null)}
      />

      {/* Multi-Source Ingestion Pipeline Modal */}
      <IngestModal
        isOpen={isIngestModalOpen}
        onClose={() => setIsIngestModalOpen(false)}
        onIngest={handleIngestSources}
        isIngesting={isAnalyzingLive}
      />

      {/* 60-Second Leaver Review Modal */}
      <LeaverReviewModal
        isOpen={isLeaverModalOpen}
        onClose={() => setIsLeaverModalOpen(false)}
        questions={questions}
        onSubmitReview={handleSubmitReview}
        isSubmitting={isSubmittingReview}
        leaverName={workspace?.leaver_name}
      />
    </div>
  );
}
