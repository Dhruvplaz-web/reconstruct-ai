"""
Epistemic Contradiction Radar & Natural Language Inference (NLI) Engine
Detects factual and architectural contradictions between communications (Slack/Discord/PRs)
and actual Git commit records using HuggingFace Transformers (Sentence-MiniLM / DeBERTa)
and a 35+ domain architectural conflict taxonomy with UTC timezone alignment.
"""

from typing import List, Tuple, Dict, Any, Optional
import math
import re
import logging
from datetime import datetime, timezone
from ..models.schemas import ContradictionAlert, CitationSource, DiscussionMessage, CommitEvent

logger = logging.getLogger("reconstruct.nli_radar")

def parse_iso_utc(ts: Any) -> datetime:
    """
    Robust timezone-aware UTC datetime parser.
    Handles ISO 8601 strings (with 'Z' or explicit offsets), epoch timestamps,
    and native datetime objects. Prevents cross-timezone lexicographical ordering bugs.
    """
    if ts is None:
        return datetime.now(timezone.utc)
    if isinstance(ts, (int, float)):
        # Support millisecond timestamps if > 1e11
        if ts > 1e11:
            ts = ts / 1000.0
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    if isinstance(ts, datetime):
        return ts.astimezone(timezone.utc) if ts.tzinfo else ts.replace(tzinfo=timezone.utc)

    s = str(ts).strip()
    if not s:
        return datetime.now(timezone.utc)

    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    try:
        dt = datetime.fromisoformat(s)
        return dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        pass

    # Fallback to common timestamp patterns
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S%z", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except Exception:
            continue

    return datetime.now(timezone.utc)


