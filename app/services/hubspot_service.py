from __future__ import annotations

from typing import Any

import httpx

from app.config import settings

HUBSPOT_BASE = "https://api.hubapi.com"

# Contact properties we pull from HubSpot and map into our lead store.
CONTACT_PROPERTIES = [
    "firstname",
    "lastname",
    "phone",
    "mobilephone",
    "email",
    "city",
    "state",
    "hs_lead_status",
    "notes_last_contacted",
    "message",
]


def hubspot_configured() -> bool:
    return bool(settings.hubspot_access_token)


def _headers() -> dict[str, str]:
    if not settings.hubspot_access_token:
        raise ValueError("HUBSPOT_ACCESS_TOKEN is not configured in .env")
    return {
        "Authorization": f"Bearer {settings.hubspot_access_token}",
        "Content-Type": "application/json",
    }


def _map_contact_to_lead(contact: dict[str, Any]) -> dict[str, Any] | None:
    props = contact.get("properties", {}) or {}
    phone = (props.get("phone") or props.get("mobilephone") or "").strip()
    if not phone:
        return None

    name = " ".join(
        p for p in [props.get("firstname"), props.get("lastname")] if p
    ).strip()
    area = " ".join(p for p in [props.get("city"), props.get("state")] if p).strip()

    return {
        "external_id": str(contact.get("id", "")),
        "phone": phone,
        "fields": {
            "name": name,
            "email": (props.get("email") or "").strip(),
            "property_id": "",
            "budget": "",
            "area": area,
            "notes": (props.get("message") or props.get("notes_last_contacted") or "").strip(),
        },
    }


def fetch_contacts(limit: int = 100) -> list[dict[str, Any]]:
    """Fetch HubSpot contacts and map to lead dicts (only those with a phone)."""
    leads: list[dict[str, Any]] = []
    after: str | None = None

    with httpx.Client(timeout=45) as client:
        while True:
            params: dict[str, Any] = {
                "limit": min(limit, 100),
                "properties": ",".join(CONTACT_PROPERTIES),
            }
            if after:
                params["after"] = after

            resp = client.get(
                f"{HUBSPOT_BASE}/crm/v3/objects/contacts",
                headers=_headers(),
                params=params,
            )
            if resp.status_code >= 400:
                raise RuntimeError(
                    f"HubSpot fetch failed ({resp.status_code}): {resp.text}"
                )

            data = resp.json()
            for contact in data.get("results", []):
                mapped = _map_contact_to_lead(contact)
                if mapped:
                    leads.append(mapped)

            paging = data.get("paging", {}).get("next", {})
            after = paging.get("after")
            if not after or len(leads) >= limit:
                break

    return leads[:limit]
