"""Accounts, login sessions and one-time tokens in MongoDB.

Users live in the `user` collection with the field names Better Auth used
(`name`, `emailVerified`, `createdAt`, ...), so accounts made before the API
owned login keep their role, plan and coins. Billing code updates the same
documents with atomic operators, so this store never replaces a whole user.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import DuplicateKeyError

USERS = "user"
SESSIONS = "auth_sessions"
TOKENS = "auth_tokens"
# Better Auth stored password hashes here, one document per login method.
LEGACY_ACCOUNTS = "account"

TokenPurpose = Literal["verify_email", "reset_password"]


class EmailTakenError(Exception):
    """Raised when an account with this email already exists."""


@dataclass(frozen=True, slots=True)
class UserRecord:
    id: str
    email: str
    name: str
    email_verified: bool
    role: Literal["user", "admin"]
    password_hash: str | None


def utc_now() -> datetime:
    # MongoDB stores milliseconds. Round here so values read back are equal.
    now = datetime.now(UTC)
    return now.replace(microsecond=(now.microsecond // 1000) * 1000)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def _object_id(user_id: str) -> ObjectId | None:
    return ObjectId(user_id) if ObjectId.is_valid(user_id) else None


def _record(document: dict[str, Any]) -> UserRecord:
    return UserRecord(
        id=str(document["_id"]),
        email=document["email"],
        name=document.get("name") or "",
        email_verified=document.get("emailVerified") is True,
        role="admin" if document.get("role") == "admin" else "user",
        password_hash=document.get("password_hash"),
    )


_USER_FIELDS = {"email": 1, "name": 1, "emailVerified": 1, "role": 1, "password_hash": 1}


class MongoAuthStore:
    def __init__(self, database: AsyncDatabase) -> None:
        self._db = database

    async def ensure_indexes(self) -> None:
        await self._db[USERS].create_index("email", unique=True)
        await self._db[USERS].create_index(
            "google_sub",
            unique=True,
            partialFilterExpression={"google_sub": {"$type": "string"}},
        )
        await self._db[SESSIONS].create_index("token_hash", unique=True)
        await self._db[SESSIONS].create_index("user_id")
        # MongoDB deletes these documents once expires_at has passed.
        await self._db[SESSIONS].create_index("expires_at", expireAfterSeconds=0)
        await self._db[TOKENS].create_index("token_hash", unique=True)
        await self._db[TOKENS].create_index("expires_at", expireAfterSeconds=0)

    # Users

    async def create_user(
        self,
        *,
        email: str,
        name: str,
        password_hash: str | None,
        email_verified: bool = False,
    ) -> UserRecord:
        now = utc_now()
        document: dict[str, Any] = {
            "email": normalize_email(email),
            "name": name,
            "emailVerified": email_verified,
            "role": "user",
            "plan": "normal",
            "balance": 0,
            "createdAt": now,
            "updatedAt": now,
        }
        if password_hash is not None:
            document["password_hash"] = password_hash
        try:
            result = await self._db[USERS].insert_one(document)
        except DuplicateKeyError as exc:
            raise EmailTakenError(email) from exc
        document["_id"] = result.inserted_id
        return _record(document)

    async def get_user(self, user_id: str) -> UserRecord | None:
        object_id = _object_id(user_id)
        if object_id is None:
            return None
        document = await self._db[USERS].find_one({"_id": object_id}, _USER_FIELDS)
        return _record(document) if document else None

    async def find_by_email(self, email: str) -> UserRecord | None:
        document = await self._db[USERS].find_one(
            {"email": normalize_email(email)}, _USER_FIELDS
        )
        return _record(document) if document else None

    async def legacy_password_hash(self, user_id: str) -> str | None:
        """The Better Auth scrypt hash of an account that has not logged in since."""
        object_id = _object_id(user_id)
        if object_id is None:
            return None
        account = await self._db[LEGACY_ACCOUNTS].find_one(
            {"userId": object_id, "providerId": "credential"}, {"password": 1}
        )
        password = account.get("password") if account else None
        return password if isinstance(password, str) else None

    async def set_password(self, user_id: str, password_hash: str) -> None:
        await self._db[USERS].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password_hash": password_hash, "updatedAt": utc_now()}},
        )

    async def mark_email_verified(self, user_id: str) -> None:
        await self._db[USERS].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"emailVerified": True, "updatedAt": utc_now()}},
        )

    async def upsert_google_user(self, *, google_sub: str, email: str, name: str) -> UserRecord:
        """Find the account by Google id, else link by (verified) email, else create it."""
        now = utc_now()
        document = await self._db[USERS].find_one_and_update(
            {"google_sub": google_sub},
            {"$set": {"emailVerified": True, "updatedAt": now}},
            projection=_USER_FIELDS,
            return_document=ReturnDocument.AFTER,
        )
        if document is None:
            existing = await self._db[USERS].find_one(
                {"email": normalize_email(email)}, {"emailVerified": 1}
            )
            if existing is not None:
                update: dict[str, Any] = {
                    "$set": {"google_sub": google_sub, "emailVerified": True, "updatedAt": now}
                }
                if existing.get("emailVerified") is not True:
                    # Nobody proved they own this email before. Drop the password
                    # so whoever registered it cannot log in to the Google user's account.
                    update["$unset"] = {"password_hash": ""}
                    await self._db[LEGACY_ACCOUNTS].delete_many(
                        {"userId": existing["_id"], "providerId": "credential"}
                    )
                document = await self._db[USERS].find_one_and_update(
                    {"_id": existing["_id"]},
                    update,
                    projection=_USER_FIELDS,
                    return_document=ReturnDocument.AFTER,
                )
        if document is not None:
            return _record(document)
        user = await self.create_user(
            email=email, name=name, password_hash=None, email_verified=True
        )
        await self._db[USERS].update_one(
            {"_id": ObjectId(user.id)}, {"$set": {"google_sub": google_sub}}
        )
        return user

    # Sessions

    async def create_session(self, *, user_id: str, token_hash: str, expires_at: datetime) -> None:
        await self._db[SESSIONS].insert_one(
            {
                "user_id": ObjectId(user_id),
                "token_hash": token_hash,
                "created_at": utc_now(),
                "expires_at": expires_at,
            }
        )

    async def session_user_id(self, token_hash: str, *, now: datetime) -> str | None:
        # The TTL index removes expired sessions only about once a minute.
        session = await self._db[SESSIONS].find_one(
            {"token_hash": token_hash, "expires_at": {"$gt": now}}, {"user_id": 1}
        )
        return str(session["user_id"]) if session else None

    async def delete_session(self, token_hash: str) -> None:
        await self._db[SESSIONS].delete_one({"token_hash": token_hash})

    async def delete_user_sessions(self, user_id: str) -> int:
        result = await self._db[SESSIONS].delete_many({"user_id": ObjectId(user_id)})
        return result.deleted_count

    # One-time tokens

    async def create_token(
        self,
        *,
        user_id: str,
        purpose: TokenPurpose,
        token_hash: str,
        expires_at: datetime,
    ) -> None:
        # A new link replaces the earlier ones for the same purpose.
        await self._db[TOKENS].delete_many({"user_id": ObjectId(user_id), "purpose": purpose})
        await self._db[TOKENS].insert_one(
            {
                "user_id": ObjectId(user_id),
                "purpose": purpose,
                "token_hash": token_hash,
                "expires_at": expires_at,
            }
        )

    async def consume_token(
        self, *, token_hash: str, purpose: TokenPurpose, now: datetime
    ) -> str | None:
        """Delete the token and return its user id, or None if it is unknown or expired."""
        token = await self._db[TOKENS].find_one_and_delete(
            {"token_hash": token_hash, "purpose": purpose}
        )
        if token is None or _aware(token["expires_at"]) <= now:
            return None
        return str(token["user_id"])


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)
