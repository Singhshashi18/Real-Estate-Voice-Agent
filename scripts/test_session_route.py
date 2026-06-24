"""Test session route forwards SDP via urllib3 multipart."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from app.main import app
from app.services.auth_service import authenticate_user, create_access_token, create_user

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


def main() -> None:
    client = TestClient(app)
    user = authenticate_user("demo@example.com", "DemoPass123")
    if not user:
        user = create_user("Demo", "demo@example.com", "DemoPass123")
    token = create_access_token(user["id"])

    r = client.post(
        "/api/session",
        content=OFFER,
        headers={
            "Content-Type": "application/sdp",
            "Authorization": f"Bearer {token}",
        },
    )
    print("status:", r.status_code)
    text = r.text
    if r.status_code == 200:
        print("answer sdp starts:", text[:40])
    else:
        detail = r.json().get("detail", text)
        print("detail:", str(detail)[:200])
        if "EOF" in str(detail):
            print("FAIL: still getting SDP EOF")
        elif "sdp" in str(detail).lower() and "required" in str(detail).lower():
            print("FAIL: sdp field missing in multipart")
        elif "unmarshal" in str(detail).lower():
            print("FAIL: sdp parse error")
        else:
            print("OK: past SDP forwarding (may be model/SDP validity error)")


if __name__ == "__main__":
    main()