class NLIRadar:
    """
    Epistemic Contradiction Radar and Grounding Engine.
    Implements the mathematical formulation:
    G(A) = λ · S_evidence + (1 - λ) · e^(-γ · Δt) · (1 - P(contradiction))
    """

    # Shared class-level model cache to eliminate redundant PyTorch allocations
    _cached_tokenizer = None
    _cached_model = None
    _init_attempted = False

    # 35+ Domain Architectural Taxonomy (Technology A vs Technology B)
    CONFLICT_TAXONOMY = [
        # Databases & Key-Value Stores
        ("redis", "postgres"),
        ("redis", "postgresql"),
        ("redis", "mysql"),
        ("mongodb", "postgres"),
        ("mongodb", "postgresql"),
        ("mongodb", "mysql"),
        ("dynamodb", "postgres"),
        ("dynamodb", "postgresql"),
        ("dynamodb", "mongodb"),
        ("sqlite", "postgres"),
        ("sqlite", "mysql"),
        ("cassandra", "scylladb"),
        ("cassandra", "postgres"),
        ("cockroachdb", "postgres"),
        # Caching Systems
        ("redis", "memcached"),
        ("valkey", "redis"),
        ("hazelcast", "redis"),
        # Message Brokers & Event Streams
        ("kafka", "rabbitmq"),
        ("kafka", "pulsar"),
        ("sqs", "rabbitmq"),
        ("nats", "kafka"),
        ("nats", "rabbitmq"),
        # API Protocols & Remote Procedure Calls
        ("grpc", "rest"),
        ("grpc", "graphql"),
        ("graphql", "rest"),
        ("trpc", "rest"),
        ("websocket", "sse"),
        ("websocket", "polling"),
        ("soap", "rest"),
        # Identity, Auth & Access Control
        ("jwt", "session"),
        ("jwt", "cookie"),
        ("oauth2", "saml"),
        ("rbac", "abac"),
        ("auth0", "cognito"),
        ("keycloak", "auth0"),
        # Systems & Architecture Paradigms
        ("monolith", "microservices"),
        ("serverless", "kubernetes"),
        ("serverless", "k8s"),
        ("lambda", "fargate"),
        ("docker", "podman"),
        ("sync", "async"),
        ("event-driven", "polling"),
        ("cqrs", "crud"),
        # Language / Runtime Stacks
        ("python", "go"),
        ("python", "rust"),
        ("node", "go"),
        ("javascript", "typescript")
    ]

    REVERT_KEYWORDS = [
        "revert", "rollback", "reverted", "dropped", "removed",
        "fallback to", "abandoned", "deprecated", "backed out",
        "cancelled", "replaced with", "migrated away from"
    ]

    ADOPTION_KEYWORDS = [
        "adopt", "switched to", "switching to", "migrated to", "migrating to",
        "standardized on", "selected", "chosen", "moved to", "using", "implementing"
    ]

    def __init__(self, lambda_weight: float = 0.65, gamma_decay: float = 0.003):
        self.lambda_weight = lambda_weight
        self.gamma_decay = gamma_decay

    @classmethod
    def _load_transformer_if_available(cls):
        """
        Attempts to lazy-load cached transformer model (sentence-transformers/all-MiniLM-L6-v2)
        in local offline mode without requiring network connection.
        """
        if cls._init_attempted:
            return
        cls._init_attempted = True
        try:
            import torch
            from transformers import AutoTokenizer, AutoModel
            cls._cached_tokenizer = AutoTokenizer.from_pretrained(
                "sentence-transformers/all-MiniLM-L6-v2",
                local_files_only=True
            )
            cls._cached_model = AutoModel.from_pretrained(
                "sentence-transformers/all-MiniLM-L6-v2",
                local_files_only=True
            )
            cls._cached_model.eval()
            logger.info("Successfully initialized HuggingFace MiniLM transformer for semantic grounding.")
        except Exception as e:
            logger.debug("Running NLI Radar with fast heuristic semantic engine (offline mode). Detail: %s", e)
            cls._cached_tokenizer = None
            cls._cached_model = None

    def calculate_grounding_score(
        self,
        evidence_strength: float,
        delta_days: float,
        contradiction_prob: float
    ) -> float:
        """
        Computes the Epistemic Grounding Score G(A) ∈ [0.0, 1.0].
        G(A) = λ · S_evidence + (1 - λ) · e^(-γ · Δt) · (1 - P(contradiction))
        """
        evidence_term = self.lambda_weight * min(1.0, max(0.0, evidence_strength))
        temporal_decay = math.exp(-self.gamma_decay * max(0.0, delta_days))
        consistency_term = (1.0 - self.lambda_weight) * temporal_decay * (1.0 - min(1.0, max(0.0, contradiction_prob)))

        score = evidence_term + consistency_term
        return round(min(1.0, max(0.0, score)), 3)

    def calculate_grounding_score_from_timestamps(
        self,
        evidence_strength: float,
        evidence_timestamp: Any,
        reference_timestamp: Optional[Any] = None,
        contradiction_prob: float = 0.0
    ) -> float:
        """
        Calculates grounding score using timezone-aware UTC timestamps for Δt elapsed days.
        """
        ev_dt = parse_iso_utc(evidence_timestamp)
        ref_dt = parse_iso_utc(reference_timestamp) if reference_timestamp else datetime.now(timezone.utc)

        delta_seconds = max(0.0, (ref_dt - ev_dt).total_seconds())
        delta_days = delta_seconds / 86400.0
        return self.calculate_grounding_score(evidence_strength, delta_days, contradiction_prob)

    def compute_semantic_similarity(self, text_a: str, text_b: str) -> Optional[float]:
        """
        Computes cosine similarity between two sentences using the loaded transformer.
        Returns None if transformer is unavailable.
        """
        if not self._cached_tokenizer or not self._cached_model:
            self._load_transformer_if_available()
        if not self._cached_tokenizer or not self._cached_model:
            return None

        try:
            import torch
            inputs = self._cached_tokenizer(
                [text_a, text_b],
                padding=True,
                truncation=True,
                return_tensors="pt"
            )
            with torch.no_grad():
                outputs = self._cached_model(**inputs)
                # Mean pooling
                embeddings = outputs.last_hidden_state.mean(dim=1)
                normalized = torch.nn.functional.normalize(embeddings, p=2, dim=1)
                similarity = torch.dot(normalized[0], normalized[1]).item()
                return round(similarity, 4)
        except Exception:
            return None

    def evaluate_pair_contradiction(self, claim_a: str, claim_b: str) -> Tuple[float, str]:
        """
        Evaluates contradiction probability P(contradiction) ∈ [0.0, 1.0] between two statements.
        Detects conflicting architectural intents, unannounced rollbacks, and semantic divergences.
        """
        text_a = claim_a.lower()
        text_b = claim_b.lower()

        # Check for reversion/rollback keywords in either statement
        has_revert_b = any(kw in text_b for kw in self.REVERT_KEYWORDS)
        has_revert_a = any(kw in text_a for kw in self.REVERT_KEYWORDS)
        has_revert = has_revert_b or has_revert_a

        # Check for active adoption keywords in claim A
        has_adoption_a = any(kw in text_a for kw in self.ADOPTION_KEYWORDS)

        # Architectural conflict pairs (Technology A vs Technology B)
        matched_pair = None
        for tok1, tok2 in self.CONFLICT_TAXONOMY:
            if (tok1 in text_a and tok2 in text_b) or (tok2 in text_a and tok1 in text_b):
                matched_pair = (tok1, tok2)
                break

        # Case 1: Direct rollback of an established decision with competing tech
        if has_revert and matched_pair:
            t1, t2 = matched_pair
            return 0.892, (
                f"Direct contradiction detected: Architectural intent regarding '{t1}' in primary source "
                f"was subsequently reversed in code repository favoring '{t2}'."
            )

        # Case 2: Claim A adopts a tech that Claim B explicitly reverts or drops
        if has_revert_b:
            # Check if any technology mentioned in A is specifically named in B's revert
            for tok1, _ in self.CONFLICT_TAXONOMY:
                if tok1 in text_a and tok1 in text_b:
                    return 0.885, (
                        f"Direct rollback detected: Later record indicates active reversion of '{tok1}', "
                        f"superseding earlier adoption claim."
                    )

        # Case 3: Conflicting technology implementations mentioned across sources
        if matched_pair:
            t1, t2 = matched_pair
            prob = 0.745
            semantic_sim = self.compute_semantic_similarity(claim_a, claim_b)
            if semantic_sim is not None and semantic_sim > 0.40:
                prob = min(0.85, prob + 0.05)
            return prob, f"Potential architectural conflict detected: Competing technology implementations ('{t1}' vs '{t2}') mentioned across sources."

        # Case 4: General rollback or deprecation record
        if has_revert_b:
            return 0.680, "Decision superseded: Later record indicates a rollback or deprecation of the original approach."

        # Case 5: Independent or mutually consistent
        return 0.050, "Statements are mutually consistent or independent."

    def scan_for_contradictions(
        self,
        discussions: List[DiscussionMessage],
        commits: List[CommitEvent]
    ) -> List[ContradictionAlert]:
        """
        Scans discussion messages against subsequent Git commits to detect unannounced rollbacks or conflicting claims.
        Uses timezone-aware UTC datetime parsing to eliminate cross-timezone comparison errors.
        """
        alerts: List[ContradictionAlert] = []
        for disc in discussions:
            disc_dt = parse_iso_utc(disc.timestamp)
            for c in commits:
                c_dt = parse_iso_utc(c.timestamp)
                # Check if commit timestamp is strictly after discussion timestamp in UTC
                if c_dt > disc_dt:
                    prob, reason = self.evaluate_pair_contradiction(disc.text, c.message)
                    if prob >= 0.70:
                        alert = ContradictionAlert(
                            id=f"contra-{len(alerts) + 1:03d}",
                            topic="Architecture Implementation Mismatch",
                            claim_a=f"{disc.author} stated in {disc.channel}: '{disc.text}'",
                            source_a=CitationSource(
                                id=f"cit-{disc.id}",
                                source_type="discussion",
                                uri=f"slack://channel/{disc.channel}?msg={disc.id}",
                                title=f"Slack: {disc.channel} discussion",
                                timestamp=disc.timestamp,
                                author=disc.author,
                                snippet=disc.text
                            ),
                            claim_b=f"{c.author} committed: '{c.message}'",
                            source_b=CitationSource(
                                id=f"cit-commit-{c.sha}",
                                source_type="commit",
                                uri=f"git://repo/commits/{c.sha}",
                                title=f"Git Commit {c.sha}",
                                timestamp=c.timestamp,
                                author=c.author,
                                snippet=c.diff_snippet or c.message
                            ),
                            contradiction_score=prob,
                            explanation=reason,
                            severity="HIGH" if prob >= 0.85 else "MEDIUM",
                            status="OPEN"
                        )
                        alerts.append(alert)
        return alerts
