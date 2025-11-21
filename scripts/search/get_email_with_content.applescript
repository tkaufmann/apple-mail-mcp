-- Search for emails by subject keyword and return with full content preview
-- Arguments: account, subject_keyword, max_results, max_content_length, mailbox

-- Helper function for case-insensitive matching
on lowercase(str)
	set lowerStr to do shell script "echo " & quoted form of str & " | tr '[:upper:]' '[:lower:]'"
	return lowerStr
end lowercase

on run argv
	set targetAccountName to item 1 of argv
	set subjectKeyword to item 2 of argv
	set maxResults to item 3 of argv as integer
	set maxContentLength to item 4 of argv as integer
	set mailboxName to item 5 of argv

	tell application "Mail"
		set outputText to "SEARCH RESULTS FOR: " & subjectKeyword & return
		set outputText to outputText & "Searching in: " & mailboxName & return & return
		set resultCount to 0

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

			repeat with currentMailbox in searchMailboxes
				set mailboxMessages to every message of currentMailbox
				set currentMailboxName to name of currentMailbox

				repeat with aMessage in mailboxMessages
					if resultCount ≥ maxResults then exit repeat

					try
						set messageSubject to subject of aMessage

						-- Convert to lowercase for case-insensitive matching
						set lowerSubject to my lowercase(messageSubject)
						set lowerKeyword to my lowercase(subjectKeyword)

						-- Check if subject contains keyword (case insensitive)
						if lowerSubject contains lowerKeyword then
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
							set outputText to outputText & "   Mailbox: " & currentMailboxName & return

							-- Get content preview
							try
								set msgContent to content of aMessage
								set AppleScript's text item delimiters to {return, linefeed}
								set contentParts to text items of msgContent
								set AppleScript's text item delimiters to " "
								set cleanText to contentParts as string
								set AppleScript's text item delimiters to ""

								-- Handle content length limit (0 = unlimited)
								if maxContentLength > 0 and length of cleanText > maxContentLength then
									set contentPreview to text 1 thru maxContentLength of cleanText & "..."
								else
									set contentPreview to cleanText
								end if

								set outputText to outputText & "   Content: " & contentPreview & return
							on error
								set outputText to outputText & "   Content: [Not available]" & return
							end try

							set outputText to outputText & return
							set resultCount to resultCount + 1
						end if
					end try
				end repeat
			end repeat

			set outputText to outputText & "========================================" & return
			set outputText to outputText & "FOUND: " & resultCount & " matching email(s)" & return
			set outputText to outputText & "========================================" & return

		on error errMsg
			return "Error: " & errMsg
		end try

		return outputText
	end tell
end run
