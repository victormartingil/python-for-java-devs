"""Exercise 01-03 — match/case: switch expressions with OR patterns and guards.

Implement retry_decision. The tests are the spec:

    uv run pytest 01-python-essentials/exercises -v

Anchor: Java 21 switch expressions — but `case` also takes OR patterns
(200 | 201) and guards (case c if c >= 500). See classify_http_status
in 01-python-essentials/tour.py.
"""


def retry_decision(status_code: int) -> str:
    """Map an HTTP response status to a client retry action:

    - 200, 201 or 204          -> "ok"
    - 429                      -> "retry after delay"
    - 500, 502, 503 or 504     -> "retry"
    - any other 4xx            -> "fail fast"   (use a guard: 400 <= c < 500)
    - anything else            -> "unknown"

    Use match/case, not an if/elif ladder.
    """
    raise NotImplementedError("TODO(ex03): match/case with OR patterns and a guard")
