"""Password hashing (Argon2id via pwdlib) + JWT (PyJWT) — module 09's stack, verbatim.

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn app.main:app --reload   (from 11-project-architecture/)
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()  # Argon2id


def hash_password(plain: str) -> str:
    return password_hasher.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return password_hasher.verify(plain, hashed)


def create_access_token(
    *, subject: str, secret_key: str, algorithm: str, expires_minutes: int
) -> str:
    now = datetime.now(UTC)
    payload = {"sub": subject, "iat": now, "exp": now + timedelta(minutes=expires_minutes)}
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_access_token(token: str, *, secret_key: str, algorithm: str) -> dict[str, Any]:
    """Verify signature + expiry. Algorithms always pinned explicitly.
    Raises jwt.exceptions.InvalidTokenError."""
    return jwt.decode(token, secret_key, algorithms=[algorithm])
