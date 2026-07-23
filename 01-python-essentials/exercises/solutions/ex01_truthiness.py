"""SOLUTION 01-02 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""


def resolve_limit(configured: int | None, default: int) -> int:
    return configured if configured is not None else default


def describe_queue(pending: list[str]) -> str:
    if pending:
        return f"{len(pending)} pending"
    return "queue is empty"
