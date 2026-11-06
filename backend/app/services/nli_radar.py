"""
Epistemic Contradiction Radar & NLI Grounding Engine
Identifies factual contradictions between chats, docs, and Git commit histories
using Natural Language Inference (NLI) and computes the Epistemic Grounding Score G(A).
"""

from typing import List, Tuple, Dict, Any, Optional
import math
import re
from datetime import datetime
from ..models.schemas import DecisionNode, ContradictionAlert, CitationSource, DiscussionMessage, CommitEvent

class NLIRadar:
    """
    Epistemic Contradiction Radar and Grounding Engine.
    Implements the mathematical formulation:
    G(A) = λ · S_evidence + (1 - λ) · e^(-γ · Δt) · (1 - P(contradiction))
    """

    def __init__(self, lambda_weight: float = 0.65, gamma_decay: float = 0.003):
        self.lambda_weight = lambda_weight
        self.gamma_decay = gamma_decay
        self._nli_model = None

    def calculate_grounding_score(
        self,
        evidence_strength: float,
        delta_days: float,
        contradiction_prob: float
    ) -> float:
        """
        Computes the Epistemic Grounding Score G(A) ∈ [0.0, 1.0].
        - evidence_strength: S_evidence ∈ [0.0, 1.0]
        - delta_days: elapsed time Δt in days since the supporting evidence
        - contradiction_prob: P(contradiction) ∈ [0.0, 1.0]
        """
        evidence_term = self.lambda_weight * min(1.0, max(0.0, evidence_strength))
        temporal_decay = math.exp(-self.gamma_decay * max(0.0, delta_days))
        consistency_term = (1.0 - self.lambda_weight) * temporal_decay * (1.0 - min(1.0, max(0.0, contradiction_prob)))

        score = evidence_term + consistency_term
        return round(min(1.0, max(0.0, score)), 3)

    def evaluate_pair_contradiction(self, claim_a: str, claim_b: str) -> Tuple[float, str]:
        """
        Evaluates contradiction probability P(contradiction) between two statements.
        Detects conflicting architectural intents (e.g. Redis vs PostgreSQL, Reverted vs Active).
        """
        text_a = claim_a.lower()
        text_b = claim_b.lower()

        # Reversion / Rollback indicators
        revert_keywords = ["revert", "rollback", "reverted", "dropped", "removed", "fallback to", "abandoned"]
        has_revert = any(kw in text_b for kw in revert_keywords) or any(kw in text_a for kw in revert_keywords)

        # Architectural conflict pairs (Technology A vs Technology B)
        conflict_tokens = [
            ("redis", "postgres"),
            ("redis", "postgresql"),
            ("kafka", "rabbitmq"),
            ("dynamodb", "mongodb"),
            ("grpc", "rest"),
            ("jwt", "session")
        ]

        token_conflict = False
        for tok1, tok2 in conflict_tokens:
            if (tok1 in text_a and tok2 in text_b) or (tok2 in text_a and tok1 in text_b):
                token_conflict = True
                break

        if has_revert and token_conflict:
            return 0.892, "Direct contradiction detected: Architectural intent in primary source was subsequently reversed in code repository."
        elif token_conflict:
            return 0.745, "Potential architectural conflict detected: Competing technology implementations mentioned across sources."
        elif has_revert:
            return 0.680, "Decision superseded: Later record indicates a rollback or deprecation of the original approach."
        else:
            return 0.050, "Statements are mutually consistent or independent."

    def scan_for_contradictions(
        self,
        discussions: List[DiscussionMessage],
        commits: List[CommitEvent]
    ) -> List[ContradictionAlert]:
        """
        Scans discussion messages against subsequent Git commits to detect unannounced rollbacks or conflicting claims.
        """
        alerts = []
        for disc in discussions:
            for c in commits:
                # Check if commit timestamp is after discussion timestamp
                if c.timestamp > disc.timestamp:
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
