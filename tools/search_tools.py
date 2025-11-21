"""
ABOUTME: Email search tools for Apple Mail MCP Server
Provides tools for searching emails by various criteria including subject, sender, and thread.
"""

from typing import Optional
from mcp_instance import mcp
from utils.applescript import run_applescript_file, inject_preferences


@mcp.tool()
@inject_preferences
def get_email_with_content(
    account: str,
    subject_keyword: str,
    max_results: int = 5,
    max_content_length: int = 300,
    mailbox: str = "INBOX"
) -> str:
    """
    Search for emails by subject keyword and return with full content preview.

    Args:
        account: Account name to search in (e.g., "Gmail", "Work")
        subject_keyword: Keyword to search for in email subjects
        max_results: Maximum number of matching emails to return (default: 5)
        max_content_length: Maximum content length in characters (default: 300, 0 = unlimited)
        mailbox: Mailbox to search (default: "INBOX", use "All" for all mailboxes)

    Returns:
        Detailed email information including content preview
    """
    result = run_applescript_file(
        "search/get_email_with_content.applescript",
        account,
        subject_keyword,
        max_results,
        max_content_length,
        mailbox
    )
    return result


@mcp.tool()
@inject_preferences
def search_emails(
    account: str,
    mailbox: str = "INBOX",
    subject_keyword: Optional[str] = None,
    sender: Optional[str] = None,
    has_attachments: Optional[bool] = None,
    read_status: str = "all",
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    include_content: bool = False,
    max_results: int = 20
) -> str:
    """
    Unified search tool - search emails with advanced filtering across any mailbox.

    Args:
        account: Account name to search in (e.g., "Gmail", "Work")
        mailbox: Mailbox to search (default: "INBOX", use "All" for all mailboxes, or specific folder name)
        subject_keyword: Optional keyword to search in subject
        sender: Optional sender email or name to filter by
        has_attachments: Optional filter for emails with attachments (True/False/None)
        read_status: Filter by read status: "all", "read", "unread" (default: "all")
        date_from: Optional start date filter (format: "YYYY-MM-DD")
        date_to: Optional end date filter (format: "YYYY-MM-DD")
        include_content: Whether to include email content preview (slower)
        max_results: Maximum number of results to return (default: 20)

    Returns:
        Formatted list of matching emails with all requested details
    """
    # Convert optional parameters to strings for AppleScript
    has_attachments_str = "none"
    if has_attachments is True:
        has_attachments_str = "true"
    elif has_attachments is False:
        has_attachments_str = "false"

    result = run_applescript_file(
        "search/search_emails.applescript",
        account,
        mailbox,
        subject_keyword or "",
        sender or "",
        has_attachments_str,
        read_status,
        date_from or "",
        date_to or "",
        "true" if include_content else "false",
        max_results
    )
    return result


@mcp.tool()
@inject_preferences
def get_email_thread(
    account: str,
    subject_keyword: str,
    mailbox: str = "INBOX",
    max_messages: int = 50
) -> str:
    """
    Get an email conversation thread - all messages with the same or similar subject.

    Args:
        account: Account name (e.g., "Gmail", "Work")
        subject_keyword: Keyword to identify the thread (e.g., "Re: Project Update")
        mailbox: Mailbox to search in (default: "INBOX", use "All" for all mailboxes)
        max_messages: Maximum number of thread messages to return (default: 50)

    Returns:
        Formatted thread view with all related messages sorted by date
    """
    # For thread detection, we'll strip common prefixes in Python
    thread_keywords = ['Re:', 'Fwd:', 'FW:', 'RE:', 'Fw:']
    cleaned_keyword = subject_keyword
    for prefix in thread_keywords:
        cleaned_keyword = cleaned_keyword.replace(prefix, '').strip()

    result = run_applescript_file(
        "search/get_email_thread.applescript",
        account,
        cleaned_keyword,
        mailbox,
        max_messages
    )
    return result
