"""
Local Execution Test Script - Batch Mode

Tests the complete Lambda pipeline locally using mock DynamoDB and real Gemini API.
Processes all conversations from a randomly selected date.
"""

import json
import os
import sys
import random
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set mocking flag for local execution
os.environ["AWS_SAM_LOCAL"] = "true"
os.environ["USER_CREDITS_TABLE_NAME"] = "RIJG-UserCredits"

# Import after setting environment variables
from src.app import lambda_handler


def load_all_conversations():
    """Load all conversations from the conversations.json file."""
    data_path = (
        Path(__file__).parent.parent
        / "data"
        / "raw_conversations"
        / "conversations.json"
    )

    if not data_path.exists():
        raise FileNotFoundError(f"Test data not found at: {data_path}")

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Ensure we have a list of conversations
    if not isinstance(data, list):
        data = [data]

    return data


def group_conversations_by_date(conversations):
    """
    Group conversations by their creation date (YYYY-MM-DD).

    Args:
        conversations: List of conversation dictionaries

    Returns:
        Dictionary mapping date strings to lists of conversations
    """
    grouped = defaultdict(list)

    for conv in conversations:
        create_time = conv.get("create_time")
        if create_time:
            # Convert Unix timestamp to date string
            dt = datetime.fromtimestamp(create_time)
            date_str = dt.strftime("%Y-%m-%d")
        else:
            # Use current date if no timestamp
            date_str = datetime.now().strftime("%Y-%m-%d")

        grouped[date_str].append(conv)

    return dict(grouped)


def process_conversation(conversation_data, index, total):
    """
    Process a single conversation through the Lambda handler.

    Args:
        conversation_data: Conversation dictionary
        index: Current conversation number (1-based)
        total: Total number of conversations

    Returns:
        Tuple of (success: bool, markdown: str or None, metadata: dict or None, error: str or None)
    """
    print(
        f"\n[{index}/{total}] Processing: {conversation_data.get('title', 'Unknown')[:60]}..."
    )

    # Construct Lambda event
    event = {
        "body": json.dumps(
            {"user_id": "test-user-local", "conversation": conversation_data}
        )
    }

    try:
        response = lambda_handler(event, None)
        response_body = json.loads(response["body"])

        if response["statusCode"] == 200:
            print(f"  ✓ SUCCESS")
            return (
                True,
                response_body.get("markdown_content"),
                response_body.get("metadata"),
                None,
            )
        else:
            error_msg = response_body.get(
                "message", response_body.get("error", "Unknown error")
            )
            print(f"  ✗ FAILED - Status {response['statusCode']}: {error_msg}")
            return (False, None, None, error_msg)

    except Exception as e:
        print(f"  ✗ EXCEPTION: {type(e).__name__}: {str(e)}")
        return (False, None, None, str(e))


def main():
    """Run the batch test execution."""
    print("=" * 80)
    print("RECURSIVE INTELLIGENCE JOURNAL GENERATOR - BATCH TEST")
    print("=" * 80)
    print()

    # Verify environment variables
    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        return

    print("✓ Environment variables loaded")
    print(f"✓ AWS_SAM_LOCAL: {os.environ.get('AWS_SAM_LOCAL')}")
    print()

    # Load all conversations
    print("Loading conversations...")
    try:
        all_conversations = load_all_conversations()
        print(f"✓ Loaded {len(all_conversations)} total conversations")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in conversations.json: {e}")
        return
    print()

    # Group by date
    print("Grouping conversations by date...")
    grouped = group_conversations_by_date(all_conversations)
    print(f"✓ Found conversations across {len(grouped)} different dates")

    # Display date summary
    for date_str in sorted(grouped.keys()):
        print(f"  - {date_str}: {len(grouped[date_str])} conversations")
    print()

    # Select random date
    selected_date = random.choice(list(grouped.keys()))
    selected_conversations = grouped[selected_date]

    print("=" * 80)
    print(
        f"Selected Date: {selected_date} | Conversations found: {len(selected_conversations)}"
    )
    print("=" * 80)
    print()

    # Process all conversations from selected date
    results = []
    successful = 0
    failed = 0

    for idx, conversation in enumerate(selected_conversations, 1):
        success, markdown, metadata, error = process_conversation(
            conversation, idx, len(selected_conversations)
        )

        results.append(
            {
                "success": success,
                "markdown": markdown,
                "metadata": metadata,
                "error": error,
                "title": conversation.get("title", "Unknown"),
            }
        )

        if success:
            successful += 1
        else:
            failed += 1

    # Summary
    print()
    print("=" * 80)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 80)
    print(
        f"Total: {len(selected_conversations)} | Success: {successful} | Failed: {failed}"
    )
    print()

    # Write output file
    output_path = Path(__file__).parent / f"output_test_{selected_date}.md"

    print(f"Writing results to: {output_path}")

    with open(output_path, "w", encoding="utf-8") as f:
        # Write header
        f.write(f"# Journal Generation Test Results\n\n")
        f.write(f"**Date:** {selected_date}\n\n")
        f.write(f"**Total Conversations:** {len(selected_conversations)}\n\n")
        f.write(f"**Successful:** {successful}\n\n")
        f.write(f"**Failed:** {failed}\n\n")
        f.write("---\n\n")

        # Write each result
        for idx, result in enumerate(results, 1):
            f.write(f"## Entry {idx}: {result['title']}\n\n")

            if result["success"]:
                f.write(f"**Status:** ✓ Success\n\n")

                if result["metadata"]:
                    f.write(f"**Topic:** {result['metadata'].get('topic', 'N/A')}\n\n")
                    f.write(
                        f"**Tags:** {', '.join(result['metadata'].get('tags', []))}\n\n"
                    )

                f.write("### Generated Journal Entry\n\n")
                f.write(result["markdown"])
                f.write("\n\n")
            else:
                f.write(f"**Status:** ✗ Failed\n\n")
                f.write(f"**Error:** {result['error']}\n\n")

            f.write("---\n\n")

    print(f"✓ Output written to: {output_path}")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
