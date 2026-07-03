from __future__ import annotations

import time
from typing import Any

import httpx

from app.config import settings

ELEVENLABS_BASE = "https://api.elevenlabs.io/v1"


def _headers() -> dict[str, str]:
    if not settings.elevenlabs_api_key:
        raise ValueError("ELEVENLABS_API_KEY is not configured in .env")
    return {"xi-api-key": settings.elevenlabs_api_key, "Content-Type": "application/json"}


def outbound_configured() -> bool:
    return bool(
        settings.elevenlabs_api_key
        and settings.elevenlabs_outbound_agent_id
        and settings.elevenlabs_phone_number_id
    )


def list_phone_numbers() -> list[dict[str, Any]]:
    if not settings.elevenlabs_api_key:
        return []
    with httpx.Client(timeout=30) as client:
        resp = client.get(f"{ELEVENLABS_BASE}/convai/phone-numbers", headers=_headers())
    if resp.status_code >= 400:
        return []
    data = resp.json()
    if isinstance(data, list):
        return data
    return data.get("phone_numbers", data.get("items", []))


def submit_batch_call(
    *,
    call_name: str,
    recipients: list[dict[str, Any]],
    scheduled_time_unix: int | None = None,
) -> dict[str, Any]:
    if not outbound_configured():
        raise ValueError(
            "Set ELEVENLABS_API_KEY, ELEVENLABS_OUTBOUND_AGENT_ID, "
            "and ELEVENLABS_PHONE_NUMBER_ID in .env"
        )

    body = {
        "call_name": call_name,
        "agent_id": settings.elevenlabs_outbound_agent_id,
        "agent_phone_number_id": settings.elevenlabs_phone_number_id,
        "scheduled_time_unix": scheduled_time_unix or int(time.time()),
        "recipients": recipients,
    }

    with httpx.Client(timeout=60) as client:
        resp = client.post(
            f"{ELEVENLABS_BASE}/convai/batch-calling/submit",
            headers=_headers(),
            json=body,
        )

    if resp.status_code >= 400:
        detail = resp.text
        try:
            detail = resp.json().get("detail", detail)
        except Exception:
            pass
        raise RuntimeError(f"ElevenLabs batch submit failed ({resp.status_code}): {detail}")

    return resp.json()


def get_batch_call(batch_id: str) -> dict[str, Any]:
    with httpx.Client(timeout=30) as client:
        resp = client.get(
            f"{ELEVENLABS_BASE}/convai/batch-calling/{batch_id}",
            headers=_headers(),
        )
    if resp.status_code >= 400:
        raise RuntimeError(f"ElevenLabs batch get failed ({resp.status_code}): {resp.text}")
    return resp.json()


def cancel_batch_call(batch_id: str) -> dict[str, Any]:
    with httpx.Client(timeout=30) as client:
        resp = client.post(
            f"{ELEVENLABS_BASE}/convai/batch-calling/{batch_id}/cancel",
            headers=_headers(),
        )
    if resp.status_code >= 400:
        raise RuntimeError(f"ElevenLabs batch cancel failed ({resp.status_code}): {resp.text}")
    return resp.json()


def initiate_single_outbound_call(
    *,
    to_number: str,
    dynamic_variables: dict[str, str],
) -> dict[str, Any]:
    if not outbound_configured():
        raise ValueError("ElevenLabs outbound is not fully configured in .env")

    body = {
        "agent_id": settings.elevenlabs_outbound_agent_id,
        "agent_phone_number_id": settings.elevenlabs_phone_number_id,
        "to_number": to_number,
        "conversation_initiation_client_data": {
            "dynamic_variables": dynamic_variables,
        },
    }

    with httpx.Client(timeout=60) as client:
        resp = client.post(
            f"{ELEVENLABS_BASE}/convai/twilio/outbound-call",
            headers=_headers(),
            json=body,
        )

    if resp.status_code >= 400:
        raise RuntimeError(f"ElevenLabs outbound call failed ({resp.status_code}): {resp.text}")
    return resp.json()
