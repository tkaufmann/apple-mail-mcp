-- Manage draft emails - list, create, send, or delete drafts
-- Arguments: account, action, subject, to, body, cc, bcc, draft_subject

on run argv
	set targetAccountName to item 1 of argv
	set actionType to item 2 of argv -- "list", "create", "send", "delete"
	set emailSubject to item 3 of argv -- Can be empty
	set toRecipients to item 4 of argv -- Can be empty
	set emailBody to item 5 of argv -- Can be empty
	set ccRecipients to item 6 of argv -- Can be empty
	set bccRecipients to item 7 of argv -- Can be empty
	set draftSubjectKeyword to item 8 of argv -- Can be empty

	tell application "Mail"
		if actionType is "list" then
			-- LIST DRAFTS
			set outputText to "DRAFT EMAILS - " & targetAccountName & return & return

			try
				set targetAccount to account targetAccountName
				set draftsMailbox to mailbox "Drafts" of targetAccount
				set draftMessages to every message of draftsMailbox
				set draftCount to count of draftMessages

				set outputText to outputText & "Found " & draftCount & " draft(s)" & return & return

				repeat with aDraft in draftMessages
					try
						set draftSubject to subject of aDraft
						set draftDate to date sent of aDraft

						set outputText to outputText & "✉ " & draftSubject & return
						set outputText to outputText & "   Created: " & (draftDate as string) & return & return
					end try
				end repeat

			on error errMsg
				return "Error: " & errMsg
			end try

		else if actionType is "create" then
			-- CREATE DRAFT
			set outputText to "CREATING DRAFT" & return & return

			try
				set targetAccount to account targetAccountName

				-- Create new outgoing message (draft)
				set newDraft to make new outgoing message with properties {subject:emailSubject, content:emailBody, visible:false}

				-- Set the sender account
				set sender of newDraft to targetAccount

				-- Add recipients
				tell newDraft
					make new to recipient at end of to recipients with properties {address:toRecipients}

					-- Add CC recipients if provided
					if ccRecipients is not "" then
						set AppleScript's text item delimiters to ","
						set ccList to text items of ccRecipients
						set AppleScript's text item delimiters to ""

						repeat with ccAddr in ccList
							set trimmedAddr to my trimString(ccAddr)
							if trimmedAddr is not "" then
								make new cc recipient at end of cc recipients with properties {address:trimmedAddr}
							end if
						end repeat
					end if

					-- Add BCC recipients if provided
					if bccRecipients is not "" then
						set AppleScript's text item delimiters to ","
						set bccList to text items of bccRecipients
						set AppleScript's text item delimiters to ""

						repeat with bccAddr in bccList
							set trimmedAddr to my trimString(bccAddr)
							if trimmedAddr is not "" then
								make new bcc recipient at end of bcc recipients with properties {address:trimmedAddr}
							end if
						end repeat
					end if
				end tell

				-- The draft is automatically saved to Drafts folder

				set outputText to outputText & "✓ Draft created successfully!" & return & return
				set outputText to outputText & "Subject: " & emailSubject & return
				set outputText to outputText & "To: " & toRecipients & return

			on error errMsg
				return "Error: " & errMsg
			end try

		else if actionType is "send" then
			-- SEND DRAFT
			set outputText to "SENDING DRAFT" & return & return

			try
				set targetAccount to account targetAccountName
				set draftsMailbox to mailbox "Drafts" of targetAccount
				set draftMessages to every message of draftsMailbox
				set foundDraft to missing value

				-- Find the draft
				repeat with aDraft in draftMessages
					try
						set draftSubject to subject of aDraft

						if draftSubject contains draftSubjectKeyword then
							set foundDraft to aDraft
							exit repeat
						end if
					end try
				end repeat

				if foundDraft is not missing value then
					set draftSubject to subject of foundDraft

					-- Send the draft
					send foundDraft

					set outputText to outputText & "✓ Draft sent successfully!" & return
					set outputText to outputText & "Subject: " & draftSubject & return

				else
					set outputText to outputText & "⚠ No draft found matching: " & draftSubjectKeyword & return
				end if

			on error errMsg
				return "Error: " & errMsg
			end try

		else if actionType is "delete" then
			-- DELETE DRAFT
			set outputText to "DELETING DRAFT" & return & return

			try
				set targetAccount to account targetAccountName
				set draftsMailbox to mailbox "Drafts" of targetAccount
				set draftMessages to every message of draftsMailbox
				set foundDraft to missing value

				-- Find the draft
				repeat with aDraft in draftMessages
					try
						set draftSubject to subject of aDraft

						if draftSubject contains draftSubjectKeyword then
							set foundDraft to aDraft
							exit repeat
						end if
					end try
				end repeat

				if foundDraft is not missing value then
					set draftSubject to subject of foundDraft

					-- Delete the draft
					delete foundDraft

					set outputText to outputText & "✓ Draft deleted successfully!" & return
					set outputText to outputText & "Subject: " & draftSubject & return

				else
					set outputText to outputText & "⚠ No draft found matching: " & draftSubjectKeyword & return
				end if

			on error errMsg
				return "Error: " & errMsg
			end try

		else
			return "Error: Invalid action '" & actionType & "'. Use: list, create, send, delete"
		end if

		return outputText
	end tell
end run

-- Helper function to trim whitespace
on trimString(theString)
	set trimmedString to theString
	try
		repeat while trimmedString starts with " "
			set trimmedString to text 2 thru -1 of trimmedString
		end repeat
		repeat while trimmedString ends with " "
			set trimmedString to text 1 thru -2 of trimmedString
		end repeat
	end try
	return trimmedString
end trimString
