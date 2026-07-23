"""pytest for Java devs: fixtures ≈ @BeforeEach, parametrize ≈ @ParameterizedTest.

Note what's NOT here: no test class, no annotations on test methods,
no assertion library — plain functions and plain `assert`.
"""

import pytest
from textutils import slugify, truncate, word_count


# --- Fixtures ≈ @BeforeEach (+ DI into the test by parameter name) -----------
@pytest.fixture
def sample_text() -> str:
    """A fixture: pytest calls it and injects the result wherever a test
    declares a parameter with the same name. Fresh instance per test by default."""
    return "The Quick Brown Fox"


def test_word_count_with_fixture(sample_text: str) -> None:
    assert word_count(sample_text) == 4


def test_word_count_empty() -> None:
    assert word_count("") == 0


# --- Parametrize ≈ @ParameterizedTest with @CsvSource -------------------------
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Hello World", "hello-world"),
        ("Hello, World!", "hello-world"),
        ("  spaces  everywhere  ", "spaces-everywhere"),
        ("Already-a-slug", "already-a-slug"),
        ("", ""),
    ],
)
def test_slugify_cases(raw: str, expected: str) -> None:
    assert slugify(raw) == expected


# --- Markers ≈ @Tag -----------------------------------------------------------
@pytest.mark.slow
def test_word_count_on_large_input() -> None:
    # Deselect with: uv run pytest -m "not slow"
    assert word_count("word " * 100_000) == 100_000


# --- Exceptions: assertRaises, one line ---------------------------------------
def test_truncate_rejects_tiny_max_length() -> None:
    with pytest.raises(ValueError, match="max_length"):
        truncate("hello", 0)


def test_truncate_shortens_and_keeps_short_text() -> None:
    assert truncate("hello world", 8) == "hello w…"
    assert truncate("hi", 8) == "hi"
