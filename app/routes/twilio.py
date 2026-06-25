from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response, WebSocket, WebSocketDisconnect

from app.config import settings
from app.services.twilio_service import (
    build_voice_twiml,
    log_call_status,
    twilio_configured,
    validate_twilio_request,
)

router = APIRouter(prefix="/api/twilio", tags=["twilio"])


def _public_url(request: Request) -> str:
    base = settings.api_public_url.rstrip("/")
    if base.startswith("http"):
        return base
    return str(request.base_url).rstrip("/")


@router.post("/voice")
async def inbound_voice(request: Request):
    """
    Twilio inbound voice webhook.
    Recommended: import your Twilio number in ElevenLabs instead of pointing here.
    This endpoint is a fallback / media-stream bridge.
    """
    form = dict(await request.form())
    url = f"{_public_url(request)}/api/twilio/voice"
    signature = request.headers.get("X-Twilio-Signature")

    if settings.twilio_auth_token and not validate_twilio_request(url, form, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    return Response(content=build_voice_twiml(), media_type="application/xml")


@router.post("/status")
async def call_status(request: Request):
    form = dict(await request.form())
    url = f"{_public_url(request)}/api/twilio/status"
    signature = request.headers.get("X-Twilio-Signature")

    if settings.twilio_auth_token and not validate_twilio_request(url, form, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    log_call_status(form)
    return {"ok": True}


@router.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    """
    Twilio Media Streams WebSocket (placeholder).
    For production phone calls, use ElevenLabs + Twilio import (see docs/TELEPHONY_SETUP.md).
    """
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass


@router.get("/setup")
def twilio_setup_info():
    return {
        "configured": twilio_configured(),
        "phone_number": settings.twilio_phone_number or None,
        "recommended": (
            "Import this number in ElevenLabs Conversational AI → Phone Numbers "
            "(ElevenLabs configures Twilio webhooks for you)."
        ),
        "voice_webhook_url": f"{settings.api_public_url.rstrip('/')}/api/twilio/voice",
        "status_webhook_url": f"{settings.api_public_url.rstrip('/')}/api/twilio/status",
    }
