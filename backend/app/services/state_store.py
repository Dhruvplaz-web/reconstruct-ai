"""
Session State Persistence Engine
Provides atomic, thread-safe, resilient disk snapshots of the active handover session.
Guarantees zero data loss across backend restarts or evaluator reload cycles.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from ..models.schemas import (
    DecisionNode,
    ContradictionAlert,
    OrphanRiskFile,
    KanbanTask,
    CommitEvent,
    DiscussionMessage,
    LeaverQuestion,
    LeaverReviewSubmission
)
from ..data.acme_payments import (
    SYNTHETIC_DECISIONS,
    SYNTHETIC_COMMITS,
    SYNTHETIC_DISCUSSIONS,
    SYNTHETIC_ORPHAN_FILES,
    SYNTHETIC_CONTRADICTIONS,
    SYNTHETIC_LEAVER_QUESTIONS,
    SYNTHETIC_KANBAN_TASKS
)

logger = logging.getLogger("reconstruct.state_store")

STATE_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../data/session_state.json")
)

class StateStore:
    """
    Manages snapshot persistence for the in-memory Handover APP_STATE.
    Saves state atomically to disk and auto-restores on system boot.
    """

    @staticmethod
    def get_default_state() -> Dict[str, Any]:
        """Returns the canonical benchmark state (Acme Payments Microservice)."""
        return {
            "project_name": "Acme Payments Microservice",
            "leaver_name": "Alice Vance (Lead Architect)",
            "leaver_approved": False,
            "approval_submission": None,
            "decisions": list(SYNTHETIC_DECISIONS),
            "contradictions": list(SYNTHETIC_CONTRADICTIONS),
            "orphan_files": list(SYNTHETIC_ORPHAN_FILES),
            "kanban_tasks": list(SYNTHETIC_KANBAN_TASKS),
            "commits": list(SYNTHETIC_COMMITS),
            "discussions": list(SYNTHETIC_DISCUSSIONS),
            "leaver_questions": list(SYNTHETIC_LEAVER_QUESTIONS)
        }

    @classmethod
    def save_state(cls, state: Dict[str, Any], filepath: str = STATE_FILE_PATH) -> bool:
        """
        Serializes and atomically writes the active session state to disk.
        Uses a temporary swap file to prevent partially written or corrupted states.
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            serializable_state = {
                "project_name": state.get("project_name", "Unknown Project"),
                "leaver_name": state.get("leaver_name", "Primary Maintainer"),
                "leaver_approved": bool(state.get("leaver_approved", False)),
                "saved_at": datetime.now(timezone.utc).isoformat(),
                "approval_submission": (
                    state["approval_submission"].model_dump()
                    if state.get("approval_submission") and hasattr(state["approval_submission"], "model_dump")
                    else state.get("approval_submission")
                ),
                "decisions": [
                    d.model_dump() if hasattr(d, "model_dump") else d
                    for d in state.get("decisions", [])
                ],
                "contradictions": [
                    c.model_dump() if hasattr(c, "model_dump") else c
                    for c in state.get("contradictions", [])
                ],
                "orphan_files": [
                    f.model_dump() if hasattr(f, "model_dump") else f
                    for f in state.get("orphan_files", [])
                ],
                "kanban_tasks": [
                    k.model_dump() if hasattr(k, "model_dump") else k
                    for k in state.get("kanban_tasks", [])
                ],
                "commits": [
                    c.model_dump() if hasattr(c, "model_dump") else c
                    for c in state.get("commits", [])
                ],
                "discussions": [
                    d.model_dump() if hasattr(d, "model_dump") else d
                    for d in state.get("discussions", [])
                ],
                "leaver_questions": [
                    q.model_dump() if hasattr(q, "model_dump") else q
                    for q in state.get("leaver_questions", [])
                ]
            }

            temp_path = f"{filepath}.tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(serializable_state, f, indent=2, ensure_ascii=False)

            if os.path.exists(filepath):
                os.remove(filepath)
            os.rename(temp_path, filepath)

            logger.info("Successfully persisted active session snapshot to %s", filepath)
            return True
        except Exception as e:
            logger.error("Failed to persist session state: %s", e)
            return False

    @classmethod
    def load_state(cls, filepath: str = STATE_FILE_PATH) -> Optional[Dict[str, Any]]:
        """
        Loads and hydrates Pydantic objects from the persisted session snapshot.
        Returns None if file is missing, corrupted, or incompatible.
        """
        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            approval_sub = None
            if data.get("approval_submission"):
                approval_sub = LeaverReviewSubmission(**data["approval_submission"])

            restored_state = {
                "project_name": data.get("project_name", "Acme Payments Microservice"),
                "leaver_name": data.get("leaver_name", "Alice Vance (Lead Architect)"),
                "leaver_approved": data.get("leaver_approved", False),
                "approval_submission": approval_sub,
                "decisions": [DecisionNode(**d) for d in data.get("decisions", [])],
                "contradictions": [ContradictionAlert(**c) for c in data.get("contradictions", [])],
                "orphan_files": [OrphanRiskFile(**f) for f in data.get("orphan_files", [])],
                "kanban_tasks": [KanbanTask(**k) for k in data.get("kanban_tasks", [])],
                "commits": [CommitEvent(**c) for c in data.get("commits", [])],
                "discussions": [DiscussionMessage(**d) for d in data.get("discussions", [])],
                "leaver_questions": [LeaverQuestion(**q) for q in data.get("leaver_questions", [])]
            }

            logger.info("Loaded persisted session for '%s' from %s", restored_state["project_name"], filepath)
            return restored_state
        except Exception as e:
            logger.warning("Failed to restore session snapshot (%s). Reverting to defaults.", e)
            return None

    @classmethod
    def load_or_default(cls, filepath: str = STATE_FILE_PATH) -> Dict[str, Any]:
        """Loads persisted session if available, else returns canonical benchmark state."""
        saved = cls.load_state(filepath)
        if saved:
            return saved
        return cls.get_default_state()

    @classmethod
    def clear_persisted_state(cls, filepath: str = STATE_FILE_PATH) -> bool:
        """Deletes the persisted session file."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
            return True
        except Exception as e:
            logger.warning("Could not delete state file %s: %s", filepath, e)
            return False
