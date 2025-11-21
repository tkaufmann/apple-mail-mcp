-- Get comprehensive email statistics and analytics
-- Arguments: account, scope, sender, mailbox, days_back

on run argv
	set targetAccountName to item 1 of argv
	set scopeType to item 2 of argv -- "account_overview", "sender_stats", "mailbox_breakdown"
	set senderFilter to item 3 of argv -- Can be empty
	set mailboxFilter to item 4 of argv -- Can be empty
	set daysBack to item 5 of argv as integer

	tell application "Mail"
		-- Calculate date threshold if days_back > 0
		if daysBack > 0 then
			set targetDate to (current date) - (daysBack * days)
			set useDateFilter to true
		else
			set useDateFilter to false
		end if

		if scopeType is "account_overview" then
			-- ACCOUNT OVERVIEW
			set outputText to "╔══════════════════════════════════════════╗" & return
			set outputText to outputText & "║      EMAIL STATISTICS - " & targetAccountName & "       ║" & return
			set outputText to outputText & "╚══════════════════════════════════════════╝" & return & return

			try
				set targetAccount to account targetAccountName
				set allMailboxes to every mailbox of targetAccount

				-- Initialize counters
				set totalEmails to 0
				set totalUnread to 0
				set totalRead to 0
				set totalFlagged to 0
				set totalWithAttachments to 0

				-- Analyze all mailboxes
				repeat with aMailbox in allMailboxes
					set mailboxMessages to every message of aMailbox

					repeat with aMessage in mailboxMessages
						try
							set messageDate to date received of aMessage

							-- Apply date filter if specified
							set includeMessage to true
							if useDateFilter and messageDate < targetDate then
								set includeMessage to false
							end if

							if includeMessage then
								set totalEmails to totalEmails + 1

								-- Count read/unread
								if read status of aMessage then
									set totalRead to totalRead + 1
								else
									set totalUnread to totalUnread + 1
								end if

								-- Count flagged
								try
									if flagged status of aMessage then
										set totalFlagged to totalFlagged + 1
									end if
								end try

								-- Count attachments
								set attachmentCount to count of mail attachments of aMessage
								if attachmentCount > 0 then
									set totalWithAttachments to totalWithAttachments + 1
								end if
							end if
						end try
					end repeat
				end repeat

				-- Format output
				set outputText to outputText & "📊 VOLUME METRICS" & return
				set outputText to outputText & "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" & return
				set outputText to outputText & "Total Emails: " & totalEmails & return

				if totalEmails > 0 then
					set unreadPercent to round ((totalUnread / totalEmails) * 100)
					set readPercent to round ((totalRead / totalEmails) * 100)
					set attachPercent to round ((totalWithAttachments / totalEmails) * 100)

					set outputText to outputText & "Unread: " & totalUnread & " (" & unreadPercent & "%)" & return
					set outputText to outputText & "Read: " & totalRead & " (" & readPercent & "%)" & return
					set outputText to outputText & "Flagged: " & totalFlagged & return
					set outputText to outputText & "With Attachments: " & totalWithAttachments & " (" & attachPercent & "%)" & return
				end if

			on error errMsg
				return "Error: " & errMsg
			end try

		else if scopeType is "sender_stats" then
			-- SENDER STATISTICS
			set outputText to "SENDER STATISTICS" & return & return
			set outputText to outputText & "Sender: " & senderFilter & return
			set outputText to outputText & "Account: " & targetAccountName & return & return

			try
				set targetAccount to account targetAccountName
				set allMailboxes to every mailbox of targetAccount

				set totalFromSender to 0
				set unreadFromSender to 0
				set withAttachments to 0

				repeat with aMailbox in allMailboxes
					set mailboxMessages to every message of aMailbox

					repeat with aMessage in mailboxMessages
						try
							set messageSender to sender of aMessage
							set messageDate to date received of aMessage

							-- Check sender match and date filter
							set includeMessage to messageSender contains senderFilter
							if includeMessage and useDateFilter and messageDate < targetDate then
								set includeMessage to false
							end if

							if includeMessage then
								set totalFromSender to totalFromSender + 1

								if not (read status of aMessage) then
									set unreadFromSender to unreadFromSender + 1
								end if

								if (count of mail attachments of aMessage) > 0 then
									set withAttachments to withAttachments + 1
								end if
							end if
						end try
					end repeat
				end repeat

				set outputText to outputText & "Total emails: " & totalFromSender & return
				set outputText to outputText & "Unread: " & unreadFromSender & return
				set outputText to outputText & "With attachments: " & withAttachments & return

			on error errMsg
				return "Error: " & errMsg
			end try

		else if scopeType is "mailbox_breakdown" then
			-- MAILBOX STATISTICS
			set mailboxParam to mailboxFilter
			if mailboxParam is "" then
				set mailboxParam to "INBOX"
			end if

			set outputText to "MAILBOX STATISTICS" & return & return
			set outputText to outputText & "Mailbox: " & mailboxParam & return
			set outputText to outputText & "Account: " & targetAccountName & return & return

			try
				set targetAccount to account targetAccountName
				try
					set targetMailbox to mailbox mailboxParam of targetAccount
				on error
					if mailboxParam is "INBOX" then
						set targetMailbox to mailbox "Inbox" of targetAccount
					else
						error "Mailbox not found"
					end if
				end try

				set mailboxMessages to every message of targetMailbox
				set totalMessages to count of mailboxMessages
				set unreadMessages to unread count of targetMailbox

				set outputText to outputText & "Total messages: " & totalMessages & return
				set outputText to outputText & "Unread: " & unreadMessages & return
				set outputText to outputText & "Read: " & (totalMessages - unreadMessages) & return

			on error errMsg
				return "Error: " & errMsg
			end try

		else
			return "Error: Invalid scope '" & scopeType & "'. Use: account_overview, sender_stats, mailbox_breakdown"
		end if

		return outputText
	end tell
end run
