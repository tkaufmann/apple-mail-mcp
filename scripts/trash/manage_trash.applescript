-- Manage trash operations - delete emails or empty trash
-- Arguments: account, action, subject_keyword, sender, mailbox, max_deletes

on run argv
	set targetAccountName to item 1 of argv
	set actionType to item 2 of argv -- "empty_trash", "delete_permanent", "move_to_trash"
	set subjectKeyword to item 3 of argv -- Can be empty
	set senderFilter to item 4 of argv -- Can be empty
	set mailboxName to item 5 of argv
	set maxDeletes to item 6 of argv as integer

	tell application "Mail"
		if actionType is "empty_trash" then
			-- EMPTY TRASH
			set outputText to "EMPTYING TRASH" & return & return

			try
				set targetAccount to account targetAccountName
				set trashMailbox to mailbox "Trash" of targetAccount
				set trashMessages to every message of trashMailbox
				set messageCount to count of trashMessages

				-- Delete all messages in trash
				repeat with aMessage in trashMessages
					delete aMessage
				end repeat

				set outputText to outputText & "✓ Emptied trash for account: " & targetAccountName & return
				set outputText to outputText & "   Deleted " & messageCount & " message(s)" & return

			on error errMsg
				return "Error: " & errMsg
			end try

		else if actionType is "delete_permanent" then
			-- DELETE PERMANENT (from trash)
			set outputText to "PERMANENTLY DELETING EMAILS" & return & return
			set deleteCount to 0

			try
				set targetAccount to account targetAccountName
				set trashMailbox to mailbox "Trash" of targetAccount
				set trashMessages to every message of trashMailbox

				repeat with aMessage in trashMessages
					if deleteCount ≥ maxDeletes then exit repeat

					try
						set messageSubject to subject of aMessage
						set messageSender to sender of aMessage

						-- Apply filter conditions
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

		else
			-- MOVE TO TRASH
			set outputText to "MOVING EMAILS TO TRASH" & return & return
			set deleteCount to 0

			try
				set targetAccount to account targetAccountName
				-- Get source mailbox
				try
					set sourceMailbox to mailbox mailboxName of targetAccount
				on error
					if mailboxName is "INBOX" then
						set sourceMailbox to mailbox "Inbox" of targetAccount
					else
						error "Mailbox not found: " & mailboxName
					end if
				end try

				-- Get trash mailbox
				set trashMailbox to mailbox "Trash" of targetAccount
				set sourceMessages to every message of sourceMailbox

				repeat with aMessage in sourceMessages
					if deleteCount ≥ maxDeletes then exit repeat

					try
						set messageSubject to subject of aMessage
						set messageSender to sender of aMessage
						set messageDate to date received of aMessage

						-- Apply filter conditions
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
		end if

		return outputText
	end tell
end run
