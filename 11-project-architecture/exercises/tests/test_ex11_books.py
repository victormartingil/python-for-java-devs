"""Spec for ex02 (implement the in-memory adapter) — make these pass."""

import pytest
from ex11_books import (
    BookNotFoundError,
    BookService,
    DuplicateIsbnError,
    InMemoryBookRepository,
)


@pytest.fixture
def service() -> BookService:
    return BookService(InMemoryBookRepository())


async def test_register_assigns_ids_in_order(service: BookService) -> None:
    first = await service.register("978-1", "Dune")
    second = await service.register("978-2", "Foundation")
    assert (first.id, second.id) == (1, 2)


async def test_catalog_lists_in_id_order(service: BookService) -> None:
    await service.register("978-1", "Dune")
    await service.register("978-2", "Foundation")
    assert [b.title for b in await service.catalog()] == ["Dune", "Foundation"]


async def test_lookup_by_isbn(service: BookService) -> None:
    await service.register("978-1", "Dune")
    assert (await service.lookup("978-1")).title == "Dune"


async def test_lookup_missing_raises(service: BookService) -> None:
    with pytest.raises(BookNotFoundError):
        await service.lookup("000-0")


async def test_duplicate_isbn_is_rejected(service: BookService) -> None:
    await service.register("978-1", "Dune")
    with pytest.raises(DuplicateIsbnError):
        await service.register("978-1", "Dune: the musical")


async def test_delete_roundtrip() -> None:
    repo = InMemoryBookRepository()
    service = BookService(repo)
    book = await service.register("978-1", "Dune")
    assert await repo.delete(book.id) is True
    assert await repo.delete(book.id) is False
    assert list(await repo.list()) == []
