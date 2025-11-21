-- List attachments for emails matching a subject keyword
-- Arguments: account, subject_keyword, max_results

on run argv
	set targetAccountName to item 1 of argv
	set subjectKeyword to item 2 of argv
	set maxResults to item 3 of argv as integer

	tell application "Mail"
		set outputText to "ATTACHMENTS FOR: " & subjectKeyword & return & return
		set resultCount to 0

		try
			set targetAccount to account targetAccountName
			-- Try to get inbox (handle both "INBOX" and "Inbox")
			try
				set inboxMailbox to mailbox "INBOX" of targetAccount
			on error
				set inboxMailbox to mailbox "Inbox" of targetAccount
			end try
			set inboxMessages to every message of inboxMailbox

			repeat with aMessage in inboxMessages
				if resultCount ≥ maxResults then exit repeat

				try
					set messageSubject to subject of aMessage

					-- Check if subject contains keyword
					if messageSubject contains subjectKeyword then
						set messageSender to sender of aMessage
						set messageDate to date received of aMessage

						set outputText to outputText & "✉ " & messageSubject & return
						set outputText to outputText & "   From: " & messageSender & return
						set outputText to outputText & "   Date: " & (messageDate as string) & return & return

						-- Get attachments
						set msgAttachments to mail attachments of aMessage
						set attachmentCount to count of msgAttachments

						if attachmentCount > 0 then
							set outputText to outputText & "   Attachments (" & attachmentCount & "):" & return

							repeat with anAttachment in msgAttachments
								set attachmentName to name of anAttachment
								try
									set attachmentSize to size of anAttachment
									set sizeInKB to (attachmentSize / 1024) as integer
									set outputText to outputText & "   📎 " & attachmentName & " (" & sizeInKB & " KB)" & return
								on error
									set outputText to outputText & "   📎 " & attachmentName & return
								end try
							end repeat
						else
							set outputText to outputText & "   No attachments" & return
						end if

						set outputText to outputText & return
						set resultCount to resultCount + 1
					end if
				end try
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
