"""Password hashing + JWT with the CURRENT official FastAPI stack.

- Hashing: pwdlib with Argon2id — the algorithm OWASP recommends today.
- Tokens:  PyJWT, with `algorithms` always pinned explicitly.

⚠️ NOT python-jose (unmaintained, CVE-2024-33663) and NOT passlib
(no release since 2020, broken with bcrypt >= 5). See the README warning box.

Run the API:  uv run uvicorn secureapp.main:app --reload   (from 09-fastapi-pro-di-auth-config/)
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

# PasswordHash.recommended() = Argon2id with sane defaults. One instance, reused.
password_hasher = PasswordHash.recommended()


def hash_password(plain: str) -> str:
    return password_hasher.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return password_hasher.verify(plain, hashed)


def create_access_token(
    *, subject: str, secret_key: str, algorithm: str, expires_minutes: int
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,  # JWT standard claim: the principal (≈ UserDetails.getUsername())
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_access_token(token: str, *, secret_key: str, algorithm: str) -> dict[str, Any]:
    """Verify signature + expiry and return the claims.

    `algorithms=[...]` is pinned EXPLICITLY — decoding without it is the
    classic algorithm-confusion vulnerability. Raises jwt.exceptions.InvalidTokenError
    (covers expired, bad signature, malformed) — one exception type to catch.
    """
    return jwt.decode(token, secret_key, algorithms=[algorithm])
