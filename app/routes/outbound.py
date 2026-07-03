from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.config import settings
from app.routes.auth import get_current_user
from app.services.elevenlabs_outbound import list_phone_numbers, outbound_configured
from app.services.elevenlabs_service import build_elevenlabs_tool_definitions
from app.services.outbound_prompt import (
    build_outbound_agent_instructions,
    build_outbound_first_message,
)
from app.services.outbound_service import (
    CSV_COLUMNS,
    cancel_campaign,
    create_and_submit_campaign,
    get_campaign,
    list_campaigns,
    parse_leads_csv,
    refresh_campaign,
)

router = APIRouter(prefix="/api/outbound", tags=["outbound"])


class SubmitCampaignRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    leads: list[dict[str, str]] = Field(min_length=1, max_length=500)


@router.get("/status")
def outbound_status(_user: dict = Depends(get_current_user)):
    return {
        "configured": outbound_configured(),
        "elevenlabs_api_key": bool(settings.elevenlabs_api_key),
        "outbound_agent_id": settings.elevenlabs_outbound_agent_id or None,
        "phone_number_id": settings.elevenlabs_phone_number_id or None,
        "caller_id": settings.twilio_phone_number or None,
        "csv_columns": list(CSV_COLUMNS),
        "required_columns": ["phone"],
    }


@router.get("/setup-kit")
def outbound_setup_kit(_user: dict = Depends(get_current_user)):
    base = settings.api_public_url.rstrip("/")
    secret = settings.telephony_webhook_secret
    tools = []
    for tool in build_elevenlabs_tool_definitions():
        tools.append(
            {
                "name": tool["name"],
                "description": tool["description"],
                "url": tool["api_schema"]["url"],
                "auth_header": f"Authorization: Bearer {secret}" if secret else "(set TELEPHONY_WEBHOOK_SECRET)",
            }
        )

    return {
        "mode": "elevenlabs_outbound_dashboard",
        "summary": (
            "Create a separate outbound agent in ElevenLabs, add the same 6 webhook tools, "
            "assign +16614864467, then set agent_id and phone_number_id in .env."
        ),
        "agent": {
            "name_suggestion": f"{settings.company_name} Outbound — {settings.organizer_name}",
            "language": "en",
            "first_message": build_outbound_first_message(),
            "system_prompt": build_outbound_agent_instructions(),
            "dynamic_variables": [
                "customer_name",
                "customer_email",
                "property_id",
                "budget",
                "area",
                "notes",
            ],
        },
        "server_tools": tools,
        "env_required": [
            "ELEVENLABS_API_KEY",
            "ELEVENLABS_OUTBOUND_AGENT_ID",
            "ELEVENLABS_PHONE_NUMBER_ID",
            "API_PUBLIC_URL",
            "TELEPHONY_WEBHOOK_SECRET",
        ],
        "urls": {"tool_base": f"{base}/api/telephony/tools"},
    }


@router.get("/phone-numbers")
def outbound_phone_numbers(_user: dict = Depends(get_current_user)):
    if not settings.elevenlabs_api_key:
        raise HTTPException(status_code=400, detail="ELEVENLABS_API_KEY is not set")
    return {"phone_numbers": list_phone_numbers()}


@router.post("/parse-csv")
async def parse_csv(
    file: UploadFile = File(...),
    _user: dict = Depends(get_current_user),
):
    content = (await file.read()).decode("utf-8-sig")
    try:
        leads, warnings = parse_leads_csv(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"leads": leads, "warnings": warnings, "count": len(leads)}


@router.get("/campaigns")
def get_campaigns(user: dict = Depends(get_current_user)):
    return {"campaigns": list_campaigns(user["id"])}


@router.get("/campaigns/{campaign_id}")
def get_campaign_detail(campaign_id: str, user: dict = Depends(get_current_user)):
    try:
        return get_campaign(campaign_id, user["id"])
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/campaigns")
def submit_campaign(body: SubmitCampaignRequest, user: dict = Depends(get_current_user)):
    if not outbound_configured():
        raise HTTPException(
            status_code=400,
            detail=(
                "Outbound not configured. Set ELEVENLABS_API_KEY, "
                "ELEVENLABS_OUTBOUND_AGENT_ID, and ELEVENLABS_PHONE_NUMBER_ID in .env"
            ),
        )
    try:
        return create_and_submit_campaign(
            user_id=user["id"],
            name=body.name,
            leads=body.leads,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/campaigns/{campaign_id}/refresh")
def sync_campaign(campaign_id: str, user: dict = Depends(get_current_user)):
    try:
        return refresh_campaign(campaign_id, user["id"])
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/campaigns/{campaign_id}/cancel")
def stop_campaign(campaign_id: str, user: dict = Depends(get_current_user)):
    try:
        return cancel_campaign(campaign_id, user["id"])
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
