"""Spec for ex02_comprehension — make these pass."""

from ex02_comprehension import User, urgent_emails, urgent_emails_loop

USERS: list[User] = [
    {"name": "Ada", "email": "ADA@example.com", "active": True},
    {"name": "Bob", "email": "bob@other.org", "active": True},
    {"name": "Cleo", "email": "cleo@example.com", "active": False},
    {"name": "Dan", "email": "DAN@EXAMPLE.COM", "active": True},
]


def test_matches_the_loop_version() -> None:
    assert urgent_emails(USERS) == urgent_emails_loop(USERS)


def test_exact_result() -> None:
    # filtered (active + domain), lowercased, sorted
    assert urgent_emails(USERS) == ["ada@example.com", "dan@example.com"]


def test_empty_input() -> None:
    assert urgent_emails([]) == []


def test_result_is_a_fresh_list() -> None:
    # Mutating the result must not corrupt the next call's result.
    urgent_emails(USERS).clear()
    assert urgent_emails(USERS) == ["ada@example.com", "dan@example.com"]
