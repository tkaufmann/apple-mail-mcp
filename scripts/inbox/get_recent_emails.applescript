-- Get the most recent emails from a specific account
-- Arguments: account (string), count (int), include_content (true/false)

on run argv
	set targetAccountName to item 1 of argv
	set emailCount to item 2 of argv as integer
	set includeContent to item 3 of argv as boolean

	tell application "Mail"
		set outputText to "RECENT EMAILS - " & targetAccountName & return & return

		try
			set targetAccount to account targetAccountName
			-- Try to get inbox (handle both "INBOX" and "Inbox")
			try
				set inboxMailbox to mailbox "INBOX" of targetAccount
			on error
				set inboxMailbox to mailbox "Inbox" of targetAccount
			end try
			set inboxMessages to every message of inboxMailbox

			set currentIndex to 0
			repeat with aMessage in inboxMessages
				set currentIndex to currentIndex + 1
				if currentIndex > emailCount then exit repeat

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

					-- Include content preview if requested
					if includeContent then
						try
							set msgContent to content of aMessage
							set AppleScript's text item delimiters to {return, linefeed}
							set contentParts to text items of msgContent
							set AppleScript's text item delimiters to " "
							set cleanText to contentParts as string
							set AppleScript's text item delimiters to ""

							if length of cleanText > 200 then
								set contentPreview to text 1 thru 200 of cleanText & "..."
							else
								set contentPreview to cleanText
			end if

							set outputText to outputText & "   Preview: " & contentPreview & return
						on error
							set outputText to outputText & "   Preview: [Not available]" & return
						end try
					end if

					set outputText to outputText & return
				end try
			end repeat

			set outputText to outputText & "========================================" & return
			set outputText to outputText & "Showing " & (currentIndex - 1) & " email(s)" & return
			set outputText to outputText & "========================================" & return

		on error errMsg
			return "Error: " & errMsg
		end try

		return outputText
	end tell
end run
