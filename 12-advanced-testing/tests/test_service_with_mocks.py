"""unittest.mock deep-dive ≈ the Mockito toolbox, applied to module 11's service.

JUnit/Mockito mapping for this file:
    @Mock TaskRepository repo;            → repo = AsyncMock(spec=TaskRepository)
    when(repo.get(1)).thenReturn(task)    → repo.get.return_value = record
    when(...).thenThrow(...)              → repo.get.side_effect = SomeError()
    verify(repo).delete(1)                → repo.delete.assert_awaited_once_with(1)
    verifyNoMoreInteractions(repo)        → (no direct equivalent — assert on mock_calls)
    @InjectMocks TaskService service;     → service = TaskService(repo)   (plain constructor!)

Key difference from Mockito: there is no mock *framework* creating proxies for
you. A Mock is just a Python object that records every attribute access and
call. Async methods need AsyncMock (awaiting a plain Mock returns a Mock, not
the value — the #1 Mockito-to-Python migration bug).
"""

from unittest.mock import AsyncMock, Mock, call, patch

import pytest
from app.core.exceptions import NotFoundError
from app.tasks.repository import TaskRecord, TaskRepository
from app.tasks.schemas import TaskCreate, TaskUpdate
from app.tasks.service import TaskService

# --- stubbing: return_value -------------------------------------------------


async def test_get_returns_stubbed_record() -> None:
    """when(repo.get(1)).thenReturn(record) — stubbing a single method."""
    repo = AsyncMock(spec=TaskRepository)
    record = TaskRecord(id=1, title="Write module 12", description=None, completed=False)
    repo.get.return_value = record

    service = TaskService(repo)
    result = await service.get(1)

    assert result.title == "Write module 12"
    repo.get.assert_awaited_once_with(1)  # verify(repo, times(1)).get(1)


async def test_get_missing_raises_domain_error() -> None:
    """The service translates repo returning None into NotFoundError (→ 404)."""
    repo = AsyncMock(spec=TaskRepository)
    repo.get.return_value = None

    with pytest.raises(NotFoundError):
        await TaskService(repo).get(999)


async def test_list_maps_every_record_to_response() -> None:
    repo = AsyncMock(spec=TaskRepository)
    repo.list.return_value = [
        TaskRecord(id=1, title="a", description=None, completed=False),
        TaskRecord(id=2, title="b", description="d", completed=True),
    ]

    results = await TaskService(repo).list(completed=True)

    assert [r.title for r in results] == ["a", "b"]
    repo.list.assert_awaited_once_with(completed=True)


# --- call verification -------------------------------------------------------


async def test_update_passes_the_dto_through_unmodified() -> None:
    """Capture the argument and inspect it — ≈ Mockito's ArgumentCaptor."""
    repo = AsyncMock(spec=TaskRepository)
    repo.update.return_value = TaskRecord(id=7, title="new", description=None, completed=True)

    await TaskService(repo).update(7, TaskUpdate(title="new", completed=True))

    repo.update.assert_awaited_once()
    task_id, dto = repo.update.await_args.args  # ArgumentCaptor.getValue()
    assert task_id == 7
    assert dto.title == "new" and dto.completed is True
    assert dto.description is None  # exclude_unset must keep it untouched


async def test_full_flow_verifies_call_order() -> None:
    """verify(inOrder(...)) — mock_calls records the whole conversation."""
    repo = AsyncMock(spec=TaskRepository)
    repo.create.return_value = TaskRecord(id=1, title="x", description=None, completed=False)
    repo.delete.return_value = True

    service = TaskService(repo)
    await service.create(TaskCreate(title="x"))
    await service.delete(1)

    assert repo.mock_calls == [
        call.create(TaskCreate(title="x")),
        call.delete(1),
    ]


# --- side_effect: exceptions and sequences ------------------------------------


async def test_side_effect_exception_propagates() -> None:
    """when(...).thenThrow(...) — the repo is down; the service must not hide it."""
    repo = AsyncMock(spec=TaskRepository)
    repo.list.side_effect = ConnectionError("database is gone")

    with pytest.raises(ConnectionError, match="database is gone"):
        await TaskService(repo).list()


async def test_side_effect_sequence_simulates_flaky_dependency() -> None:
    """when(...).thenReturn(a).thenThrow(...) — a different result per call."""
    repo = AsyncMock(spec=TaskRepository)
    repo.get.side_effect = [
        None,  # first call: not found
        TaskRecord(id=1, title="appeared", description=None, completed=False),
    ]
    service = TaskService(repo)

    with pytest.raises(NotFoundError):
        await service.get(1)
    assert (await service.get(1)).title == "appeared"
    assert repo.get.await_count == 2


# --- patch: replacing collaborators at their import location ------------------

NOTIFY = "notify"  # module under test for the patching examples


def test_patch_replaces_the_function_where_it_is_USED() -> None:
    """The golden rule of patch(): patch where the name is LOOKED UP, not where
    it's defined. Here both are the same module; with `from x import y` you'd
    patch "consumer_module.y" — the Python equivalent of injecting the mock."""
    import notify

    with patch("notify.post_webhook", return_value=200) as fake_http:
        result = notify.send_completion_notice("https://hooks.example.test/x", "Deploy")

    assert result == "sent"
    fake_http.assert_called_once_with("https://hooks.example.test/x", "Task completed: Deploy")


def test_patch_object_and_error_branch() -> None:
    """patch.object is the same thing with a direct reference (refactor-safe)."""
    import notify

    with patch.object(notify, "post_webhook", return_value=500):
        with pytest.raises(notify.NotificationError, match="500"):
            notify.send_completion_notice("https://hooks.example.test/x", "Deploy")


def test_plain_mock_for_sync_collaborators() -> None:
    """Not everything is async: Mock (not AsyncMock) for plain callables."""
    formatter = Mock(spec=str.upper)
    formatter.return_value = "DEPLOY"

    assert formatter("deploy") == "DEPLOY"
    formatter.assert_called_once_with("deploy")
