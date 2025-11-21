"""
ABOUTME: Email composition tools for Apple Mail MCP Server
Provides tools for composing new emails, replying to emails, and forwarding messages.
"""

from typing import Optional
from mcp_instance import mcp
from utils.applescript import run_applescript_file, inject_preferences


@mcp.tool()
@inject_preferences
def compose_email(
    account: str,
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None
) -> str:
    """
    Compose and send a new email from a specific account.

    Args:
        account: Account name to send from (e.g., "Gmail", "Work", "Personal")
        to: Recipient email address(es), comma-separated for multiple
        subject: Email subject line
        body: Email body text
        cc: Optional CC recipients, comma-separated for multiple
        bcc: Optional BCC recipients, comma-separated for multiple

    Returns:
        Confirmation message with details of the sent email
    """
    result = run_applescript_file(
        "composition/compose_email.applescript",
        account,
        to,
        subject,
        body,
        cc or "",
        bcc or ""
    )
    return result


@mcp.tool()
@inject_preferences
def reply_to_email(
    account: str,
    subject_keyword: str,
    reply_body: str,
    reply_to_all: bool = False
) -> str:
    """
    Reply to an email matching a subject keyword.

    Args:
        account: Account name (e.g., "Gmail", "Work")
        subject_keyword: Keyword to search for in email subjects
        reply_body: The body text of the reply
        reply_to_all: If True, reply to all recipients; if False, reply only to sender (default: False)

    Returns:
        Confirmation message with details of the reply sent
    """
    result = run_applescript_file(
        "composition/reply_to_email.applescript",
        account,
        subject_keyword,
        reply_body,
        "true" if reply_to_all else "false"
    )
    return result


@mcp.tool()
@inject_preferences
def forward_email(
    account: str,
    subject_keyword: str,
    to: str,
    message: Optional[str] = None,
    mailbox: str = "INBOX"
) -> str:
    """
    Forward an email to one or more recipients.

    Args:
        account: Account name (e.g., "Gmail", "Work")
        subject_keyword: Keyword to search for in email subjects
        to: Recipient email address(es), comma-separated for multiple
        message: Optional message to add before forwarded content
        mailbox: Mailbox to search in (default: "INBOX")

    Returns:
        Confirmation message with details of forwarded email
    """
    result = run_applescript_file(
        "composition/forward_email.applescript",
        account,
        subject_keyword,
        to,
        message or "",
        mailbox
    )
    return result
