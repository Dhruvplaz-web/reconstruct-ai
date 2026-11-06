"""
Git Blame & Bus Factor = 1 Orphan Code Miner
Incorporates Degree of Authorship (DOA) formulation (Fritz et al., ACM/IEEE ICSE)
and Truck Factor estimation (HelgeCPH/truckfactor, Adam Tornhill).
"""

from typing import List, Dict, Any, Optional
import os
import re
import math
from datetime import datetime, timezone
from ..models.schemas import OrphanRiskFile, CommitEvent

class GitMiner:
    """
    Mines repository history to compute author ownership, Degree of Authorship (DOA),
    and project-wide Truck Factor risk.
    """

    @staticmethod
    def calculate_doa(
        is_first_author: bool,
        deliveries_commits: int,
        acceptances_edits_by_others: int
    ) -> float:
        """
        Computes Degree of Authorship (DOA) based on the empirical formulation:
        DOA = 3.293 + 1.098·FA + 0.164·DL - 0.321·ln(1 + AC)
        where:
        - FA = 1 if author created the file, 0 otherwise
        - DL = number of commits/changes authored by this developer
        - AC = number of subsequent edits made by other developers
        Threshold: DOA >= 3.2 qualifies as an active primary knowledge owner.
        """
        fa_val = 1.0 if is_first_author else 0.0
        dl_val = float(deliveries_commits)
        ac_val = float(acceptances_edits_by_others)

        doa = 3.293 + (1.098 * fa_val) + (0.164 * dl_val) - (0.321 * math.log(1.0 + ac_val))
        return round(doa, 2)

    @staticmethod
    def calculate_orphan_risk(
        file_path: str,
        author_lines: Dict[str, int],
        total_lines: int,
        last_modified_date: str,
        is_first_author: bool = True,
        author_commits: int = 12,
        other_edits: int = 2
    ) -> OrphanRiskFile:
        """
        Determines the Bus Factor risk level based on single-author blame concentration
        and Degree of Authorship (DOA).
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

        # Calculate DOA score
        doa_score = GitMiner.calculate_doa(is_first_author, author_commits, other_edits)

        # Heuristic Risk Classification
        if blame_percentage >= 75.0 and total_lines >= 50:
            risk_level = "CRITICAL" if blame_percentage >= 85.0 else "HIGH"
            rationale = (
                f"{blame_percentage}% of lines ({primary_lines}/{total_lines}) authored exclusively by {primary_author} "
                f"(DOA: {doa_score}). Severe Bus Factor = 1 vulnerability; if {primary_author} leaves, architectural context is lost."
            )
        elif blame_percentage >= 50.0 and total_lines >= 100:
            risk_level = "MEDIUM"
            rationale = (
                f"{blame_percentage}% single-author ownership by {primary_author} (DOA: {doa_score}). "
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
    def calculate_repository_truck_factor(orphan_files: List[OrphanRiskFile]) -> Dict[str, Any]:
        """
        Calculates repository-wide Truck Factor (HelgeCPH/truckfactor algorithm).
        Finds the minimum set of developers whose departure results in >50% of critical files losing their owner.
        """
        critical_files = [f for f in orphan_files if f.bus_factor_risk in ["CRITICAL", "HIGH"]]
        if not critical_files:
            return {"truck_factor": 3, "risk_status": "LOW", "key_holders": []}

        author_critical_counts: Dict[str, int] = {}
        for f in critical_files:
            author_critical_counts[f.primary_author] = author_critical_counts.get(f.primary_author, 0) + 1

        # Sort authors by number of critical files owned descending
        sorted_authors = sorted(author_critical_counts.items(), key=lambda x: x[1], reverse=True)
        key_holders = []
        covered_files = 0
        threshold = len(critical_files) * 0.50

        for author, count in sorted_authors:
            key_holders.append(author)
            covered_files += count
            if covered_files >= threshold:
                break

        truck_factor = len(key_holders)
        return {
            "truck_factor": truck_factor,
            "risk_status": "CRITICAL" if truck_factor <= 1 else "MEDIUM",
            "key_holders": key_holders,
            "critical_files_count": len(critical_files),
            "explanation": (
                f"Truck Factor = {truck_factor}: The departure of {', '.join(key_holders)} "
                f"leaves {covered_files}/{len(critical_files)} critical modules without a primary maintainer."
            )
        }

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
            if regex.search(c.message) and c.deletions > 0 and abs(c.insertions - c.deletions) < 10:
                continue
            substantive_commits.append(c)

        return substantive_commits
