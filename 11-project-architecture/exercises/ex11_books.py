"""Exercise 11-02 — implement the adapter yourself.

Module 11's payoff: the service depends on a Protocol (the "port"), and any
object with the right shape plugs in (the "adapter"). BookRepository and
BookService are given — you write InMemoryBookRepository, the test adapter,
in a fresh domain so you produce the pattern instead of copying it.

    uv run pytest 11-project-architecture/exercises -v

Hint: InMemoryTaskRepository in ex11_repository.py (and module 11's
app/tasks/repository.py) is the same pattern, already solved.
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
    """TODO(ex02): the adapter you are writing — a dict-backed BookRepository.

    Ids start at 1 and increment. list() returns books in insertion (id) order.
    Do NOT inherit from BookRepository — the match is structural.
    The __init__ is given; the four methods are yours.
    """

    def __init__(self) -> None:
        self._rows: dict[int, BookRecord] = {}
        self._next_id: int = 1

    async def create(self, isbn: str, title: str) -> BookRecord:
        raise NotImplementedError("TODO(ex02): build the record, store it, return it")

    async def list(self) -> Sequence[BookRecord]:
        raise NotImplementedError("TODO(ex02): all records, in id order")

    async def get_by_isbn(self, isbn: str) -> BookRecord | None:
        raise NotImplementedError("TODO(ex02): first record whose isbn matches, else None")

    async def delete(self, book_id: int) -> bool:
        raise NotImplementedError("TODO(ex02): True when a row was removed, else False")
