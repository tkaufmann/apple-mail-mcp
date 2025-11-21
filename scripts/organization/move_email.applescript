-- Move email(s) matching a subject keyword from one mailbox to another
-- Arguments: account, subject_keyword, to_mailbox, from_mailbox, max_moves, mailbox_path_parts (JSON array as string)

on run argv
	set targetAccountName to item 1 of argv
	set subjectKeyword to item 2 of argv
	set toMailboxPath to item 3 of argv
	set fromMailboxName to item 4 of argv
	set maxMoves to item 5 of argv as integer
	set mailboxPathParts to item 6 of argv -- JSON array passed as string (e.g., "Project,Amplify")

	tell application "Mail"
		set outputText to "MOVING EMAILS" & return & return
		set movedCount to 0

		try
			set targetAccount to account targetAccountName

			-- Try to get source mailbox (handle both "INBOX"/"Inbox" variations)
			try
				set sourceMailbox to mailbox fromMailboxName of targetAccount
			on error
				if fromMailboxName is "INBOX" then
					set sourceMailbox to mailbox "Inbox" of targetAccount
				else
					error "Source mailbox not found"
				end if
			end try

			-- Get destination mailbox (handles nested mailboxes)
			set AppleScript's text item delimiters to ","
			set pathParts to text items of mailboxPathParts
			set AppleScript's text item delimiters to ""

			-- Build nested mailbox reference
			if (count of pathParts) > 1 then
				-- Nested mailbox - start from innermost
				set destMailbox to mailbox (item -1 of pathParts) of mailbox (item 1 of pathParts) of targetAccount

				-- Handle deeper nesting if needed
				if (count of pathParts) > 2 then
					repeat with i from 2 to ((count of pathParts) - 1)
						set destMailbox to mailbox (item -1 of pathParts) of mailbox (item i of pathParts) of targetAccount
					end repeat
				end if
			else
				-- Top-level mailbox
				set destMailbox to mailbox toMailboxPath of targetAccount
			end if

			set sourceMessages to every message of sourceMailbox

			repeat with aMessage in sourceMessages
				if movedCount ≥ maxMoves then exit repeat

				try
					set messageSubject to subject of aMessage

					-- Check if subject contains keyword (case insensitive)
					if messageSubject contains subjectKeyword then
						set messageSender to sender of aMessage
						set messageDate to date received of aMessage

						-- Move the message
						move aMessage to destMailbox

						set outputText to outputText & "✓ Moved: " & messageSubject & return
						set outputText to outputText & "  From: " & messageSender & return
						set outputText to outputText & "  Date: " & (messageDate as string) & return
						set outputText to outputText & "  " & fromMailboxName & " → " & toMailboxPath & return & return

						set movedCount to movedCount + 1
					end if
				end try
			end repeat

			set outputText to outputText & "========================================" & return
			set outputText to outputText & "TOTAL MOVED: " & movedCount & " email(s)" & return
			set outputText to outputText & "========================================" & return

		on error errMsg
			return "Error: " & errMsg & return & "Please check that account and mailbox names are correct. For nested mailboxes, use '/' separator (e.g., 'Projects/Amplify Impact')."
		end try

		return outputText
	end tell
end run
