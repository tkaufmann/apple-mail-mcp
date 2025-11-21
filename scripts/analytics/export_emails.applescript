-- Export emails to files for backup or analysis
-- Arguments: account, scope, subject_keyword, mailbox, save_directory, format

on run argv
	set targetAccountName to item 1 of argv
	set scopeType to item 2 of argv -- "single_email", "entire_mailbox"
	set subjectKeyword to item 3 of argv -- Can be empty
	set mailboxName to item 4 of argv
	set saveDirectory to item 5 of argv
	set exportFormat to item 6 of argv -- "txt", "html"

	tell application "Mail"
		if scopeType is "single_email" then
			-- EXPORT SINGLE EMAIL
			set outputText to "EXPORTING EMAIL" & return & return

			try
				set targetAccount to account targetAccountName
				-- Try to get mailbox
				try
					set targetMailbox to mailbox mailboxName of targetAccount
				on error
					if mailboxName is "INBOX" then
						set targetMailbox to mailbox "Inbox" of targetAccount
					else
						error "Mailbox not found: " & mailboxName
					end if
				end try

				set mailboxMessages to every message of targetMailbox
				set foundMessage to missing value

				-- Find the email
				repeat with aMessage in mailboxMessages
					try
						set messageSubject to subject of aMessage

						if messageSubject contains subjectKeyword then
							set foundMessage to aMessage
							exit repeat
						end if
					end try
				end repeat

				if foundMessage is not missing value then
					set messageSubject to subject of foundMessage
					set messageSender to sender of foundMessage
					set messageDate to date received of foundMessage
					set messageContent to content of foundMessage

					-- Create safe filename
					set safeSubject to messageSubject
					set AppleScript's text item delimiters to "/"
					set safeSubjectParts to text items of safeSubject
					set AppleScript's text item delimiters to "-"
					set safeSubject to safeSubjectParts as string
					set AppleScript's text item delimiters to ""

					set fileName to safeSubject & "." & exportFormat
					set filePath to saveDirectory & "/" & fileName

					-- Prepare export content
					if exportFormat is "txt" then
						set exportContent to "Subject: " & messageSubject & return
						set exportContent to exportContent & "From: " & messageSender & return
						set exportContent to exportContent & "Date: " & (messageDate as string) & return & return
						set exportContent to exportContent & messageContent
					else if exportFormat is "html" then
						set exportContent to "<html><body>"
						set exportContent to exportContent & "<h2>" & messageSubject & "</h2>"
						set exportContent to exportContent & "<p><strong>From:</strong> " & messageSender & "</p>"
						set exportContent to exportContent & "<p><strong>Date:</strong> " & (messageDate as string) & "</p>"
						set exportContent to exportContent & "<hr>" & messageContent
						set exportContent to exportContent & "</body></html>"
					end if

					-- Write to file
					try
						set fileRef to open for access POSIX file filePath with write permission
						set eof of fileRef to 0
						write exportContent to fileRef as «class utf8»
						close access fileRef
					on error errMsg
						try
							close access POSIX file filePath
						end try
						error errMsg
					end try

					set outputText to outputText & "✓ Email exported successfully!" & return & return
					set outputText to outputText & "Subject: " & messageSubject & return
					set outputText to outputText & "Saved to: " & filePath & return

				else
					set outputText to outputText & "⚠ No email found matching: " & subjectKeyword & return
				end if

			on error errMsg
				return "Error: " & errMsg
			end try

		else if scopeType is "entire_mailbox" then
			-- EXPORT ENTIRE MAILBOX
			set outputText to "EXPORTING MAILBOX" & return & return

			try
				set targetAccount to account targetAccountName
				-- Try to get mailbox
				try
					set targetMailbox to mailbox mailboxName of targetAccount
				on error
					if mailboxName is "INBOX" then
						set targetMailbox to mailbox "Inbox" of targetAccount
					else
						error "Mailbox not found: " & mailboxName
					end if
				end try

				set mailboxMessages to every message of targetMailbox
				set messageCount to count of mailboxMessages
				set exportCount to 0

				-- Create export directory
				set exportDir to saveDirectory & "/" & mailboxName & "_export"
				do shell script "mkdir -p " & quoted form of exportDir

				repeat with aMessage in mailboxMessages
					try
						set messageSubject to subject of aMessage
						set messageSender to sender of aMessage
						set messageDate to date received of aMessage
						set messageContent to content of aMessage

						-- Create safe filename with index
						set exportCount to exportCount + 1
						set fileName to exportCount & "_" & messageSubject & "." & exportFormat

						-- Remove unsafe characters
						set AppleScript's text item delimiters to "/"
						set fileNameParts to text items of fileName
						set AppleScript's text item delimiters to "-"
						set fileName to fileNameParts as string
						set AppleScript's text item delimiters to ""

						set filePath to exportDir & "/" & fileName

						-- Prepare export content
						if exportFormat is "txt" then
							set exportContent to "Subject: " & messageSubject & return
							set exportContent to exportContent & "From: " & messageSender & return
							set exportContent to exportContent & "Date: " & (messageDate as string) & return & return
							set exportContent to exportContent & messageContent
						else if exportFormat is "html" then
							set exportContent to "<html><body>"
							set exportContent to exportContent & "<h2>" & messageSubject & "</h2>"
							set exportContent to exportContent & "<p><strong>From:</strong> " & messageSender & "</p>"
							set exportContent to exportContent & "<p><strong>Date:</strong> " & (messageDate as string) & "</p>"
							set exportContent to exportContent & "<hr>" & messageContent
							set exportContent to exportContent & "</body></html>"
						end if

						-- Write to file
						try
							set fileRef to open for access POSIX file filePath with write permission
							set eof of fileRef to 0
							write exportContent to fileRef as «class utf8»
							close access fileRef
						on error
							try
								close access POSIX file filePath
							end try
							-- Continue with next email if one fails
						end try

					on error
						-- Continue with next email if one fails
					end try
				end repeat

				set outputText to outputText & "✓ Mailbox exported successfully!" & return & return
				set outputText to outputText & "Mailbox: " & mailboxName & return
				set outputText to outputText & "Total emails: " & messageCount & return
				set outputText to outputText & "Exported: " & exportCount & return
				set outputText to outputText & "Location: " & exportDir & return

			on error errMsg
				return "Error: " & errMsg
			end try

		else
			return "Error: Invalid scope '" & scopeType & "'. Use: single_email, entire_mailbox"
		end if

		return outputText
	end tell
end run
