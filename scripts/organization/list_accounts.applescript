-- List all Mail accounts
-- Returns: Pipe-separated list of account names

tell application "Mail"
	set accountNames to {}
	set allAccounts to every account

	repeat with anAccount in allAccounts
		set accountName to name of anAccount
		set end of accountNames to accountName
	end repeat

	set AppleScript's text item delimiters to "|"
	return accountNames as string
end tell
