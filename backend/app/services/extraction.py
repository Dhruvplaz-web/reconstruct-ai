"""
Dynamic Decision & Knowledge Gap Extractor
Transforms real-time Git commits and live file blame distributions
into verifiable DecisionNodes, targeted LeaverQuestions, and Onboarding Kanban tasks.
"""

from typing import List, Dict, Any
from ..models.schemas import (
    CommitEvent,
    DecisionNode,
    CitationSource,
    LeaverQuestion,
    KanbanTask,
    OrphanRiskFile
)

class KnowledgeExtractor:
    """
    Synthesizes architectural decisions and targeted handover questions from live git activity traces.
    """

    @staticmethod
    def extract_decisions_from_commits(commits: List[CommitEvent]) -> List[DecisionNode]:
        """
        Extracts candidate architectural decisions from live Git commit messages and diffs.
        """
        decisions: List[DecisionNode] = []
        for idx, c in enumerate(commits):
            # Focus on feature, refactor, or architecture commits
            msg_lower = c.message.lower()
            if any(prefix in msg_lower for prefix in ["feat", "arch", "refactor", "security", "chore", "revert"]):
                # Clean title from commit message
                first_line = c.message.split("\n")[0]
                clean_title = first_line[:65]

                citation = CitationSource(
                    id=f"cit-live-commit-{c.sha}",
                    source_type="commit",
                    uri=f"git://local-repo/commits/{c.sha}",
                    title=f"Git Commit {c.sha} by {c.author}",
                    timestamp=c.timestamp,
                    author=c.author,
                    snippet=c.diff_snippet or f"Commit {c.sha}: {c.message}\nFiles: {', '.join(c.files_changed[:5])}"
                )

                dec = DecisionNode(
                    id=f"dec-live-{idx + 1:02d}",
                    title=f"Architecture Contract: {clean_title}",
                    summary=f"Implementation verified from commit {c.sha} altering {len(c.files_changed)} files.",
                    rationale=f"Authored by {c.author}. Code changes: +{c.insertions} / -{c.deletions} lines in repository.",
                    timestamp=c.timestamp,
                    authors=[c.author],
                    status="REVERTED" if "revert" in msg_lower else "ACTIVE",
                    citations=[citation],
                    grounding_score=round(min(0.98, max(0.70, 0.75 + (len(c.files_changed) * 0.02))), 2),
                    has_contradiction=False,
                    quarantined_for_review=False
                )
                decisions.append(dec)

            if len(decisions) >= 5:
                break

        return decisions

    @staticmethod
    def generate_live_leaver_questions(orphan_files: List[OrphanRiskFile]) -> List[LeaverQuestion]:
        """
        Generates targeted 60-second micro-interview questions based on the highest single-author files in the live repo.
        """
        questions: List[LeaverQuestion] = []
        for idx, ofile in enumerate(orphan_files[:3]):
            q = LeaverQuestion(
                id=f"q-live-{idx + 1}",
                file_path=ofile.file_path,
                question=(
                    f"You authored {ofile.blame_percentage}% of {ofile.file_path} ({ofile.single_author_lines}/{ofile.total_lines} lines). "
                    f"What is the primary operational consideration when modifying this file?"
                ),
                context=f"Detected via live git blame: Single-author concentration risk ({ofile.bus_factor_risk}).",
                options=[
                    f"Ensure unit tests in {ofile.file_path} pass and verify backward compatibility before merge.",
                    f"Configuration parameters in {ofile.file_path} require restart of background workers.",
                    f"Standard implementation with no hidden side-effects."
                ],
                suggested_answer=f"Ensure unit tests in {ofile.file_path} pass and verify backward compatibility before merge."
            )
            questions.append(q)

        return questions

    @staticmethod
    def generate_live_kanban(orphan_files: List[OrphanRiskFile], decisions: List[DecisionNode]) -> List[KanbanTask]:
        """
        Generates actionable Day 1, 7, 30 tasks from live repository analysis.
        """
        tasks: List[KanbanTask] = []
        
        # Day 1 Tasks: Review the highest orphan risk files
        for idx, ofile in enumerate(orphan_files[:2]):
            tasks.append(KanbanTask(
                id=f"kb-live-day1-{idx + 1}",
                stage="DAY_1",
                title=f"Inspect Single-Author Module: {ofile.file_path}",
                description=f"Review lines authored by {ofile.primary_author} ({ofile.blame_percentage}% blame) to map core interfaces.",
                priority="URGENT" if ofile.bus_factor_risk == "CRITICAL" else "HIGH",
                category="CODE_WALKTHROUGH",
                linked_file=ofile.file_path,
                completed=False
            ))

        # Day 7 Tasks: Verify recent architecture contracts
        for idx, dec in enumerate(decisions[:2]):
            tasks.append(KanbanTask(
                id=f"kb-live-day7-{idx + 1}",
                stage="DAY_7",
                title=f"Verify Contract: {dec.title[:45]}",
                description=f"Validate integration tests for decision {dec.id} authored by {', '.join(dec.authors)}.",
                priority="HIGH",
                category="ARCHITECTURE",
                completed=False
            ))

        # Day 30 Task: Refactor single-author hotspots
        if orphan_files:
            tasks.append(KanbanTask(
                id="kb-live-day30-01",
                stage="DAY_30",
                title=f"Increase Bus Factor on {orphan_files[0].file_path}",
                description="Pair program with a secondary contributor to eliminate single-author dependency.",
                priority="MEDIUM",
                category="ARCHITECTURE",
                linked_file=orphan_files[0].file_path,
                completed=False
            ))

        return tasks
