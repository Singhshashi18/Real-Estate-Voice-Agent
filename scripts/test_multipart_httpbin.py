"""Inspect httpx multipart encoding (no OpenAI call)."""
from __future__ import annotations

import httpx

OFFER = b"v=0\r\no=- 1 2 IN IP4 127.0.0.1\r\n"
SESSION = b'{"type":"realtime"}'

variants = {
    "none-filename-str": {
        "sdp": (None, OFFER.decode(), "application/sdp"),
        "session": (None, SESSION.decode(), "application/json"),
    },
    "sdp-filename-bytes": {
        "sdp": ("sdp", OFFER, "application/sdp"),
        "session": ("session.json", SESSION, "application/json"),
    },
    "list-form": [
        ("sdp", ("sdp", OFFER, "application/sdp")),
        ("session", ("session.json", SESSION, "application/json")),
    ],
}


def main() -> None:
    for name, files in variants.items():
        r = httpx.post("https://httpbin.org/post", files=files, timeout=30)
        data = r.json()
        print("---", name)
        print("form keys:", list(data.get("form", {}).keys()))
        print("files keys:", list(data.get("files", {}).keys()))
        if "sdp" in data.get("files", {}):
            print("sdp file len:", len(data["files"]["sdp"]))


if __name__ == "__main__":
    main()
