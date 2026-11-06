"""
Automated PyTest Test Suite for Reconstruct.ai Backend
Direct, high-speed verification of Git Blame Miner with DOA & Truck Factor,
NLIRadar, ABAC Security, W3C PROV-DM Document Export, and FastAPI API routes.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
import json
from backend.app.services.git_miner import GitMiner
from backend.app.services.nli_radar import NLIRadar, parse_iso_utc
from backend.app.services.abac_filter import ABACFilter
from backend.app.services.graph_engine import TemporalGraphEngine
from backend.app.services.discussion_miner import DiscussionMiner
from backend.app.api.router import (
    health_check,
    reset_synthetic_playground,
    get_orphan_risk,
    get_truck_factor_analysis,
    get_contradictions,
    get_temporal_graph,
    export_w3c_prov,
    export_adr,
    get_leaver_questions,
    submit_leaver_review,
    get_handover_workspace,
    ingest_live_repository,
    ingest_discussions,
    verify_leaver_review,
    LiveRepoRequest,
    DiscussionIngestRequest,
    VerificationRequest
)
from backend.app.models.schemas import LeaverReviewSubmission
from backend.app.data.acme_payments import (
    SYNTHETIC_DECISIONS, SYNTHETIC_COMMITS, SYNTHETIC_DISCUSSIONS, SYNTHETIC_KANBAN_TASKS, SYNTHETIC_ORPHAN_FILES
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

def test_git_miner_orphan_risk_and_doa():
    # Test high single-author concentration (>75%) & DOA
    author_lines = {"Alice Vance": 380, "Bob Martin": 40}
    risk = GitMiner.calculate_orphan_risk(
        "services/ledger_engine.py", author_lines, 420, "2026-01-10",
        is_first_author=True, author_commits=14, other_edits=1
    )
    assert risk.bus_factor_risk == "CRITICAL"
    assert risk.blame_percentage > 85.0
    assert risk.primary_author == "Alice Vance"
    assert "DOA:" in risk.risk_rationale

    # Test Degree of Authorship formula explicitly
    doa = GitMiner.calculate_doa(is_first_author=True, deliveries_commits=10, acceptances_edits_by_others=2)
    assert doa > 5.0

    # Test moderate ownership (50-74%) -> MEDIUM
    collab_lines = {"Charlie Day": 120, "Bob Martin": 160}
    med_risk = GitMiner.calculate_orphan_risk("services/webhook_dispatcher.py", collab_lines, 280, "2026-02-22")
    assert med_risk.bus_factor_risk == "MEDIUM"

    # Test distributed collaborative ownership (<50%) -> LOW
    distributed_lines = {"Alice": 30, "Bob": 35, "Charlie": 35}
    low_risk = GitMiner.calculate_orphan_risk("utils/helpers.py", distributed_lines, 100, "2026-02-20")
    assert low_risk.bus_factor_risk == "LOW"

def test_truck_factor_calculation():
    tf_data = GitMiner.calculate_repository_truck_factor(SYNTHETIC_ORPHAN_FILES)
    assert tf_data["truck_factor"] == 1
    assert tf_data["risk_status"] == "CRITICAL"
    assert "Alice Vance" in tf_data["key_holders"]

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

def test_nli_utc_timezone_cross_comparison():
    radar = NLIRadar()
    # Discussion at 3:30 PM IST (10:00:00 UTC)
    disc_time_str = "2026-03-01T15:30:00+05:30"
    # Commit at 10:15 AM UTC (10:15:00 UTC) -> Chronologically AFTER the discussion!
    commit_time_str = "2026-03-01T10:15:00Z"

    # Lexicographical string check fails ('10:15:00Z' < '15:30:00+05:30')
    assert commit_time_str < disc_time_str

    # Timezone-aware UTC parsing succeeds
    disc_dt = parse_iso_utc(disc_time_str)
    commit_dt = parse_iso_utc(commit_time_str)
    assert commit_dt > disc_dt

    from backend.app.models.schemas import DiscussionMessage, CommitEvent
    disc = DiscussionMessage(
        id="disc-tz-1",
        channel="architecture",
        author="Alice",
        timestamp=disc_time_str,
        text="Standardized on Redis for idempotency cache."
    )
    commit = CommitEvent(
        sha="a1b2c3d",
        author="Bob",
        timestamp=commit_time_str,
        message="Revert Redis adapter and fallback to PostgreSQL"
    )

    alerts = radar.scan_for_contradictions([disc], [commit])
    assert len(alerts) == 1
    assert alerts[0].severity == "HIGH"
    assert alerts[0].contradiction_score >= 0.85

def test_nli_expanded_taxonomy_contradictions():
    radar = NLIRadar()
    # gRPC vs REST
    p1, r1 = radar.evaluate_pair_contradiction("We are adopting gRPC for internal service communication.", "Migrate all endpoints to REST json.")
    assert p1 >= 0.70
    assert "grpc" in r1 and "rest" in r1

    # Kafka vs RabbitMQ
    p2, r2 = radar.evaluate_pair_contradiction("Publish events to Kafka cluster.", "Replaced with RabbitMQ message broker.")
    assert p2 >= 0.85

    # Monolith vs Microservices
    p3, r3 = radar.evaluate_pair_contradiction("We are breaking up the monolith into microservices.", "Deploy monolithic jar to production.")
    assert p3 >= 0.70

def test_grounding_score_from_timestamps():
    radar = NLIRadar()
    score_fresh = radar.calculate_grounding_score_from_timestamps(
        evidence_strength=0.9,
        evidence_timestamp="2026-03-01T12:00:00Z",
        reference_timestamp="2026-03-01T12:00:00Z"
    )
    assert score_fresh > 0.90

    score_aged = radar.calculate_grounding_score_from_timestamps(
        evidence_strength=0.5,
        evidence_timestamp="2025-01-01T00:00:00Z",
        reference_timestamp="2026-01-01T00:00:00Z",
        contradiction_prob=0.8
    )
    assert score_aged < 0.40

def test_transformer_semantic_similarity():
    radar = NLIRadar()
    sim = radar.compute_semantic_similarity(
        "We switched idempotency storage to Redis cluster.",
        "Revert Redis adapter due to split-brain double charge; fallback to PostgreSQL."
    )
    # If transformer is loaded, similarity should be a valid cosine metric
    if sim is not None:
        assert 0.20 <= sim <= 0.95

def test_abac_security_negative_test():
    # Inject a temporary sensitive contradiction to test scrub coverage
    from backend.app.models.schemas import ContradictionAlert, CitationSource
    from backend.app.api.router import APP_STATE
    APP_STATE["contradictions"].append(
        ContradictionAlert(
            id="contra-secret-test",
            topic="Secret Leak Check",
            claim_a="Leaked password='super_secret_123' in chat",
            source_a=CitationSource(
                id="cit-secret-1",
                source_type="discussion",
                uri="slack://channel/general",
                title="Secret Discussion",
                timestamp="2026-03-01T12:00:00Z",
                author="Alice",
                snippet="Use sk_test_secret_key_leaked_here"
            ),
            claim_b="Committed sec_salt_test_hash in git",
            source_b=CitationSource(
                id="cit-secret-2",
                source_type="commit",
                uri="git://repo/commits/abc",
                title="Secret Commit",
                timestamp="2026-03-01T13:00:00Z",
                author="Bob",
                snippet="git commit with password='pass'"
            ),
            contradiction_score=0.9,
            explanation="Contains secret credentials",
            severity="HIGH",
            status="OPEN"
        )
    )

    ws_junior = get_handover_workspace(role="JUNIOR_SUCCESSOR")
    raw_junior_text = str(ws_junior)
    assert "sk_test_51M0MockRestrictedKey991823719" not in raw_junior_text
    assert "sec_salt_998144201aefb3c9" not in raw_junior_text
    assert "sk_test_secret_key_leaked_here" not in raw_junior_text
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
    assert "ed25519:" in res["signature"]
    assert res["algorithm"] == "Ed25519 (RFC 8032)"
    assert len(res["public_key"]) == 64  # 32-byte raw Ed25519 public key as hex

    contras = get_contradictions()
    assert contras[0].status == "RESOLVED_BY_LEAVER"

def test_ed25519_tamper_evident_verification():
    # 1. Sign a review submission
    questions = get_leaver_questions()
    original_responses = {q.id: q.suggested_answer for q in questions}
    sub_payload = LeaverReviewSubmission(
        responses=original_responses,
        approved_by="Alice Vance (Lead Architect)",
        additional_notes="Production ledger verified."
    )
    submit_res = submit_leaver_review(sub_payload)
    
    canonical_data = {
        "approved_by": "Alice Vance (Lead Architect)",
        "timestamp": submit_res["timestamp"],
        "responses": original_responses,
        "additional_notes": "Production ledger verified."
    }
    
    # 2. Verify with valid unmodified payload -> Mathematical verification succeeds
    valid_res = verify_leaver_review(VerificationRequest(
        payload=canonical_data,
        signature=submit_res["signature"],
        public_key=submit_res["public_key"]
    ))
    assert valid_res["valid"] is True
    assert valid_res["status"] == "CRYPTOGRAPHICALLY_VERIFIED"
    assert valid_res["tamper_evident"] is True

    # 3. Verify with tampered payload -> Mathematical verification FAILS (tamper-evident proof)
    tampered_data = dict(canonical_data)
    tampered_data["approved_by"] = "Mallory (Attacker)"
    invalid_res = verify_leaver_review(VerificationRequest(
        payload=tampered_data,
        signature=submit_res["signature"],
        public_key=submit_res["public_key"]
    ))
    assert invalid_res["valid"] is False
    assert invalid_res["status"] == "SIGNATURE_MISMATCH"

def test_w3c_prov_export():
    prov_res = export_w3c_prov()
    prov_data = json.loads(prov_res.body.decode())
    assert "entity" in prov_data
    assert "prefix" in prov_data
    assert "recon" in prov_data["prefix"]

def test_adr_markdown_export():
    adr_text = export_adr()
    assert "# ADR-" in adr_text
    assert "## Status" in adr_text
    assert "## Context" in adr_text
    assert "## Verifiable Sources" in adr_text

def test_live_repository_real_time_mining():
    """
    Real-Time Data Test:
    Executes live Git repository mining on the current real repository.
    Verifies actual commits, line-by-line git blame on real files,
    live author extraction ('Dhruv Patil'), real DOA calculations,
    and dynamic decision/question synthesis.
    """
    res = ingest_live_repository(LiveRepoRequest(repo_path="."))
    assert res["success"] is True
    assert res["mode"] == "REAL_TIME_GIT_ANALYSIS"
    assert res["commits_analyzed"] >= 5
    assert res["source_files_blamed"] >= 5
    assert res["truck_factor"] >= 1
    assert "Dhruv Patil" in res["key_maintainers"]
    assert len(res["top_single_author_files"]) > 0
    assert res["extracted_decisions_count"] > 0
    assert res["generated_onboarding_tasks_count"] > 0

    # Verify that live workspace reflects real-time repository data
    ws = get_handover_workspace(role="ADMIN")
    assert "Live Repo" in ws.project_name
    assert "Dhruv Patil" in ws.leaver_name
    assert len(ws.orphan_risk_files) > 0
    assert any("run_app.py" in f.file_path or "main.py" in f.file_path for f in ws.orphan_risk_files)
    assert len(ws.decisions) > 0
    assert len(ws.kanban_tasks) > 0

def test_discussion_miner_slack_and_discord_parsing():
    # 1. Test Slack Export Parsing
    sample_slack = [
        {
            "client_msg_id": "99b1a03e-test",
            "type": "message",
            "text": "Architecture sync: We switched payment lock engine to Redis cluster.",
            "user": "U12345",
            "user_profile": {"real_name": "Alice Vance"},
            "ts": "1770908700.000100"
        }
    ]
    slack_msgs = DiscussionMiner.parse_slack_export(sample_slack, channel="arch")
    assert len(slack_msgs) == 1
    assert slack_msgs[0].author == "Alice Vance"
    assert "Redis" in slack_msgs[0].text
    assert slack_msgs[0].channel == "arch"

    # 2. Test Discord Export Parsing
    sample_discord = [
        {
            "id": "11998822",
            "author": {"name": "Bob", "nickname": "Bob Martin"},
            "content": "Reverted Redis adapter due to race condition; restored Postgres.",
            "timestamp": "2026-02-18T10:00:00Z"
        }
    ]
    discord_msgs = DiscussionMiner.parse_discord_export(sample_discord, channel="dev")
    assert len(discord_msgs) == 1
    assert discord_msgs[0].author == "Bob Martin"
    assert "Reverted Redis" in discord_msgs[0].text

    # 3. Test Raw Transcript Parsing
    transcript = "[2026-02-12 14:30:00] Alice Vance: We decided to deploy RabbitMQ.\nBob Martin: Confirmed."
    raw_msgs = DiscussionMiner.parse_raw_transcript(transcript)
    assert len(raw_msgs) == 2
    assert raw_msgs[0].author == "Alice Vance"
    assert "RabbitMQ" in raw_msgs[0].text

def test_multi_source_ingestion_with_live_discussions():
    # Ingest live repository with paired discussions to test NLI radar integration
    raw_slack_json = json.dumps([
        {
            "client_msg_id": "slack-live-01",
            "text": "In today's sync we agreed to switch payment idempotency to Redis cluster.",
            "user_profile": {"real_name": "Alice Vance"},
            "ts": "1770908700.000100"
        }
    ])
    res = ingest_live_repository(LiveRepoRequest(
        repo_path=".",
        discussions_raw=raw_slack_json,
        pair_sample_discussions=True
    ))
    assert res["success"] is True
    assert res["discussions_ingested"] >= 1
    
    # Test discussion endpoint explicitly
    disc_res = ingest_discussions(DiscussionIngestRequest(
        content="Alice Vance: We tested redis vs postgres.",
        channel="architecture"
    ))
    assert disc_res["success"] is True
    assert disc_res["messages_parsed"] >= 1

def test_empirical_icse_doa_and_solo_truck_factor():
    import git
    repo = git.Repo(".", search_parent_directories=True)
    
    # 1. Test real ICSE Git log metrics extraction
    metrics = GitMiner.compute_file_icse_metrics(repo, "run_app.py", "Dhruv Patil")
    assert "is_first_author" in metrics
    assert "deliveries" in metrics
    assert "acceptances" in metrics
    assert metrics["deliveries"] >= 1

    # 2. Test Solo Author Truck Factor: verify Truck Factor is 1 (CRITICAL), never inverted to 3 (LOW)
    from backend.app.models.schemas import OrphanRiskFile
    solo_files = [
        OrphanRiskFile(
            file_path="small_module_a.py",
            primary_author="SoloDev",
            blame_percentage=100.0,
            total_lines=20,
            single_author_lines=20,
            last_modified_date="2026-03-01",
            bus_factor_risk="LOW",
            risk_rationale="Small file"
        ),
        OrphanRiskFile(
            file_path="small_module_b.py",
            primary_author="SoloDev",
            blame_percentage=100.0,
            total_lines=15,
            single_author_lines=15,
            last_modified_date="2026-03-01",
            bus_factor_risk="LOW",
            risk_rationale="Small file"
        )
    ]
    tf_solo = GitMiner.calculate_repository_truck_factor(solo_files)
    assert tf_solo["truck_factor"] == 1
    assert tf_solo["risk_status"] == "CRITICAL"
    assert "SoloDev" in tf_solo["key_holders"]
