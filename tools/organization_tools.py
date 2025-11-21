"""
ABOUTME: Email organization tools for Apple Mail MCP Server
Provides tools for moving emails, managing email status, and listing mailboxes and accounts.
"""

from typing import Optional, List
from mcp_instance import mcp
from utils.applescript import run_applescript, inject_preferences


@mcp.tool()
@inject_preferences
def list_accounts() -> List[str]:
    """
    List all available Mail accounts.

    Returns:
        List of account names
    """

    script = '''
    tell application "Mail"
        set accountNames to {}
        set allAccounts to every account

        repeat with anAccount in allAccounts
            set accountName to name of anAccount
            set end of accountNames to accountName
        end repeat

        set AppleScript's text item delimiters to "|"
        return accountNames as string
    end tell
    '''

    result = run_applescript(script)
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

    count_script = '''
        try
            set msgCount to count of messages of aMailbox
            set unreadCount to unread count of aMailbox
            set outputText to outputText & " (" & msgCount & " total, " & unreadCount & " unread)"
        on error
            set outputText to outputText & " (count unavailable)"
        end try
    ''' if include_counts else ''

    account_filter = f'''
        if accountName is "{account}" then
    ''' if account else ''

    account_filter_end = 'end if' if account else ''

    script = f'''
    tell application "Mail"
        set outputText to "MAILBOXES" & return & return
        set allAccounts to every account

        repeat with anAccount in allAccounts
            set accountName to name of anAccount

            {account_filter}
                set outputText to outputText & "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" & return
                set outputText to outputText & "📁 ACCOUNT: " & accountName & return
                set outputText to outputText & "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" & return & return

                try
                    set accountMailboxes to every mailbox of anAccount

                    repeat with aMailbox in accountMailboxes
                        set mailboxName to name of aMailbox
                        set outputText to outputText & "  📂 " & mailboxName

                        {count_script}

                        set outputText to outputText & return

                        -- List sub-mailboxes with path notation
                        try
                            set subMailboxes to every mailbox of aMailbox
                            repeat with subBox in subMailboxes
                                set subName to name of subBox
                                set outputText to outputText & "    └─ " & subName & " [Path: " & mailboxName & "/" & subName & "]"

                                {count_script.replace('aMailbox', 'subBox') if include_counts else ''}

                                set outputText to outputText & return
                            end repeat
                        end try
                    end repeat

                    set outputText to outputText & return
                on error errMsg
                    set outputText to outputText & "  ⚠ Error accessing mailboxes: " & errMsg & return & return
                end try
            {account_filter_end}
        end repeat

        return outputText
    end tell
    '''

    result = run_applescript(script)
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

    # Parse nested mailbox path
    mailbox_parts = to_mailbox.split('/')

    # Build the nested mailbox reference
    if len(mailbox_parts) > 1:
        # Nested mailbox
        dest_mailbox_script = f'mailbox "{mailbox_parts[-1]}" of '
        for i in range(len(mailbox_parts) - 2, -1, -1):
            dest_mailbox_script += f'mailbox "{mailbox_parts[i]}" of '
        dest_mailbox_script += 'targetAccount'
    else:
        # Top-level mailbox
        dest_mailbox_script = f'mailbox "{to_mailbox}" of targetAccount'

    script = f'''
    tell application "Mail"
        set outputText to "MOVING EMAILS" & return & return
        set movedCount to 0

        try
            set targetAccount to account "{account}"
            -- Try to get source mailbox (handle both "INBOX"/"Inbox" variations)
            try
                set sourceMailbox to mailbox "{from_mailbox}" of targetAccount
            on error
                if "{from_mailbox}" is "INBOX" then
                    set sourceMailbox to mailbox "Inbox" of targetAccount
                else
                    error "Source mailbox not found"
                end if
            end try

            -- Get destination mailbox (handles nested mailboxes)
            set destMailbox to {dest_mailbox_script}
            set sourceMessages to every message of sourceMailbox

            repeat with aMessage in sourceMessages
                if movedCount >= {max_moves} then exit repeat

                try
                    set messageSubject to subject of aMessage

                    -- Check if subject contains keyword (case insensitive)
                    if messageSubject contains "{subject_keyword}" then
                        set messageSender to sender of aMessage
                        set messageDate to date received of aMessage

                        -- Move the message
                        move aMessage to destMailbox

                        set outputText to outputText & "✓ Moved: " & messageSubject & return
                        set outputText to outputText & "  From: " & messageSender & return
                        set outputText to outputText & "  Date: " & (messageDate as string) & return
                        set outputText to outputText & "  {from_mailbox} → {to_mailbox}" & return & return

                        set movedCount to movedCount + 1
                    end if
                end try
            end repeat

            set outputText to outputText & "========================================" & return
            set outputText to outputText & "TOTAL MOVED: " & movedCount & " email(s)" & return
            set outputText to outputText & "========================================" & return

        on error errMsg
            return "Error: " & errMsg & return & "Please check that account and mailbox names are correct. For nested mailboxes, use '/' separator (e.g., 'Projects/Amplify Impact')."
        end try

        return outputText
    end tell
    '''

    result = run_applescript(script)
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

    # Build search condition
    conditions = []
    if subject_keyword:
        conditions.append(f'messageSubject contains "{subject_keyword}"')
    if sender:
        conditions.append(f'messageSender contains "{sender}"')

    condition_str = ' and '.join(conditions) if conditions else 'true'

    # Build action script
    if action == "mark_read":
        action_script = 'set read status of aMessage to true'
        action_label = "Marked as read"
    elif action == "mark_unread":
        action_script = 'set read status of aMessage to false'
        action_label = "Marked as unread"
    elif action == "flag":
        action_script = 'set flagged status of aMessage to true'
        action_label = "Flagged"
    elif action == "unflag":
        action_script = 'set flagged status of aMessage to false'
        action_label = "Unflagged"
    else:
        return f"Error: Invalid action '{action}'. Use: mark_read, mark_unread, flag, unflag"

    script = f'''
    tell application "Mail"
        set outputText to "UPDATING EMAIL STATUS: {action_label}" & return & return
        set updateCount to 0

        try
            set targetAccount to account "{account}"
            -- Try to get mailbox
            try
                set targetMailbox to mailbox "{mailbox}" of targetAccount
            on error
                if "{mailbox}" is "INBOX" then
                    set targetMailbox to mailbox "Inbox" of targetAccount
                else
                    error "Mailbox not found: {mailbox}"
                end if
            end try

            set mailboxMessages to every message of targetMailbox

            repeat with aMessage in mailboxMessages
                if updateCount >= {max_updates} then exit repeat

                try
                    set messageSubject to subject of aMessage
                    set messageSender to sender of aMessage
                    set messageDate to date received of aMessage

                    -- Apply filter conditions
                    if {condition_str} then
                        {action_script}

                        set outputText to outputText & "✓ {action_label}: " & messageSubject & return
                        set outputText to outputText & "   From: " & messageSender & return
                        set outputText to outputText & "   Date: " & (messageDate as string) & return & return

                        set updateCount to updateCount + 1
                    end if
                end try
            end repeat

            set outputText to outputText & "========================================" & return
            set outputText to outputText & "TOTAL UPDATED: " & updateCount & " email(s)" & return
            set outputText to outputText & "========================================" & return

        on error errMsg
            return "Error: " & errMsg
        end try

        return outputText
    end tell
    '''

    result = run_applescript(script)
    return result
