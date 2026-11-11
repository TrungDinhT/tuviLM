"""Login routes: email and password, email verification, password reset, Google."""

from __future__ import annotations

import logging
import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field, field_validator
from pymongo.errors import PyMongoError

from tuvi_api.auth import google
from tuvi_api.auth.dependencies import (
    OAUTH_STATE_COOKIE,
    SESSION_COOKIE,
    clear_session_cookie,
    current_user_id,
    get_auth_settings,
    get_auth_store,
    get_rate_limiter,
    set_session_cookie,
)
from tuvi_api.auth.email import reset_password_email, send_email_logged, verification_email
from tuvi_api.auth.passwords import (
    hash_password,
    hash_token,
    new_token,
    verify_better_auth_password,
    verify_password,
)
from tuvi_api.auth.rate_limit import RateLimiter
from tuvi_api.auth.settings import AuthSettings
from tuvi_api.auth.store import (
    EmailTakenError,
    MongoAuthStore,
    TokenPurpose,
    UserRecord,
    normalize_email,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

Store = Annotated[MongoAuthStore, Depends(get_auth_store)]
Settings = Annotated[AuthSettings, Depends(get_auth_settings)]
Limiter = Annotated[RateLimiter, Depends(get_rate_limiter)]

# Compared against when the email is unknown, so a failed login takes the same
# time whether or not the account exists.
_DUMMY_PASSWORD_HASH = hash_password(secrets.token_urlsafe(16))


def _email(value: str) -> str:
    value = value.strip()
    local, _, domain = value.partition("@")
    if not local or "." not in domain or " " in value:
        raise ValueError("Invalid email address.")
    return value


class UserPayload(BaseModel):
    id: str
    email: str
    name: str
    role: str


class SessionResponse(BaseModel):
    user: UserPayload | None
    google_enabled: bool


class UserResponse(BaseModel):
    user: UserPayload


class RegisterRequest(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=2, max_length=80)

    _check_email = field_validator("email")(_email)

    @field_validator("name")
    @classmethod
    def _strip_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Name must have at least 2 characters.")
        return value


class LoginRequest(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=128)


class EmailRequest(BaseModel):
    email: str = Field(max_length=254)

    _check_email = field_validator("email")(_email)


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=8, max_length=128)


def _payload(user: UserRecord) -> UserPayload:
    return UserPayload(id=user.id, email=user.email, name=user.name, role=user.role)


@router.get("/session", response_model=SessionResponse)
async def session(
    store: Store,
    settings: Settings,
    user_id: Annotated[str | None, Depends(current_user_id)],
) -> SessionResponse:
    user = await store.get_user(user_id) if user_id else None
    return SessionResponse(
        user=_payload(user) if user else None,
        google_enabled=settings.google_enabled,
    )


@router.post("/register", status_code=202)
async def register(
    payload: RegisterRequest,
    background: BackgroundTasks,
    store: Store,
    settings: Settings,
    limiter: Limiter,
) -> dict[str, str]:
    """Create the account and email a verification link. No session until verified."""
    limiter.check(f"register:{normalize_email(payload.email)}", limit=5, window_seconds=600)
    try:
        user = await store.create_user(
            email=payload.email,
            name=payload.name,
            password_hash=await run_in_threadpool(hash_password, payload.password),
        )
    except EmailTakenError as exc:
        raise HTTPException(status_code=409, detail="Email is already registered.") from exc
    await _send_verification(user, background, store, settings)
    return {"status": "verification_sent"}


@router.post("/login", response_model=UserResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    store: Store,
    settings: Settings,
    limiter: Limiter,
) -> UserResponse:
    limiter.check(f"login:{normalize_email(payload.email)}", limit=10, window_seconds=300)
    user = await store.find_by_email(payload.email)
    if not await _password_matches(user, payload.password, store):
        raise HTTPException(status_code=401, detail="Wrong email or password.")
    assert user is not None
    # Checked only after the password matched, so it does not reveal accounts.
    if not user.email_verified:
        raise HTTPException(status_code=403, detail="Email is not verified.")
    await _start_session(response, user, store, settings)
    return UserResponse(user=_payload(user))


@router.post("/logout", status_code=204)
async def logout(request: Request, store: Store, settings: Settings) -> Response:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        await store.delete_session(hash_token(token))
    response = Response(status_code=204)
    clear_session_cookie(response, settings)
    return response


@router.post("/verification-email", status_code=202)
async def resend_verification(
    payload: EmailRequest,
    background: BackgroundTasks,
    store: Store,
    settings: Settings,
    limiter: Limiter,
) -> dict[str, str]:
    """Always 202, so the answer does not reveal whether the email has an account."""
    limiter.check(f"verify:{normalize_email(payload.email)}", limit=3, window_seconds=600)
    user = await store.find_by_email(payload.email)
    if user is not None and not user.email_verified:
        await _send_verification(user, background, store, settings)
    return {"status": "verification_sent"}


@router.get("/verify-email")
async def verify_email(token: str, store: Store, settings: Settings) -> Response:
    """The link in the verification email. Verifies, signs in, and opens /login."""
    user_id = await store.consume_token(
        token_hash=hash_token(token), purpose="verify_email", now=datetime.now(UTC)
    )
    user = await store.get_user(user_id) if user_id else None
    if user is None:
        return RedirectResponse(f"{settings.public_url}/login?error=INVALID_TOKEN", 302)
    await store.mark_email_verified(user.id)
    # /login sends a signed-in user on to their saved charts.
    response = RedirectResponse(f"{settings.public_url}/login", 302)
    await _start_session(response, user, store, settings)
    return response


