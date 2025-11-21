"""
ABOUTME: Draft email management tools for Apple Mail MCP Server
Provides tools for creating, listing, sending, and deleting draft emails.
"""

from typing import Optional
from mcp_instance import mcp
from utils.applescript import run_applescript_file, inject_preferences


@mcp.tool()
@inject_preferences
def manage_drafts(
    account: str,
    action: str,
    subject: Optional[str] = None,
    to: Optional[str] = None,
    body: Optional[str] = None,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    draft_subject: Optional[str] = None
) -> str:
    """
    Manage draft emails - list, create, send, or delete drafts.

    Args:
        account: Account name (e.g., "Gmail", "Work")
        action: Action to perform: "list", "create", "send", "delete"
        subject: Email subject (required for create)
        to: Recipient email(s) for create (comma-separated)
        body: Email body (required for create)
        cc: Optional CC recipients for create
        bcc: Optional BCC recipients for create
        draft_subject: Subject keyword to find draft (required for send/delete)

    Returns:
        Formatted output based on action
    """
    # Validate action
    valid_actions = ["list", "create", "send", "delete"]
    if action not in valid_actions:
        return f"Error: Invalid action '{action}'. Use: {', '.join(valid_actions)}"

    # Validate required parameters for create action
    if action == "create":
        if not subject or not to or not body:
            return "Error: 'subject', 'to', and 'body' are required for creating drafts"

    # Validate required parameters for send/delete actions
    if action in ["send", "delete"]:
        if not draft_subject:
            return f"Error: 'draft_subject' is required for {action} action"

    result = run_applescript_file(
        "draft/manage_drafts.applescript",
        account,
        action,
        subject or "",
        to or "",
        body or "",
        cc or "",
        bcc or "",
        draft_subject or ""
    )
    return result
