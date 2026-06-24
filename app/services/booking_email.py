from __future__ import annotations

import base64
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from app.config import settings
from app.services.google_auth import (
    _load_stored_credentials,
    _refresh_if_expired,
    get_organizer_email,
    has_gmail_send_scope,
)


def send_booking_confirmation(
    *,
    guest_name: str,
    guest_email: str,
    property_label: str,
    slot_label: str,
    meet_link: str,
) -> dict:
    """Send a confirmation email to the guest inbox via Gmail API."""
    organizer = get_organizer_email()
    if not organizer:
        return {
            "sent": False,
            "message": "Could not determine sender email for confirmation.",
        }

    creds = _load_stored_credentials()
    if creds:
        creds = _refresh_if_expired(creds)

    if not has_gmail_send_scope(creds):
        return {
            "sent": False,
            "message": (
                "Gmail send not authorized yet. Run once in your project folder: "
                "python scripts/setup_google_auth.py — sign in and allow Gmail access. "
                "Also enable Gmail API in Google Cloud Console."
            ),
        }

    meet_line = meet_link or "Open the event in Google Calendar for the Meet link."
    body = f"""Hi {guest_name},

Your Karyan property visit is confirmed.

Property: {property_label}
When: {slot_label}
Google Meet: {meet_line}

A calendar event has also been added to your schedule.

See you soon,
{settings.organizer_name}
{settings.company_name}
"""

    message = MIMEText(body)
    message["to"] = guest_email
    message["from"] = organizer
    message["subject"] = f"Karyan visit confirmed — {property_label}"

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        service = build("gmail", "v1", credentials=creds)
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return {
            "sent": True,
            "message": f"Confirmation email sent to {guest_email}.",
        }
    except Exception as exc:
        return {"sent": False, "message": f"Could not send confirmation email: {exc}"}
