"""Exercise 02-01 — comprehension refactor: the loop you wrote vs the line you'll write.

urgent_emails_loop is the Java-style reference (given, working). Rewrite it as
urgent_emails: one comprehension + sorted(). The tests are the spec:

    uv run pytest 02-collections-and-comprehensions/exercises -v

Hint: see urgent_titles_java_style vs urgent_titles_pythonic in
02-collections-and-comprehensions/collections_demo.py.
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
    """Return the lowercased @example.com emails of active users, sorted.

    Java:    users.stream().filter(...).map(...).sorted().toList()
    Python:  one comprehension (filter + map in a single expression),
             then sorted(...) — which returns a new list.
    """
    raise NotImplementedError("TODO(ex01): one comprehension + sorted()")
