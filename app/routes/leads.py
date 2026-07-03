from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.config import settings
from app.routes.auth import get_current_user
from app.services.crm_sync_service import _try_auto_call, sync_hubspot
from app.services.elevenlabs_outbound import outbound_configured
from app.services.hubspot_service import hubspot_configured
from app.services.leads_service import (
    delete_lead,
    get_lead,
    list_leads,
    set_lead_status,
    upsert_lead,
)

router = APIRouter(prefix="/api/leads", tags=["leads"])


class ManualLeadRequest(BaseModel):
    phone: str = Field(min_length=5, max_length=20)
    name: str = ""
    email: str = ""
    property_id: str = ""
    budget: str = ""
    area: str = ""
    notes: str = ""


class SyncRequest(BaseModel):
    auto_call: bool | None = None
    limit: int = Field(default=100, ge=1, le=500)


@router.get("/status")
def leads_status(_user: dict = Depends(get_current_user)):
    return {
        "hubspot_configured": hubspot_configured(),
        "outbound_configured": outbound_configured(),
        "auto_call_default": settings.outbound_auto_call,
        "sources": ["hubspot", "manual", "csv", "webhook"],
    }


@router.get("")
def get_leads(
    status: str | None = None,
    source: str | None = None,
    user: dict = Depends(get_current_user),
):
    return {"leads": list_leads(user["id"], status=status, source=source)}


@router.post("")
def create_lead(body: ManualLeadRequest, user: dict = Depends(get_current_user)):
    try:
        lead, is_new = upsert_lead(
            user_id=user["id"],
            phone=body.phone,
            source="manual",
            fields={
                "name": body.name,
                "email": body.email,
                "property_id": body.property_id,
                "budget": body.budget,
                "area": body.area,
                "notes": body.notes,
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"lead": lead, "created": is_new}


@router.delete("/{lead_id}")
def remove_lead(lead_id: str, user: dict = Depends(get_current_user)):
    delete_lead(lead_id, user["id"])
    return {"ok": True}


@router.post("/{lead_id}/call")
def call_lead(lead_id: str, user: dict = Depends(get_current_user)):
    if not outbound_configured():
        raise HTTPException(status_code=400, detail="Outbound calling is not configured")
    try:
        lead = get_lead(lead_id, user["id"])
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    result = _try_auto_call(lead)
    if not result.get("called"):
        raise HTTPException(status_code=502, detail=result.get("reason", "Call failed"))
    return {"ok": True, **result}


@router.post("/{lead_id}/do-not-call")
def mark_do_not_call(lead_id: str, user: dict = Depends(get_current_user)):
    try:
        return {"lead": set_lead_status(lead_id, user["id"], "do_not_call")}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/sync/hubspot")
def sync_from_hubspot(body: SyncRequest, user: dict = Depends(get_current_user)) -> dict[str, Any]:
    if not hubspot_configured():
        raise HTTPException(
            status_code=400,
            detail="HUBSPOT_ACCESS_TOKEN is not configured in .env",
        )
    try:
        return sync_hubspot(user["id"], auto_call=body.auto_call, limit=body.limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
