from __future__ import annotations

from typing import Any

from app.config import settings
from app.services.elevenlabs_outbound import (
    initiate_single_outbound_call,
    outbound_configured,
)
from app.services.hubspot_service import fetch_contacts, hubspot_configured
from app.services.leads_service import (
    lead_dynamic_variables,
    list_leads,
    set_lead_status,
    upsert_lead,
)


def _try_auto_call(lead: dict[str, Any]) -> dict[str, str]:
    """Start an outbound call for a lead; never raise (report status instead)."""
    if not outbound_configured():
        return {"called": False, "reason": "outbound_not_configured"}
    if lead.get("status") == "do_not_call":
        return {"called": False, "reason": "do_not_call"}

    try:
        resp = initiate_single_outbound_call(
            to_number=lead["phone"],
            dynamic_variables=lead_dynamic_variables(lead),
        )
        conversation_id = resp.get("conversation_id") or resp.get("callSid") or "started"
        set_lead_status(lead["id"], lead["user_id"], "calling", call_result=conversation_id)
        return {"called": True, "conversation_id": conversation_id}
    except Exception as exc:  # noqa: BLE001 — surface as per-lead result
        set_lead_status(lead["id"], lead["user_id"], "failed", call_result=str(exc)[:300])
        return {"called": False, "reason": str(exc)[:300]}


def sync_hubspot(
    user_id: int,
    *,
    auto_call: bool | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """Pull HubSpot contacts into the leads store; auto-call new leads if enabled."""
    if not hubspot_configured():
        raise ValueError("HUBSPOT_ACCESS_TOKEN is not configured in .env")

    if auto_call is None:
        auto_call = settings.outbound_auto_call

    contacts = fetch_contacts(limit=limit)

    new_count = 0
    updated_count = 0
    call_results: list[dict[str, Any]] = []

    for contact in contacts:
        lead, is_new = upsert_lead(
            user_id=user_id,
            phone=contact["phone"],
            source="hubspot",
            external_id=contact.get("external_id"),
            fields=contact["fields"],
        )
        if is_new:
            new_count += 1
            if auto_call:
                result = _try_auto_call(lead)
                call_results.append({"phone": lead["phone"], **result})
        else:
            updated_count += 1

    return {
        "source": "hubspot",
        "fetched": len(contacts),
        "new_leads": new_count,
        "updated_leads": updated_count,
        "auto_call": auto_call,
        "calls": call_results,
        "leads": list_leads(user_id, source="hubspot"),
    }
