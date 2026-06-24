import json

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.config import settings
from app.routes.auth import get_current_user
from app.services.openai_session import build_session_config
from app.services.realtime_multipart import build_realtime_call_body

router = APIRouter(prefix="/api", tags=["session"])


def _openai_error_message(response: httpx.Response) -> str:
    try:
        data = response.json()
        error = data.get("error")
        if isinstance(error, dict) and error.get("message"):
            return str(error["message"])
    except Exception:
        pass
    return response.text or "OpenAI realtime session failed"


@router.post("/session")
async def create_realtime_session(
    request: Request,
    _user: dict = Depends(get_current_user),
):
    if not settings.openai_api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured.")

    offer_sdp = (await request.body()).decode("utf-8").strip()
    if not offer_sdp:
        raise HTTPException(status_code=400, detail="Missing SDP offer in request body.")
    if not offer_sdp.startswith("v=0"):
        raise HTTPException(
            status_code=400,
            detail="Invalid SDP offer received from browser. Please retry the call.",
        )

    session_config = json.dumps(build_session_config())
    body, content_type = build_realtime_call_body(offer_sdp, session_config)

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/realtime/calls",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": content_type,
                },
                content=body,
            )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502, detail=f"Failed to reach OpenAI: {exc}"
        ) from exc

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=_openai_error_message(response),
        )

    return Response(content=response.text, media_type="application/sdp")
