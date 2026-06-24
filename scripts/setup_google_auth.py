"""Re-authorize Google Calendar + Gmail send and save token.json."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.services.google_auth import authorize_gmail_scope, has_gmail_send_scope


def main() -> None:
    print("Opening browser for Google sign-in...")
    print("If you see Error 403: access_denied:")
    print("  1. Google Cloud Console -> APIs & Services -> OAuth consent screen")
    print("  2. Add your Gmail under Test users")
    print("  3. Sign in with that same Gmail account")
    print("  4. Enable Google Calendar API and Gmail API")
    print()
    print("Approve BOTH Calendar and Gmail permissions when prompted.")
    creds = authorize_gmail_scope()
    print("Google authorization successful.")
    print(f"Token saved to token.json. Valid: {creds.valid}")
    if has_gmail_send_scope(creds):
        print("Gmail send: enabled — booking confirmations will email guests.")
    else:
        print("Gmail send: NOT enabled — run again and approve Gmail access.")


if __name__ == "__main__":
    main()
