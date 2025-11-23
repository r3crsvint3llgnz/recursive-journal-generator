"""
Conversation Parser Module

Extracts metadata and formats conversation text from raw ChatGPT conversation dictionaries.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any


def parse_conversation(conversation_data: dict) -> dict:
    """
    Parse a ChatGPT conversation dictionary and extract metadata and formatted content.

    Args:
        conversation_data: Raw ChatGPT conversation dictionary with 'mapping' structure

    Returns:
        Dictionary containing:
            - title: Conversation title
            - date: Date in YYYY-MM-DD format
            - time: Time in HH:MM format
            - source_id: Unique conversation ID
            - raw_text: Clean combined text for AI processing
            - transcript: Formatted markdown transcript with User/Assistant labels
    """
    # Extract basic metadata
    title = conversation_data.get("title", "Untitled Conversation")
    conversation_id = conversation_data.get("id", "unknown")
    create_time = conversation_data.get("create_time")

    # Handle timestamp conversion
    if create_time:
        dt = datetime.fromtimestamp(create_time)
        date_str = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%H:%M")
    else:
        # Default to current time if missing
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")

    # Extract and sort messages from mapping
    mapping = conversation_data.get("mapping", {})
    messages = _extract_messages_from_mapping(mapping)

    # Generate raw text and transcript
    raw_text = _generate_raw_text(messages)
    transcript = _generate_transcript(messages)

    return {
        "title": title,
        "date": date_str,
        "time": time_str,
        "source_id": conversation_id,
        "raw_text": raw_text,
        "transcript": transcript,
    }


def _extract_messages_from_mapping(mapping: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract messages from ChatGPT's tree-structured mapping and sort chronologically.

    ChatGPT conversations use a tree structure with parent links. This function
    traverses the structure and sorts messages by creation time.

    Args:
        mapping: The 'mapping' dictionary from ChatGPT JSON

    Returns:
        List of message dictionaries sorted by create_time
    """
    messages = []

    for node_id, node_data in mapping.items():
        message = node_data.get("message")
        if not message:
            continue

        # Extract relevant message data
        content = message.get("content")
        if not content:
            continue

        # Get text parts from content
        parts = content.get("parts", [])
        if not parts or not any(parts):
            continue

        # Combine all text parts
        text = "\n".join(str(part) for part in parts if part)
        if not text.strip():
            continue

        messages.append(
            {
                "id": message.get("id", node_id),
                "author_role": message.get("author", {}).get("role", "unknown"),
                "create_time": message.get("create_time", 0),
                "text": text.strip(),
            }
        )

    # Sort by creation time to ensure chronological order
    messages.sort(key=lambda m: m["create_time"])

    return messages


def _generate_raw_text(messages: List[Dict[str, Any]]) -> str:
    """
    Generate clean combined text for AI processing.

    Args:
        messages: List of sorted message dictionaries

    Returns:
        Clean text combining user and assistant messages
    """
    text_parts = []

    for msg in messages:
        role = msg["author_role"]
        text = msg["text"]

        if role == "user":
            text_parts.append(f"User: {text}")
        elif role == "assistant":
            text_parts.append(f"Assistant: {text}")

    return "\n\n".join(text_parts)


def _generate_transcript(messages: List[Dict[str, Any]]) -> str:
    """
    Generate formatted Markdown transcript with User/Assistant labels.

    Args:
        messages: List of sorted message dictionaries

    Returns:
        Markdown-formatted transcript
    """
    transcript_parts = []

    for msg in messages:
        role = msg["author_role"]
        text = msg["text"]

        if role == "user":
            transcript_parts.append(f"**User:** {text}")
        elif role == "assistant":
            transcript_parts.append(f"**Assistant:** {text}")

    return "\n\n".join(transcript_parts)
