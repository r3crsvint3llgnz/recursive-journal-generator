"""Helpers for normalizing uploaded conversation exports."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from src.conversation_parser import parse_conversation


def extract_user_and_import_from_key(object_key: str) -> Tuple[str, str]:
    """Derive user_id and import_id from an S3 object key."""
    parts = object_key.split("/")
    if len(parts) < 3 or parts[0] != "imports":
        raise ValueError("Object key must follow imports/<user_id>/<file>.json structure")

    user_id = parts[1]
    filename = parts[-1]
    if not user_id:
        raise ValueError("Missing user id in object key")

    import_id = filename.rsplit(".", 1)[0] or filename
    return user_id, import_id


def coerce_conversations(payload: Any) -> List[Dict[str, Any]]:
    """Ensure payload is a list of conversations."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        return [payload]
    raise ValueError("Conversation payload must be an object or list of objects")


def build_conversation_items(
    conversations: List[Dict[str, Any]],
    user_id: str,
    import_id: str,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Convert raw conversations into DynamoDB items."""
    now_iso = datetime.now(timezone.utc).isoformat()
    items: List[Dict[str, Any]] = []
    failed_ids: List[str] = []

    for convo in conversations:
        try:
            parsed = parse_conversation(convo)
        except Exception as exc:  # pragma: no cover - parse already unit tested
            convo_id = convo.get("id", "unknown")
            failed_ids.append(f"{convo_id}: {exc}")
            continue

        source_id = parsed.get("source_id", "unknown")
        sort_key = f"{parsed.get('date', 'unknown')}#{source_id}"

        item = {
            "user_id": user_id,
            "sort_key": sort_key,
            "conversation_id": source_id,
            "import_id": import_id,
            "title": parsed.get("title"),
            "date": parsed.get("date"),
            "time": parsed.get("time"),
            "transcript": parsed.get("transcript"),
            "raw_text": parsed.get("raw_text"),
            "status": "parsed",
            "created_at": now_iso,
        }
        items.append(item)

    return items, failed_ids


def parse_json_payload(body: bytes) -> Any:
    """Load JSON bytes from S3."""
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON payload: {exc}") from exc
