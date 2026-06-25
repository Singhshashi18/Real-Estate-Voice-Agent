from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any

import httpx

from app.config import settings
from app.services.openai_session import REALTIME_TOOLS, build_agent_instructions


def verify_webhook_signature(payload: bytes, signature_header: str | None) -> bool:
    """Validate ElevenLabs-Signature header when webhook secret is configured."""
    secret = settings.elevenlabs_webhook_secret
    if not secret:
        return True
    if not signature_header:
        return False

    parts = dict(item.split("=", 1) for item in signature_header.split(",") if "=" in item)
    timestamp = parts.get("t")
    received = parts.get("v0")
    if not timestamp or not received:
        return False

    try:
        if abs(time.time() - int(timestamp)) > 300:
            return False
    except ValueError:
        return False

    signed = f"{timestamp}.{payload.decode('utf-8')}".encode()
    expected = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, received)


def build_elevenlabs_tool_definitions() -> list[dict[str, Any]]:
    """Server-tool webhook configs for ElevenLabs Conversational AI dashboard."""
    base = settings.api_public_url.rstrip("/")
    secret = settings.telephony_webhook_secret
    headers = (
        [{"name": "Authorization", "value": f"Bearer {secret}"}]
        if secret
        else []
    )

    tools: list[dict[str, Any]] = []
    for tool in REALTIME_TOOLS:
        if tool["name"] == "end_call":
            continue

        properties = tool.get("parameters", {}).get("properties", {})
        required = tool.get("parameters", {}).get("required", [])

        tools.append(
            {
                "type": "webhook",
                "name": tool["name"],
                "description": tool["description"],
                "api_schema": {
                    "url": f"{base}/api/telephony/tools/{tool['name']}",
                    "method": "POST",
                    "request_headers": headers,
                    "request_body_schema": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                },
            }
        )
    return tools


def build_dashboard_setup_kit() -> dict[str, Any]:
    """
    Copy-paste kit for ElevenLabs Conversational AI dashboard.
    Agent, voice, and phone number are configured in ElevenLabs — not in .env.
    """
    base = settings.api_public_url.rstrip("/")
    secret = settings.telephony_webhook_secret
    company = settings.company_name
    agent_name = settings.organizer_name

    tools_for_dashboard = []
    for tool in build_elevenlabs_tool_definitions():
        tools_for_dashboard.append(
            {
                "name": tool["name"],
                "description": tool["description"],
                "url": tool["api_schema"]["url"],
                "method": "POST",
                "auth_header": f"Authorization: Bearer {secret}" if secret else "(set TELEPHONY_WEBHOOK_SECRET)",
            }
        )

    return {
        "mode": "elevenlabs_dashboard",
        "summary": (
            "Create the agent in ElevenLabs, pick the voice there, add server tools below, "
            "then import your Twilio number in ElevenLabs Phone Numbers."
        ),
        "agent": {
            "name_suggestion": f"{company} Receptionist — {agent_name}",
            "language": "en",
            "first_message": (
                f"Hi, thank you for calling {company}. I'm {agent_name}. "
                "How can I help you find a home today?"
            ),
            "system_prompt": build_agent_instructions(),
        },
        "voice": {
            "note": "Choose and assign voice in ElevenLabs agent settings — no voice ID needed in .env.",
        },
        "server_tools": tools_for_dashboard,
        "twilio": {
            "note": (
                "ElevenLabs → Phone Numbers → Import from Twilio. "
                "Enter Twilio Account SID + Auth Token there, then assign this agent."
            ),
        },
        "backend_env_required": [
            "API_PUBLIC_URL (public HTTPS, e.g. ngrok)",
            "TELEPHONY_WEBHOOK_SECRET (same Bearer token on every tool in ElevenLabs)",
        ],
        "urls": {
            "setup_kit": f"{base}/api/telephony/setup-kit",
            "tool_base": f"{base}/api/telephony/tools",
            "status": f"{base}/api/telephony/status",
        },
    }


def build_agent_export() -> dict[str, Any]:
    """Alias for build_dashboard_setup_kit()."""
    return build_dashboard_setup_kit()


def list_voices() -> list[dict[str, Any]]:
    """Helper for setup — list available ElevenLabs voices."""
    if not settings.elevenlabs_api_key:
        return []
    with httpx.Client(timeout=30) as client:
        resp = client.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": settings.elevenlabs_api_key},
        )
    if resp.status_code >= 400:
        return []
    return resp.json().get("voices", [])
