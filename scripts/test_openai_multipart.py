"""Compare multipart strategies against OpenAI realtime/calls."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx
import requests
from urllib3.fields import RequestField
from urllib3.filepost import encode_multipart_formdata

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.config import settings
from app.services.openai_session import build_session_config

OFFER = (
    "v=0\r\n"
    "o=- 123456789 0 IN IP4 127.0.0.1\r\n"
    "s=-\r\n"
    "t=0 0\r\n"
    "a=group:BUNDLE 0\r\n"
    "m=audio 9 UDP/TLS/RTP/SAVPF 111\r\n"
    "c=IN IP4 0.0.0.0\r\n"
    "a=rtcp:9 IN IP4 0.0.0.0\r\n"
    "a=ice-ufrag:abcd\r\n"
    "a=ice-pwd:abcdefghijklmnopqrstuvwxyz\r\n"
    "a=fingerprint:sha-256 00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF\r\n"
    "a=setup:actpass\r\n"
    "a=mid:0\r\n"
    "a=sendrecv\r\n"
    "a=rtpmap:111 opus/48000/2\r\n"
)
SESSION = json.dumps(build_session_config())
HEADERS = {"Authorization": f"Bearer {settings.openai_api_key}"}


def via_requests() -> tuple[int, str]:
    r = requests.post(
        "https://api.openai.com/v1/realtime/calls",
        headers=HEADERS,
        files={
            "sdp": ("sdp", OFFER.encode(), "application/sdp"),
            "session": ("session.json", SESSION.encode(), "application/json"),
        },
        timeout=60,
    )
    return r.status_code, r.text[:250]


def via_urllib3_httpx() -> tuple[int, str]:
    offer_bytes = OFFER.encode()
    session_bytes = SESSION.encode()
    sdp_field = RequestField(name="sdp", data=offer_bytes)
    sdp_field.make_multipart(content_type="application/sdp")
    session_field = RequestField(name="session", data=session_bytes)
    session_field.make_multipart(content_type="application/json")
    body, content_type = encode_multipart_formdata([sdp_field, session_field])
    r = httpx.post(
        "https://api.openai.com/v1/realtime/calls",
        headers={**HEADERS, "Content-Type": content_type},
        content=body,
        timeout=60,
    )
    return r.status_code, r.text[:250]


if __name__ == "__main__":
    for name, fn in [("requests", via_requests), ("urllib3+httpx", via_urllib3_httpx)]:
        code, text = fn()
        print(f"--- {name}: {code}")
        print(text)
        print()
