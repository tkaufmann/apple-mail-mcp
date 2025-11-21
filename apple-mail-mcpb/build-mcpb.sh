#!/bin/bash

# Build script for creating Apple Mail MCP Bundle (.mcpb)
# This creates a distributable package for Claude Desktop installation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SOURCE_DIR="${SCRIPT_DIR}/.."
BUILD_DIR="${SCRIPT_DIR}/build"
OUTPUT_DIR="${SCRIPT_DIR}/../"
PACKAGE_NAME="apple-mail-mcp"
VERSION=$(grep '"version"' "${SCRIPT_DIR}/manifest.json" | sed -E 's/.*"version": "([^"]+)".*/\1/')

echo -e "${GREEN}Building Apple Mail MCP Bundle v${VERSION}${NC}"
echo "========================================="

# Step 1: Clean build directory
echo -e "\n${YELLOW}Step 1: Cleaning build directory...${NC}"
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"

# Step 2: Copy manifest.json
echo -e "\n${YELLOW}Step 2: Copying manifest.json...${NC}"
cp "${SCRIPT_DIR}/manifest.json" "${BUILD_DIR}/"

# Step 3: Copy Python source files
echo -e "\n${YELLOW}Step 3: Copying Python source files...${NC}"

# Check if source directory exists
if [ ! -d "${SOURCE_DIR}" ]; then
    echo -e "  ${RED}✗${NC} Source directory not found: ${SOURCE_DIR}"
    exit 1
fi

# Copy the main Python script
if [ ! -f "${SOURCE_DIR}/main.py" ]; then
    echo -e "  ${RED}✗${NC} Python script not found: ${SOURCE_DIR}/main.py"
    exit 1
fi
cp "${SOURCE_DIR}/main.py" "${BUILD_DIR}/"
chmod +x "${BUILD_DIR}/main.py"

# Copy the mcp_instance module
if [ ! -f "${SOURCE_DIR}/mcp_instance.py" ]; then
    echo -e "  ${RED}✗${NC} MCP instance not found: ${SOURCE_DIR}/mcp_instance.py"
    exit 1
fi
cp "${SOURCE_DIR}/mcp_instance.py" "${BUILD_DIR}/"

# Copy tool modules directory
if [ ! -d "${SOURCE_DIR}/tools" ]; then
    echo -e "  ${RED}✗${NC} Tools directory not found: ${SOURCE_DIR}/tools"
    exit 1
fi
cp -r "${SOURCE_DIR}/tools" "${BUILD_DIR}/"

# Copy utils directory
if [ ! -d "${SOURCE_DIR}/utils" ]; then
    echo -e "  ${RED}✗${NC} Utils directory not found: ${SOURCE_DIR}/utils"
    exit 1
fi
cp -r "${SOURCE_DIR}/utils" "${BUILD_DIR}/"

# Copy resources and prompts directories (if they exist and are not empty)
if [ -d "${SOURCE_DIR}/resources" ]; then
    cp -r "${SOURCE_DIR}/resources" "${BUILD_DIR}/"
fi
if [ -d "${SOURCE_DIR}/prompts" ]; then
    cp -r "${SOURCE_DIR}/prompts" "${BUILD_DIR}/"
fi

# Copy requirements.txt
if [ ! -f "${SOURCE_DIR}/requirements.txt" ]; then
    echo -e "  ${RED}✗${NC} requirements.txt not found: ${SOURCE_DIR}/requirements.txt"
    exit 1
fi
cp "${SOURCE_DIR}/requirements.txt" "${BUILD_DIR}/"

# Copy startup wrapper script
echo -e "\n${YELLOW}Step 4: Copying startup wrapper script...${NC}"
if [ ! -f "${SOURCE_DIR}/start_mcp.sh" ]; then
    echo -e "  ${RED}✗${NC} Startup script not found: ${SOURCE_DIR}/start_mcp.sh"
    exit 1
fi
cp "${SOURCE_DIR}/start_mcp.sh" "${BUILD_DIR}/"
chmod +x "${BUILD_DIR}/start_mcp.sh"

# Note: Virtual environment will be created on user's machine during first run
echo -e "\n${YELLOW}Step 5: Skipping venv creation (will be created on user's machine)...${NC}"
echo -e "  ${GREEN}✓${NC} Venv will be initialized automatically on first run using user's Python installation"

# Step 6: Create README
echo -e "\n${YELLOW}Step 6: Creating README...${NC}"
cat > "${BUILD_DIR}/README.md" << 'EOF'
# Apple Mail MCP Server

Natural language interface for Apple Mail with 18 powerful email management tools.

## Quick Installation

1. Install this .mcpb file in Claude Desktop (Developer > MCP Servers > Install from file)
2. Grant permissions when prompted for Mail.app access
3. Restart Claude Desktop
4. Start using! Ask Claude to manage your emails

## Features

### Email Reading & Search
- **List Inbox Emails**: View all emails across accounts or filter by specific account
- **Search with Content**: Find emails by subject with full content preview
- **Recent Emails**: Get the most recent messages from any account
- **Unread Count**: Quick overview of unread emails per account

