"""Google sign-in with the OAuth 2.0 authorization code flow.

The state value is kept in a short-lived httpOnly cookie, so no server-side
session middleware is needed.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode

import httpx

from tuvi_api.auth.settings import AuthSettings

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


class GoogleAuthError(Exception):
    """Raised when Google does not return a usable, verified identity."""


@dataclass(frozen=True, slots=True)
class GoogleIdentity:
    sub: str
    email: str
    display_name: str | None


def authorize_url(settings: AuthSettings, *, state: str) -> str:
    query = urlencode(
        {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "prompt": "select_account",
        }
    )
    return f"{AUTHORIZE_URL}?{query}"


async def exchange_code(
    settings: AuthSettings,
    *,
    code: str,
    client: httpx.AsyncClient | None = None,
) -> GoogleIdentity:
    owns_client = client is None
    http = client or httpx.AsyncClient(timeout=10)
    try:
        token_response = await http.post(
            TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_response.status_code != 200:
            raise GoogleAuthError(f"token exchange failed: {token_response.status_code}")
        access_token = token_response.json().get("access_token")
        if not access_token:
            raise GoogleAuthError("token response has no access_token")

        userinfo_response = await http.get(
            USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if userinfo_response.status_code != 200:
            raise GoogleAuthError(f"userinfo failed: {userinfo_response.status_code}")
        info = userinfo_response.json()
    finally:
        if owns_client:
            await http.aclose()

    if not info.get("sub") or not info.get("email"):
        raise GoogleAuthError("userinfo has no sub or email")
    # Accounts are linked by email, so only a verified email is accepted.
    if info.get("email_verified") is not True:
        raise GoogleAuthError("Google email is not verified")
    return GoogleIdentity(sub=info["sub"], email=info["email"], display_name=info.get("name"))
