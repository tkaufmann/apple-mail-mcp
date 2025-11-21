-- Save a specific attachment from an email to disk
-- Arguments: account, subject_keyword, attachment_name, save_path

on run argv
	set targetAccountName to item 1 of argv
	set subjectKeyword to item 2 of argv
	set attachmentNameFilter to item 3 of argv
	set savePath to item 4 of argv

	tell application "Mail"
		set outputText to ""

		try
			set targetAccount to account targetAccountName
			-- Try to get inbox (handle both "INBOX" and "Inbox")
			try
				set inboxMailbox to mailbox "INBOX" of targetAccount
			on error
				set inboxMailbox to mailbox "Inbox" of targetAccount
			end try
			set inboxMessages to every message of inboxMailbox
			set foundAttachment to false

			repeat with aMessage in inboxMessages
				try
					set messageSubject to subject of aMessage

					-- Check if subject contains keyword
					if messageSubject contains subjectKeyword then
						set msgAttachments to mail attachments of aMessage

						repeat with anAttachment in msgAttachments
							set attachmentFileName to name of anAttachment

							if attachmentFileName contains attachmentNameFilter then
								-- Save the attachment
								save anAttachment in POSIX file savePath

								set outputText to "✓ Attachment saved successfully!" & return & return
								set outputText to outputText & "Email: " & messageSubject & return
								set outputText to outputText & "Attachment: " & attachmentFileName & return
								set outputText to outputText & "Saved to: " & savePath & return

								set foundAttachment to true
								exit repeat
							end if
						end repeat

						if foundAttachment then exit repeat
					end if
				end try
			end repeat

			if not foundAttachment then
				set outputText to "⚠ Attachment not found" & return
				set outputText to outputText & "Email keyword: " & subjectKeyword & return
				set outputText to outputText & "Attachment name: " & attachmentNameFilter & return
			end if

		on error errMsg
			return "Error: " & errMsg
		end try

		return outputText
	end tell
end run
