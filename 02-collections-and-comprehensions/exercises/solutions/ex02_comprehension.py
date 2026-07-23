"""SOLUTION 02-01 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

from typing import TypedDict


class User(TypedDict):
    name: str
    email: str
    active: bool


def urgent_emails_loop(users: list[User]) -> list[str]:
    """The day-one Java port: temp list, loop, condition, append, sort. It works.

    Note the normalization: lowercase BEFORE comparing — domains are
    case-insensitive ("DAN@EXAMPLE.COM" must match too).
    """
    result = []
    for user in users:
        if user["active"] and user["email"].lower().endswith("@example.com"):
            result.append(user["email"].lower())
    return sorted(result)


def urgent_emails(users: list[User]) -> list[str]:
    return sorted(
        user["email"].lower()
        for user in users
        if user["active"] and user["email"].lower().endswith("@example.com")
    )
