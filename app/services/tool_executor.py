from __future__ import annotations

from typing import Any

from app.services import calendar_service, knowledge_base
from app.services.email_utils import validate_email


def execute_tool(name: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run agent tools server-side (browser WebRTC + phone/ElevenLabs webhooks)."""
    args = args or {}

    if name == "search_properties":
        return knowledge_base.search_properties(
            location=args.get("location"),
            bhk=args.get("bhk"),
            property_type=args.get("property_type"),
            max_budget_lakhs=args.get("max_budget_lakhs"),
            budget=args.get("budget"),
            query=args.get("query"),
        )

    if name == "get_inventory_overview":
        return knowledge_base.get_inventory_overview()

    if name == "get_property_details":
        return knowledge_base.get_property_details(str(args.get("property_id", "")))

    if name == "check_availability":
        return calendar_service.check_availability(
            str(args.get("date", "")),
            args.get("preferred_time"),
        )

    if name == "validate_email":
        return validate_email(str(args.get("email", "")))

    if name == "book_meeting":
        return calendar_service.book_meeting(
            str(args.get("name", "")),
            str(args.get("email", "")),
            str(args.get("date", "")),
            str(args.get("time", "")),
            property_id=args.get("property_id"),
            property_name=args.get("property_name"),
        )

    if name == "end_call":
        return {
            "success": True,
            "message": "Give your closing line, then the call will end.",
        }

    raise ValueError(f"Unknown tool: {name}")


def format_tool_result_for_agent(result: dict[str, Any]) -> str:
    """Compact string ElevenLabs / LLM can read aloud."""
    if result.get("message"):
        return str(result["message"])
    return str(result)
