from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from app.config import settings
from app.services.elevenlabs_service import (
    build_dashboard_setup_kit,
    build_elevenlabs_tool_definitions,
    list_voices,
    verify_webhook_signature,
)
from app.services.openai_session import REALTIME_TOOLS
from app.services.tool_executor import execute_tool, format_tool_result_for_agent

router = APIRouter(prefix="/api/telephony", tags=["telephony"])


def verify_telephony_auth(
    authorization: str | None = Header(default=None),
    x_webhook_secret: str | None = Header(default=None, alias="X-Webhook-Secret"),
) -> None:
    secret = settings.telephony_webhook_secret
    if not secret:
        return

    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    elif x_webhook_secret:
        token = x_webhook_secret

    if token != secret:
        raise HTTPException(status_code=401, detail="Invalid telephony webhook secret")


@router.get("/status")
def telephony_status():
    return {
        "mode": "elevenlabs_dashboard",
        "twilio_configured": bool(settings.twilio_account_sid and settings.twilio_auth_token),
        "twilio_phone": settings.twilio_phone_number or None,
        "webhook_secret_set": bool(settings.telephony_webhook_secret),
        "public_url": settings.api_public_url,
        "webhook_base": f"{settings.api_public_url.rstrip('/')}/api/telephony/tools",
        "setup_kit_url": f"{settings.api_public_url.rstrip('/')}/api/telephony/setup-kit",
    }


@router.get("/setup-kit")
def setup_kit():
    """
    Everything to copy into ElevenLabs when creating your agent manually:
    system prompt, first message, and server tool URLs.
    """
    return build_dashboard_setup_kit()


@router.get("/agent-export")
def agent_export():
    """Alias for setup-kit (prompt + tools for ElevenLabs dashboard)."""
    return build_dashboard_setup_kit()


@router.get("/tool-definitions")
def tool_definitions():
    return {"tools": build_elevenlabs_tool_definitions(), "openai_tools": REALTIME_TOOLS}


@router.get("/voices")
def elevenlabs_voices():
    """Optional — only works if ELEVENLABS_API_KEY is in .env."""
    return {"voices": list_voices()}


@router.post("/tools/{tool_name}")
async def run_tool(
    tool_name: str,
    request: Request,
    _: None = Depends(verify_telephony_auth),
    elevenlabs_signature: str | None = Header(default=None, alias="ElevenLabs-Signature"),
):
    body = await request.body()
    if settings.elevenlabs_webhook_secret and not verify_webhook_signature(
        body, elevenlabs_signature
    ):
        raise HTTPException(status_code=401, detail="Invalid ElevenLabs signature")

    try:
        payload: dict[str, Any] = json.loads(body) if body else {}
    except json.JSONDecodeError:
        payload = {}

    # ElevenLabs may nest params under "parameters" or send flat JSON
    args = payload.get("parameters") if isinstance(payload.get("parameters"), dict) else payload

    try:
        result = execute_tool(tool_name, args)
        return {
            "result": format_tool_result_for_agent(result),
            "data": result,
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Tool failed: {exc}") from exc
