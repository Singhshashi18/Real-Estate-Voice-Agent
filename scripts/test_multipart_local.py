import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.realtime_multipart import build_realtime_call_body

body, ct = build_realtime_call_body(
    "v=0\r\no=- 1 2 IN IP4 127.0.0.1\r\n",
    '{"type":"realtime"}',
)
print("content-type:", ct[:80])
print("has v=0:", b"v=0" in body)
print('has sdp field:', b'name="sdp"' in body)
print("body size:", len(body))
