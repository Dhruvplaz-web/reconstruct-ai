"""
Automated PyTest Test Suite for Reconstruct.ai Backend
Direct, high-speed verification of Git Blame Miner, NLIRadar, ABAC Security,
NetworkX Graph Engine, and FastAPI API routes.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from backend.app.services.git_miner import GitMiner
from backend.app.services.nli_radar import NLIRadar
from backend.app.services.abac_filter import ABACFilter
from backend.app.services.graph_engine import TemporalGraphEngine
from backend.app.api.router import (
    health_check,
    reset_synthetic_playground,
    get_orphan_risk,
    get_contradictions,
    get_temporal_graph,
    get_leaver_questions,
    submit_leaver_review,
    get_handover_workspace
)
from backend.app.models.schemas import LeaverReviewSubmission
from backend.app.data.acme_payments import (
    SYNTHETIC_DECISIONS, SYNTHETIC_COMMITS, SYNTHETIC_DISCUSSIONS, SYNTHETIC_KANBAN_TASKS
)

def test_health():
    res = health_check()
    assert res["status"] == "healthy"
    assert "JSPM RSCOE" in res["institution"]
    assert "TEAM DOMINATOR" in res["team"]

def test_synthetic_playground_reset():
    res = reset_synthetic_playground()
    assert res["commits_loaded"] >= 5
    assert res["orphan_risks_detected"] >= 2
    assert res["contradictions_flagged"] >= 1

def test_git_miner_orphan_risk():
    author_lines = {"Alice Vance": 380, "Bob Martin": 40}
    risk = GitMiner.calculate_orphan_risk("services/ledger_engine.py", author_lines, 420, "2026-01-10")
    assert risk.bus_factor_risk == "CRITICAL"
    assert risk.blame_percentage > 85.0
    assert risk.primary_author == "Alice Vance"

    # Test moderate ownership (50-74%) -> MEDIUM
    collab_lines = {"Charlie Day": 120, "Bob Martin": 160}
    med_risk = GitMiner.calculate_orphan_risk("services/webhook_dispatcher.py", collab_lines, 280, "2026-02-22")
    assert med_risk.bus_factor_risk == "MEDIUM"

    # Test distributed collaborative ownership (<50%) -> LOW
    distributed_lines = {"Alice": 30, "Bob": 35, "Charlie": 35}
    low_risk = GitMiner.calculate_orphan_risk("utils/helpers.py", distributed_lines, 100, "2026-02-20")
    assert low_risk.bus_factor_risk == "LOW"

def test_nli_radar_contradiction_detection():
    radar = NLIRadar()
    premise = "In today's sync we switched idempotency storage to Redis cluster."
    hypothesis = "Revert Redis adapter due to split-brain double charge; fallback to PostgreSQL."
    prob, reason = radar.evaluate_pair_contradiction(premise, hypothesis)
    assert prob >= 0.85
    assert "Direct contradiction detected" in reason

def test_grounding_score_decay_formula():
    radar = NLIRadar(lambda_weight=0.65, gamma_decay=0.003)
    high_score = radar.calculate_grounding_score(1.0, 0, 0.0)
    assert 0.98 <= high_score <= 1.0

    low_score = radar.calculate_grounding_score(0.2, 180, 0.9)
    assert low_score < 0.40

def test_abac_security_negative_test():
    """
    Negative Security Boundary Test:
    Ensures that JUNIOR_SUCCESSOR role permanently masks secrets with redaction chips,
    while ADMIN role preserves access.
    """
    ws_junior = get_handover_workspace(role="JUNIOR_SUCCESSOR")
    raw_junior_text = str(ws_junior)
    assert "sk_test_51M0MockRestrictedKey991823719" not in raw_junior_text
    assert "sec_salt_998144201aefb3c9" not in raw_junior_text
    assert "[REDACTED BY PERMISSION POLICY" in raw_junior_text

    ws_admin = get_handover_workspace(role="ADMIN")
    assert ws_admin.viewer_role == "ADMIN"

def test_leaver_review_submission():
    questions = get_leaver_questions()
    sub_payload = LeaverReviewSubmission(
        responses={q.id: q.suggested_answer for q in questions},
        approved_by="Alice Vance (Lead Architect)"
    )
    res = submit_leaver_review(sub_payload)
    assert res["success"] is True
    assert "sig_prov_ed25519" in res["signature"]

    contras = get_contradictions()
    assert contras[0].status == "RESOLVED_BY_LEAVER"

def test_temporal_graph_is_dag():
    dag = TemporalGraphEngine.build_graph(SYNTHETIC_DECISIONS, SYNTHETIC_COMMITS, SYNTHETIC_DISCUSSIONS, SYNTHETIC_KANBAN_TASKS)
    assert dag["is_dag"] is True
    assert dag["node_count"] > 10
    assert dag["edge_count"] > 0
