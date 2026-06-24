from __future__ import annotations

from urllib3.fields import RequestField
from urllib3.filepost import encode_multipart_formdata


def build_realtime_call_body(offer_sdp: str, session_config: str) -> tuple[bytes, str]:
    """Build multipart/form-data body for OpenAI /v1/realtime/calls."""
    normalized = offer_sdp.replace("\r\n", "\n").strip().replace("\n", "\r\n")
    if not normalized.endswith("\r\n"):
        normalized += "\r\n"
    offer_bytes = normalized.encode("utf-8")
    session_bytes = session_config.encode("utf-8")

    sdp_field = RequestField(name="sdp", data=offer_bytes)
    sdp_field.make_multipart(content_type="application/sdp")

    session_field = RequestField(name="session", data=session_bytes)
    session_field.make_multipart(content_type="application/json")

    body, content_type = encode_multipart_formdata([sdp_field, session_field])
    return body, content_type
