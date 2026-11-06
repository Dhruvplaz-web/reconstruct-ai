"""
Server-Side Attribute-Based Access Control (ABAC) Redaction Engine
Enforces least-privilege security policies before JSON serialization.
Redacts confidential HR, infrastructure keys, and proprietary tokens for junior successors.
"""

from typing import List, Dict, Any, Optional
import re
from ..models.schemas import HandoverWorkspace, DecisionNode, CitationSource, OrphanRiskFile

class ABACFilter:
    """
    Attribute-Based Access Control (ABAC) Policy Enforcer.
    Ensures restricted records are stripped server-side before client transmission.
    """

    REDACTION_CHIP = "[REDACTED BY PERMISSION POLICY: Tier-2 Clearance Required]"

    # Sensitive token regexes
    SECRET_PATTERNS = [
        re.compile(r"sk_live_[a-zA-Z0-9_\-]+"),
        re.compile(r"sec_salt_[a-zA-Z0-9_\-]+"),
        re.compile(r"arn:aws:kms:[a-zA-Z0-9_\-:/]+"),
        re.compile(r"\b(password|secret|apikey|token)\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE)
    ]

    @classmethod
    def redact_text(cls, text: str) -> str:
        """Replaces sensitive credential patterns with a redaction marker."""
        redacted = text
        for pattern in cls.SECRET_PATTERNS:
            redacted = pattern.sub(cls.REDACTION_CHIP, redacted)
        return redacted

    @classmethod
    def filter_workspace(cls, workspace: HandoverWorkspace, role: str) -> HandoverWorkspace:
        """
        Applies role-based filtering to a complete HandoverWorkspace.
        If role is JUNIOR_SUCCESSOR, redacts confidential records and diffs.
        """
        normalized_role = role.upper()
        if normalized_role in ["ADMIN", "LEAD", "SECURITY_OWNER"]:
            # Full clearance: return unmodified
            workspace.viewer_role = "ADMIN"
            return workspace

        # Apply Junior Successor restrictions
        workspace.viewer_role = "JUNIOR_SUCCESSOR"

        # 1. Filter Decisions & Citations
        filtered_decisions = []
        for dec in workspace.decisions:
            dec_copy = dec.model_copy(deep=True)
            filtered_citations = []
            for cit in dec_copy.citations:
                cit_copy = cit.model_copy(deep=True)
                if cit_copy.security_tag in ["CONFIDENTIAL_HR", "CONFIDENTIAL_INFRA"]:
                    cit_copy.snippet = cls.REDACTION_CHIP
                    cit_copy.title = f"{cit_copy.title} (Redacted)"
                else:
                    cit_copy.snippet = cls.redact_text(cit_copy.snippet)
                filtered_citations.append(cit_copy)

            dec_copy.citations = filtered_citations
            dec_copy.summary = cls.redact_text(dec_copy.summary)
            dec_copy.rationale = cls.redact_text(dec_copy.rationale)
            filtered_decisions.append(dec_copy)

        workspace.decisions = filtered_decisions

        # 2. Filter Orphan Risk Files
        filtered_orphan_files = []
        for orf in workspace.orphan_risk_files:
            orf_copy = orf.model_copy(deep=True)
            if "secrets" in orf_copy.file_path.lower():
                orf_copy.risk_rationale = (
                    "Sole owner of payment infrastructure credentials. "
                    f"Credential values: {cls.REDACTION_CHIP}"
                )
            filtered_orphan_files.append(orf_copy)

        workspace.orphan_risk_files = filtered_orphan_files

        # 3. Filter Contradiction Alerts (scrub secrets from claims & snippets)
        filtered_contradictions = []
        for contra in workspace.contradictions:
            c_copy = contra.model_copy(deep=True)
            c_copy.claim_a = cls.redact_text(c_copy.claim_a)
            c_copy.claim_b = cls.redact_text(c_copy.claim_b)
            c_copy.explanation = cls.redact_text(c_copy.explanation)
            if c_copy.source_a:
                if c_copy.source_a.security_tag in ["CONFIDENTIAL_HR", "CONFIDENTIAL_INFRA"]:
                    c_copy.source_a.snippet = cls.REDACTION_CHIP
                    c_copy.source_a.title = f"{c_copy.source_a.title} (Redacted)"
                else:
                    c_copy.source_a.snippet = cls.redact_text(c_copy.source_a.snippet)
            if c_copy.source_b:
                if c_copy.source_b.security_tag in ["CONFIDENTIAL_HR", "CONFIDENTIAL_INFRA"]:
                    c_copy.source_b.snippet = cls.REDACTION_CHIP
                    c_copy.source_b.title = f"{c_copy.source_b.title} (Redacted)"
                else:
                    c_copy.source_b.snippet = cls.redact_text(c_copy.source_b.snippet)
            filtered_contradictions.append(c_copy)
        workspace.contradictions = filtered_contradictions

        # 4. Filter Commits
        if hasattr(workspace, "commits") and workspace.commits:
            filtered_commits = []
            for c in workspace.commits:
                c_copy = c.model_copy(deep=True)
                c_copy.message = cls.redact_text(c_copy.message)
                if c_copy.diff_snippet:
                    c_copy.diff_snippet = cls.redact_text(c_copy.diff_snippet)
                filtered_commits.append(c_copy)
            workspace.commits = filtered_commits

        # 5. Filter Discussions
        if hasattr(workspace, "discussions") and workspace.discussions:
            filtered_discussions = []
            for d in workspace.discussions:
                d_copy = d.model_copy(deep=True)
                d_copy.text = cls.redact_text(d_copy.text)
                filtered_discussions.append(d_copy)
            workspace.discussions = filtered_discussions

        return workspace

