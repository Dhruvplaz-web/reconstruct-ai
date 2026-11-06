"""
Acme Payments Microservice — Synthetic Benchmark Dataset
Simulates realistic developer turnover, single-author orphan code (Bus Factor = 1),
cross-source contradictions (Slack vs Git), and security redaction boundaries.
"""

from typing import List, Dict, Any
from ..models.schemas import (
    CommitEvent,
    DiscussionMessage,
    CitationSource,
    DecisionNode,
    ContradictionAlert,
    OrphanRiskFile,
    LeaverQuestion,
    KanbanTask,
    HandoverWorkspace
)

# 1. Synthetic Commit History
SYNTHETIC_COMMITS: List[CommitEvent] = [
    CommitEvent(
        sha="a1b2c3d",
        author="Alice Vance",
        email="alice@acmepayments.internal",
        timestamp="2026-01-10T14:32:00Z",
        message="feat(ledger): implement double-entry immutable ledger engine with atomic balance verification",
        files_changed=["services/ledger_engine.py", "models/account.py"],
        insertions=380,
        deletions=12,
        diff_snippet="""+ def transfer_funds(source_id: str, dest_id: str, amount_cents: int, db: Session):
+     with db.begin():
+         # Critical: lock rows in deterministic order to prevent deadlocks
+         first_id, second_id = sorted([source_id, dest_id])
+         db.execute("SELECT * FROM accounts WHERE id IN (:a, :b) FOR UPDATE", {"a": first_id, "b": second_id})
+         # Apply double-entry debit and credit records
+         insert_ledger_entry(source_id, -amount_cents)
+         insert_ledger_entry(dest_id, amount_cents)""",
        security_tag="PUBLIC"
    ),
    CommitEvent(
        sha="b4e5f6a",
        author="Alice Vance",
        email="alice@acmepayments.internal",
        timestamp="2026-01-28T09:15:00Z",
        message="feat(idempotency): experiment with Redis distributed key cache for high throughput",
        files_changed=["services/idempotency.py", "config/redis_config.py"],
        insertions=120,
        deletions=45,
        diff_snippet="""+ class RedisIdempotencyAdapter:
+     def acquire_key(self, key: str, ttl_seconds: int = 86400) -> bool:
+         return self.redis_client.set(f"idemp:{key}", "IN_PROGRESS", nx=True, ex=ttl_seconds)""",
        security_tag="PUBLIC"
    ),
    CommitEvent(
        sha="c8f192b",
        author="Bob Martin",
        email="bob@acmepayments.internal",
        timestamp="2026-02-18T16:45:00Z",
        message="revert(idempotency): rollback Redis adapter due to split-brain double charge; restore postgres SELECT FOR UPDATE",
        files_changed=["services/idempotency.py"],
        insertions=85,
        deletions=110,
        diff_snippet="""- # Removed Redis distributed adapter: network partitions cause duplicate transaction execution
+ # Fallback to ACID PostgreSQL idempotency table with unique constraint on transaction_key
+ def acquire_postgres_idempotency_lock(key: str, db: Session):
+     return db.execute("INSERT INTO idempotency_keys (key, status) VALUES (:k, 'LOCKED') ON CONFLICT DO NOTHING RETURNING id", {"k": key}).fetchone()""",
        security_tag="PUBLIC"
    ),
    CommitEvent(
        sha="d9a8b7c",
        author="Charlie Day",
        email="charlie@acmepayments.internal",
        timestamp="2026-02-22T11:20:00Z",
        message="feat(webhooks): async webhook dispatcher with exponential jitter backoff",
        files_changed=["services/webhook_dispatcher.py", "tasks/celery_workers.py"],
        insertions=190,
        deletions=20,
        diff_snippet="""+ @celery.task(bind=True, max_retries=5)
+ def dispatch_merchant_webhook(self, merchant_id: str, event_payload: dict):
+     delay = min(3600, (2 ** self.request.retries) + random.uniform(1, 5))
+     try:
+         send_signed_http_post(merchant_id, event_payload)
+     except TransientNetworkError as exc:
+         raise self.retry(exc=exc, countdown=delay)""",
        security_tag="PUBLIC"
    ),
    CommitEvent(
        sha="e4f3a21",
        author="Alice Vance",
        email="alice@acmepayments.internal",
        timestamp="2026-03-01T17:05:00Z",
        message="security(infra): configure production payment gateway credentials and webhook salts",
        files_changed=["config/payment_secrets.py"],
        insertions=40,
        deletions=5,
        diff_snippet="""+ # RESTRICTED INFRASTRUCTURE CONFIGURATION
+ STRIPE_LIVE_API_KEY = "sk_test_51M0MockRestrictedKey991823719"  # pragma: allowlist secret
+ WEBHOOK_HMAC_SIGNING_SALT = "sec_salt_998144201aefb3c9"         # pragma: allowlist secret
+ AWS_PAYMENT_KMS_ARN = "arn:aws:kms:us-east-1:123456789012:key/payments-vault-2026" """,
        security_tag="CONFIDENTIAL_INFRA"
    )
]

