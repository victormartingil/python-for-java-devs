"""Spec for ex04_protocol — make these pass."""

from ex04_protocol import DictStorageGateway, StorageGateway, fetch_or_default


def test_put_then_get_roundtrip() -> None:
    gateway = DictStorageGateway()
    gateway.put("lang", "python")
    assert gateway.get("lang") == "python"


def test_get_unknown_key_returns_none() -> None:
    assert DictStorageGateway().get("missing") is None


def test_put_overwrites() -> None:
    gateway = DictStorageGateway()
    gateway.put("lang", "java")
    gateway.put("lang", "python")
    assert gateway.get("lang") == "python"


def test_satisfies_the_protocol_structurally() -> None:
    # Typed as the Protocol: only the shape matters, not the class name.
    gateway: StorageGateway = DictStorageGateway()
    gateway.put("k", "v")
    assert fetch_or_default(gateway, "k", "<none>") == "v"
    assert fetch_or_default(gateway, "absent", "<none>") == "<none>"


def test_instances_are_independent() -> None:
    first, second = DictStorageGateway(), DictStorageGateway()
    first.put("k", "v")
    assert second.get("k") is None
