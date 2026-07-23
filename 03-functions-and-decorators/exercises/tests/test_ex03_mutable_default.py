"""Spec for ex03_mutable_default — make these pass."""

from ex03_mutable_default import add_item


def test_calls_without_cart_are_independent() -> None:
    first = add_item("milk")
    second = add_item("eggs")
    assert first == ["milk"]
    assert second == ["eggs"], "state leaked between calls — the mutable default trap"


def test_explicit_cart_is_appended_in_place() -> None:
    cart = ["milk"]
    result = add_item("eggs", cart)
    assert cart == ["milk", "eggs"], "the caller's list must see the change"
    assert result is cart, "same object — identity, not a copy"