### Email Organization
- **List Mailboxes**: View all folders/mailboxes with message counts
- **Move Emails**: Move messages between folders using subject keywords
- Supports nested mailboxes (e.g., "Projects/Amplify Impact")

### Email Composition
- **Reply to Emails**: Reply to messages matching subject keywords
- **Compose New Emails**: Send new emails with TO, CC, and BCC
- Reply to all recipients option

### Attachment Management
- **List Attachments**: View all attachments with names and sizes
- **Save Attachments**: Download specific attachments to disk

## Key Tools

### `list_inbox_emails`
List all emails from your inbox:
- Filter by account name (e.g., "Gmail", "Work")
- Limit number of emails returned
- Filter read/unread status

### `get_email_with_content`
Search for emails with content preview:
- Search by subject keyword
- Specify account to search
- Configurable content length
- Returns full email details

### `list_mailboxes`
View folder structure:
- List all folders for an account or all accounts
- Shows message counts (total and unread)
- Displays nested folder hierarchy

### `move_email`
Organize your inbox:
- Move emails by subject keyword
- Supports nested mailboxes with "/" separator
- Safety limit on number of moves
- Example: Move to "Projects/Amplify Impact"

### `reply_to_email`
Respond to messages:
- Search by subject keyword
- Custom reply body
- Reply to sender or all recipients
- Sends immediately

### `compose_email`
Send new emails:
- Specify sender account
- TO, CC, and BCC recipients
- Custom subject and body
- Immediate sending

### `list_email_attachments`
View attachments:
- Search by subject keyword
- Shows attachment names and sizes
- List for multiple matching emails

### `save_email_attachment`
Download attachments:
- Search by subject keyword
- Specify attachment name
- Save to custom path

## Configuration

**Email Preferences (Optional):**
Configure preferences in Claude Desktop settings under this MCP to customize behavior:
- Default email account
- Preferred maximum results
- Frequently used folders

**MCP Configuration:**
No additional configuration required! Uses your Apple Mail accounts.

## Permissions

On first run, macOS will prompt for permissions:
- **Mail.app Control**: Required to automate Mail
- **Mail Data Access**: Required to read email content

Grant these permissions for full functionality.

## Usage Examples

Ask Claude:
- "Show me all unread emails in my Gmail account"
- "Search for emails about 'project update' in my work account"
- "Move emails with 'meeting' in the subject to my Archive folder"
- "Reply to the email about 'Domain name' with 'Thanks for the update!'"
- "List all attachments in emails about 'invoice'"
- "Compose an email to john@example.com with subject 'Hello' from my personal account"
- "What folders do I have in my work account?"

## Requirements

- macOS with Apple Mail configured
- Python 3.7+
- Mail app with at least one account configured
- Appropriate macOS permissions granted

## Notes

- Email operations require Mail.app to be running
- Some operations (like fetching content) may be slower than metadata-only operations
- Exchange accounts may have different mailbox structures
- Moving and replying to emails includes safety limits
- Email sending is immediate - use with caution

## Support

For issues or questions:
- GitHub: https://github.com/patrickfreyer/apple-mail-mcp
EOF

# Step 7: Create the MCPB package
echo -e "\n${YELLOW}Step 7: Creating MCPB package...${NC}"
cd "${BUILD_DIR}"
OUTPUT_FILE="${OUTPUT_DIR}/${PACKAGE_NAME}-v${VERSION}.mcpb"

# Create zip archive with .mcpb extension
zip -r -q "${OUTPUT_FILE}" . -x "*.DS_Store" "*__MACOSX*" "*.git*"

# Step 8: Verify package
echo -e "\n${YELLOW}Step 8: Verifying package...${NC}"
if [ -f "${OUTPUT_FILE}" ]; then
    FILE_SIZE=$(du -h "${OUTPUT_FILE}" | cut -f1)
    echo -e "  ${GREEN}✓${NC} Package created successfully"
    echo -e "  ${GREEN}✓${NC} Size: ${FILE_SIZE}"
    echo -e "  ${GREEN}✓${NC} Location: ${OUTPUT_FILE}"

    # List contents summary
    echo -e "\n  Package contents:"
    unzip -l "${OUTPUT_FILE}" | head -20
else
    echo -e "  ${RED}✗${NC} Failed to create package"
    exit 1
fi

# Step 8: Clean up
echo -e "\n${YELLOW}Step 8: Cleaning up...${NC}"
rm -rf "${BUILD_DIR}"

echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}Build completed successfully!${NC}"
echo -e "\nPackage created: ${GREEN}${OUTPUT_FILE}${NC}"
echo -e "\n${YELLOW}Installation Instructions:${NC}"
echo -e "  1. Open Claude Desktop settings"
echo -e "  2. Navigate to Developer > MCP Servers"
echo -e "  3. Click 'Install from file' and select the .mcpb file"
echo -e "  4. Grant Mail.app permissions when prompted"
echo -e "  5. Restart Claude Desktop"
echo -e "\n${GREEN}Ready to use!${NC}"
echo -e "Ask Claude to manage your emails with 18 powerful tools."
