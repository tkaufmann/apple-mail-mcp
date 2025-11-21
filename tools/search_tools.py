"""
ABOUTME: Email search tools for Apple Mail MCP Server
Provides tools for searching emails by various criteria including subject, sender, and thread.
"""

from typing import Optional
from mcp_instance import mcp
from utils.applescript import run_applescript, inject_preferences


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

    # Build mailbox selection logic
    if mailbox == "All":
        mailbox_script = '''
            set allMailboxes to every mailbox of targetAccount
            set searchMailboxes to allMailboxes
        '''
        search_location = "all mailboxes"
    else:
        mailbox_script = f'''
            try
                set searchMailbox to mailbox "{mailbox}" of targetAccount
            on error
                if "{mailbox}" is "INBOX" then
                    set searchMailbox to mailbox "Inbox" of targetAccount
                else
                    error "Mailbox not found: {mailbox}"
                end if
            end try
            set searchMailboxes to {{searchMailbox}}
        '''
        search_location = mailbox

    script = f'''
    on lowercase(str)
        set lowerStr to do shell script "echo " & quoted form of str & " | tr '[:upper:]' '[:lower:]'"
        return lowerStr
    end lowercase

    tell application "Mail"
        set outputText to "SEARCH RESULTS FOR: {subject_keyword}" & return
        set outputText to outputText & "Searching in: {search_location}" & return & return
        set resultCount to 0

        try
            set targetAccount to account "{account}"
            {mailbox_script}

            repeat with currentMailbox in searchMailboxes
                set mailboxMessages to every message of currentMailbox
                set mailboxName to name of currentMailbox

                repeat with aMessage in mailboxMessages
                    if resultCount >= {max_results} then exit repeat

                    try
                        set messageSubject to subject of aMessage

                        -- Convert to lowercase for case-insensitive matching
                        set lowerSubject to my lowercase(messageSubject)
                        set lowerKeyword to my lowercase("{subject_keyword}")

                        -- Check if subject contains keyword (case insensitive)
                        if lowerSubject contains lowerKeyword then
                            set messageSender to sender of aMessage
                            set messageDate to date received of aMessage
                            set messageRead to read status of aMessage

                            if messageRead then
                                set readIndicator to "✓"
                            else
                                set readIndicator to "✉"
                            end if

                            set outputText to outputText & readIndicator & " " & messageSubject & return
                            set outputText to outputText & "   From: " & messageSender & return
                            set outputText to outputText & "   Date: " & (messageDate as string) & return
                            set outputText to outputText & "   Mailbox: " & mailboxName & return

                            -- Get content preview
                            try
                                set msgContent to content of aMessage
                                set AppleScript's text item delimiters to {{return, linefeed}}
                                set contentParts to text items of msgContent
                                set AppleScript's text item delimiters to " "
                                set cleanText to contentParts as string
                                set AppleScript's text item delimiters to ""

                                -- Handle content length limit (0 = unlimited)
                                if {max_content_length} > 0 and length of cleanText > {max_content_length} then
                                    set contentPreview to text 1 thru {max_content_length} of cleanText & "..."
                                else
                                    set contentPreview to cleanText
                                end if

                                set outputText to outputText & "   Content: " & contentPreview & return
                            on error
                                set outputText to outputText & "   Content: [Not available]" & return
                            end try

                            set outputText to outputText & return
                            set resultCount to resultCount + 1
                        end if
                    end try
                end repeat
            end repeat

            set outputText to outputText & "========================================" & return
            set outputText to outputText & "FOUND: " & resultCount & " matching email(s)" & return
            set outputText to outputText & "========================================" & return

        on error errMsg
            return "Error: " & errMsg
        end try

        return outputText
    end tell
    '''

    result = run_applescript(script)
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

    # Build AppleScript search conditions
    conditions = []

    if subject_keyword:
        conditions.append(f'messageSubject contains "{subject_keyword}"')

    if sender:
        conditions.append(f'messageSender contains "{sender}"')

    if has_attachments is not None:
        if has_attachments:
            conditions.append('(count of mail attachments of aMessage) > 0')
        else:
            conditions.append('(count of mail attachments of aMessage) = 0')

    if read_status == "read":
        conditions.append('messageRead is true')
    elif read_status == "unread":
        conditions.append('messageRead is false')

    # Combine conditions with AND logic
    condition_str = ' and '.join(conditions) if conditions else 'true'

    # Handle content preview
    content_script = '''
        try
            set msgContent to content of aMessage
            set AppleScript's text item delimiters to {{return, linefeed}}
            set contentParts to text items of msgContent
            set AppleScript's text item delimiters to " "
            set cleanText to contentParts as string
            set AppleScript's text item delimiters to ""

            if length of cleanText > 300 then
                set contentPreview to text 1 thru 300 of cleanText & "..."
            else
                set contentPreview to cleanText
            end if

            set outputText to outputText & "   Content: " & contentPreview & return
        on error
            set outputText to outputText & "   Content: [Not available]" & return
        end try
    ''' if include_content else ''

    # Build mailbox selection logic
    if mailbox == "All":
        mailbox_script = '''
            set allMailboxes to every mailbox of targetAccount
            set searchMailboxes to allMailboxes
        '''
    else:
        mailbox_script = f'''
            try
                set searchMailbox to mailbox "{mailbox}" of targetAccount
            on error
                if "{mailbox}" is "INBOX" then
                    set searchMailbox to mailbox "Inbox" of targetAccount
                else
                    error "Mailbox not found: {mailbox}"
                end if
            end try
            set searchMailboxes to {{searchMailbox}}
        '''

    script = f'''
    tell application "Mail"
        set outputText to "SEARCH RESULTS" & return & return
        set outputText to outputText & "Searching in: {mailbox}" & return
        set outputText to outputText & "Account: {account}" & return & return
        set resultCount to 0

        try
            set targetAccount to account "{account}"
            {mailbox_script}

            repeat with currentMailbox in searchMailboxes
                set mailboxMessages to every message of currentMailbox
                set mailboxName to name of currentMailbox

                repeat with aMessage in mailboxMessages
                    if resultCount >= {max_results} then exit repeat

                    try
                        set messageSubject to subject of aMessage
                        set messageSender to sender of aMessage
                        set messageDate to date received of aMessage
                        set messageRead to read status of aMessage

                        -- Apply search conditions
                        if {condition_str} then
                            set readIndicator to "✉"
                            if messageRead then
                                set readIndicator to "✓"
                            end if

                            set outputText to outputText & readIndicator & " " & messageSubject & return
                            set outputText to outputText & "   From: " & messageSender & return
                            set outputText to outputText & "   Date: " & (messageDate as string) & return
                            set outputText to outputText & "   Mailbox: " & mailboxName & return

                            {content_script}

                            set outputText to outputText & return
                            set resultCount to resultCount + 1
                        end if
                    end try
                end repeat
            end repeat

            set outputText to outputText & "========================================" & return
            set outputText to outputText & "FOUND: " & resultCount & " matching email(s)" & return
            set outputText to outputText & "========================================" & return

        on error errMsg
            return "Error: " & errMsg
        end try

        return outputText
    end tell
    '''

    result = run_applescript(script)
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

    # For thread detection, we'll strip common prefixes
    thread_keywords = ['Re:', 'Fwd:', 'FW:', 'RE:', 'Fw:']
    cleaned_keyword = subject_keyword
    for prefix in thread_keywords:
        cleaned_keyword = cleaned_keyword.replace(prefix, '').strip()

    mailbox_script = f'''
        try
            set searchMailbox to mailbox "{mailbox}" of targetAccount
        on error
            if "{mailbox}" is "INBOX" then
                set searchMailbox to mailbox "Inbox" of targetAccount
            else if "{mailbox}" is "All" then
                set searchMailboxes to every mailbox of targetAccount
                set useAllMailboxes to true
            else
                error "Mailbox not found: {mailbox}"
            end if
        end try

        if "{mailbox}" is not "All" then
            set searchMailboxes to {{searchMailbox}}
            set useAllMailboxes to false
        end if
    '''

    script = f'''
    tell application "Mail"
        set outputText to "EMAIL THREAD VIEW" & return & return
        set outputText to outputText & "Thread topic: {cleaned_keyword}" & return
        set outputText to outputText & "Account: {account}" & return & return
        set threadMessages to {{}}

        try
            set targetAccount to account "{account}"
            {mailbox_script}

            -- Collect all matching messages from all mailboxes
            repeat with currentMailbox in searchMailboxes
                set mailboxMessages to every message of currentMailbox

                repeat with aMessage in mailboxMessages
                    if (count of threadMessages) >= {max_messages} then exit repeat

                    try
                        set messageSubject to subject of aMessage

                        -- Remove common prefixes for matching
                        set cleanSubject to messageSubject
                        if cleanSubject starts with "Re: " then
                            set cleanSubject to text 5 thru -1 of cleanSubject
                        end if
                        if cleanSubject starts with "Fwd: " or cleanSubject starts with "FW: " then
                            set cleanSubject to text 6 thru -1 of cleanSubject
                        end if

                        -- Check if this message is part of the thread
                        if cleanSubject contains "{cleaned_keyword}" or messageSubject contains "{cleaned_keyword}" then
                            set end of threadMessages to aMessage
                        end if
                    end try
                end repeat
            end repeat

            -- Display thread messages
            set messageCount to count of threadMessages
            set outputText to outputText & "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" & return
            set outputText to outputText & "FOUND " & messageCount & " MESSAGE(S) IN THREAD" & return
            set outputText to outputText & "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" & return & return

            repeat with aMessage in threadMessages
                try
                    set messageSubject to subject of aMessage
                    set messageSender to sender of aMessage
                    set messageDate to date received of aMessage
                    set messageRead to read status of aMessage

                    if messageRead then
                        set readIndicator to "✓"
                    else
                        set readIndicator to "✉"
                    end if

                    set outputText to outputText & readIndicator & " " & messageSubject & return
                    set outputText to outputText & "   From: " & messageSender & return
                    set outputText to outputText & "   Date: " & (messageDate as string) & return

                    -- Get content preview
                    try
                        set msgContent to content of aMessage
                        set AppleScript's text item delimiters to {{return, linefeed}}
                        set contentParts to text items of msgContent
                        set AppleScript's text item delimiters to " "
                        set cleanText to contentParts as string
                        set AppleScript's text item delimiters to ""

                        if length of cleanText > 150 then
                            set contentPreview to text 1 thru 150 of cleanText & "..."
                        else
                            set contentPreview to cleanText
                        end if

                        set outputText to outputText & "   Preview: " & contentPreview & return
                    end try

                    set outputText to outputText & return
                end try
            end repeat

        on error errMsg
            return "Error: " & errMsg
        end try

        return outputText
    end tell
    '''

    result = run_applescript(script)
    return result
