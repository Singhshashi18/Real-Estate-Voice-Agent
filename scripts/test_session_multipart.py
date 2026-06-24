"""Quick check: multipart SDP forwarding shape."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import httpx

from app.config import settings
from app.services.auth_service import authenticate_user, create_access_token, create_user
from app.services.openai_session import build_session_config

OFFER = """v=0
o=- 123456789 0 IN IP4 127.0.0.1
s=-
t=0 0
a=group:BUNDLE 0
m=audio 9 UDP/TLS/RTP/SAVPF 111
c=IN IP4 0.0.0.0
a=rtcp:9 IN IP4 0.0.0.0
a=ice-ufrag:abcd
a=ice-pwd:abcdefghijklmnopqrstuvwxyz
a=fingerprint:sha-256 00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF
a=setup:actpass
a=mid:0
a=sendrecv
a=rtpmap:111 opus/48000/2
"""

session_config = json.dumps(build_session_config())


def test_openai_forward() -> None:
    user = authenticate_user("demo@example.com", "DemoPass123")
    if not user:
        user = create_user("Demo", "demo@example.com", "DemoPass123")
    token = create_access_token(user["id"])

    with httpx.Client(timeout=60) as client:
        r = client.post(
            "https://api.openai.com/v1/realtime/calls",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            files={
                "sdp": ("sdp", OFFER.encode("utf-8"), "application/sdp"),
                "session": ("session.json", session_config.encode("utf-8"), "application/json"),
            },
        )
    print("OpenAI status:", r.status_code)
    print("OpenAI body:", r.text[:300])


if __name__ == "__main__":
    test_openai_forward()
