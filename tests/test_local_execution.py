"""
Local Execution Test Script - Random Stress Test

Tests the complete Lambda pipeline locally using mock DynamoDB and real Gemini API.
Processes 10 randomly selected conversations from the entire dataset.

Usage:
    python tests/test_local_execution.py          # New random selection
    python tests/test_local_execution.py --rerun  # Rerun with last selection
"""

import json
import os
import sys
import random
import argparse
from pathlib import Path
from datetime import datetime

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


def save_test_selection(conversations):
    """Save the selected conversations for potential rerun."""
    selection_path = Path(__file__).parent / "last_test_selection.json"

    with open(selection_path, "w", encoding="utf-8") as f:
        json.dump(conversations, f, indent=2)

    print(f"✓ Saved test selection to: {selection_path}")


def load_test_selection():
    """Load previously saved test selection."""
    selection_path = Path(__file__).parent / "last_test_selection.json"

    if not selection_path.exists():
        raise FileNotFoundError(
            "No previous test selection found. Run without --rerun first."
        )

    with open(selection_path, "r", encoding="utf-8") as f:
        conversations = json.load(f)

    print(f"✓ Loaded previous test selection: {len(conversations)} conversations")
    return conversations


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
    title = conversation_data.get("title", "Unknown")
    print(f"\n[{index}/{total}] Processing: {title[:60]}...")

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
    """Run the random stress test."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run journal generation stress test")
    parser.add_argument(
        "--rerun",
        action="store_true",
        help="Rerun test with the same conversations from last run",
    )
    args = parser.parse_args()

    print("=" * 80)
    if args.rerun:
        print("RECURSIVE INTELLIGENCE JOURNAL GENERATOR - RERUN TEST")
    else:
        print("RECURSIVE INTELLIGENCE JOURNAL GENERATOR - RANDOM STRESS TEST")
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

    # Load or select conversations
    if args.rerun:
        # Rerun mode - load previous selection
        print("Loading previous test selection...")
        try:
            selected_conversations = load_test_selection()
            sample_size = len(selected_conversations)
            is_rerun = True
        except FileNotFoundError as e:
            print(f"ERROR: {e}")
            return
    else:
        # Normal mode - random selection
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

        # Select 10 random conversations (or all if less than 10)
        sample_size = min(10, len(all_conversations))
        selected_conversations = random.sample(all_conversations, sample_size)

        # Save the selection for potential rerun
        save_test_selection(selected_conversations)
        is_rerun = False

    print()

    print("=" * 80)
    if is_rerun:
        print(f"Rerunning Test: {sample_size} conversations (same as last run)")
    else:
        print(f"Randomly Selected: {sample_size} conversations for stress test")
    print("=" * 80)
    print()

    # Process all selected conversations
    results = []
    successful = 0
    failed = 0

    for idx, conversation in enumerate(selected_conversations, 1):
        success, markdown, metadata, error = process_conversation(
            conversation, idx, sample_size
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
    print("STRESS TEST COMPLETE")
    print("=" * 80)
    print(f"Total: {sample_size} | Success: {successful} | Failed: {failed}")
    print()

    # Write output file
    if is_rerun:
        output_path = Path(__file__).parent / "output_test_random_10_rerun.md"
    else:
        output_path = Path(__file__).parent / "output_test_random_10.md"

    print(f"Writing results to: {output_path}")

    with open(output_path, "w", encoding="utf-8") as f:
        # Write header
        f.write(f"# Journal Generation Stress Test Results\n\n")
        if is_rerun:
            f.write(f"**Test Type:** Rerun (Same Conversations)\n\n")
        else:
            f.write(f"**Test Type:** Random Sample\n\n")
        f.write(f"**Sample Size:** {sample_size}\n\n")
        if not is_rerun:
            f.write(f"**Total Conversations in Dataset:** {len(all_conversations)}\n\n")
        f.write(f"**Successful:** {successful}\n\n")
        f.write(f"**Failed:** {failed}\n\n")
        f.write(f"**Success Rate:** {(successful/sample_size*100):.1f}%\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
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

    if is_rerun:
        print("=" * 80)
        print("TIP: Compare with 'output_test_random_10.md' to see the differences")
        print("=" * 80)
    else:
        print("=" * 80)
        print("TIP: Run with '--rerun' flag to test the same conversations again")
        print("=" * 80)


if __name__ == "__main__":
    main()
