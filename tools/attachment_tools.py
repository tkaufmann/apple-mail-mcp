"""
ABOUTME: Email attachment management tools for Apple Mail MCP Server
Provides tools for listing and saving email attachments.
"""

from mcp_instance import mcp
from utils.applescript import run_applescript, inject_preferences


@mcp.tool()
@inject_preferences
def list_email_attachments(
    account: str,
    subject_keyword: str,
    max_results: int = 1
) -> str:
    """
    List attachments for emails matching a subject keyword.

    Args:
        account: Account name (e.g., "Gmail", "Work", "Personal")
        subject_keyword: Keyword to search for in email subjects
        max_results: Maximum number of matching emails to check (default: 1)

    Returns:
        List of attachments with their names and sizes
    """

    script = f'''
    tell application "Mail"
        set outputText to "ATTACHMENTS FOR: {subject_keyword}" & return & return
        set resultCount to 0

        try
            set targetAccount to account "{account}"
            -- Try to get inbox (handle both "INBOX" and "Inbox")
            try
                set inboxMailbox to mailbox "INBOX" of targetAccount
            on error
                set inboxMailbox to mailbox "Inbox" of targetAccount
            end try
            set inboxMessages to every message of inboxMailbox

            repeat with aMessage in inboxMessages
                if resultCount >= {max_results} then exit repeat

                try
                    set messageSubject to subject of aMessage

                    -- Check if subject contains keyword
                    if messageSubject contains "{subject_keyword}" then
                        set messageSender to sender of aMessage
                        set messageDate to date received of aMessage

                        set outputText to outputText & "✉ " & messageSubject & return
                        set outputText to outputText & "   From: " & messageSender & return
                        set outputText to outputText & "   Date: " & (messageDate as string) & return & return

                        -- Get attachments
                        set msgAttachments to mail attachments of aMessage
                        set attachmentCount to count of msgAttachments

                        if attachmentCount > 0 then
                            set outputText to outputText & "   Attachments (" & attachmentCount & "):" & return

                            repeat with anAttachment in msgAttachments
                                set attachmentName to name of anAttachment
                                try
                                    set attachmentSize to size of anAttachment
                                    set sizeInKB to (attachmentSize / 1024) as integer
                                    set outputText to outputText & "   📎 " & attachmentName & " (" & sizeInKB & " KB)" & return
                                on error
                                    set outputText to outputText & "   📎 " & attachmentName & return
                                end try
                            end repeat
                        else
                            set outputText to outputText & "   No attachments" & return
                        end if

                        set outputText to outputText & return
                        set resultCount to resultCount + 1
                    end if
                end try
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
def save_email_attachment(
    account: str,
    subject_keyword: str,
    attachment_name: str,
    save_path: str
) -> str:
    """
    Save a specific attachment from an email to disk.

    Args:
        account: Account name (e.g., "Gmail", "Work", "Personal")
        subject_keyword: Keyword to search for in email subjects
        attachment_name: Name of the attachment to save
        save_path: Full path where to save the attachment

    Returns:
        Confirmation message with save location
    """

    script = f'''
    tell application "Mail"
        set outputText to ""

        try
            set targetAccount to account "{account}"
            -- Try to get inbox (handle both "INBOX" and "Inbox")
            try
                set inboxMailbox to mailbox "INBOX" of targetAccount
            on error
                set inboxMailbox to mailbox "Inbox" of targetAccount
            end try
            set inboxMessages to every message of inboxMailbox
            set foundAttachment to false

            repeat with aMessage in inboxMessages
                try
                    set messageSubject to subject of aMessage

                    -- Check if subject contains keyword
                    if messageSubject contains "{subject_keyword}" then
                        set msgAttachments to mail attachments of aMessage

                        repeat with anAttachment in msgAttachments
                            set attachmentFileName to name of anAttachment

                            if attachmentFileName contains "{attachment_name}" then
                                -- Save the attachment
                                save anAttachment in POSIX file "{save_path}"

                                set outputText to "✓ Attachment saved successfully!" & return & return
                                set outputText to outputText & "Email: " & messageSubject & return
                                set outputText to outputText & "Attachment: " & attachmentFileName & return
                                set outputText to outputText & "Saved to: {save_path}" & return

                                set foundAttachment to true
                                exit repeat
                            end if
                        end repeat

                        if foundAttachment then exit repeat
                    end if
                end try
            end repeat

            if not foundAttachment then
                set outputText to "⚠ Attachment not found" & return
                set outputText to outputText & "Email keyword: {subject_keyword}" & return
                set outputText to outputText & "Attachment name: {attachment_name}" & return
            end if

        on error errMsg
            return "Error: " & errMsg
        end try

        return outputText
    end tell
    '''

    result = run_applescript(script)
    return result
