from __future__ import annotations

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.config import settings

CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]

GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"

# Request all scopes on fresh sign-in; existing tokens may only have calendar.
ALL_SCOPES = [*CALENDAR_SCOPES, GMAIL_SEND_SCOPE]


def _load_stored_credentials() -> Credentials | None:
    if not settings.google_token_path.exists():
        return None
    # Do not pass ALL_SCOPES here — that falsely marks ungranted scopes as present.
    return Credentials.from_authorized_user_file(str(settings.google_token_path))


def _refresh_if_expired(creds: Credentials) -> Credentials:
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        settings.google_token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def has_gmail_send_scope(creds: Credentials | None) -> bool:
    return bool(creds and GMAIL_SEND_SCOPE in (creds.scopes or []))


def get_credentials() -> Credentials:
    """Calendar access — does not force browser re-auth if calendar scopes are valid."""
    creds = _load_stored_credentials()
    if creds:
        creds = _refresh_if_expired(creds)
        if creds.valid and set(CALENDAR_SCOPES).issubset(set(creds.scopes or [])):
            return creds

    if not settings.google_credentials_path.exists():
        raise FileNotFoundError(
            f"Missing {settings.google_credentials_path.name}. "
            "Place your Google OAuth client credentials file in the project root."
        )

    flow = InstalledAppFlow.from_client_secrets_file(
        str(settings.google_credentials_path), ALL_SCOPES
    )
    creds = flow.run_local_server(port=0)
    settings.google_token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def authorize_gmail_scope() -> Credentials:
    """Interactive re-auth to add Gmail send — run via scripts/setup_google_auth.py."""
    if not settings.google_credentials_path.exists():
        raise FileNotFoundError(
            f"Missing {settings.google_credentials_path.name}. "
            "Place your Google OAuth client credentials file in the project root."
        )

    flow = InstalledAppFlow.from_client_secrets_file(
        str(settings.google_credentials_path), ALL_SCOPES
    )
    creds = flow.run_local_server(port=0)
    settings.google_token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def get_calendar_service():
    return build("calendar", "v3", credentials=get_credentials())


def get_organizer_email() -> str | None:
    """Email of the Google account that owns the calendar (OAuth token)."""
    try:
        service = get_calendar_service()
        primary = service.calendarList().get(calendarId=settings.google_calendar_id).execute()
        cal_id = primary.get("id", "")
        if cal_id and "@" in cal_id:
            return cal_id.lower()
    except Exception:
        pass
    return None
