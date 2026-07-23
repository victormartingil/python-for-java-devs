"""Spec for ex02_dict_zip — make these pass."""

import pytest
from ex02_dict_zip import invert, to_lookup


def test_to_lookup_pairs_in_order() -> None:
    assert to_lookup([1, 2, 3], ["ada", "grace", "linus"]) == {1: "ada", 2: "grace", 3: "linus"}


def test_to_lookup_rejects_mismatched_lengths() -> None:
    # zip(strict=True) raises instead of silently dropping the extra name.
    with pytest.raises(ValueError):
        to_lookup([1, 2], ["ada", "grace", "linus"])


def test_invert_swaps_keys_and_values() -> None:
    assert invert({1: "ada", 2: "grace"}) == {"ada": 1, "grace": 2}


def test_invert_empty() -> None:
    assert invert({}) == {}