# 2. Synthetic Chat / Slack Discussion Threads
SYNTHETIC_DISCUSSIONS: List[DiscussionMessage] = [
    DiscussionMessage(
        id="msg-slack-001",
        author="Alice Vance",
        channel="#arch-payments",
        timestamp="2026-02-12T10:14:00Z",
        text="Heads up team: in today's architecture sync we decided to switch idempotency key storage to our Redis cluster with 24hr TTL to withstand Black Friday checkout spikes.",
        thread_id="th-idemp-01",
        security_tag="PUBLIC"
    ),
    DiscussionMessage(
        id="msg-slack-002",
        author="Bob Martin",
        channel="#arch-payments",
        timestamp="2026-02-12T10:22:00Z",
        text="Are we confident about Redis persistence? In our staging cluster last week, a 300ms network partition let two concurrent checkout clicks through because the replica hadn't synced yet.",
        thread_id="th-idemp-01",
        security_tag="PUBLIC"
    ),
    DiscussionMessage(
        id="msg-slack-003",
        author="Alice Vance",
        channel="#arch-payments",
        timestamp="2026-02-12T10:35:00Z",
        text="Valid concern Bob. I added Redlock multi-node consensus in commit b4e5f6a, let's monitor latency in staging.",
        thread_id="th-idemp-01",
        security_tag="PUBLIC"
    ),
    DiscussionMessage(
        id="msg-slack-004",
        author="Dana Scully (VP Eng)",
        channel="#eng-leadership-confidential",
        timestamp="2026-02-28T14:00:00Z",
        text="Alice's departure is confirmed for March 15. We must ensure the core ledger and payment gateway keys are audited. Her current severance and IP handover checklist are filed in Workday #WD-4912.",
        thread_id="th-hr-01",
        security_tag="CONFIDENTIAL_HR"
    )
]

# 3. Orphan Risk Files (Bus Factor = 1)
SYNTHETIC_ORPHAN_FILES: List[OrphanRiskFile] = [
    OrphanRiskFile(
        file_path="services/ledger_engine.py",
        primary_author="Alice Vance",
        blame_percentage=88.4,
        total_lines=420,
        single_author_lines=371,
        last_modified_date="2026-01-10",
        bus_factor_risk="CRITICAL",
        risk_rationale="88.4% of ledger core authored solely by Alice Vance with zero secondary commits in 55 days. Contains mission-critical double-entry accounting formulas and row-level locking."
    ),
    OrphanRiskFile(
        file_path="config/payment_secrets.py",
        primary_author="Alice Vance",
        blame_percentage=94.2,
        total_lines=68,
        single_author_lines=64,
        last_modified_date="2026-03-01",
        bus_factor_risk="HIGH",
        risk_rationale="Sole owner of live Stripe API keys and KMS decryption wrappers. Requires credential rotation protocol before offboarding."
    ),
    OrphanRiskFile(
        file_path="services/webhook_dispatcher.py",
        primary_author="Charlie Day",
        blame_percentage=44.1,
        total_lines=280,
        single_author_lines=123,
        last_modified_date="2026-02-22",
        bus_factor_risk="LOW",
        risk_rationale="Collaborative ownership between Charlie Day and Bob Martin. Low succession risk."
    )
]