@router.post("/forgot-password", status_code=202)
async def forgot_password(
    payload: EmailRequest,
    background: BackgroundTasks,
    store: Store,
    settings: Settings,
    limiter: Limiter,
) -> dict[str, str]:
    """Always 202, so the answer does not reveal whether the email has an account."""
    limiter.check(f"reset:{normalize_email(payload.email)}", limit=3, window_seconds=600)
    user = await store.find_by_email(payload.email)
    if user is not None:
        token = await _new_link_token(user, "reset_password", store, settings)
        url = f"{settings.public_url}/reset-password?token={token}"
        background.add_task(
            send_email_logged,
            settings,
            reset_password_email(to=user.email, name=user.name, url=url),
        )
    return {"status": "reset_sent"}


@router.post("/reset-password", status_code=204)
async def reset_password(payload: ResetPasswordRequest, store: Store) -> Response:
    user_id = await store.consume_token(
        token_hash=hash_token(payload.token), purpose="reset_password", now=datetime.now(UTC)
    )
    if user_id is None or await store.get_user(user_id) is None:
        raise HTTPException(status_code=400, detail="INVALID_TOKEN")
    await store.set_password(user_id, await run_in_threadpool(hash_password, payload.password))
    # The link reached this person's inbox, so the email is theirs.
    await store.mark_email_verified(user_id)
    await store.delete_user_sessions(user_id)
    return Response(status_code=204)


@router.get("/google/start")
async def google_start(settings: Settings) -> Response:
    if not settings.google_enabled:
        raise HTTPException(status_code=404, detail="Google sign-in is not configured.")
    state = secrets.token_urlsafe(24)
    response = RedirectResponse(google.authorize_url(settings, state=state), status_code=302)
    response.set_cookie(
        OAUTH_STATE_COOKIE,
        state,
        max_age=600,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/api/v1/auth/google",
    )
    return response


@router.get("/google/callback")
async def google_callback(
    request: Request,
    store: Store,
    settings: Settings,
    code: str | None = None,
    state: str | None = None,
) -> Response:
    expected_state = request.cookies.get(OAUTH_STATE_COOKIE)
    failure = RedirectResponse(f"{settings.public_url}/login?error=google", status_code=302)
    if not settings.google_enabled or not code or not state or not expected_state:
        return failure
    if not secrets.compare_digest(state, expected_state):
        return failure
    try:
        identity = await google.exchange_code(settings, code=code)
    except Exception:  # network errors as well as GoogleAuthError
        logger.exception("Google sign-in failed")
        return failure

    try:
        user = await store.upsert_google_user(
            google_sub=identity.sub,
            email=identity.email,
            name=identity.display_name or "",
        )
    except PyMongoError:
        logger.exception("Google sign-in could not save the account")
        return failure
    # /login sends a signed-in user on to their saved charts.
    response = RedirectResponse(f"{settings.public_url}/login", status_code=302)
    response.delete_cookie(OAUTH_STATE_COOKIE, path="/api/v1/auth/google")
    await _start_session(response, user, store, settings)
    return response


async def _password_matches(user: UserRecord | None, password: str, store: MongoAuthStore) -> bool:
    # Hashing takes tens of ms of CPU; in a thread it does not stall other requests.
    if user is None:
        await run_in_threadpool(verify_password, password, _DUMMY_PASSWORD_HASH)
        return False
    if user.password_hash is not None:
        return await run_in_threadpool(verify_password, password, user.password_hash)
    # An account from before the API owned login: check the Better Auth hash
    # once, then keep an Argon2 hash so the old one is not needed again.
    legacy_hash = await store.legacy_password_hash(user.id)
    if legacy_hash is None:
        await run_in_threadpool(verify_password, password, _DUMMY_PASSWORD_HASH)
        return False
    if not await run_in_threadpool(verify_better_auth_password, password, legacy_hash):
        return False
    await store.set_password(user.id, await run_in_threadpool(hash_password, password))
    return True


async def _new_link_token(
    user: UserRecord, purpose: TokenPurpose, store: MongoAuthStore, settings: AuthSettings
) -> str:
    token = new_token()
    await store.create_token(
        user_id=user.id,
        purpose=purpose,
        token_hash=hash_token(token),
        expires_at=datetime.now(UTC) + timedelta(minutes=settings.link_minutes),
    )
    return token


async def _send_verification(
    user: UserRecord,
    background: BackgroundTasks,
    store: MongoAuthStore,
    settings: AuthSettings,
) -> None:
    token = await _new_link_token(user, "verify_email", store, settings)
    url = f"{settings.public_url}/api/v1/auth/verify-email?token={token}"
    # Sent after the response, so the request takes the same time for any email.
    background.add_task(
        send_email_logged,
        settings,
        verification_email(to=user.email, name=user.name, url=url),
    )


async def _start_session(
    response: Response, user: UserRecord, store: MongoAuthStore, settings: AuthSettings
) -> None:
    token = new_token()
    await store.create_session(
        user_id=user.id,
        token_hash=hash_token(token),
        expires_at=datetime.now(UTC) + timedelta(days=settings.session_days),
    )
    set_session_cookie(response, token, settings)
