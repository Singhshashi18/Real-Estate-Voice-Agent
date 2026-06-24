from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.services import auth_service, oauth_service

router = APIRouter(prefix="/api/auth/oauth", tags=["oauth"])


@router.get("/providers")
def oauth_providers():
    return {"providers": oauth_service.get_enabled_providers()}


@router.get("/{provider}")
async def oauth_start(provider: str):
    if provider not in oauth_service.get_enabled_providers():
        raise HTTPException(
            status_code=404,
            detail=f"{provider.title()} sign-in is not configured on the server",
        )

    state = oauth_service.create_oauth_state(provider)
    url = oauth_service.build_authorize_url(provider, state)
    return RedirectResponse(url=url, status_code=302)


@router.get("/{provider}/callback")
async def oauth_callback(provider: str, code: str | None = None, state: str | None = None):
    if not code or not state:
        return RedirectResponse(
            url=oauth_service.frontend_callback_url(
                error="Sign-in was cancelled or failed"
            ),
            status_code=302,
        )

    if not oauth_service.verify_oauth_state(state, provider):
        return RedirectResponse(
            url=oauth_service.frontend_callback_url(
                error="Invalid sign-in session. Please try again."
            ),
            status_code=302,
        )

    if provider not in oauth_service.get_enabled_providers():
        return RedirectResponse(
            url=oauth_service.frontend_callback_url(
                error=f"{provider.title()} sign-in is not configured"
            ),
            status_code=302,
        )

    try:
        profile = await oauth_service.exchange_code(provider, code, state)
        user = auth_service.get_or_create_oauth_user(
            profile["provider"],
            profile["subject"],
            profile["email"],
            profile["name"],
        )
        token = auth_service.create_access_token(user["id"])
    except Exception as exc:
        return RedirectResponse(
            url=oauth_service.frontend_callback_url(error=str(exc)),
            status_code=302,
        )

    return RedirectResponse(
        url=oauth_service.frontend_callback_url(token=token),
        status_code=302,
    )
