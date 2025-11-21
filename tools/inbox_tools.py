"""
ABOUTME: Inbox management tools for Apple Mail MCP Server
Provides tools for listing, viewing, and getting overview of inbox emails.
"""

from typing import Optional
from mcp_instance import mcp
from utils.applescript import run_applescript_file, inject_preferences


@mcp.tool()
@inject_preferences
def list_inbox_emails(
    account: Optional[str] = None,
    max_emails: int = 0,
    include_read: bool = True
) -> str:
    """
    List all emails from inbox across all accounts or a specific account.

    Args:
        account: Optional account name to filter (e.g., "Gmail", "Work"). If None, shows all accounts.
        max_emails: Maximum number of emails to return per account (0 = all)
        include_read: Whether to include read emails (default: True)

    Returns:
        Formatted list of emails with subject, sender, date, and read status
    """
    result = run_applescript_file(
        "inbox/list_inbox_emails.applescript",
        account or "",
        max_emails,
        "true" if include_read else "false"
    )
    return result


@mcp.tool()
@inject_preferences
def get_recent_emails(
    account: str,
    count: int = 10,
    include_content: bool = False
) -> str:
    """
    Get the most recent emails from a specific account.

    Args:
        account: Account name (e.g., "Gmail", "Work")
        count: Number of recent emails to retrieve (default: 10)
        include_content: Whether to include content preview (slower, default: False)

    Returns:
        Formatted list of recent emails
    """
    result = run_applescript_file(
        "inbox/get_recent_emails.applescript",
        account,
        count,
        "true" if include_content else "false"
    )
    return result
