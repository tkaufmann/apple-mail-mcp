"""
ABOUTME: Email composition tools for Apple Mail MCP Server
Provides tools for composing new emails, replying to emails, and forwarding messages.
"""

from typing import Optional
from mcp_instance import mcp
from utils.applescript import run_applescript, inject_preferences


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

    # Escape quotes for AppleScript
    escaped_subject = subject.replace('"', '\\"')
    escaped_body = body.replace('"', '\\"')

    # Build CC recipients if provided
    cc_script = ''
    if cc:
        cc_addresses = [addr.strip() for addr in cc.split(',')]
        for addr in cc_addresses:
            cc_script += f'''
            make new cc recipient at end of cc recipients of newMessage with properties {{address:"{addr}"}}
            '''

    # Build BCC recipients if provided
    bcc_script = ''
    if bcc:
        bcc_addresses = [addr.strip() for addr in bcc.split(',')]
        for addr in bcc_addresses:
            bcc_script += f'''
            make new bcc recipient at end of bcc recipients of newMessage with properties {{address:"{addr}"}}
            '''

    script = f'''
    tell application "Mail"
        set outputText to "COMPOSING EMAIL" & return & return

        try
            set targetAccount to account "{account}"

            -- Create new outgoing message
            set newMessage to make new outgoing message with properties {{subject:"{escaped_subject}", content:"{escaped_body}", visible:false}}

            -- Set the sender account
            set sender of newMessage to targetAccount

            -- Add TO recipients
            tell newMessage
                make new to recipient at end of to recipients with properties {{address:"{to}"}}
                {cc_script}
                {bcc_script}
            end tell

            -- Send the message
            send newMessage

            set outputText to outputText & "✓ Email sent successfully!" & return & return
            set outputText to outputText & "From: " & name of targetAccount & return
            set outputText to outputText & "To: {to}" & return
    '''

    if cc:
        script += f'''
            set outputText to outputText & "CC: {cc}" & return
    '''

    if bcc:
        script += f'''
            set outputText to outputText & "BCC: {bcc}" & return
    '''

    script += f'''
            set outputText to outputText & "Subject: {escaped_subject}" & return
            set outputText to outputText & "Body: " & "{escaped_body}" & return

        on error errMsg
            return "Error: " & errMsg & return & "Please check that the account name and email addresses are correct."
        end try

        return outputText
    end tell
    '''

    result = run_applescript(script)
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

    # Escape quotes in reply_body for AppleScript
    escaped_body = reply_body.replace('"', '\\"')

    # Build the reply command based on reply_to_all flag
    if reply_to_all:
        reply_command = 'set replyMessage to reply foundMessage with opening window reply to all'
    else:
        reply_command = 'set replyMessage to reply foundMessage with opening window'

    script = f'''
    tell application "Mail"
        set outputText to "SENDING REPLY" & return & return

        try
            set targetAccount to account "{account}"
            -- Try to get inbox (handle both "INBOX" and "Inbox")
            try
                set inboxMailbox to mailbox "INBOX" of targetAccount
            on error
                set inboxMailbox to mailbox "Inbox" of targetAccount
            end try
            set inboxMessages to every message of inboxMailbox
            set foundMessage to missing value

            -- Find the first matching message
            repeat with aMessage in inboxMessages
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

                -- Create reply
                {reply_command}

                -- Ensure the reply is from the correct account
                set sender of replyMessage to targetAccount

                -- Set reply content
                set content of replyMessage to "{escaped_body}"

                -- Send the reply
                send replyMessage

                set outputText to outputText & "✓ Reply sent successfully!" & return & return
                set outputText to outputText & "Original email:" & return
                set outputText to outputText & "  Subject: " & messageSubject & return
                set outputText to outputText & "  From: " & messageSender & return
                set outputText to outputText & "  Date: " & (messageDate as string) & return & return
                set outputText to outputText & "Reply body:" & return
                set outputText to outputText & "  " & "{escaped_body}" & return

            else
                set outputText to outputText & "⚠ No email found matching: {subject_keyword}" & return
            end if

        on error errMsg
            return "Error: " & errMsg & return & "Please check that the account name is correct and the email exists."
        end try

        return outputText
    end tell
    '''

    result = run_applescript(script)
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

    escaped_message = message.replace('"', '\\"') if message else ""

    script = f'''
    tell application "Mail"
        set outputText to "FORWARDING EMAIL" & return & return

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

            -- Find the first matching message
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

                -- Create forward
                set forwardMessage to forward foundMessage with opening window

                -- Set sender account
                set sender of forwardMessage to targetAccount

                -- Add recipients
                make new to recipient at end of to recipients of forwardMessage with properties {{address:"{to}"}}

                -- Add optional message
                if "{escaped_message}" is not "" then
                    set content of forwardMessage to "{escaped_message}" & return & return & content of forwardMessage
                end if

                -- Send the forward
                send forwardMessage

                set outputText to outputText & "✓ Email forwarded successfully!" & return & return
                set outputText to outputText & "Original email:" & return
                set outputText to outputText & "  Subject: " & messageSubject & return
                set outputText to outputText & "  From: " & messageSender & return
                set outputText to outputText & "  Date: " & (messageDate as string) & return & return
                set outputText to outputText & "Forwarded to: {to}" & return

            else
                set outputText to outputText & "⚠ No email found matching: {subject_keyword}" & return
            end if

        on error errMsg
            return "Error: " & errMsg
        end try

        return outputText
    end tell
    '''

    result = run_applescript(script)
    return result