# 4. Citations & Decisions
CITATION_SLACK_IDEMP = CitationSource(
    id="cit-slack-001",
    source_type="discussion",
    uri="slack://acmepayments/#arch-payments?msg=msg-slack-001",
    title="Slack: #arch-payments thread by Alice Vance",
    timestamp="2026-02-12T10:14:00Z",
    author="Alice Vance",
    snippet="Heads up team: in today's architecture sync we decided to switch idempotency key storage to our Redis cluster with 24hr TTL..."
)

CITATION_COMMIT_REVERT = CitationSource(
    id="cit-commit-c8f192b",
    source_type="commit",
    uri="git://repo/commits/c8f192b",
    title="Git Commit c8f192b by Bob Martin",
    timestamp="2026-02-18T16:45:00Z",
    author="Bob Martin",
    snippet="revert(idempotency): rollback Redis adapter due to split-brain double charge; restore postgres SELECT FOR UPDATE on idempotency_keys"
)

CITATION_COMMIT_LEDGER = CitationSource(
    id="cit-commit-a1b2c3d",
    source_type="commit",
    uri="git://repo/commits/a1b2c3d",
    title="Git Commit a1b2c3d by Alice Vance",
    timestamp="2026-01-10T14:32:00Z",
    author="Alice Vance",
    snippet="feat(ledger): implement double-entry immutable ledger engine with atomic balance verification and sorted account locking"
)

# 5. Contradiction Alert (DeBERTa-v3 detected)
SYNTHETIC_CONTRADICTIONS: List[ContradictionAlert] = [
    ContradictionAlert(
        id="contra-001",
        topic="Idempotency Storage Engine (Redis vs PostgreSQL)",
        claim_a="Alice stated on Slack (Feb 12) that idempotency keys are stored in the Redis cluster with 24h TTL.",
        source_a=CITATION_SLACK_IDEMP,
        claim_b="Bob Martin reverted Redis in Git commit c8f192b (Feb 18), declaring PostgreSQL SELECT FOR UPDATE as the active ACID production truth.",
        source_b=CITATION_COMMIT_REVERT,
        contradiction_score=0.892,
        explanation="DeBERTa-v3 Cross-Encoder detected an explicit 89.2% contradiction probability between the Slack architectural intent and the subsequent Git commit rollback. Production truth is PostgreSQL.",
        severity="HIGH",
        status="OPEN"
    )
]

# 6. Core Decisions
SYNTHETIC_DECISIONS: List[DecisionNode] = [
    DecisionNode(
        id="dec-001",
        title="PostgreSQL Table Idempotency Locking over Redis",
        summary="ACID-compliant row locking in PostgreSQL idempotency_keys table is strictly enforced to prevent duplicate charges during network partitions.",
        rationale="While Redis provided sub-millisecond responses, staging network partitions caused split-brain scenarios where concurrent checkouts generated duplicate charges.",
        timestamp="2026-02-18T16:45:00Z",
        authors=["Bob Martin", "Alice Vance"],
        status="ACTIVE",
        citations=[CITATION_COMMIT_REVERT, CITATION_SLACK_IDEMP],
        grounding_score=0.915,
        has_contradiction=True,
        quarantined_for_review=True
    ),
    DecisionNode(
        id="dec-002",
        title="Double-Entry Immutable Ledger Accounting Model",
        summary="All monetary movements must create balancing debit and credit entries with deterministic account ID sorting before acquiring row locks.",
        rationale="Guarantees zero negative-sum balance drift and completely eliminates deadlock conditions between concurrent bi-directional transfers.",
        timestamp="2026-01-10T14:32:00Z",
        authors=["Alice Vance"],
        status="ACTIVE",
        citations=[CITATION_COMMIT_LEDGER],
        grounding_score=0.962,
        has_contradiction=False,
        quarantined_for_review=False
    )
]

