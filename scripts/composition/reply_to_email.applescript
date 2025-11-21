-- Reply to an email matching a subject keyword
-- Arguments: account, subject_keyword, reply_body, reply_to_all

on run argv
	set targetAccountName to item 1 of argv
	set subjectKeyword to item 2 of argv
	set replyBody to item 3 of argv
	set replyToAll to item 4 of argv as boolean

	tell application "Mail"
		set outputText to "SENDING REPLY" & return & return

		try
			set targetAccount to account targetAccountName

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

					if messageSubject contains subjectKeyword then
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
				if replyToAll then
					set replyMessage to reply foundMessage with opening window reply to all
				else
					set replyMessage to reply foundMessage with opening window
				end if

				-- Ensure the reply is from the correct account
				set sender of replyMessage to targetAccount

				-- Set reply content
				set content of replyMessage to replyBody

				-- Send the reply
				send replyMessage

				set outputText to outputText & "✓ Reply sent successfully!" & return & return
				set outputText to outputText & "Original email:" & return
				set outputText to outputText & "  Subject: " & messageSubject & return
				set outputText to outputText & "  From: " & messageSender & return
				set outputText to outputText & "  Date: " & (messageDate as string) & return & return
				set outputText to outputText & "Reply body:" & return
				set outputText to outputText & "  " & replyBody & return

			else
				set outputText to outputText & "⚠ No email found matching: " & subjectKeyword & return
			end if

		on error errMsg
			return "Error: " & errMsg & return & "Please check that the account name is correct and the email exists."
		end try

		return outputText
	end tell
end run
