"""Password hashing and one-time tokens."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import unicodedata

from pwdlib import PasswordHash

_password_hash = PasswordHash.recommended()

# Better Auth's scrypt parameters, for accounts created before the API owned login.
_SCRYPT_N = 16384
_SCRYPT_R = 16
_SCRYPT_P = 1
_SCRYPT_KEY_LENGTH = 64


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _password_hash.verify(password, password_hash)


def verify_better_auth_password(password: str, stored: str) -> bool:
    """Check a Better Auth hash: "<hex salt>:<hex scrypt key>".

    Better Auth uses the hex salt string itself (not its bytes) as the salt.
    """
    salt, _, key = stored.partition(":")
    if not salt or not key:
        return False
    derived = hashlib.scrypt(
        unicodedata.normalize("NFKC", password).encode(),
        salt=salt.encode(),
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=_SCRYPT_KEY_LENGTH,
        maxmem=128 * _SCRYPT_N * _SCRYPT_R * 2,
    )
    return hmac.compare_digest(derived.hex(), key)


def new_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Only the hash is stored, so a database leak does not expose live tokens."""
    return hashlib.sha256(token.encode()).hexdigest()
