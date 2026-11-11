from __future__ import annotations

from pydantic import BaseModel, Field


class AuthSettings(BaseModel):
    # Public URL of the web app, as the browser sees it. The API is served under
    # the same origin through the web app's /api rewrite, so email links and the
    # Google redirect use this URL.
    base_url: str = "http://localhost:3000"
    mongo_uri: str = "mongodb://localhost:27017"
    database_name: str = "tuvilm"
    session_days: int = Field(default=30, gt=0)
    # Email verification and password reset links stay valid this long.
    link_minutes: int = Field(default=60, gt=0)
    google_client_id: str | None = None
    google_client_secret: str | None = None
    # Mail is sent through Resend. Without a key, the API logs the mail (and its
    # link) instead. On https the API does not start without them.
    resend_api_key: str | None = None
    email_from: str | None = None

    @property
    def public_url(self) -> str:
        return self.base_url.rstrip("/")

    @property
    def cookie_secure(self) -> bool:
        return self.base_url.startswith("https://")

    @property
    def google_enabled(self) -> bool:
        return bool(self.google_client_id and self.google_client_secret)

    @property
    def google_redirect_uri(self) -> str:
        return f"{self.public_url}/api/v1/auth/google/callback"

    @property
    def email_enabled(self) -> bool:
        return bool(self.resend_api_key and self.email_from)
