# Known Issues

✅ **All previously known issues have been resolved!**

## Fixed Issues

### Sender Bug in Composition Tools
- **Tools affected**: compose_email, manage_drafts, reply_to_email, forward_email
- **Error**: "account id ... kann nicht in Typ rich text umgewandelt werden"
- **Fix**: Changed from `set sender to targetAccount` to using `email addresses of targetAccount`
- **Status**: ✅ Fixed

### Syntax Errors
- **reply_to_email**: Fixed "with reply to all" syntax (added second "with")
- **get_email_with_content**: Moved lowercase() function outside of on run argv
- **Status**: ✅ Fixed

## Removed Features

### get_inbox_overview
- **Reason**: Too slow - iterates over all mailboxes of all accounts
- **Alternative**: Use list_mailboxes + get_unread_count instead

### Email Management Expert Skill
- **Reason**: Not needed
- **Location**: skill-email-management/ (removed)

### Analytics Tools
- **Removed**: get_statistics, export_emails
- **Reason**: Too slow/complex for large mailboxes
- **Kept**: get_unread_count (simple and fast)

---

*Last updated: 2025-11-21*
