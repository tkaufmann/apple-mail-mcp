"""
ABOUTME: AppleScript utilities for Apple Mail MCP Server
Provides helper functions for executing AppleScript commands and parsing email data.
"""

import subprocess
import os
from pathlib import Path
from typing import List, Dict, Any

# Load user preferences from environment
USER_PREFERENCES = os.environ.get("USER_EMAIL_PREFERENCES", "")

# Base path for AppleScript files
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


def inject_preferences(func):
    """Decorator that appends user preferences to tool docstrings"""
    if USER_PREFERENCES:
        if func.__doc__:
            func.__doc__ = func.__doc__.rstrip() + f"\n\nUser Preferences: {USER_PREFERENCES}"
        else:
            func.__doc__ = f"User Preferences: {USER_PREFERENCES}"
    return func


def run_applescript(script: str) -> str:
    """Execute AppleScript string and return output"""
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        raise Exception("AppleScript execution timed out")
    except Exception as e:
        raise Exception(f"AppleScript execution failed: {str(e)}")


def run_applescript_file(script_path: str, *args) -> str:
    """
    Execute AppleScript file with arguments and return output.

    Args:
        script_path: Path relative to scripts/ directory (e.g., "organization/list_accounts.applescript")
        *args: Arguments to pass to the AppleScript (accessed via 'on run argv' in the script)

    Returns:
        Script output as string

    Example:
        run_applescript_file("inbox/list_inbox_emails.applescript", "Gmail", 10)
    """
    full_path = SCRIPTS_DIR / script_path

    if not full_path.exists():
        raise FileNotFoundError(f"AppleScript file not found: {full_path}")

    try:
        # Build command: osascript <script_path> <arg1> <arg2> ...
        cmd = ['osascript', str(full_path)] + [str(arg) for arg in args]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            raise Exception(f"AppleScript error: {result.stderr}")

        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        raise Exception(f"AppleScript execution timed out: {script_path}")
    except Exception as e:
        raise Exception(f"AppleScript execution failed ({script_path}): {str(e)}")


def parse_email_list(output: str) -> List[Dict[str, Any]]:
    """Parse the structured email output from AppleScript"""
    emails = []
    lines = output.split('\n')

    current_email = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith('=') or line.startswith('━') or line.startswith('📧') or line.startswith('⚠'):
            continue

        if line.startswith('✉') or line.startswith('✓'):
            # New email entry
            if current_email:
                emails.append(current_email)

            is_read = line.startswith('✓')
            subject = line[2:].strip()  # Remove indicator
            current_email = {
                'subject': subject,
                'is_read': is_read
            }
        elif line.startswith('From:'):
            current_email['sender'] = line[5:].strip()
        elif line.startswith('Date:'):
            current_email['date'] = line[5:].strip()
        elif line.startswith('Preview:'):
            current_email['preview'] = line[8:].strip()
        elif line.startswith('TOTAL EMAILS'):
            # End of email list
            if current_email:
                emails.append(current_email)
            break

    if current_email and current_email not in emails:
        emails.append(current_email)

    return emails
