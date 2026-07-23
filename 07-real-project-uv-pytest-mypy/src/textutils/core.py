"""Core text utilities. Fully type-annotated: mypy runs with
disallow_untyped_defs = true, and that's the house style for real projects.
"""

import re

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    """'Hello, World!' -> 'hello-world'. Locale-naive on purpose: demo code."""
    return _NON_ALNUM.sub("-", text.lower()).strip("-")


def word_count(text: str) -> int:
    """Count whitespace-separated words. Empty string -> 0."""
    return len(text.split())


def truncate(text: str, max_length: int, *, ellipsis: str = "…") -> str:
    """Shorten text to max_length chars including the ellipsis.

    Note the `*`: `ellipsis` is keyword-only (impossible to express in Java).
    """
    if max_length < len(ellipsis):
        raise ValueError(f"max_length must be >= {len(ellipsis)}")
    if len(text) <= max_length:
        return text
    return text[: max_length - len(ellipsis)] + ellipsis
