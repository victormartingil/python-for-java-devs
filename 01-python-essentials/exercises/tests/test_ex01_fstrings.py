"""Spec for ex01_fstrings — make these pass."""

from ex01_fstrings import format_user_badge


def test_badge_exact_format() -> None:
    assert format_user_badge("ada", 9.456, 7) == "ada | score: 9.5 | rank: #007"


def test_badge_rounds_score_to_one_decimal() -> None:
    assert format_user_badge("grace", 9.44, 12) == "grace | score: 9.4 | rank: #012"


def test_badge_pads_rank_to_three_digits() -> None:
    assert format_user_badge("linus", 10.0, 3) == "linus | score: 10.0 | rank: #003"


def test_badge_rank_beyond_padding_is_not_truncated() -> None:
    assert format_user_badge("edsger", 7.0, 1234) == "edsger | score: 7.0 | rank: #1234"
