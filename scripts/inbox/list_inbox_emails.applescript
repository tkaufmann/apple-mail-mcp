-- List all emails from inbox across all accounts or a specific account
-- Arguments: account (string or empty), max_emails (int), include_read (true/false)

on run argv
	set accountFilter to item 1 of argv
	set maxEmails to item 2 of argv as integer
	set includeRead to item 3 of argv as boolean

	tell application "Mail"
		set outputText to "INBOX EMAILS - ALL ACCOUNTS" & return & return
		set totalCount to 0
		set allAccounts to every account

		repeat with anAccount in allAccounts
			set accountName to name of anAccount

			-- Skip if account filter is set and doesn't match
			if accountFilter is not "" and accountName is not accountFilter then
				-- Skip this account
			else
				try
					-- Try to get inbox (handle both "INBOX" and "Inbox")
					try
						set inboxMailbox to mailbox "INBOX" of anAccount
					on error
						set inboxMailbox to mailbox "Inbox" of anAccount
					end try
					set inboxMessages to every message of inboxMailbox
					set messageCount to count of inboxMessages

					if messageCount > 0 then
						set outputText to outputText & "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" & return
						set outputText to outputText & "📧 ACCOUNT: " & accountName & " (" & messageCount & " messages)" & return
						set outputText to outputText & "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" & return & return

						set currentIndex to 0
						repeat with aMessage in inboxMessages
							set currentIndex to currentIndex + 1
							if maxEmails > 0 and currentIndex > maxEmails then exit repeat

							try
								set messageSubject to subject of aMessage
								set messageSender to sender of aMessage
								set messageDate to date received of aMessage
								set messageRead to read status of aMessage

								set shouldInclude to true
								if not includeRead and messageRead then
									set shouldInclude to false
								end if

								if shouldInclude then
									if messageRead then
										set readIndicator to "✓"
									else
										set readIndicator to "✉"
									end if

									set outputText to outputText & readIndicator & " " & messageSubject & return
									set outputText to outputText & "   From: " & messageSender & return
									set outputText to outputText & "   Date: " & (messageDate as string) & return
									set outputText to outputText & return

									set totalCount to totalCount + 1
								end if
							end try
						end repeat
					end if
				on error errMsg
					set outputText to outputText & "⚠ Error accessing inbox for account " & accountName & return
					set outputText to outputText & "   " & errMsg & return & return
				end try
			end if
		end repeat

		set outputText to outputText & "========================================" & return
		set outputText to outputText & "TOTAL EMAILS: " & totalCount & return
		set outputText to outputText & "========================================" & return

		return outputText
	end tell
end run
