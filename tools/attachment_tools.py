"""
ABOUTME: Email attachment management tools for Apple Mail MCP Server
Provides tools for listing and saving email attachments.
"""

from mcp_instance import mcp
from utils.applescript import run_applescript_file, inject_preferences


@mcp.tool()
@inject_preferences
def list_email_attachments(
    account: str,
    subject_keyword: str,
    max_results: int = 1
) -> str:
    """
    List attachments for emails matching a subject keyword.

    Args:
        account: Account name (e.g., "Gmail", "Work", "Personal")
        subject_keyword: Keyword to search for in email subjects
        max_results: Maximum number of matching emails to check (default: 1)

    Returns:
        List of attachments with their names and sizes
    """
    result = run_applescript_file(
        "attachment/list_email_attachments.applescript",
        account,
        subject_keyword,
        max_results
    )
    return result


@mcp.tool()
@inject_preferences
def save_email_attachment(
    account: str,
    subject_keyword: str,
    attachment_name: str,
    save_path: str
) -> str:
    """
    Save a specific attachment from an email to disk.

    Args:
        account: Account name (e.g., "Gmail", "Work", "Personal")
        subject_keyword: Keyword to search for in email subjects
        attachment_name: Name of the attachment to save
        save_path: Full path where to save the attachment

    Returns:
        Confirmation message with save location
    """
    result = run_applescript_file(
        "attachment/save_email_attachment.applescript",
        account,
        subject_keyword,
        attachment_name,
        save_path
    )
    return result
