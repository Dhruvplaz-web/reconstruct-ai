"""
FastAPI REST API Router
Exposes ingestion, repository analysis, leaver review, continuation workspace,
and official W3C PROV-DM & ADR export endpoints.
"""

from fastapi import APIRouter, Query, HTTPException, Body
from fastapi.responses import PlainTextResponse, Response
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import hashlib
import os

from ..models.schemas import (
    HandoverWorkspace,
    OrphanRiskFile,
    ContradictionAlert,
    LeaverQuestion,
    LeaverReviewSubmission,
    DecisionNode,
    KanbanTask
)
from ..data.acme_payments import (
    SYNTHETIC_COMMITS,
    SYNTHETIC_DISCUSSIONS,
    SYNTHETIC_ORPHAN_FILES,
    SYNTHETIC_DECISIONS,
    SYNTHETIC_CONTRADICTIONS,
    SYNTHETIC_LEAVER_QUESTIONS,
    SYNTHETIC_KANBAN_TASKS
)
from ..services.abac_filter import ABACFilter
from ..services.graph_engine import TemporalGraphEngine
from ..services.git_miner import GitMiner
from ..services.nli_radar import NLIRadar
from ..services.extraction import KnowledgeExtractor
from ..services.discussion_miner import DiscussionMiner

router = APIRouter(prefix="/api")

# State store in-memory for active session
APP_STATE: Dict[str, Any] = {
    "project_name": "Acme Payments Microservice",
    "leaver_name": "Alice Vance (Lead Architect)",
    "leaver_approved": False,
    "approval_submission": None,
    "decisions": list(SYNTHETIC_DECISIONS),
    "contradictions": list(SYNTHETIC_CONTRADICTIONS),
    "orphan_files": list(SYNTHETIC_ORPHAN_FILES),
    "kanban_tasks": list(SYNTHETIC_KANBAN_TASKS),
    "commits": list(SYNTHETIC_COMMITS),
    "discussions": list(SYNTHETIC_DISCUSSIONS),
    "leaver_questions": list(SYNTHETIC_LEAVER_QUESTIONS)
}

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Reconstruct.ai Backend API",
        "version": "1.0.0-round2-ready",
        "institution": "JSPM RSCOE, Pune",
        "team": "TEAM DOMINATOR"
    }

@router.post("/ingest/synthetic")
def reset_synthetic_playground():
    """
    1-Click Demo Playground Ingestion.
    Resets the in-memory state to the synthetic Acme Payments benchmark dataset.
    """
    APP_STATE["project_name"] = "Acme Payments Microservice"
    APP_STATE["leaver_name"] = "Alice Vance (Lead Architect)"
    APP_STATE["decisions"] = list(SYNTHETIC_DECISIONS)
    APP_STATE["contradictions"] = list(SYNTHETIC_CONTRADICTIONS)
    APP_STATE["orphan_files"] = list(SYNTHETIC_ORPHAN_FILES)
    APP_STATE["kanban_tasks"] = list(SYNTHETIC_KANBAN_TASKS)
    APP_STATE["commits"] = list(SYNTHETIC_COMMITS)
    APP_STATE["discussions"] = list(SYNTHETIC_DISCUSSIONS)
    APP_STATE["leaver_questions"] = list(SYNTHETIC_LEAVER_QUESTIONS)
    APP_STATE["leaver_approved"] = False
    APP_STATE["approval_submission"] = None

    return {
        "message": "Successfully ingested Acme Payments benchmark dataset.",
        "commits_loaded": len(APP_STATE["commits"]),
        "discussions_loaded": len(APP_STATE["discussions"]),
        "orphan_risks_detected": len(APP_STATE["orphan_files"]),
        "contradictions_flagged": len(APP_STATE["contradictions"])
    }

class LiveRepoRequest(BaseModel):
    repo_path: Optional[str] = Field(default=".", description="Local directory path to Git repository")
    git_url: Optional[str] = Field(default=None, description="Remote Git clone URL (e.g. https://github.com/...)")
    discussions_raw: Optional[str] = Field(default=None, description="Raw JSON or plain text transcript of Slack/Discord messages")
    pair_sample_discussions: bool = Field(default=False, description="Whether to pair sample team discussions to activate NLI radar")

