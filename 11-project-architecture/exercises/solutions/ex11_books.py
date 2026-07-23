"""SOLUTION 11-02 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol


@dataclass
class BookRecord:
    id: int
    isbn: str
    title: str


class DuplicateIsbnError(Exception):
    """Domain error: the ISBN is already registered."""


class BookNotFoundError(Exception):
    """Domain error: no book with that ISBN."""


class BookRepository(Protocol):
    """The port (given): structural — implementations never name it."""

    async def create(self, isbn: str, title: str) -> BookRecord: ...
    async def list(self) -> Sequence[BookRecord]: ...
    async def get_by_isbn(self, isbn: str) -> BookRecord | None: ...
    async def delete(self, book_id: int) -> bool: ...


class BookService:
    """The consumer (given): framework-free, speaks only the Protocol."""

    def __init__(self, books: BookRepository) -> None:
        self._books = books

    async def register(self, isbn: str, title: str) -> BookRecord:
        if await self._books.get_by_isbn(isbn) is not None:
            raise DuplicateIsbnError(f"isbn {isbn} already registered")
        return await self._books.create(isbn, title)

    async def catalog(self) -> Sequence[BookRecord]:
        return await self._books.list()

    async def lookup(self, isbn: str) -> BookRecord:
        book = await self._books.get_by_isbn(isbn)
        if book is None:
            raise BookNotFoundError(f"isbn {isbn} not found")
        return book


class InMemoryBookRepository:
    def __init__(self) -> None:
        self._rows: dict[int, BookRecord] = {}
        self._next_id: int = 1

    async def create(self, isbn: str, title: str) -> BookRecord:
        record = BookRecord(id=self._next_id, isbn=isbn, title=title)
        self._rows[record.id] = record
        self._next_id += 1
        return record

    async def list(self) -> Sequence[BookRecord]:
        return list(self._rows.values())

    async def get_by_isbn(self, isbn: str) -> BookRecord | None:
        return next((r for r in self._rows.values() if r.isbn == isbn), None)

    async def delete(self, book_id: int) -> bool:
        return self._rows.pop(book_id, None) is not None
