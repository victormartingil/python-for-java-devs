from collections_demo import (
    TASKS,
    counts_by_priority,
    titles_by_status,
    urgent_titles_java_style,
    urgent_titles_pythonic,
)


def test_both_styles_agree() -> None:
    assert urgent_titles_java_style(TASKS) == urgent_titles_pythonic(TASKS)


def test_pythonic_result() -> None:
    # estimate 5 before 3 on ties? No — stable sort keeps input order within ties.
    assert urgent_titles_pythonic(TASKS) == ["FIX LOGIN", "ADD TESTS", "WRITE DOCS"]


def test_counts_by_priority() -> None:
    assert counts_by_priority(TASKS) == {"high": 4, "low": 1}


def test_titles_by_status() -> None:
    grouped = titles_by_status(TASKS)
    assert grouped[True] == ["ship release"]
    assert set(grouped[False]) == {"write docs", "fix login", "refactor dao", "add tests"}
