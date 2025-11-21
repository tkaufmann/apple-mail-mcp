-- Get the count of unread emails for each account
-- No arguments required

tell application "Mail"
	set resultList to {}
	set allAccounts to every account

	repeat with anAccount in allAccounts
		set accountName to name of anAccount

		try
			-- Try to get inbox (handle both "INBOX" and "Inbox")
			try
				set inboxMailbox to mailbox "INBOX" of anAccount
			on error
				set inboxMailbox to mailbox "Inbox" of anAccount
			end try
			set unreadCount to unread count of inboxMailbox
			set end of resultList to accountName & ":" & unreadCount
		on error
			set end of resultList to accountName & ":ERROR"
		end try
	end repeat

	set AppleScript's text item delimiters to "|"
	return resultList as string
end tell
