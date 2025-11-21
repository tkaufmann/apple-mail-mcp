-- List all mailboxes (folders) for a specific account or all accounts
-- Arguments: account (empty for all), include_counts

on run argv
	set accountFilter to item 1 of argv -- Can be empty string for all accounts
	set includeCounts to item 2 of argv as boolean

	tell application "Mail"
		set outputText to "MAILBOXES" & return & return
		set allAccounts to every account

		repeat with anAccount in allAccounts
			set accountName to name of anAccount

			-- Skip if account filter is set and doesn't match
			set shouldProcess to true
			if accountFilter is not "" and accountName is not accountFilter then
				set shouldProcess to false
			end if

			if shouldProcess then
				set outputText to outputText & "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" & return
				set outputText to outputText & "📁 ACCOUNT: " & accountName & return
				set outputText to outputText & "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" & return & return

				try
					set accountMailboxes to every mailbox of anAccount

					repeat with aMailbox in accountMailboxes
						set mailboxName to name of aMailbox
						set outputText to outputText & "  📂 " & mailboxName

						-- Add message counts if requested
						if includeCounts then
							try
								set msgCount to count of messages of aMailbox
								set unreadCount to unread count of aMailbox
								set outputText to outputText & " (" & msgCount & " total, " & unreadCount & " unread)"
							on error
								set outputText to outputText & " (count unavailable)"
							end try
						end if

						set outputText to outputText & return

						-- List sub-mailboxes with path notation
						try
							set subMailboxes to every mailbox of aMailbox
							repeat with subBox in subMailboxes
								set subName to name of subBox
								set outputText to outputText & "    └─ " & subName & " [Path: " & mailboxName & "/" & subName & "]"

								-- Add counts for sub-mailboxes if requested
								if includeCounts then
									try
										set subMsgCount to count of messages of subBox
										set subUnreadCount to unread count of subBox
										set outputText to outputText & " (" & subMsgCount & " total, " & subUnreadCount & " unread)"
									on error
										set outputText to outputText & " (count unavailable)"
									end try
								end if

								set outputText to outputText & return
							end repeat
						end try
					end repeat

					set outputText to outputText & return
				on error errMsg
					set outputText to outputText & "  ⚠ Error accessing mailboxes: " & errMsg & return & return
				end try
			end if
		end repeat

		return outputText
	end tell
end run
