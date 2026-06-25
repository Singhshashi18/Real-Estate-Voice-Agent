from __future__ import annotations

import logging
from urllib.parse import urljoin

from twilio.request_validator import RequestValidator

from app.config import settings

logger = logging.getLogger(__name__)


def twilio_configured() -> bool:
    return bool(
        settings.twilio_account_sid
        and settings.twilio_auth_token
        and settings.twilio_phone_number
    )


def validate_twilio_request(url: str, form: dict[str, str], signature: str | None) -> bool:
    if not settings.twilio_auth_token:
        return False
    if not signature:
        return False
    validator = RequestValidator(settings.twilio_auth_token)
    return validator.validate(url, form, signature)


def build_voice_twiml() -> str:
    """
    Fallback TwiML when NOT using ElevenLabs-native Twilio import.
    Connects the call to our media-stream WebSocket (future) or plays setup message.
    """
    ws_url = urljoin(
        settings.api_public_url.replace("https://", "wss://").replace("http://", "ws://"),
        "/api/twilio/media-stream",
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="Polly.Joanna">
    Connecting you to {settings.company_name}. One moment please.
  </Say>
  <Connect>
    <Stream url="{ws_url}" />
  </Connect>
</Response>"""


def log_call_status(form: dict[str, str]) -> None:
    logger.info(
        "Twilio call %s status=%s from=%s to=%s duration=%s",
        form.get("CallSid"),
        form.get("CallStatus"),
        form.get("From"),
        form.get("To"),
        form.get("CallDuration"),
    )
