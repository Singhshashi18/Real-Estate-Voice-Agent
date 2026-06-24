from __future__ import annotations

import base64
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus, urlencode

import httpx
from jose import JWTError, jwt

from app.config import settings

OAUTH_STATE_TTL_MINUTES = 10
OAUTH_PLACEHOLDER_PASSWORD = "!oauth-only!"

_pkce_store: dict[str, str] = {}


def _oauth_callback_url(provider: str) -> str:
    base = settings.api_public_url.rstrip("/")
    return f"{base}/api/auth/oauth/{provider}/callback"


def create_oauth_state(provider: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=OAUTH_STATE_TTL_MINUTES)
    payload = {"provider": provider, "exp": expire, "nonce": secrets.token_urlsafe(8)}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_oauth_state(state: str, provider: str) -> bool:
    try:
        payload = jwt.decode(
            state, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return payload.get("provider") == provider
    except JWTError:
        return False


def get_enabled_providers() -> list[str]:
    providers: list[str] = []
    if settings.google_oauth_client_id and settings.google_oauth_client_secret:
        providers.append("google")
    if settings.github_client_id and settings.github_client_secret:
        providers.append("github")
    if settings.x_client_id and settings.x_client_secret:
        providers.append("x")
    return providers


def build_google_authorize_url(state: str) -> str:
    params = {
        "client_id": settings.google_oauth_client_id,
        "redirect_uri": _oauth_callback_url("google"),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"


def build_github_authorize_url(state: str) -> str:
    params = {
        "client_id": settings.github_client_id,
        "redirect_uri": _oauth_callback_url("github"),
        "scope": "read:user user:email",
        "state": state,
    }
    return f"https://github.com/login/oauth/authorize?{urlencode(params)}"


def _create_pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(48)
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .decode()
        .rstrip("=")
    )
    return verifier, challenge


def build_x_authorize_url(state: str) -> str:
    verifier, challenge = _create_pkce_pair()
    _pkce_store[state] = verifier
    params = {
        "response_type": "code",
        "client_id": settings.x_client_id,
        "redirect_uri": _oauth_callback_url("x"),
        "scope": "tweet.read users.read offline.access",
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    return f"https://twitter.com/i/oauth2/authorize?{urlencode(params)}"


def build_authorize_url(provider: str, state: str) -> str:
    if provider == "google":
        return build_google_authorize_url(state)
    if provider == "github":
        return build_github_authorize_url(state)
    if provider == "x":
        return build_x_authorize_url(state)
    raise ValueError(f"Unsupported provider: {provider}")


async def exchange_google_code(code: str) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_oauth_client_id,
                "client_secret": settings.google_oauth_client_secret,
                "redirect_uri": _oauth_callback_url("google"),
                "grant_type": "authorization_code",
            },
        )
        token_resp.raise_for_status()
        access_token = token_resp.json()["access_token"]

        user_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_resp.raise_for_status()
        profile = user_resp.json()

    return {
        "provider": "google",
        "subject": str(profile["id"]),
        "email": profile.get("email", "").lower().strip(),
        "name": profile.get("name") or profile.get("email", "").split("@")[0],
    }


async def exchange_github_code(code: str) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
                "redirect_uri": _oauth_callback_url("github"),
            },
        )
        token_resp.raise_for_status()
        access_token = token_resp.json()["access_token"]

        user_resp = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
            },
        )
        user_resp.raise_for_status()
        profile = user_resp.json()

        email = (profile.get("email") or "").lower().strip()
        if not email:
            emails_resp = await client.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )
            emails_resp.raise_for_status()
            emails = emails_resp.json()
            primary = next(
                (e for e in emails if e.get("primary") and e.get("verified")),
                None,
            )
            fallback = next((e for e in emails if e.get("verified")), None)
            chosen = primary or fallback
            if not chosen:
                raise ValueError("GitHub account has no verified email")
            email = chosen["email"].lower().strip()

    return {
        "provider": "github",
        "subject": str(profile["id"]),
        "email": email,
        "name": profile.get("name") or profile.get("login") or email.split("@")[0],
    }


async def exchange_x_code(code: str, state: str) -> dict:
    verifier = _pkce_store.pop(state, None)
    if not verifier:
        raise ValueError("OAuth session expired. Try signing in again.")

    credentials = f"{settings.x_client_id}:{settings.x_client_secret}"
    basic = base64.b64encode(credentials.encode()).decode()

    async with httpx.AsyncClient(timeout=20) as client:
        token_resp = await client.post(
            "https://api.twitter.com/2/oauth2/token",
            headers={
                "Authorization": f"Basic {basic}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": _oauth_callback_url("x"),
                "code_verifier": verifier,
            },
        )
        token_resp.raise_for_status()
        access_token = token_resp.json()["access_token"]

        user_resp = await client.get(
            "https://api.twitter.com/2/users/me",
            params={"user.fields": "name,username"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_resp.raise_for_status()
        profile = user_resp.json()["data"]

    username = profile.get("username", "user")
    return {
        "provider": "x",
        "subject": str(profile["id"]),
        "email": f"{username}@x.oauth.local",
        "name": profile.get("name") or username,
    }


async def exchange_code(provider: str, code: str, state: str) -> dict:
    if provider == "google":
        return await exchange_google_code(code)
    if provider == "github":
        return await exchange_github_code(code)
    if provider == "x":
        return await exchange_x_code(code, state)
    raise ValueError(f"Unsupported provider: {provider}")


def frontend_callback_url(token: str | None = None, error: str | None = None) -> str:
    base = settings.frontend_url.rstrip("/")
    if error:
        return f"{base}/auth/callback?error={quote_plus(error)}"
    if not token:
        raise ValueError("token is required when error is not set")
    return f"{base}/auth/callback?token={token}"
