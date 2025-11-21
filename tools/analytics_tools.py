"""
ABOUTME: Email analytics and statistics tools for Apple Mail MCP Server
Provides tools for getting email statistics, analytics, and exporting email data.
"""

import os
from typing import Optional, Dict
from mcp_instance import mcp
from utils.applescript import run_applescript, inject_preferences


@mcp.tool()
@inject_preferences
def get_unread_count() -> Dict[str, int]:
    """
    Get the count of unread emails for each account.

    Returns:
        Dictionary mapping account names to unread email counts
    """

    script = '''
    tell application "Mail"
        set resultList to {}
        set allAccounts to every account

        repeat with anAccount in allAccounts
            set accountName to name of anAccount

            try
                -- Try to get inbox (handle both "INBOX" and "Inbox")
                try
                    set inboxMailbox to mailbox "INBOX" of anAccount
                on error
                    set inboxMailbox to mailbox "Inbox" of anAccount
                end try
                set unreadCount to unread count of inboxMailbox
                set end of resultList to accountName & ":" & unreadCount
            on error
                set end of resultList to accountName & ":ERROR"
            end try
        end repeat

        set AppleScript's text item delimiters to "|"
        return resultList as string
    end tell
    '''

    result = run_applescript(script)

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

    # Calculate date threshold if days_back > 0
    date_filter = ""
    if days_back > 0:
        date_filter = f'''
            set targetDate to (current date) - ({days_back} * days)
        '''
        date_check = 'and messageDate > targetDate'
    else:
        date_filter = ""
        date_check = ""

    if scope == "account_overview":
        script = f'''
        tell application "Mail"
            set outputText to "╔══════════════════════════════════════════╗" & return
            set outputText to outputText & "║      EMAIL STATISTICS - {account}       ║" & return
            set outputText to outputText & "╚══════════════════════════════════════════╝" & return & return

            {date_filter}

            try
                set targetAccount to account "{account}"
                set allMailboxes to every mailbox of targetAccount

                -- Initialize counters
                set totalEmails to 0
                set totalUnread to 0
                set totalRead to 0
                set totalFlagged to 0
                set totalWithAttachments to 0
                set senderCounts to {{}}
                set mailboxCounts to {{}}

                -- Analyze all mailboxes
                repeat with aMailbox in allMailboxes
                    set mailboxName to name of aMailbox
                    set mailboxMessages to every message of aMailbox
                    set mailboxTotal to 0

                    repeat with aMessage in mailboxMessages
                        try
                            set messageDate to date received of aMessage

                            -- Apply date filter if specified
                            if true {date_check} then
                                set totalEmails to totalEmails + 1
                                set mailboxTotal to mailboxTotal + 1

                                -- Count read/unread
                                if read status of aMessage then
                                    set totalRead to totalRead + 1
                                else
                                    set totalUnread to totalUnread + 1
                                end if

                                -- Count flagged
                                try
                                    if flagged status of aMessage then
                                        set totalFlagged to totalFlagged + 1
                                    end if
                                end try

                                -- Count attachments
                                set attachmentCount to count of mail attachments of aMessage
                                if attachmentCount > 0 then
                                    set totalWithAttachments to totalWithAttachments + 1
                                end if

                                -- Track senders (top 10)
                                set messageSender to sender of aMessage
                                set senderFound to false
                                repeat with senderPair in senderCounts
                                    if item 1 of senderPair is messageSender then
                                        set item 2 of senderPair to (item 2 of senderPair) + 1
                                        set senderFound to true
                                        exit repeat
                                    end if
                                end repeat
                                if not senderFound then
                                    set end of senderCounts to {{messageSender, 1}}
                                end if
                            end if
                        end try
                    end repeat

                    -- Store mailbox counts
                    if mailboxTotal > 0 then
                        set end of mailboxCounts to {{mailboxName, mailboxTotal}}
                    end if
                end repeat

                -- Format output
                set outputText to outputText & "📊 VOLUME METRICS" & return
                set outputText to outputText & "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" & return
                set outputText to outputText & "Total Emails: " & totalEmails & return
                set outputText to outputText & "Unread: " & totalUnread & " (" & (round ((totalUnread / totalEmails) * 100)) & "%)" & return
                set outputText to outputText & "Read: " & totalRead & " (" & (round ((totalRead / totalEmails) * 100)) & "%)" & return
                set outputText to outputText & "Flagged: " & totalFlagged & return
                set outputText to outputText & "With Attachments: " & totalWithAttachments & " (" & (round ((totalWithAttachments / totalEmails) * 100)) & "%)" & return
                set outputText to outputText & return

                -- Top senders (show top 5)
                set outputText to outputText & "👥 TOP SENDERS" & return
                set outputText to outputText & "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" & return
                set topCount to 0
                repeat with senderPair in senderCounts
                    set topCount to topCount + 1
                    if topCount > 5 then exit repeat
                    set outputText to outputText & item 1 of senderPair & ": " & item 2 of senderPair & " emails" & return
                end repeat
                set outputText to outputText & return

                -- Mailbox distribution (show top 5)
                set outputText to outputText & "📁 MAILBOX DISTRIBUTION" & return
                set outputText to outputText & "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" & return
                set topCount to 0
                repeat with mailboxPair in mailboxCounts
                    set topCount to topCount + 1
                    if topCount > 5 then exit repeat
                    set mailboxPercent to round ((item 2 of mailboxPair / totalEmails) * 100)
                    set outputText to outputText & item 1 of mailboxPair & ": " & item 2 of mailboxPair & " (" & mailboxPercent & "%)" & return
                end repeat

            on error errMsg
                return "Error: " & errMsg
            end try

            return outputText
        end tell
        '''

    elif scope == "sender_stats":
        if not sender:
            return "Error: 'sender' parameter required for sender_stats scope"

        script = f'''
        tell application "Mail"
            set outputText to "SENDER STATISTICS" & return & return
            set outputText to outputText & "Sender: {sender}" & return
            set outputText to outputText & "Account: {account}" & return & return

            {date_filter}

            try
                set targetAccount to account "{account}"
                set allMailboxes to every mailbox of targetAccount

                set totalFromSender to 0
                set unreadFromSender to 0
                set withAttachments to 0

                repeat with aMailbox in allMailboxes
                    set mailboxMessages to every message of aMailbox

                    repeat with aMessage in mailboxMessages
                        try
                            set messageSender to sender of aMessage
                            set messageDate to date received of aMessage

                            if messageSender contains "{sender}" {date_check} then
                                set totalFromSender to totalFromSender + 1

                                if not (read status of aMessage) then
                                    set unreadFromSender to unreadFromSender + 1
                                end if

                                if (count of mail attachments of aMessage) > 0 then
                                    set withAttachments to withAttachments + 1
                                end if
                            end if
                        end try
                    end repeat
                end repeat

                set outputText to outputText & "Total emails: " & totalFromSender & return
                set outputText to outputText & "Unread: " & unreadFromSender & return
                set outputText to outputText & "With attachments: " & withAttachments & return

            on error errMsg
                return "Error: " & errMsg
            end try

            return outputText
        end tell
        '''

    elif scope == "mailbox_breakdown":
        mailbox_param = mailbox if mailbox else "INBOX"

        script = f'''
        tell application "Mail"
            set outputText to "MAILBOX STATISTICS" & return & return
            set outputText to outputText & "Mailbox: {mailbox_param}" & return
            set outputText to outputText & "Account: {account}" & return & return

            try
                set targetAccount to account "{account}"
                try
                    set targetMailbox to mailbox "{mailbox_param}" of targetAccount
                on error
                    if "{mailbox_param}" is "INBOX" then
                        set targetMailbox to mailbox "Inbox" of targetAccount
                    else
                        error "Mailbox not found"
                    end if
                end try

                set mailboxMessages to every message of targetMailbox
                set totalMessages to count of mailboxMessages
                set unreadMessages to unread count of targetMailbox

                set outputText to outputText & "Total messages: " & totalMessages & return
                set outputText to outputText & "Unread: " & unreadMessages & return
                set outputText to outputText & "Read: " & (totalMessages - unreadMessages) & return

            on error errMsg
                return "Error: " & errMsg
            end try

            return outputText
        end tell
        '''

    else:
        return f"Error: Invalid scope '{scope}'. Use: account_overview, sender_stats, mailbox_breakdown"

    result = run_applescript(script)
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

    # Expand home directory
    save_dir = os.path.expanduser(save_directory)

    if scope == "single_email":
        if not subject_keyword:
            return "Error: 'subject_keyword' required for single_email scope"

        script = f'''
        tell application "Mail"
            set outputText to "EXPORTING EMAIL" & return & return

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
                set foundMessage to missing value

                -- Find the email
                repeat with aMessage in mailboxMessages
                    try
                        set messageSubject to subject of aMessage

                        if messageSubject contains "{subject_keyword}" then
                            set foundMessage to aMessage
                            exit repeat
                        end if
                    end try
                end repeat

                if foundMessage is not missing value then
                    set messageSubject to subject of foundMessage
                    set messageSender to sender of foundMessage
                    set messageDate to date received of foundMessage
                    set messageContent to content of foundMessage

                    -- Create safe filename
                    set safeSubject to messageSubject
                    set AppleScript's text item delimiters to "/"
                    set safeSubjectParts to text items of safeSubject
                    set AppleScript's text item delimiters to "-"
                    set safeSubject to safeSubjectParts as string
                    set AppleScript's text item delimiters to ""

                    set fileName to safeSubject & ".{format}"
                    set filePath to "{save_dir}/" & fileName

                    -- Prepare export content
                    if "{format}" is "txt" then
                        set exportContent to "Subject: " & messageSubject & return
                        set exportContent to exportContent & "From: " & messageSender & return
                        set exportContent to exportContent & "Date: " & (messageDate as string) & return & return
                        set exportContent to exportContent & messageContent
                    else if "{format}" is "html" then
                        set exportContent to "<html><body>"
                        set exportContent to exportContent & "<h2>" & messageSubject & "</h2>"
                        set exportContent to exportContent & "<p><strong>From:</strong> " & messageSender & "</p>"
                        set exportContent to exportContent & "<p><strong>Date:</strong> " & (messageDate as string) & "</p>"
                        set exportContent to exportContent & "<hr>" & messageContent
                        set exportContent to exportContent & "</body></html>"
                    end if

                    -- Write to file
                    set fileRef to open for access POSIX file filePath with write permission
                    set eof of fileRef to 0
                    write exportContent to fileRef as «class utf8»
                    close access fileRef

                    set outputText to outputText & "✓ Email exported successfully!" & return & return
                    set outputText to outputText & "Subject: " & messageSubject & return
                    set outputText to outputText & "Saved to: " & filePath & return

                else
                    set outputText to outputText & "⚠ No email found matching: {subject_keyword}" & return
                end if

            on error errMsg
                try
                    close access file filePath
                end try
                return "Error: " & errMsg
            end try

            return outputText
        end tell
        '''

    elif scope == "entire_mailbox":
        script = f'''
        tell application "Mail"
            set outputText to "EXPORTING MAILBOX" & return & return

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
                set messageCount to count of mailboxMessages
                set exportCount to 0

                -- Create export directory
                set exportDir to "{save_dir}/{mailbox}_export"
                do shell script "mkdir -p " & quoted form of exportDir

                repeat with aMessage in mailboxMessages
                    try
                        set messageSubject to subject of aMessage
                        set messageSender to sender of aMessage
                        set messageDate to date received of aMessage
                        set messageContent to content of aMessage

                        -- Create safe filename with index
                        set exportCount to exportCount + 1
                        set fileName to exportCount & "_" & messageSubject & ".{format}"

                        -- Remove unsafe characters
                        set AppleScript's text item delimiters to "/"
                        set fileNameParts to text items of fileName
                        set AppleScript's text item delimiters to "-"
                        set fileName to fileNameParts as string
                        set AppleScript's text item delimiters to ""

                        set filePath to exportDir & "/" & fileName

                        -- Prepare export content
                        if "{format}" is "txt" then
                            set exportContent to "Subject: " & messageSubject & return
                            set exportContent to exportContent & "From: " & messageSender & return
                            set exportContent to exportContent & "Date: " & (messageDate as string) & return & return
                            set exportContent to exportContent & messageContent
                        else if "{format}" is "html" then
                            set exportContent to "<html><body>"
                            set exportContent to exportContent & "<h2>" & messageSubject & "</h2>"
                            set exportContent to exportContent & "<p><strong>From:</strong> " & messageSender & "</p>"
                            set exportContent to exportContent & "<p><strong>Date:</strong> " & (messageDate as string) & "</p>"
                            set exportContent to exportContent & "<hr>" & messageContent
                            set exportContent to exportContent & "</body></html>"
                        end if

                        -- Write to file
                        set fileRef to open for access POSIX file filePath with write permission
                        set eof of fileRef to 0
                        write exportContent to fileRef as «class utf8»
                        close access fileRef

                    on error
                        -- Continue with next email if one fails
                    end try
                end repeat

                set outputText to outputText & "✓ Mailbox exported successfully!" & return & return
                set outputText to outputText & "Mailbox: {mailbox}" & return
                set outputText to outputText & "Total emails: " & messageCount & return
                set outputText to outputText & "Exported: " & exportCount & return
                set outputText to outputText & "Location: " & exportDir & return

            on error errMsg
                return "Error: " & errMsg
            end try

            return outputText
        end tell
        '''

    else:
        return f"Error: Invalid scope '{scope}'. Use: single_email, entire_mailbox"

    result = run_applescript(script)
    return result
