"""
Template Engine Module

Loads and renders Jinja2 templates for Obsidian journal entries.
"""

import os
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound


def render_journal_entry(data: dict) -> str:
    """
    Render an Obsidian journal entry from template with provided data.

    Args:
        data: Dictionary containing template variables:
            - title: Journal entry title
            - date: Date in YYYY-MM-DD format
            - time: Time in HH:MM format
            - topic: Main topic/theme
            - tags: List of tags
            - source_id: Original conversation ID
            - rewritten_entry_body: Main journal content
            - transcript: Raw conversation transcript

    Returns:
        Rendered Markdown string ready for Obsidian

    Raises:
        TemplateNotFound: If the template file cannot be found
        Exception: For other template rendering errors
    """
    try:
        # Get the directory containing this module
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Templates directory is adjacent to src/
        templates_dir = os.path.join(os.path.dirname(current_dir), "templates")

        # Create Jinja2 environment with FileSystemLoader
        env = Environment(
            loader=FileSystemLoader(templates_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

        # Load the template
        template = env.get_template("obsidian_journal.md")

        # Render with provided data
        rendered = template.render(**data)

        return rendered

    except TemplateNotFound as e:
        raise TemplateNotFound(f"Template file not found: {e}")
    except Exception as e:
        raise Exception(f"Error rendering template: {str(e)}")


def validate_template_data(data: dict) -> None:
    """
    Validate that required fields are present in template data.

    Args:
        data: Dictionary to validate

    Raises:
        ValueError: If required fields are missing
    """
    required_fields = [
        "title",
        "date",
        "time",
        "topic",
        "tags",
        "source_id",
        "rewritten_entry_body",
        "transcript",
    ]

    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        raise ValueError(
            f"Missing required template fields: {', '.join(missing_fields)}"
        )

    # Validate tags is a list
    if not isinstance(data.get("tags"), list):
        raise ValueError("'tags' must be a list")


def render_journal_entry_safe(data: dict) -> str:
    """
    Render journal entry with validation.

    Args:
        data: Template data dictionary

    Returns:
        Rendered Markdown string

    Raises:
        ValueError: If data validation fails
        Exception: For rendering errors
    """
    validate_template_data(data)
    return render_journal_entry(data)
