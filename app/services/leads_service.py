from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from app.services.auth_service import DB_PATH, init_db
from app.services.outbound_service import normalize_phone

LEAD_FIELDS = ("name", "email", "property_id", "budget", "area", "notes")
VALID_SOURCES = ("hubspot", "manual", "csv", "webhook")
VALID_STATUSES = ("new", "queued", "calling", "called", "failed", "do_not_call")


def _conn() -> sqlite3.Connection:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_leads_db() -> None:
    init_db()
    with _conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                phone TEXT NOT NULL,
                name TEXT DEFAULT '',
                email TEXT DEFAULT '',
                property_id TEXT DEFAULT '',
                budget TEXT DEFAULT '',
                area TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                source TEXT NOT NULL DEFAULT 'manual',
                external_id TEXT,
                status TEXT NOT NULL DEFAULT 'new',
                last_called_at TEXT,
                last_call_result TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(user_id, phone)
            )
            """
        )
        conn.commit()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def upsert_lead(
    *,
    user_id: int,
    phone: str,
    source: str = "manual",
    external_id: str | None = None,
    fields: dict[str, str] | None = None,
) -> tuple[dict[str, Any], bool]:
    """Insert or update a lead (dedupe by phone). Returns (lead, is_new)."""
    init_leads_db()
    normalized = normalize_phone(phone)
    fields = {k: (fields or {}).get(k, "") for k in LEAD_FIELDS}
    now = _now()

    with _conn() as conn:
        existing = conn.execute(
            "SELECT * FROM leads WHERE user_id = ? AND phone = ?",
            (user_id, normalized),
        ).fetchone()

        if existing:
            merged = {
                k: (fields.get(k) or existing[k] or "") for k in LEAD_FIELDS
            }
            conn.execute(
                """
                UPDATE leads
                SET name = ?, email = ?, property_id = ?, budget = ?, area = ?,
                    notes = ?, source = ?, external_id = COALESCE(?, external_id),
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    merged["name"],
                    merged["email"],
                    merged["property_id"],
                    merged["budget"],
                    merged["area"],
                    merged["notes"],
                    source,
                    external_id,
                    now,
                    existing["id"],
                ),
            )
            conn.commit()
            return get_lead(existing["id"], user_id), False

        lead_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO leads (
                id, user_id, phone, name, email, property_id, budget, area, notes,
                source, external_id, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', ?, ?)
            """,
            (
                lead_id,
                user_id,
                normalized,
                fields["name"],
                fields["email"],
                fields["property_id"],
                fields["budget"],
                fields["area"],
                fields["notes"],
                source,
                external_id,
                now,
                now,
            ),
        )
        conn.commit()
        return get_lead(lead_id, user_id), True


def get_lead(lead_id: str, user_id: int) -> dict[str, Any]:
    init_leads_db()
    with _conn() as conn:
        row = conn.execute(
            "SELECT * FROM leads WHERE id = ? AND user_id = ?",
            (lead_id, user_id),
        ).fetchone()
    if not row:
        raise ValueError("Lead not found")
    return dict(row)


def list_leads(
    user_id: int,
    *,
    status: str | None = None,
    source: str | None = None,
) -> list[dict[str, Any]]:
    init_leads_db()
    query = "SELECT * FROM leads WHERE user_id = ?"
    params: list[Any] = [user_id]
    if status:
        query += " AND status = ?"
        params.append(status)
    if source:
        query += " AND source = ?"
        params.append(source)
    query += " ORDER BY created_at DESC"
    with _conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def delete_lead(lead_id: str, user_id: int) -> None:
    init_leads_db()
    with _conn() as conn:
        conn.execute(
            "DELETE FROM leads WHERE id = ? AND user_id = ?",
            (lead_id, user_id),
        )
        conn.commit()


def set_lead_status(
    lead_id: str,
    user_id: int,
    status: str,
    *,
    call_result: str | None = None,
) -> dict[str, Any]:
    init_leads_db()
    now = _now()
    called_at = now if status in ("calling", "called") else None
    with _conn() as conn:
        conn.execute(
            """
            UPDATE leads
            SET status = ?,
                last_called_at = COALESCE(?, last_called_at),
                last_call_result = COALESCE(?, last_call_result),
                updated_at = ?
            WHERE id = ? AND user_id = ?
            """,
            (status, called_at, call_result, now, lead_id, user_id),
        )
        conn.commit()
    return get_lead(lead_id, user_id)


def lead_dynamic_variables(lead: dict[str, Any]) -> dict[str, str]:
    return {
        "customer_name": lead.get("name") or "there",
        "customer_email": lead.get("email", "") or "",
        "property_id": lead.get("property_id", "") or "",
        "budget": lead.get("budget", "") or "",
        "area": lead.get("area", "") or "",
        "notes": lead.get("notes", "") or "",
    }
