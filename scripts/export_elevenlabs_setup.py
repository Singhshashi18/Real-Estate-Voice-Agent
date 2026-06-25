"""Print prompt + tool URLs to paste into ElevenLabs Conversational AI dashboard."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.services.elevenlabs_service import build_dashboard_setup_kit


def main() -> None:
    kit = build_dashboard_setup_kit()
    out = ROOT / "data" / "elevenlabs_setup_kit.json"
    out.write_text(json.dumps(kit, indent=2), encoding="utf-8")

    agent = kit["agent"]
    print("=" * 60)
    print("ELEVENLABS DASHBOARD SETUP")
    print("=" * 60)
    print("\n1. Go to elevenlabs.io -> Conversational AI -> Create agent")
    print(f"   Name: {agent['name_suggestion']}")
    print(f"   Language: {agent['language']}")
    print("\n2. Voice -> pick any voice you like in the dashboard (no .env needed)")
    print("\n3. First message -> paste:")
    print(f"   {agent['first_message']}")
    print("\n4. System prompt -> paste from data/elevenlabs_setup_kit.json")
    print("   (field: agent.system_prompt)")
    print("\n5. Server tools -> add each tool (POST + Authorization header):")
    for t in kit["server_tools"]:
        print(f"\n   [{t['name']}]")
        print(f"   URL: {t['url']}")
        print(f"   {t['auth_header']}")
    print("\n6. Phone Numbers -> Import Twilio -> assign this agent")
    print(f"\nFull kit saved to: {out}")


if __name__ == "__main__":
    main()
