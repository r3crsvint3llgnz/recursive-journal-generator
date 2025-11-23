"""
Gemini Processor Module

Interfaces with Google Gemini API to rewrite conversation text into journal entries.
"""

import os
import json
import time
from typing import Dict, Any, Optional
import google.generativeai as genai
from google.api_core import exceptions

# System instruction for Gemini
SYSTEM_INSTRUCTION = """You are a reflective personal journalist. Analyze the provided conversation and rewrite it as a first-person journal entry. Frame insights as 'I realized' or 'I decided'. Use bolding for key points. If the conversation clearly indicates the user is asking on behalf of someone else (e.g., 'my wife,' 'my friend'), frame the journal entry as 'I helped [person] explore...' or 'I researched [topic] for [person]...' instead of claiming the goal as your own. Maintain the first-person perspective of the user. Your output MUST be valid JSON."""

# Response schema to enforce structured output
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "A concise title for the journal entry",
        },
        "topic": {
            "type": "string",
            "description": "The main topic or theme of the conversation",
        },
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Relevant tags for categorization",
        },
        "rewritten_entry_body": {
            "type": "string",
            "description": "The first-person journal entry with markdown formatting",
        },
    },
    "required": ["title", "topic", "tags", "rewritten_entry_body"],
}


def process_with_gemini(text: str, model_name: str = "gemini-2.5-flash") -> dict:
    """
    Process conversation text with Gemini API to generate a journal entry.

    Args:
        text: The conversation text to process
        model_name: The Gemini model to use (default: gemini-2.5-flash)

    Returns:
        Dictionary containing:
            - title: Journal entry title
            - topic: Main topic/theme
            - tags: List of relevant tags
            - rewritten_entry_body: First-person journal entry with markdown

    Raises:
        ValueError: If API key is missing or response is invalid
        Exception: For other API errors
    """
    # Get API key from environment
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")

    # Configure the Gemini client
    genai.configure(api_key=api_key)

    # Initialize the model with system instruction
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=SYSTEM_INSTRUCTION,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": RESPONSE_SCHEMA,
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        },
    )

    # Generate the journal entry prompt
    prompt = f"""Convert the following conversation into a reflective first-person journal entry:

{text}

Remember to:
- Write in first person ("I realized", "I decided", etc.)
- Bold key insights and important points
- Maintain the reflective, introspective tone
- Structure the entry clearly
"""

    # Safety settings - disable filters for personal journal content
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    # Retry logic with rate limit handling
    max_retries = 3
    retry_delay = 10  # seconds

    for attempt in range(max_retries):
        try:
            # Generate content
            response = model.generate_content(prompt, safety_settings=safety_settings)

            # Parse the JSON response
            if not response.text:
                raise ValueError("Empty response from Gemini API")

            result = json.loads(response.text)

            # Validate the response structure
            required_fields = ["title", "topic", "tags", "rewritten_entry_body"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field in response: {field}")

            return result

        except exceptions.ResourceExhausted as e:
            # Rate limit hit (429 error)
            if attempt < max_retries - 1:
                print(
                    f"Rate limit hit (attempt {attempt + 1}/{max_retries}), waiting {retry_delay}s..."
                )
                time.sleep(retry_delay)
                continue
            else:
                raise Exception(
                    f"Rate limit exceeded after {max_retries} attempts: {str(e)}"
                )

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse Gemini response as JSON: {e}")

        except Exception as e:
            # For other errors, don't retry
            raise Exception(f"Gemini API error: {str(e)}")

    # Should never reach here, but just in case
    raise Exception(f"Failed after {max_retries} attempts")


def process_with_gemini_fallback(text: str) -> dict:
    """
    Process conversation with Gemini, falling back to alternative model on failure.

    Tries gemini-2.5-flash first (latest stable), falls back to gemini-2.0-flash-exp if needed.

    Args:
        text: The conversation text to process

    Returns:
        Dictionary with journal entry data
    """
    try:
        return process_with_gemini(text, model_name="gemini-2.5-flash")
    except Exception as e:
        print(f"Primary model (gemini-2.5-flash) failed, trying fallback: {e}")
        try:
            return process_with_gemini(text, model_name="gemini-2.0-flash-exp")
        except Exception as fallback_error:
            # Print available models for debugging
            try:
                available_models = [m.name for m in genai.list_models()]
                print(f"Available Models: {available_models}")
            except Exception:
                print("Could not list available models")
            raise Exception(f"Both models failed. Last error: {fallback_error}")
