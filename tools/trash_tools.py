"""
ABOUTME: Trash management tools for Apple Mail MCP Server
Provides tools for moving emails to trash, deleting permanently, and emptying trash.
"""

from typing import Optional
from mcp_instance import mcp
from utils.applescript import run_applescript_file, inject_preferences


@mcp.tool()
@inject_preferences
def manage_trash(
    account: str,
    action: str,
    subject_keyword: Optional[str] = None,
    sender: Optional[str] = None,
    mailbox: str = "INBOX",
    max_deletes: int = 5
) -> str:
    """
    Manage trash operations - delete emails or empty trash.

    Args:
        account: Account name (e.g., "Gmail", "Work")
        action: Action to perform: "move_to_trash", "delete_permanent", "empty_trash"
        subject_keyword: Optional keyword to filter emails (not used for empty_trash)
        sender: Optional sender to filter emails (not used for empty_trash)
        mailbox: Source mailbox (default: "INBOX", not used for empty_trash or delete_permanent)
        max_deletes: Maximum number of emails to delete (safety limit, default: 5)

    Returns:
        Confirmation message with details of deleted emails
    """
    # Validate action
    valid_actions = ["move_to_trash", "delete_permanent", "empty_trash"]
    if action not in valid_actions:
        return f"Error: Invalid action '{action}'. Use: {', '.join(valid_actions)}"

    result = run_applescript_file(
        "trash/manage_trash.applescript",
        account,
        action,
        subject_keyword or "",
        sender or "",
        mailbox,
        max_deletes
    )
    return result
