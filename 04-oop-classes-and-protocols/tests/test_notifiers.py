from notifiers import EmailNotifier, Notifier, SlackNotifier, Task, TaskBoard, notify_all


def test_notify_all_dispatches_structurally() -> None:
    notifiers: list[Notifier] = [EmailNotifier(), SlackNotifier()]
    receipts = notify_all(notifiers, "oncall@example.com", "hello")
    assert receipts[0].startswith("email to oncall@example.com")
    assert "#alerts" in receipts[1]


def test_custom_object_satisfies_protocol_without_inheritance() -> None:
    class SmsNotifier:  # defined here, never heard of Notifier
        def send(self, recipient: str, message: str) -> str:
            return f"sms to {recipient}"

    receipts = notify_all([SmsNotifier()], "123", "hi")  # type: ignore[list-item]
    assert receipts == ["sms to 123"]


def test_task_property_and_equality() -> None:
    big = Task("refactor", estimate=8)
    small = Task("typo", estimate=1)
    assert big.is_big and not small.is_big
    assert Task("x", 1) == Task("x", 1)  # generated __eq__


def test_frozen_task_is_immutable() -> None:
    import dataclasses

    import pytest

    with pytest.raises(dataclasses.FrozenInstanceError):
        Task("x").title = "y"  # type: ignore[misc]


def test_board_default_factory_is_per_instance() -> None:
    a, b = TaskBoard("a"), TaskBoard("b")
    a.add(Task("x"))
    assert len(a.tasks) == 1
    assert len(b.tasks) == 0  # no shared mutable state
    assert str(a) == "TaskBoard('a', 1 tasks)"
