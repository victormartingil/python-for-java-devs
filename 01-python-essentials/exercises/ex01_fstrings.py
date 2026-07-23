"""Exercise 01-01 — f-strings: formatting inline, not String.format().

Implement format_user_badge below. The tests are the spec:

    uv run pytest 01-python-essentials/exercises -v

Hint: see the f-string section of 01-python-essentials/tour.py (§5).
"""


def format_user_badge(username: str, score: float, rank: int) -> str:
    """Return "<username> | score: <score with 1 decimal> | rank: #<rank zero-padded to 3>".

    Java:    String.format("%s | score: %.1f | rank: #%03d", ...)
    Python:  one f-string with format specs — {score:.1f} and {rank:03d}.

    Example: format_user_badge("ada", 9.456, 7) -> "ada | score: 9.5 | rank: #007"
    """
    raise NotImplementedError("TODO(ex01): return the badge as a single f-string")
