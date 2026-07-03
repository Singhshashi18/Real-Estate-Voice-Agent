from __future__ import annotations

import csv
import io
import json
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from app.config import settings
from app.services.auth_service import DB_PATH, init_db
from app.services.elevenlabs_outbound import (
    cancel_batch_call,
    get_batch_call,
    submit_batch_call,
)

CSV_COLUMNS = ("phone", "name", "email", "property_id", "budget", "area", "notes")
REQUIRED_COLUMNS = ("phone",)


def _conn() -> sqlite3.Connection:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_outbound_db() -> None:
    init_db()
    with _conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS outbound_campaigns (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                elevenlabs_batch_id TEXT,
                recipient_count INTEGER NOT NULL DEFAULT 0,
                recipients_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_sync_json TEXT
            )
            """
        )
        conn.commit()


def normalize_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw.strip())
    if not digits:
        raise ValueError(f"Invalid phone: {raw}")

    if raw.strip().startswith("+"):
        return f"+{digits}"

    if len(digits) == 10:
        return f"+91{digits}"
    if len(digits) == 11 and digits.startswith("0"):
        return f"+91{digits[1:]}"
    if len(digits) == 12 and digits.startswith("91"):
        return f"+{digits}"

    return f"+{digits}"


def parse_leads_csv(content: str) -> tuple[list[dict[str, str]], list[str]]:
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames:
        raise ValueError("CSV is empty or missing a header row")

    headers = {h.strip().lower().replace(" ", "_") for h in reader.fieldnames}
    missing = [c for c in REQUIRED_COLUMNS if c not in headers]
    if missing:
        raise ValueError(f"CSV missing required columns: {', '.join(missing)}")

    leads: list[dict[str, str]] = []
    errors: list[str] = []

    for i, row in enumerate(reader, start=2):
        normalized = {
            (k or "").strip().lower().replace(" ", "_"): (v or "").strip()
            for k, v in row.items()
        }
        phone_raw = normalized.get("phone", "")
        if not phone_raw:
            errors.append(f"Row {i}: missing phone")
            continue
        try:
            phone = normalize_phone(phone_raw)
        except ValueError as exc:
            errors.append(f"Row {i}: {exc}")
            continue

        lead = {
            "phone": phone,
            "name": normalized.get("name", ""),
            "email": normalized.get("email", ""),
            "property_id": normalized.get("property_id", ""),
            "budget": normalized.get("budget", ""),
            "area": normalized.get("area", ""),
            "notes": normalized.get("notes", ""),
        }
        leads.append(lead)

    if not leads and errors:
        raise ValueError("; ".join(errors[:5]))

    return leads, errors


def _lead_to_recipient(lead: dict[str, str]) -> dict[str, Any]:
    name = lead.get("name") or "there"
    return {
        "phone_number": lead["phone"],
        "conversation_initiation_client_data": {
            "dynamic_variables": {
                "customer_name": name,
                "customer_email": lead.get("email", ""),
                "property_id": lead.get("property_id", ""),
                "budget": lead.get("budget", ""),
                "area": lead.get("area", ""),
                "notes": lead.get("notes", ""),
            },
        },
    }


def create_and_submit_campaign(
    *,
    user_id: int,
    name: str,
    leads: list[dict[str, str]],
) -> dict[str, Any]:
    init_outbound_db()
    campaign_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    recipients = [_lead_to_recipient(lead) for lead in leads]

    try:
        el_response = submit_batch_call(call_name=name, recipients=recipients)
    except Exception as exc:
        raise ValueError(str(exc)) from exc

    batch_id = (
        el_response.get("batch_id")
        or el_response.get("id")
        or el_response.get("batch_calling_id")
    )
    status = el_response.get("status", "submitted")

    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO outbound_campaigns (
                id, user_id, name, status, elevenlabs_batch_id,
                recipient_count, recipients_json, created_at, updated_at, last_sync_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                campaign_id,
                user_id,
                name,
                status,
                batch_id,
                len(leads),
                json.dumps(leads),
                now,
                now,
                json.dumps(el_response),
            ),
        )
        conn.commit()

    return get_campaign(campaign_id, user_id)


def list_campaigns(user_id: int) -> list[dict[str, Any]]:
    init_outbound_db()
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT id, name, status, elevenlabs_batch_id, recipient_count,
                   created_at, updated_at
            FROM outbound_campaigns
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_campaign(campaign_id: str, user_id: int) -> dict[str, Any]:
    init_outbound_db()
    with _conn() as conn:
        row = conn.execute(
            "SELECT * FROM outbound_campaigns WHERE id = ? AND user_id = ?",
            (campaign_id, user_id),
        ).fetchone()
    if not row:
        raise ValueError("Campaign not found")

    data = dict(row)
    data["recipients"] = json.loads(data.pop("recipients_json"))
    if data.get("last_sync_json"):
        data["elevenlabs"] = json.loads(data.pop("last_sync_json"))
    else:
        data.pop("last_sync_json", None)
    return data


def refresh_campaign(campaign_id: str, user_id: int) -> dict[str, Any]:
    campaign = get_campaign(campaign_id, user_id)
    batch_id = campaign.get("elevenlabs_batch_id")
    if not batch_id:
        return campaign

    sync = get_batch_call(batch_id)
    status = sync.get("status", campaign.get("status", "unknown"))
    now = datetime.now(timezone.utc).isoformat()

    with _conn() as conn:
        conn.execute(
            """
            UPDATE outbound_campaigns
            SET status = ?, updated_at = ?, last_sync_json = ?
            WHERE id = ? AND user_id = ?
            """,
            (status, now, json.dumps(sync), campaign_id, user_id),
        )
        conn.commit()

    return get_campaign(campaign_id, user_id)


def cancel_campaign(campaign_id: str, user_id: int) -> dict[str, Any]:
    campaign = get_campaign(campaign_id, user_id)
    batch_id = campaign.get("elevenlabs_batch_id")
    if batch_id:
        cancel_batch_call(batch_id)

    now = datetime.now(timezone.utc).isoformat()
    with _conn() as conn:
        conn.execute(
            """
            UPDATE outbound_campaigns SET status = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
            """,
            ("cancelled", now, campaign_id, user_id),
        )
        conn.commit()

    return get_campaign(campaign_id, user_id)
