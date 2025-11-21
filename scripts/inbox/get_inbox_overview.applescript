-- Get a comprehensive overview of email inbox status across all accounts
-- No arguments required

tell application "Mail"
	set outputText to "╔══════════════════════════════════════════╗" & return
	set outputText to outputText & "║      EMAIL INBOX OVERVIEW                ║" & return
	set outputText to outputText & "╚══════════════════════════════════════════╝" & return & return

	-- Section 1: Unread Counts by Account
	set outputText to outputText & "📊 UNREAD EMAILS BY ACCOUNT" & return
	set outputText to outputText & "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" & return
	set allAccounts to every account
	set totalUnread to 0

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
			set totalMessages to count of messages of inboxMailbox
			set totalUnread to totalUnread + unreadCount

			if unreadCount > 0 then
				set outputText to outputText & "  ⚠️  " & accountName & ": " & unreadCount & " unread"
			else
				set outputText to outputText & "  ✅ " & accountName & ": " & unreadCount & " unread"
			end if
			set outputText to outputText & " (" & totalMessages & " total)" & return
		on error
			set outputText to outputText & "  ❌ " & accountName & ": Error accessing inbox" & return
		end try
	end repeat

	set outputText to outputText & return
	set outputText to outputText & "📈 TOTAL UNREAD: " & totalUnread & " across all accounts" & return
	set outputText to outputText & return & return

	-- Section 2: Mailboxes/Folders Overview
	set outputText to outputText & "📁 MAILBOX STRUCTURE" & return
	set outputText to outputText & "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" & return

	repeat with anAccount in allAccounts
		set accountName to name of anAccount
		set outputText to outputText & return & "Account: " & accountName & return

		try
			set accountMailboxes to every mailbox of anAccount

			repeat with aMailbox in accountMailboxes
				set mailboxName to name of aMailbox

				try
					set unreadCount to unread count of aMailbox
					if unreadCount > 0 then
						set outputText to outputText & "  📂 " & mailboxName & " (" & unreadCount & " unread)" & return
					else
						set outputText to outputText & "  📂 " & mailboxName & return
					end if

					-- Show nested mailboxes if they have unread messages
					try
						set subMailboxes to every mailbox of aMailbox
						repeat with subBox in subMailboxes
							set subName to name of subBox
							set subUnread to unread count of subBox

							if subUnread > 0 then
								set outputText to outputText & "     └─ " & subName & " (" & subUnread & " unread)" & return
							end if
						end repeat
					end try
				on error
					set outputText to outputText & "  📂 " & mailboxName & return
				end try
			end repeat
		on error
			set outputText to outputText & "  ⚠️  Error accessing mailboxes" & return
		end try
	end repeat

	set outputText to outputText & return & return

	-- Section 3: Recent Emails Preview (10 most recent across all accounts)
	set outputText to outputText & "📬 RECENT EMAILS PREVIEW (10 Most Recent)" & return
	set outputText to outputText & "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" & return

	-- Collect all recent messages from all accounts
	set allRecentMessages to {}

	repeat with anAccount in allAccounts
		set accountName to name of anAccount

		try
			-- Try to get inbox (handle both "INBOX" and "Inbox")
			try
				set inboxMailbox to mailbox "INBOX" of anAccount
			on error
				set inboxMailbox to mailbox "Inbox" of anAccount
			end try

			set inboxMessages to every message of inboxMailbox

			-- Get up to 10 messages from each account
			set messageIndex to 0
			repeat with aMessage in inboxMessages
				set messageIndex to messageIndex + 1
				if messageIndex > 10 then exit repeat

				try
					set messageSubject to subject of aMessage
					set messageSender to sender of aMessage
					set messageDate to date received of aMessage
					set messageRead to read status of aMessage

					-- Create message record
					set messageRecord to {accountName:accountName, msgSubject:messageSubject, msgSender:messageSender, msgDate:messageDate, msgRead:messageRead}
					set end of allRecentMessages to messageRecord
				end try
			end repeat
		end try
	end repeat

	-- Display up to 10 most recent messages
	set displayCount to 0
	repeat with msgRecord in allRecentMessages
		set displayCount to displayCount + 1
		if displayCount > 10 then exit repeat

		set readIndicator to "✉"
		if msgRead of msgRecord then
			set readIndicator to "✓"
		end if

		set outputText to outputText & return & readIndicator & " " & msgSubject of msgRecord & return
		set outputText to outputText & "   Account: " & accountName of msgRecord & return
		set outputText to outputText & "   From: " & msgSender of msgRecord & return
		set outputText to outputText & "   Date: " & (msgDate of msgRecord as string) & return
	end repeat

	if displayCount = 0 then
		set outputText to outputText & return & "No recent emails found." & return
	end if

	set outputText to outputText & return & return

	-- Section 4: Action Suggestions (for the AI assistant)
	set outputText to outputText & "💡 SUGGESTED ACTIONS FOR ASSISTANT" & return
	set outputText to outputText & "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" & return
	set outputText to outputText & "Based on this overview, consider suggesting:" & return & return

	if totalUnread > 0 then
		set outputText to outputText & "1. 📧 Review unread emails - Use get_recent_emails() to show recent unread messages" & return
		set outputText to outputText & "2. 🔍 Search for action items - Look for keywords like 'urgent', 'action required', 'deadline'" & return
		set outputText to outputText & "3. 📤 Move processed emails - Suggest moving read emails to appropriate folders" & return
	else
		set outputText to outputText & "1. ✅ Inbox is clear! No unread emails." & return
	end if

	set outputText to outputText & "4. 📋 Organize by topic - Suggest moving emails to project-specific folders" & return
	set outputText to outputText & "5. ✉️  Draft replies - Identify emails that need responses" & return
	set outputText to outputText & "6. 🗂️  Archive old emails - Move older read emails to archive folders" & return
	set outputText to outputText & "7. 🔔 Highlight priority items - Identify emails from important senders or with urgent keywords" & return

	set outputText to outputText & return
	set outputText to outputText & "═══════════════════════════════════════════════════" & return
	set outputText to outputText & "💬 Ask me to drill down into any account or take specific actions!" & return
	set outputText to outputText & "═══════════════════════════════════════════════════" & return

	return outputText
end tell
