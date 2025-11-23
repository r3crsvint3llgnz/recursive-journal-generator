"""
AWS Lambda Handler for Recursive Intelligence Journal Generator

Main entry point that orchestrates credit checking, parsing, AI processing, and rendering.
"""

import json
import os
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError

# Import local modules
from src.conversation_parser import parse_conversation
from src.gemini_processor import process_with_gemini_fallback
from src.template_engine import render_journal_entry_safe

# Initialize DynamoDB outside handler for connection reuse
dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("USER_CREDITS_TABLE_NAME", "RIJG-UserCredits")
credits_table = dynamodb.Table(table_name)

# Default free credits for new users
DEFAULT_FREE_CREDITS = 5


def check_and_deduct_credits(user_id: str) -> bool:
    """
    Check if user has credits and deduct one if available.

    For MVP: Creates new users with free credits automatically.

    Args:
        user_id: Unique user identifier

    Returns:
        True if credit was successfully deducted, False if insufficient credits
    """
    # Mock credit check for local testing
    if os.environ.get("AWS_SAM_LOCAL") == "true":
        print(f"[MOCK] Bypassing credit check for local testing (user: {user_id})")
        return True

    try:
        # Try to get the user's current credits
        response = credits_table.get_item(Key={"user_id": user_id})

        if "Item" not in response:
            # User doesn't exist - create them with free credits (MVP behavior)
            credits_table.put_item(
                Item={"user_id": user_id, "credit_balance": DEFAULT_FREE_CREDITS}
            )
            print(
                f"Created new user {user_id} with {DEFAULT_FREE_CREDITS} free credits"
            )
            # Fetch the newly created item
            response = credits_table.get_item(Key={"user_id": user_id})

        current_balance = response["Item"]["credit_balance"]

        # Check if user has credits
        if current_balance <= 0:
            print(f"User {user_id} has insufficient credits: {current_balance}")
            return False

        # Deduct one credit
        new_balance = current_balance - 1
        credits_table.update_item(
            Key={"user_id": user_id},
            UpdateExpression="SET credit_balance = :new_balance",
            ExpressionAttributeValues={":new_balance": new_balance},
        )

        print(f"Deducted credit for {user_id}. New balance: {new_balance}")
        return True

    except ClientError as e:
        print(f"DynamoDB error for user {user_id}: {e}")
        # In case of DB errors, allow the request (fail open for MVP)
        return True
    except Exception as e:
        print(f"Unexpected error checking credits for {user_id}: {e}")
        return True


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for journal generation.

    Args:
        event: API Gateway event with conversation JSON in body
        context: Lambda context object

    Returns:
        API Gateway response with status code and body
    """
    try:
        # Parse the request body
        body = event.get("body", "{}")

        # Handle both string and dict body
        if isinstance(body, str):
            body = json.loads(body)

        # Extract user ID (default to test-user for MVP)
        user_id = body.get("user_id", "test-user")

        # Check and deduct credits
        if not check_and_deduct_credits(user_id):
            return {
                "statusCode": 402,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps(
                    {
                        "error": "Insufficient credits",
                        "message": "You have no remaining credits. Please purchase more to continue.",
                    }
                ),
            }

        # Extract conversation data
        conversation_data = body.get("conversation", body)

        # THE PIPELINE
        try:
            # Step 1: Parse the conversation
            print("Step 1: Parsing conversation...")
            parsed_data = parse_conversation(conversation_data)
            print(f"Parsed conversation: {parsed_data.get('title', 'Unknown')}")

            # Step 2: Process with Gemini
            print("Step 2: Processing with Gemini...")
            gemini_data = process_with_gemini_fallback(parsed_data["raw_text"])
            print(f"Gemini processing complete: {gemini_data.get('title', 'Unknown')}")

            # Step 3: Merge the data
            print("Step 3: Merging data...")
            final_data = {**parsed_data, **gemini_data}

            # Step 4: Render the Markdown
            print("Step 4: Rendering Markdown...")
            markdown_content = render_journal_entry_safe(final_data)
            print(f"Rendered {len(markdown_content)} characters of Markdown")

            # Return success response
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps(
                    {
                        "success": True,
                        "markdown_content": markdown_content,
                        "metadata": {
                            "title": final_data.get("title"),
                            "date": final_data.get("date"),
                            "topic": final_data.get("topic"),
                            "tags": final_data.get("tags"),
                            "source_id": final_data.get("source_id"),
                        },
                    }
                ),
            }

        except ValueError as e:
            # Validation or parsing errors
            print(f"Validation error: {e}")
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({"error": "Invalid input", "message": str(e)}),
            }

        except Exception as e:
            # Processing errors (Gemini, template rendering, etc.)
            print(f"Processing error: {e}")
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({"error": "Processing failed", "message": str(e)}),
            }

    except json.JSONDecodeError as e:
        # Invalid JSON in request body
        print(f"JSON decode error: {e}")
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {"error": "Invalid JSON", "message": "Request body must be valid JSON"}
            ),
        }

    except Exception as e:
        # Catch-all for unexpected errors
        print(f"Unexpected error: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                }
            ),
        }