# 7. Targeted 60-Second Leaver Questions
SYNTHETIC_LEAVER_QUESTIONS: List[LeaverQuestion] = [
    LeaverQuestion(
        id="q1-ledger-deadlock",
        file_path="services/ledger_engine.py",
        question="You authored 88.4% of ledger_engine.py. What is the critical edge-case during high-concurrency merchant payouts?",
        context="Detected in commit a1b2c3d: deterministic sorting on source_id and dest_id before acquiring database locks.",
        options=[
            "Always sort account UUIDs alphabetically before issuing 'SELECT FOR UPDATE' to avoid cyclic deadlocks under load.",
            "Increase PostgreSQL lock timeout from 5s to 60s.",
            "Use client-side mutex locking across Celery workers."
        ],
        suggested_answer="Always sort account UUIDs alphabetically before issuing 'SELECT FOR UPDATE' to avoid cyclic deadlocks under load."
    ),
    LeaverQuestion(
        id="q2-idempotency-truth",
        file_path="services/idempotency.py",
        question="A contradiction was flagged between your Feb 12 Slack note (Redis) and Bob's Feb 18 commit c8f192b (PostgreSQL). Which is production truth?",
        context="DeBERTa-v3 detected 89.2% contradiction probability between Slack message and Git rollback.",
        options=[
            "PostgreSQL SELECT FOR UPDATE is production truth. Redis was rolled back due to split-brain double charges.",
            "Redis cluster is active; Bob's commit was only for local testing.",
            "Both are active in an active-active fallback configuration."
        ],
        suggested_answer="PostgreSQL SELECT FOR UPDATE is production truth. Redis was rolled back due to split-brain double charges."
    ),
    LeaverQuestion(
        id="q3-webhook-rotation",
        file_path="config/payment_secrets.py",
        question="Where should the incoming successor rotate the production Stripe Webhook HMAC salt?",
        context="Detected in commit e4f3a21: hardcoded webhook salt flagged for rotation prior to offboarding.",
        options=[
            "Migrate from payment_secrets.py into AWS Secrets Manager path /acme/payments/prod/stripe_hmac_salt.",
            "Store in production .env file on the web EC2 instance.",
            "Keep existing key, it does not expire."
        ],
        suggested_answer="Migrate from payment_secrets.py into AWS Secrets Manager path /acme/payments/prod/stripe_hmac_salt."
    )
]

# 8. Day 1–30 Actionable Kanban Tasks
SYNTHETIC_KANBAN_TASKS: List[KanbanTask] = [
    KanbanTask(
        id="kb-day1-01",
        stage="DAY_1",
        title="Verify PostgreSQL Idempotency Row-Lock Behavior",
        description="Run `pytest tests/test_idempotency.py -k test_concurrent_duplicate_clicks` to confirm PostgreSQL blocks duplicate charges.",
        priority="URGENT",
        category="DEBUGGING",
        linked_file="services/idempotency.py",
        linked_pr="PR #42",
        citation_id="cit-commit-c8f192b",
        completed=False
    ),
    KanbanTask(
        id="kb-day1-02",
        stage="DAY_1",
        title="Walk Through Alice's Ledger Concurrency Safeguards",
        description="Inspect deterministic UUID sorting in `services/ledger_engine.py` (lines 45-62) to understand deadlock prevention.",
        priority="HIGH",
        category="CODE_WALKTHROUGH",
        linked_file="services/ledger_engine.py",
        citation_id="cit-commit-a1b2c3d",
        completed=False
    ),
    KanbanTask(
        id="kb-day7-01",
        stage="DAY_7",
        title="Rotate Stripe Live Secret Key to AWS Secrets Manager",
        description="Execute credential rotation protocol defined in Leaver Q3 before Alice's access is formally deactivated.",
        priority="URGENT",
        category="DEPLOYMENT",
        linked_file="config/payment_secrets.py",
        completed=False
    ),
    KanbanTask(
        id="kb-day7-02",
        stage="DAY_7",
        title="Simulate Webhook Retry Failures with Jitter",
        description="Trigger 500 error responses in staging merchant endpoints to verify Celery exponential backoff does not overwhelm network.",
        priority="MEDIUM",
        category="ARCHITECTURE",
        linked_file="services/webhook_dispatcher.py",
        completed=False
    ),
    KanbanTask(
        id="kb-day30-01",
        stage="DAY_30",
        title="De-couple Ledger Engine Single-Author Monolith",
        description="Refactor `services/ledger_engine.py` into distinct query repository and transaction calculation modules to resolve Bus Factor = 1.",
        priority="HIGH",
        category="ARCHITECTURE",
        linked_file="services/ledger_engine.py",
        completed=False
    )
]

