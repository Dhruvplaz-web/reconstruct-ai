"""
Git Blame & Bus Factor = 1 Orphan Code Miner
Analyzes repository commit histories, computes line-by-line ownership ratios,
and flags single-contributor modules (>75% authorship) as critical continuity risks.
"""

from typing import List, Dict, Any, Optional
import os
import re
from datetime import datetime, timezone
from ..models.schemas import OrphanRiskFile, CommitEvent

class GitMiner:
    """
    Mines repository history to compute author ownership and single-author concentration risks.
    """

    @staticmethod
    def calculate_orphan_risk(
        file_path: str,
        author_lines: Dict[str, int],
        total_lines: int,
        last_modified_date: str
    ) -> OrphanRiskFile:
        """
        Determines the Bus Factor risk level based on single-author blame concentration.
        """
        if total_lines == 0 or not author_lines:
            return OrphanRiskFile(
                file_path=file_path,
                primary_author="UNKNOWN",
                blame_percentage=0.0,
                total_lines=0,
                single_author_lines=0,
                last_modified_date=last_modified_date,
                bus_factor_risk="LOW",
                risk_rationale="Empty file or no blame records found."
            )

        # Sort authors by lines contributed descending
        sorted_authors = sorted(author_lines.items(), key=lambda x: x[1], reverse=True)
        primary_author, primary_lines = sorted_authors[0]
        blame_percentage = round((primary_lines / total_lines) * 100.0, 1)

        # Heuristic Risk Classification
        if blame_percentage >= 75.0 and total_lines >= 50:
            risk_level = "CRITICAL" if blame_percentage >= 85.0 else "HIGH"
            rationale = (
                f"{blame_percentage}% of lines ({primary_lines}/{total_lines}) were authored exclusively by {primary_author}. "
                f"Severe Bus Factor = 1 vulnerability; if {primary_author} leaves, architectural context is lost."
            )
        elif blame_percentage >= 50.0 and total_lines >= 100:
            risk_level = "MEDIUM"
            rationale = (
                f"{blame_percentage}% single-author ownership by {primary_author}. "
                f"Moderate knowledge concentration; secondary contributors have minor exposure."
            )
        else:
            risk_level = "LOW"
            rationale = (
                f"Distributed ownership: {primary_author} holds {blame_percentage}%. "
                f"Multiple contributors actively collaborate on this module."
            )

        return OrphanRiskFile(
            file_path=file_path,
            primary_author=primary_author,
            blame_percentage=blame_percentage,
            total_lines=total_lines,
            single_author_lines=primary_lines,
            last_modified_date=last_modified_date,
            bus_factor_risk=risk_level,
            risk_rationale=rationale
        )

    @staticmethod
    def filter_formatting_commits(commits: List[CommitEvent]) -> List[CommitEvent]:
        """
        Filters out commits that are purely whitespace, formatting (Prettier, Black, Ruff),
        or simple renames to prevent false-positive author blame skew.
        """
        formatting_patterns = [
            r"reformat", r"prettier", r"black format", r"style\b", r"lint\b", r"autopep8", r"ruff format"
        ]
        regex = re.compile("|".join(formatting_patterns), re.IGNORECASE)

        substantive_commits = []
        for c in commits:
            # If commit message explicitly matches formatting or has 0 file changes
            if regex.search(c.message) and c.deletions > 0 and abs(c.insertions - c.deletions) < 10:
                continue
            substantive_commits.append(c)

        return substantive_commits
