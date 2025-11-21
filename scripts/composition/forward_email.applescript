-- Forward an email to one or more recipients
-- Arguments: account, subject_keyword, to, message, mailbox

on run argv
	set targetAccountName to item 1 of argv
	set subjectKeyword to item 2 of argv
	set toRecipients to item 3 of argv
	set forwardMessage to item 4 of argv -- Can be empty string
	set mailboxName to item 5 of argv

	tell application "Mail"
		set outputText to "FORWARDING EMAIL" & return & return

		try
			set targetAccount to account targetAccountName

			-- Try to get mailbox
			try
				set targetMailbox to mailbox mailboxName of targetAccount
			on error
				if mailboxName is "INBOX" then
					set targetMailbox to mailbox "Inbox" of targetAccount
				else
					error "Mailbox not found: " & mailboxName
				end if
			end try

			set mailboxMessages to every message of targetMailbox
			set foundMessage to missing value

			-- Find the first matching message
			repeat with aMessage in mailboxMessages
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

				-- Create forward
				set forwardMsg to forward foundMessage with opening window

				-- Set sender account (use first email address from account)
				set accountEmails to email addresses of targetAccount
				if (count of accountEmails) > 0 then
					set sender of forwardMsg to item 1 of accountEmails
				end if

				-- Add recipients
				make new to recipient at end of to recipients of forwardMsg with properties {address:toRecipients}

				-- Add optional message
				if forwardMessage is not "" then
					set content of forwardMsg to forwardMessage & return & return & content of forwardMsg
				end if

				-- Send the forward
				send forwardMsg

				set outputText to outputText & "✓ Email forwarded successfully!" & return & return
				set outputText to outputText & "Original email:" & return
				set outputText to outputText & "  Subject: " & messageSubject & return
				set outputText to outputText & "  From: " & messageSender & return
				set outputText to outputText & "  Date: " & (messageDate as string) & return & return
				set outputText to outputText & "Forwarded to: " & toRecipients & return

			else
				set outputText to outputText & "⚠ No email found matching: " & subjectKeyword & return
			end if

		on error errMsg
			return "Error: " & errMsg
		end try

		return outputText
	end tell
end run
