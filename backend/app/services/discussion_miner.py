"""
Discussion Miner & Multi-Platform Chat Parser
Parses Slack exports, Discord channel dumps, and raw conversation transcripts
into validated DiscussionMessage models for NLI Contradiction Radar processing.
"""

from typing import List, Dict, Any, Optional
import json
import re
from datetime import datetime, timezone
from ..models.schemas import DiscussionMessage

class DiscussionMiner:
    """
    Ingests and normalizes discussion traces from Slack, Discord, and raw text logs.
    """

    @staticmethod
    def parse_slack_export(raw_json: Any, channel: str = "general") -> List[DiscussionMessage]:
        """
        Parses official Slack JSON export files (messages.json).
        Converts Slack epoch timestamps (e.g. '1770908700.000100') to ISO 8601 strings.
        """
        messages: List[DiscussionMessage] = []
        data_list = raw_json if isinstance(raw_json, list) else [raw_json]

        for idx, item in enumerate(data_list):
            if not isinstance(item, dict):
                continue

            # Skip subtype bot/join notifications
            if item.get("subtype") in ["channel_join", "channel_leave", "pinned_info"]:
                continue

            text = item.get("text", "").strip()
            if not text:
                continue

            # Extract author name
            author = "Unknown Contributor"
            user_profile = item.get("user_profile")
            if isinstance(user_profile, dict):
                author = user_profile.get("real_name") or user_profile.get("name") or author
            elif item.get("username"):
                author = item.get("username")
            elif item.get("user"):
                author = f"User_{item.get('user')}"

            # Convert Slack epoch 'ts' to ISO timestamp
            ts_val = item.get("ts", "")
            iso_timestamp = datetime.now(timezone.utc).isoformat()
            try:
                if ts_val:
                    epoch_float = float(ts_val)
                    iso_timestamp = datetime.fromtimestamp(epoch_float, tz=timezone.utc).isoformat()
            except Exception:
                iso_timestamp = datetime.now(timezone.utc).isoformat()

            msg_id = item.get("client_msg_id") or f"slack-msg-{idx + 1:03d}"
            thread_ts = item.get("thread_ts")

            # Check security tag
            sec_tag = "PUBLIC"
            if any(term in text.lower() for term in ["sk_live", "password", "secret", "confidential", "salary"]):
                sec_tag = "CONFIDENTIAL_HR" if "salary" in text.lower() else "INFRA_KEYS"

            messages.append(DiscussionMessage(
                id=f"slack-{msg_id[:12]}",
                author=author,
                channel=channel,
                timestamp=iso_timestamp,
                text=text,
                thread_id=thread_ts,
                security_tag=sec_tag
            ))

        return messages

    @staticmethod
    def parse_discord_export(raw_json: Any, channel: str = "dev-chat") -> List[DiscussionMessage]:
        """
        Parses Discord Chat Exporter JSON outputs.
        """
        messages: List[DiscussionMessage] = []
        data_list = raw_json if isinstance(raw_json, list) else [raw_json]

        # If data is wrapped in a messages property
        if isinstance(raw_json, dict) and "messages" in raw_json:
            data_list = raw_json["messages"]

        for idx, item in enumerate(data_list):
            if not isinstance(item, dict):
                continue

            text = item.get("content", "").strip()
            if not text:
                continue

            author = "Discord Contributor"
            author_obj = item.get("author")
            if isinstance(author_obj, dict):
                author = author_obj.get("nickname") or author_obj.get("name") or author_obj.get("username") or author

            ts_raw = item.get("timestamp", "")
            iso_ts = ts_raw if ts_raw else datetime.now(timezone.utc).isoformat()

            messages.append(DiscussionMessage(
                id=f"discord-{item.get('id', idx + 1)}",
                author=author,
                channel=channel,
                timestamp=iso_ts,
                text=text,
                thread_id=item.get("reference", {}).get("messageId"),
                security_tag="PUBLIC"
            ))

        return messages

    @staticmethod
    def parse_raw_transcript(transcript_text: str, default_channel: str = "team-sync") -> List[DiscussionMessage]:
        """
        Parses plain text transcripts using regex pattern matching:
        Example: [2026-02-12 14:30] Alice Vance: Text here
        Or: Alice Vance: Text here
        """
        messages: List[DiscussionMessage] = []
        pattern = re.compile(
            r"(?:\[(?P<timestamp>[^\]]+)\]\s*)?(?P<author>[A-Za-z0-9_\s\.\-]+?):\s*(?P<text>.+)",
            re.MULTILINE
        )

        for idx, match in enumerate(pattern.finditer(transcript_text)):
            author = match.group("author").strip()
            text = match.group("text").strip()
            ts_str = match.group("timestamp")

            iso_timestamp = datetime.now(timezone.utc).isoformat()
            if ts_str:
                try:
                    # Attempt ISO parsing or common formats
                    iso_timestamp = datetime.fromisoformat(ts_str.replace("Z", "+00:00")).isoformat()
                except Exception:
                    iso_timestamp = datetime.now(timezone.utc).isoformat()

            messages.append(DiscussionMessage(
                id=f"raw-msg-{idx + 1:03d}",
                author=author,
                channel=default_channel,
                timestamp=iso_timestamp,
                text=text,
                security_tag="PUBLIC"
            ))

        return messages

    @classmethod
    def ingest_generic(cls, content: str, channel: str = "team-discussions") -> List[DiscussionMessage]:
        """
        Auto-detects format (Slack JSON, Discord JSON, generic JSON list, or text transcript).
        """
        content_stripped = content.strip()
        if content_stripped.startswith(("{", "[")):
            try:
                parsed_json = json.loads(content_stripped)
                if isinstance(parsed_json, list) and len(parsed_json) > 0:
                    first_item = parsed_json[0]
                    if isinstance(first_item, dict):
                        if "client_msg_id" in first_item or "ts" in first_item:
                            return cls.parse_slack_export(parsed_json, channel)
                        elif "content" in first_item and "author" in first_item:
                            return cls.parse_discord_export(parsed_json, channel)
                        elif "text" in first_item and "author" in first_item:
                            # Standard simplified JSON
                            return [
                                DiscussionMessage(
                                    id=f"disc-{idx + 1:03d}",
                                    author=item.get("author", "Team Member"),
                                    channel=item.get("channel", channel),
                                    timestamp=item.get("timestamp", datetime.now(timezone.utc).isoformat()),
                                    text=item.get("text", ""),
                                    security_tag=item.get("security_tag", "PUBLIC")
                                )
                                for idx, item in enumerate(parsed_json)
                                if item.get("text")
                            ]
                elif isinstance(parsed_json, dict) and "messages" in parsed_json:
                    return cls.parse_discord_export(parsed_json, channel)
            except Exception:
                pass

        # Fallback to raw text transcript parser
        return cls.parse_raw_transcript(content, channel)
