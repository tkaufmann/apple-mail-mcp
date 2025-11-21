-- Update email status - mark as read/unread or flag/unflag emails
-- Arguments: account, action, subject_keyword, sender, mailbox, max_updates

on run argv
	set targetAccountName to item 1 of argv
	set actionType to item 2 of argv -- "mark_read", "mark_unread", "flag", "unflag"
	set subjectKeyword to item 3 of argv -- Can be empty string
	set senderFilter to item 4 of argv -- Can be empty string
	set mailboxName to item 5 of argv
	set maxUpdates to item 6 of argv as integer

	-- Set action label and determine action
	if actionType is "mark_read" then
		set actionLabel to "Marked as read"
	else if actionType is "mark_unread" then
		set actionLabel to "Marked as unread"
	else if actionType is "flag" then
		set actionLabel to "Flagged"
	else if actionType is "unflag" then
		set actionLabel to "Unflagged"
	else
		return "Error: Invalid action '" & actionType & "'. Use: mark_read, mark_unread, flag, unflag"
	end if

	tell application "Mail"
		set outputText to "UPDATING EMAIL STATUS: " & actionLabel & return & return
		set updateCount to 0

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

			repeat with aMessage in mailboxMessages
				if updateCount ≥ maxUpdates then exit repeat

				try
					set messageSubject to subject of aMessage
					set messageSender to sender of aMessage
					set messageDate to date received of aMessage

					-- Apply filter conditions (all must match)
					set matchesConditions to true

					if subjectKeyword is not "" then
						if messageSubject does not contain subjectKeyword then
							set matchesConditions to false
						end if
					end if

					if senderFilter is not "" then
						if messageSender does not contain senderFilter then
							set matchesConditions to false
						end if
					end if

					if matchesConditions then
						-- Perform action
						if actionType is "mark_read" then
							set read status of aMessage to true
						else if actionType is "mark_unread" then
							set read status of aMessage to false
						else if actionType is "flag" then
							set flagged status of aMessage to true
						else if actionType is "unflag" then
							set flagged status of aMessage to false
						end if

						set outputText to outputText & "✓ " & actionLabel & ": " & messageSubject & return
						set outputText to outputText & "   From: " & messageSender & return
						set outputText to outputText & "   Date: " & (messageDate as string) & return & return

						set updateCount to updateCount + 1
					end if
				end try
			end repeat

			set outputText to outputText & "========================================" & return
			set outputText to outputText & "TOTAL UPDATED: " & updateCount & " email(s)" & return
			set outputText to outputText & "========================================" & return

		on error errMsg
			return "Error: " & errMsg
		end try

		return outputText
	end tell
end run
