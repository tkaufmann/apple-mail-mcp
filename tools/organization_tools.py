"""
ABOUTME: Email organization tools for Apple Mail MCP Server
Provides tools for moving emails, managing email status, and listing mailboxes and accounts.
"""

from typing import Optional, List
from mcp_instance import mcp
from utils.applescript import run_applescript, run_applescript_file, inject_preferences


@mcp.tool()
@inject_preferences
def list_accounts() -> List[str]:
    """
    List all available Mail accounts.

    Returns:
        List of account names
    """
    result = run_applescript_file("organization/list_accounts.applescript")
    return result.split('|') if result else []


@mcp.tool()
@inject_preferences
def list_mailboxes(
    account: Optional[str] = None,
    include_counts: bool = True
) -> str:
    """
    List all mailboxes (folders) for a specific account or all accounts.

    Args:
        account: Optional account name to filter (e.g., "Gmail", "Work"). If None, shows all accounts.
        include_counts: Whether to include message counts for each mailbox (default: True)

    Returns:
        Formatted list of mailboxes with optional message counts.
        For nested mailboxes, shows both indented format and path format (e.g., "Projects/Amplify Impact")
    """
    result = run_applescript_file(
        "organization/list_mailboxes.applescript",
        account or "",
        "true" if include_counts else "false"
    )
    return result


@mcp.tool()
@inject_preferences
def move_email(
    account: str,
    subject_keyword: str,
    to_mailbox: str,
    from_mailbox: str = "INBOX",
    max_moves: int = 1
) -> str:
    """
    Move email(s) matching a subject keyword from one mailbox to another.

    Args:
        account: Account name (e.g., "Gmail", "Work")
        subject_keyword: Keyword to search for in email subjects
        to_mailbox: Destination mailbox name. For nested mailboxes, use "/" separator (e.g., "Projects/Amplify Impact")
        from_mailbox: Source mailbox name (default: "INBOX")
        max_moves: Maximum number of emails to move (default: 1, safety limit)

    Returns:
        Confirmation message with details of moved emails
    """
    # Parse nested mailbox path and pass as comma-separated string
    mailbox_parts = to_mailbox.split('/')
    mailbox_path_parts = ','.join(mailbox_parts)

    result = run_applescript_file(
        "organization/move_email.applescript",
        account,
        subject_keyword,
        to_mailbox,
        from_mailbox,
        max_moves,
        mailbox_path_parts
    )
    return result


@mcp.tool()
@inject_preferences
def update_email_status(
    account: str,
    action: str,
    subject_keyword: Optional[str] = None,
    sender: Optional[str] = None,
    mailbox: str = "INBOX",
    max_updates: int = 10
) -> str:
    """
    Update email status - mark as read/unread or flag/unflag emails.

    Args:
        account: Account name (e.g., "Gmail", "Work")
        action: Action to perform: "mark_read", "mark_unread", "flag", "unflag"
        subject_keyword: Optional keyword to filter emails by subject
        sender: Optional sender to filter emails by
        mailbox: Mailbox to search in (default: "INBOX")
        max_updates: Maximum number of emails to update (safety limit, default: 10)

    Returns:
        Confirmation message with details of updated emails
    """
    # Validate action before calling AppleScript
    valid_actions = ["mark_read", "mark_unread", "flag", "unflag"]
    if action not in valid_actions:
        return f"Error: Invalid action '{action}'. Use: {', '.join(valid_actions)}"

    result = run_applescript_file(
        "organization/update_email_status.applescript",
        account,
        action,
        subject_keyword or "",
        sender or "",
        mailbox,
        max_updates
    )
    return result
