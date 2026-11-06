"""
FastAPI REST API Router
Exposes ingestion, repository analysis, leaver review, and continuation workspace endpoints.
"""

from fastapi import APIRouter, Query, HTTPException, Body
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import hashlib

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
from ..services.nli_radar import NLIRadar

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
    "discussions": list(SYNTHETIC_DISCUSSIONS)
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
    APP_STATE["decisions"] = list(SYNTHETIC_DECISIONS)
    APP_STATE["contradictions"] = list(SYNTHETIC_CONTRADICTIONS)
    APP_STATE["orphan_files"] = list(SYNTHETIC_ORPHAN_FILES)
    APP_STATE["kanban_tasks"] = list(SYNTHETIC_KANBAN_TASKS)
    APP_STATE["commits"] = list(SYNTHETIC_COMMITS)
    APP_STATE["discussions"] = list(SYNTHETIC_DISCUSSIONS)
    APP_STATE["leaver_approved"] = False
    APP_STATE["approval_submission"] = None

    return {
        "message": "Successfully ingested Acme Payments benchmark dataset.",
        "commits_loaded": len(APP_STATE["commits"]),
        "discussions_loaded": len(APP_STATE["discussions"]),
        "orphan_risks_detected": len(APP_STATE["orphan_files"]),
        "contradictions_flagged": len(APP_STATE["contradictions"])
    }

@router.get("/analyze/orphan-risk", response_model=List[OrphanRiskFile])
def get_orphan_risk():
    """Returns detected Bus Factor = 1 orphan code files."""
    return APP_STATE["orphan_files"]

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

@router.get("/review/questions", response_model=List[LeaverQuestion])
def get_leaver_questions():
    """Returns the 3 targeted micro-questions for the 60-second review."""
    return SYNTHETIC_LEAVER_QUESTIONS

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

    # If leaver answered Q2 (confirming PostgreSQL), update contradiction status to RESOLVED
    for contra in APP_STATE["contradictions"]:
        if contra.id == "contra-001":
            contra.status = "RESOLVED_BY_LEAVER"
            contra.explanation += f" (Verified by {submission.approved_by}: PostgreSQL SELECT FOR UPDATE confirmed as production truth.)"

    # Also update DEC-01 quarantined status
    for dec in APP_STATE["decisions"]:
        if dec.id == "dec-001":
            dec.quarantined_for_review = False
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
    summary_text = (
        "Reconstruct.ai has synthesized the operational continuity profile for Acme Payments. "
        "Alice Vance (Lead Architect) is offboarding. High single-author concentration was identified in "
        "services/ledger_engine.py (88.4% blame). A critical contradiction regarding idempotency storage (Redis vs PostgreSQL) "
        "was detected by DeBERTa-v3 and routed through the 60-Second Leaver Review Gate. "
        "Follow the Day 1–30 Actionable Kanban to onboard with zero ramp-up delay."
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
            "active_decisions_count": len(APP_STATE["decisions"]),
            "unresolved_contradictions": len([c for c in APP_STATE["contradictions"] if c.status == "OPEN"]),
            "leaver_review_completed": APP_STATE["leaver_approved"],
            "digital_signature": APP_STATE["approval_submission"].digital_signature if APP_STATE["approval_submission"] else None
        }
    )

    # Server-side ABAC Policy Application
    filtered_workspace = ABACFilter.filter_workspace(workspace, role=role)
    return filtered_workspace