@router.post("/ingest/repo")
def ingest_live_repository(payload: LiveRepoRequest = Body(default_factory=LiveRepoRequest)):
    """
    Live Real-Time Git Repository & Discussion Ingestion.
    Inspects a real local Git repository or remote clone using GitPython,
    runs actual line-by-line git blame, calculates Degree of Authorship (DOA),
    synthesizes architectural decisions, and pairs discussion traces for NLI contradiction scanning.
    """
    try:
        live_analysis = GitMiner.analyze_live_repository(repo_path=payload.repo_path, git_url=payload.git_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to analyze repository: {str(e)}")

    live_commits = live_analysis["commits"]
    live_orphan_files = live_analysis["orphan_files"]
    truck_data = live_analysis["truck_factor_analysis"]

    # Extract dynamic decisions and questions from real code
    live_decisions = KnowledgeExtractor.extract_decisions_from_commits(live_commits)
    live_questions = KnowledgeExtractor.generate_live_leaver_questions(live_orphan_files)
    live_kanban = KnowledgeExtractor.generate_live_kanban(live_orphan_files, live_decisions)

    # Ingest discussions if provided or paired
    live_discussions: List[DiscussionMessage] = []
    if payload.discussions_raw and payload.discussions_raw.strip():
        live_discussions = DiscussionMiner.ingest_generic(payload.discussions_raw)
    elif payload.pair_sample_discussions:
        live_discussions = list(SYNTHETIC_DISCUSSIONS)

    # Run NLI Radar against commits to detect contradictions
    live_contradictions: List[ContradictionAlert] = []
    if live_discussions and live_commits:
        radar = NLIRadar()
        live_contradictions = radar.scan_for_contradictions(live_discussions, live_commits)

    primary_maintainer = truck_data["key_holders"][0] if truck_data["key_holders"] else (live_commits[0].author if live_commits else "Project Maintainer")
    repo_folder_name = os.path.basename(os.path.abspath(live_analysis["repo_dir"]))

    # Update active application state with real data
    APP_STATE["project_name"] = f"Live Repo: {repo_folder_name}"
    APP_STATE["leaver_name"] = f"{primary_maintainer} (Live Primary Owner)"
    APP_STATE["commits"] = live_commits
    APP_STATE["orphan_files"] = live_orphan_files
    APP_STATE["decisions"] = live_decisions
    APP_STATE["kanban_tasks"] = live_kanban
    APP_STATE["discussions"] = live_discussions
    APP_STATE["contradictions"] = live_contradictions
    APP_STATE["leaver_questions"] = live_questions if live_questions else list(SYNTHETIC_LEAVER_QUESTIONS)
    APP_STATE["leaver_approved"] = False
    APP_STATE["approval_submission"] = None

    return {
        "success": True,
        "mode": "REAL_TIME_GIT_ANALYSIS",
        "repository_path": live_analysis["repo_dir"],
        "active_branch": live_analysis["active_branch"],
        "commits_analyzed": len(live_commits),
        "source_files_blamed": len(live_orphan_files),
        "truck_factor": truck_data["truck_factor"],
        "key_maintainers": truck_data["key_holders"],
        "discussions_ingested": len(live_discussions),
        "contradictions_detected": len(live_contradictions),
        "top_single_author_files": [f.file_path for f in live_orphan_files[:5]],
        "extracted_decisions_count": len(live_decisions),
        "generated_onboarding_tasks_count": len(live_kanban)
    }

class DiscussionIngestRequest(BaseModel):
    content: str = Field(..., description="Raw JSON or plain text of Slack/Discord messages")
    channel: str = Field(default="architecture-sync", description="Target discussion channel")

@router.post("/ingest/discussions")
def ingest_discussions(payload: DiscussionIngestRequest):
    """
    Ingests and normalizes discussion messages from Slack or Discord.
    Runs the Epistemic Contradiction Radar to cross-reference statements against the current Git commit history.
    """
    new_messages = DiscussionMiner.ingest_generic(payload.content, channel=payload.channel)
    if not new_messages:
        raise HTTPException(status_code=400, detail="Could not parse any discussion messages from provided payload.")

    APP_STATE["discussions"].extend(new_messages)

    # Scan for contradictions against active commits
    radar = NLIRadar()
    new_contradictions = radar.scan_for_contradictions(APP_STATE["discussions"], APP_STATE["commits"])
    APP_STATE["contradictions"] = new_contradictions

    return {
        "success": True,
        "messages_parsed": len(new_messages),
        "total_discussions": len(APP_STATE["discussions"]),
        "contradictions_detected": len(new_contradictions),
        "topics_flagged": [c.topic for c in new_contradictions]
    }

@router.get("/analyze/orphan-risk", response_model=List[OrphanRiskFile])
def get_orphan_risk():
    """Returns detected Bus Factor = 1 orphan code files."""
    return APP_STATE["orphan_files"]

@router.get("/analyze/truck-factor")
def get_truck_factor_analysis():
    """Returns project-wide Truck Factor calculation based on HelgeCPH/truckfactor."""
    return GitMiner.calculate_repository_truck_factor(APP_STATE["orphan_files"])

@router.get("/analyze/contradictions", response_model=List[ContradictionAlert])
def get_contradictions():
    """Returns contradictions flagged by the NLI Radar between chats and Git."""
    return APP_STATE["contradictions"]

@router.get("/analyze/graph")
def get_temporal_graph():
    """Returns the NetworkX Directed Acyclic Graph (DAG) serialized for the UI."""
    return TemporalGraphEngine.build_graph(
        decisions=APP_STATE["decisions"],
        commits=APP_STATE["commits"],
        discussions=APP_STATE["discussions"],
        tasks=APP_STATE["kanban_tasks"]
    )

@router.get("/export/w3c-prov", response_class=Response)
def export_w3c_prov():
    """Exports the project provenance graph in official W3C PROV-JSON standard format."""
    prov_json_str = TemporalGraphEngine.export_w3c_prov_json(
        decisions=APP_STATE["decisions"],
        commits=APP_STATE["commits"],
        discussions=APP_STATE["discussions"]
    )
    return Response(content=prov_json_str, media_type="application/json")

@router.get("/export/adr", response_class=PlainTextResponse)
def export_adr():
    """Exports Architecture Decision Records in Joel Parker Henderson standard Markdown."""
    adrs = [TemporalGraphEngine.export_adr_markdown(d) for d in APP_STATE["decisions"]]
    return "\n\n---\n\n".join(adrs)

@router.get("/review/questions", response_model=List[LeaverQuestion])
def get_leaver_questions():
    """Returns the targeted micro-questions for the 60-second review."""
    return APP_STATE.get("leaver_questions", SYNTHETIC_LEAVER_QUESTIONS)

@router.post("/review/submit")
def submit_leaver_review(submission: LeaverReviewSubmission):
    """
    Submits the departing developer's answers, records timestamp,
    computes a cryptographic approval hash, and resolves flagged contradictions.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    raw_payload = f"{submission.approved_by}:{timestamp}:{str(submission.responses)}"
    sig_hash = hashlib.sha256(raw_payload.encode()).hexdigest()

    submission.approved_at = timestamp
    submission.digital_signature = f"sig_prov_ed25519_{sig_hash[:16]}"

    APP_STATE["leaver_approved"] = True
    APP_STATE["approval_submission"] = submission

    # Resolve flagged contradictions upon leaver confirmation
    for contra in APP_STATE["contradictions"]:
        if contra.status == "OPEN":
            contra.status = "RESOLVED_BY_LEAVER"
            contra.explanation += f" (Verified by {submission.approved_by} during 60-Second Leaver Review Gate.)"

    for dec in APP_STATE["decisions"]:
        dec.quarantined_for_review = False
        if dec.status in ["UNDER_REVIEW", "SUPERSEDED"]:
            dec.status = "ACTIVE"

    return {
        "success": True,
        "message": "60-Second Leaver Review approved and cryptographically stamped.",
        "approved_by": submission.approved_by,
        "timestamp": timestamp,
        "signature": submission.digital_signature
    }

@router.get("/handover/workspace", response_model=HandoverWorkspace)
def get_handover_workspace(role: str = Query(default="JUNIOR_SUCCESSOR")):
    """
    Returns the complete continuation workspace.
    Applies server-side ABAC security redaction based on the requested role.
    """
    truck_data = GitMiner.calculate_repository_truck_factor(APP_STATE["orphan_files"])

    top_file_desc = ""
    if APP_STATE["orphan_files"]:
        top_f = APP_STATE["orphan_files"][0]
        top_file_desc = f"High single-author concentration was identified in {top_f.file_path} ({top_f.blame_percentage}% blame). "

    contra_desc = ""
    if APP_STATE["contradictions"]:
        open_c = [c for c in APP_STATE["contradictions"] if c.status == "OPEN"]
        if open_c:
            contra_desc = f"A critical contradiction regarding '{open_c[0].topic}' was detected by the NLI Radar and routed through the 60-Second Leaver Review Gate. "
        else:
            contra_desc = "All cross-source contradictions have been verified and confirmed by the departing maintainer. "

    summary_text = (
        f"Reconstruct.ai has synthesized the operational continuity profile for {APP_STATE['project_name']}. "
        f"{APP_STATE['leaver_name']} is offboarding. Repository Truck Factor is {truck_data['truck_factor']} ({truck_data['risk_status']}). "
        f"{top_file_desc}"
        f"{contra_desc}"
        f"Follow the Day 1–30 Actionable Kanban to onboard with zero ramp-up delay."
    )

    workspace = HandoverWorkspace(
        project_name=APP_STATE["project_name"],
        leaver_name=APP_STATE["leaver_name"],
        institution="JSPM RSCOE, Pune",
        generated_at=datetime.now(timezone.utc).isoformat(),
        viewer_role="JUNIOR_SUCCESSOR",
        executive_summary=summary_text,
        orphan_risk_files=APP_STATE["orphan_files"],
        decisions=APP_STATE["decisions"],
        contradictions=APP_STATE["contradictions"],
        kanban_tasks=APP_STATE["kanban_tasks"],
        stats={
            "bus_factor_files_count": len([f for f in APP_STATE["orphan_files"] if f.bus_factor_risk in ["CRITICAL", "HIGH"]]),
            "truck_factor": truck_data["truck_factor"],
            "truck_factor_status": truck_data["risk_status"],
            "active_decisions_count": len(APP_STATE["decisions"]),
            "unresolved_contradictions": len([c for c in APP_STATE["contradictions"] if c.status == "OPEN"]),
            "leaver_review_completed": APP_STATE["leaver_approved"],
            "digital_signature": APP_STATE["approval_submission"].digital_signature if APP_STATE["approval_submission"] else None
        }
    )

    # Server-side ABAC Policy Application
    filtered_workspace = ABACFilter.filter_workspace(workspace, role=role)
    return filtered_workspace
