"""SOLUTION 01-03 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""


def retry_decision(status_code: int) -> str:
    match status_code:
        case 200 | 201 | 204:
            return "ok"
        case 429:
            return "retry after delay"
        case 500 | 502 | 503 | 504:
            return "retry"
        case c if 400 <= c < 500:
            return "fail fast"
        case _:
            return "unknown"
