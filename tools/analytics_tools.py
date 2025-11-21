"""
ABOUTME: Email analytics and statistics tools for Apple Mail MCP Server
Provides tools for getting email statistics, analytics, and exporting email data.
"""

import os
from typing import Optional, Dict
from mcp_instance import mcp
from utils.applescript import run_applescript_file, inject_preferences


@mcp.tool()
@inject_preferences
def get_unread_count() -> Dict[str, int]:
    """
    Get the count of unread emails for each account.

    Returns:
        Dictionary mapping account names to unread email counts
    """
    result = run_applescript_file("analytics/get_unread_count.applescript")

    # Parse the result
    counts = {}
    for item in result.split('|'):
        if ':' in item:
            account, count = item.split(':', 1)
            if count != "ERROR":
                counts[account] = int(count)
            else:
                counts[account] = -1  # Error indicator

    return counts


@mcp.tool()
@inject_preferences
def get_statistics(
    account: str,
    scope: str = "account_overview",
    sender: Optional[str] = None,
    mailbox: Optional[str] = None,
    days_back: int = 30
) -> str:
    """
    Get comprehensive email statistics and analytics.

    Args:
        account: Account name (e.g., "Gmail", "Work")
        scope: Analysis scope: "account_overview", "sender_stats", "mailbox_breakdown"
        sender: Specific sender for "sender_stats" scope
        mailbox: Specific mailbox for "mailbox_breakdown" scope
        days_back: Number of days to analyze (default: 30, 0 = all time)

    Returns:
        Formatted statistics report with metrics and insights
    """
    # Validate scope
    valid_scopes = ["account_overview", "sender_stats", "mailbox_breakdown"]
    if scope not in valid_scopes:
        return f"Error: Invalid scope '{scope}'. Use: {', '.join(valid_scopes)}"

    # Validate required parameters for specific scopes
    if scope == "sender_stats" and not sender:
        return "Error: 'sender' parameter required for sender_stats scope"

    result = run_applescript_file(
        "analytics/get_statistics.applescript",
        account,
        scope,
        sender or "",
        mailbox or "",
        days_back
    )
    return result


@mcp.tool()
@inject_preferences
def export_emails(
    account: str,
    scope: str,
    subject_keyword: Optional[str] = None,
    mailbox: str = "INBOX",
    save_directory: str = "~/Desktop",
    format: str = "txt"
) -> str:
    """
    Export emails to files for backup or analysis.

    Args:
        account: Account name (e.g., "Gmail", "Work")
        scope: Export scope: "single_email" (requires subject_keyword) or "entire_mailbox"
        subject_keyword: Keyword to find email (required for single_email)
        mailbox: Mailbox to export from (default: "INBOX")
        save_directory: Directory to save exports (default: "~/Desktop")
        format: Export format: "txt", "html" (default: "txt")

    Returns:
        Confirmation message with export location
    """
    # Validate scope
    valid_scopes = ["single_email", "entire_mailbox"]
    if scope not in valid_scopes:
        return f"Error: Invalid scope '{scope}'. Use: {', '.join(valid_scopes)}"

    # Validate required parameters
    if scope == "single_email" and not subject_keyword:
        return "Error: 'subject_keyword' required for single_email scope"

    # Expand home directory
    save_dir = os.path.expanduser(save_directory)

    result = run_applescript_file(
        "analytics/export_emails.applescript",
        account,
        scope,
        subject_keyword or "",
        mailbox,
        save_dir,
        format
    )
    return result
