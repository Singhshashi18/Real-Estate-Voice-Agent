"""Print outbound agent prompt + tool URLs for ElevenLabs dashboard."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.config import settings
from app.services.elevenlabs_service import build_elevenlabs_tool_definitions
from app.services.outbound_prompt import (
    build_outbound_agent_instructions,
    build_outbound_first_message,
)

if __name__ == "__main__":
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
    kit = {
        "mode": "elevenlabs_outbound_dashboard",
        "agent": {
            "name_suggestion": f"{settings.company_name} Outbound — {settings.organizer_name}",
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
        "urls": {"tool_base": f"{base}/api/telephony/tools"},
        "env_required": [
            "ELEVENLABS_API_KEY",
            "ELEVENLABS_OUTBOUND_AGENT_ID",
            "ELEVENLABS_PHONE_NUMBER_ID",
        ],
    }
    out = ROOT / "data" / "elevenlabs_outbound_setup_kit.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(kit, indent=2), encoding="utf-8")
    print(json.dumps(kit, indent=2))
    print(f"\nSaved → {out}")
