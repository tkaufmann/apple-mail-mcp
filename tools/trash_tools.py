"""
ABOUTME: Trash management tools for Apple Mail MCP Server
Provides tools for moving emails to trash, deleting permanently, and emptying trash.
"""

from typing import Optional
from mcp_instance import mcp
from utils.applescript import run_applescript, inject_preferences


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

    if action == "empty_trash":
        script = f'''
        tell application "Mail"
            set outputText to "EMPTYING TRASH" & return & return

            try
                set targetAccount to account "{account}"
                set trashMailbox to mailbox "Trash" of targetAccount
                set trashMessages to every message of trashMailbox
                set messageCount to count of trashMessages

                -- Delete all messages in trash
                repeat with aMessage in trashMessages
                    delete aMessage
                end repeat

                set outputText to outputText & "✓ Emptied trash for account: {account}" & return
                set outputText to outputText & "   Deleted " & messageCount & " message(s)" & return

            on error errMsg
                return "Error: " & errMsg
            end try

            return outputText
        end tell
        '''
    elif action == "delete_permanent":
        # Build search condition
        conditions = []
        if subject_keyword:
            conditions.append(f'messageSubject contains "{subject_keyword}"')
        if sender:
            conditions.append(f'messageSender contains "{sender}"')

        condition_str = ' and '.join(conditions) if conditions else 'true'

        script = f'''
        tell application "Mail"
            set outputText to "PERMANENTLY DELETING EMAILS" & return & return
            set deleteCount to 0

            try
                set targetAccount to account "{account}"
                set trashMailbox to mailbox "Trash" of targetAccount
                set trashMessages to every message of trashMailbox

                repeat with aMessage in trashMessages
                    if deleteCount >= {max_deletes} then exit repeat

                    try
                        set messageSubject to subject of aMessage
                        set messageSender to sender of aMessage

                        -- Apply filter conditions
                        if {condition_str} then
                            set outputText to outputText & "✓ Permanently deleted: " & messageSubject & return
                            set outputText to outputText & "   From: " & messageSender & return & return

                            delete aMessage
                            set deleteCount to deleteCount + 1
                        end if
                    end try
                end repeat

                set outputText to outputText & "========================================" & return
                set outputText to outputText & "TOTAL DELETED: " & deleteCount & " email(s)" & return
                set outputText to outputText & "========================================" & return

            on error errMsg
                return "Error: " & errMsg
            end try

            return outputText
        end tell
        '''
    else:  # move_to_trash
        # Build search condition
        conditions = []
        if subject_keyword:
            conditions.append(f'messageSubject contains "{subject_keyword}"')
        if sender:
            conditions.append(f'messageSender contains "{sender}"')

        condition_str = ' and '.join(conditions) if conditions else 'true'

        script = f'''
        tell application "Mail"
            set outputText to "MOVING EMAILS TO TRASH" & return & return
            set deleteCount to 0

            try
                set targetAccount to account "{account}"
                -- Get source mailbox
                try
                    set sourceMailbox to mailbox "{mailbox}" of targetAccount
                on error
                    if "{mailbox}" is "INBOX" then
                        set sourceMailbox to mailbox "Inbox" of targetAccount
                    else
                        error "Mailbox not found: {mailbox}"
                    end if
                end try

                -- Get trash mailbox
                set trashMailbox to mailbox "Trash" of targetAccount
                set sourceMessages to every message of sourceMailbox

                repeat with aMessage in sourceMessages
                    if deleteCount >= {max_deletes} then exit repeat

                    try
                        set messageSubject to subject of aMessage
                        set messageSender to sender of aMessage
                        set messageDate to date received of aMessage

                        -- Apply filter conditions
                        if {condition_str} then
                            move aMessage to trashMailbox

                            set outputText to outputText & "✓ Moved to trash: " & messageSubject & return
                            set outputText to outputText & "   From: " & messageSender & return
                            set outputText to outputText & "   Date: " & (messageDate as string) & return & return

                            set deleteCount to deleteCount + 1
                        end if
                    end try
                end repeat

                set outputText to outputText & "========================================" & return
                set outputText to outputText & "TOTAL MOVED TO TRASH: " & deleteCount & " email(s)" & return
                set outputText to outputText & "========================================" & return

            on error errMsg
                return "Error: " & errMsg
            end try

            return outputText
        end tell
        '''

    result = run_applescript(script)
    return result
