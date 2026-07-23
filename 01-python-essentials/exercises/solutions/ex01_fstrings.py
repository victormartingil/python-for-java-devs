"""SOLUTION 01-01 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""


def format_user_badge(username: str, score: float, rank: int) -> str:
    return f"{username} | score: {score:.1f} | rank: #{rank:03d}"
