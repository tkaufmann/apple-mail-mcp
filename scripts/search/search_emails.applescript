-- Unified search tool - search emails with advanced filtering across any mailbox
-- Arguments: account, mailbox, subject_keyword, sender, has_attachments, read_status, date_from, date_to, include_content, max_results

on run argv
	set targetAccountName to item 1 of argv
	set mailboxName to item 2 of argv
	set subjectKeyword to item 3 of argv
	set senderFilter to item 4 of argv
	set hasAttachmentsFilter to item 5 of argv -- "true", "false", or "none"
	set readStatusFilter to item 6 of argv -- "all", "read", "unread"
	set dateFrom to item 7 of argv -- Not implemented yet
	set dateTo to item 8 of argv -- Not implemented yet
	set includeContent to item 9 of argv as boolean
	set maxResults to item 10 of argv as integer

	tell application "Mail"
		set outputText to "SEARCH RESULTS" & return & return
		set outputText to outputText & "Searching in: " & mailboxName & return
		set outputText to outputText & "Account: " & targetAccountName & return & return
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
						set messageSender to sender of aMessage
						set messageDate to date received of aMessage
						set messageRead to read status of aMessage
						set messageAttachmentCount to count of mail attachments of aMessage

						-- Apply search conditions (all must match)
						set matchesConditions to true

						-- Subject keyword filter
						if subjectKeyword is not "" then
							if messageSubject does not contain subjectKeyword then
								set matchesConditions to false
							end if
						end if

						-- Sender filter
						if senderFilter is not "" then
							if messageSender does not contain senderFilter then
								set matchesConditions to false
							end if
						end if

						-- Attachment filter
						if hasAttachmentsFilter is "true" then
							if messageAttachmentCount = 0 then
								set matchesConditions to false
							end if
						else if hasAttachmentsFilter is "false" then
							if messageAttachmentCount > 0 then
								set matchesConditions to false
							end if
						end if

						-- Read status filter
						if readStatusFilter is "read" then
							if messageRead is false then
								set matchesConditions to false
							end if
						else if readStatusFilter is "unread" then
							if messageRead is true then
								set matchesConditions to false
							end if
						end if

						-- If all conditions match, include this email
						if matchesConditions then
							if messageRead then
								set readIndicator to "✓"
							else
								set readIndicator to "✉"
							end if

							set outputText to outputText & readIndicator & " " & messageSubject & return
							set outputText to outputText & "   From: " & messageSender & return
							set outputText to outputText & "   Date: " & (messageDate as string) & return
							set outputText to outputText & "   Mailbox: " & currentMailboxName & return

							-- Include content preview if requested
							if includeContent then
								try
									set msgContent to content of aMessage
									set AppleScript's text item delimiters to {return, linefeed}
									set contentParts to text items of msgContent
									set AppleScript's text item delimiters to " "
									set cleanText to contentParts as string
									set AppleScript's text item delimiters to ""

									if length of cleanText > 300 then
										set contentPreview to text 1 thru 300 of cleanText & "..."
									else
										set contentPreview to cleanText
									end if

									set outputText to outputText & "   Content: " & contentPreview & return
								on error
									set outputText to outputText & "   Content: [Not available]" & return
								end try
							end if

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
