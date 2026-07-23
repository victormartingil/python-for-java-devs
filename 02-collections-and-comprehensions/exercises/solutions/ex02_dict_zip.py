"""SOLUTION 02-02 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""


def to_lookup(ids: list[int], names: list[str]) -> dict[int, str]:
    return {user_id: name for user_id, name in zip(ids, names, strict=True)}


def invert(lookup: dict[int, str]) -> dict[str, int]:
    return {name: user_id for user_id, name in lookup.items()}
