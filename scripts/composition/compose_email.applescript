-- Compose and send a new email from a specific account
-- Arguments: account, to, subject, body, cc, bcc

on run argv
	set targetAccountName to item 1 of argv
	set toRecipients to item 2 of argv
	set emailSubject to item 3 of argv
	set emailBody to item 4 of argv
	set ccRecipients to item 5 of argv -- Can be empty string
	set bccRecipients to item 6 of argv -- Can be empty string

	tell application "Mail"
		set outputText to "COMPOSING EMAIL" & return & return

		try
			set targetAccount to account targetAccountName

			-- Create new outgoing message
			set newMessage to make new outgoing message with properties {subject:emailSubject, content:emailBody, visible:false}

			-- Set the sender account
			set sender of newMessage to targetAccount

			-- Add TO recipients
			tell newMessage
				make new to recipient at end of to recipients with properties {address:toRecipients}

				-- Add CC recipients if provided
				if ccRecipients is not "" then
					set AppleScript's text item delimiters to ","
					set ccList to text items of ccRecipients
					set AppleScript's text item delimiters to ""

					repeat with ccAddr in ccList
						set trimmedAddr to my trimString(ccAddr)
						if trimmedAddr is not "" then
							make new cc recipient at end of cc recipients with properties {address:trimmedAddr}
						end if
					end repeat
				end if

				-- Add BCC recipients if provided
				if bccRecipients is not "" then
					set AppleScript's text item delimiters to ","
					set bccList to text items of bccRecipients
					set AppleScript's text item delimiters to ""

					repeat with bccAddr in bccList
						set trimmedAddr to my trimString(bccAddr)
						if trimmedAddr is not "" then
							make new bcc recipient at end of bcc recipients with properties {address:trimmedAddr}
						end if
					end repeat
				end if
			end tell

			-- Send the message
			send newMessage

			set outputText to outputText & "✓ Email sent successfully!" & return & return
			set outputText to outputText & "From: " & name of targetAccount & return
			set outputText to outputText & "To: " & toRecipients & return

			if ccRecipients is not "" then
				set outputText to outputText & "CC: " & ccRecipients & return
			end if

			if bccRecipients is not "" then
				set outputText to outputText & "BCC: " & bccRecipients & return
			end if

			set outputText to outputText & "Subject: " & emailSubject & return
			set outputText to outputText & "Body: " & emailBody & return

		on error errMsg
			return "Error: " & errMsg & return & "Please check that the account name and email addresses are correct."
		end try

		return outputText
	end tell
end run

-- Helper function to trim whitespace
on trimString(theString)
	set trimmedString to theString
	try
		repeat while trimmedString starts with " "
			set trimmedString to text 2 thru -1 of trimmedString
		end repeat
		repeat while trimmedString ends with " "
			set trimmedString to text 1 thru -2 of trimmedString
		end repeat
	end try
	return trimmedString
end trimString
