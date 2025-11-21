-- Get an email conversation thread - all messages with the same or similar subject
-- Arguments: account, cleaned_keyword, mailbox, max_messages
-- Note: cleaned_keyword should already have Re:/Fwd: prefixes removed by Python

on run argv
	set targetAccountName to item 1 of argv
	set cleanedKeyword to item 2 of argv
	set mailboxName to item 3 of argv
	set maxMessages to item 4 of argv as integer

	tell application "Mail"
		set outputText to "EMAIL THREAD VIEW" & return & return
		set outputText to outputText & "Thread topic: " & cleanedKeyword & return
		set outputText to outputText & "Account: " & targetAccountName & return & return
		set threadMessages to {}

		try
			set targetAccount to account targetAccountName

			-- Build mailbox list based on mailbox parameter
			if mailboxName is "All" then
				set searchMailboxes to every mailbox of targetAccount
			else
				try
					set searchMailbox to mailbox mailboxName of targetAccount
				on error
					if mailboxName is "INBOX" then
						set searchMailbox to mailbox "Inbox" of targetAccount
					else
						error "Mailbox not found: " & mailboxName
					end if
				end try
				set searchMailboxes to {searchMailbox}
			end if

			-- Collect all matching messages from all mailboxes
			repeat with currentMailbox in searchMailboxes
				set mailboxMessages to every message of currentMailbox

				repeat with aMessage in mailboxMessages
					if (count of threadMessages) ≥ maxMessages then exit repeat

					try
						set messageSubject to subject of aMessage

						-- Remove common prefixes for matching
						set cleanSubject to messageSubject
						if cleanSubject starts with "Re: " then
							set cleanSubject to text 5 thru -1 of cleanSubject
						end if
						if cleanSubject starts with "Fwd: " or cleanSubject starts with "FW: " or cleanSubject starts with "Fw: " then
							try
								set cleanSubject to text 6 thru -1 of cleanSubject
							end try
						end if
						if cleanSubject starts with "RE: " then
							set cleanSubject to text 5 thru -1 of cleanSubject
						end if

						-- Check if this message is part of the thread
						if cleanSubject contains cleanedKeyword or messageSubject contains cleanedKeyword then
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
						set AppleScript's text item delimiters to {return, linefeed}
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
end run
