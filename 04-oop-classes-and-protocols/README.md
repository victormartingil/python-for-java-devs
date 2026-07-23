# 04 — OOP, classes & protocols

**Goal:** Python has classes, but not Java's ceremony — and `typing.Protocol` gives you interfaces without the `implements`. This module holds the single most important idea for module 11 (architecture).

## Classes without ceremony

```python
class Task:
    def __init__(self, title: str, estimate: int = 1) -> None:  # the constructor
        self.title = title          # no field declarations needed — assign and it exists
        self.estimate = estimate
```

- `self` is explicit, always the first parameter (it's `this`, but you type it).
- No `new`, no access modifiers. "Private" is `_leading_underscore` by convention — like package-private, but by honor system.
- Everything is public-ish. Java devs find this alarming for a week; then they notice Python codebases survive.

## Dunder methods ≈ Object methods

| Python | Java |
|---|---|
| `__init__` | constructor |
| `__str__` | `toString()` |
| `__repr__` | debug `toString()` — aim for "looks like the constructor call" |
| `__eq__` (+ `__hash__`) | `equals()` / `hashCode()` |
| `__enter__` / `__exit__` | `AutoCloseable` (module 05) |
| `__len__`, `__getitem__` | implementing `Collection`, array access |

## `@dataclass` ≈ Lombok / records

```python
@dataclass
class Task:
    title: str
    estimate: int = 1          # default, like a record with a compact constructor
```

Generates `__init__`, `__repr__`, `__eq__` for free — `@Data` without the annotation processor. Variants: `@dataclass(frozen=True)` ≈ a real `record` (immutable, hashable); `@dataclass(slots=True)` for memory. Pydantic `BaseModel` (module 08) is the same idea + validation, for API boundaries.

## Properties ≈ getters, without the boilerplate

```python
@property
def is_big(self) -> bool:
    return self.estimate >= 5
```

Called as `task.is_big` — no parens, like a field. You can start with a plain attribute and *later* turn it into a computed property without breaking callers. This is why Python doesn't pre-write getters "just in case".

## Inheritance & `super()`

Works like Java, minus interfaces and `abstract` ceremony (there's `abc.ABC` if you want it, but read on — you usually don't).

## ⭐ `typing.Protocol` — structural interfaces

Here's the mental shift. In Java, decoupling requires a *nominal* contract: `class SlackNotifier implements Notifier`. The interface must exist first, and the class must name it.

Python flips it: **`Protocol` defines the shape; any class with a matching method satisfies it — without importing or naming the protocol.**

```python
class Notifier(Protocol):
    def send(self, recipient: str, message: str) -> None: ...

class SlackNotifier:              # no `implements`, no import of Notifier
    def send(self, recipient: str, message: str) -> None: ...

def notify_all(notifiers: list[Notifier], msg: str) -> None:  # type-checked!
```

`SlackNotifier` is a valid `Notifier` *because it walks like one* — duck typing, but verified by mypy at check time. This is why Python codebases decouple without interface files everywhere, and why module 11 can swap Postgres ↔ in-memory repositories using only dependency injection: the "port" is just a Protocol (or even an informal shape), the "adapter" is any object that matches.

When you still want nominal contracts (a public library API, a big team), Protocol supports explicit inheritance too. The structural option is just... free.

## Run it

```bash
uv run python 04-oop-classes-and-protocols/notifiers.py
uv run pytest 04-oop-classes-and-protocols/tests
```

## Common pitfalls for Java devs

- Forgetting `self` in a method signature → `TypeError: takes 1 positional argument but 2 were given`. Everyone hits this once.
- Class attributes vs instance attributes: `tags = []` at class level is **shared by all instances** (≈ static) — same trap as mutable defaults, different costume.
- Reaching for `abc.ABC` + `@abstractmethod` out of habit. Fine when you need it — but Protocol is the idiomatic 2026 answer.

## Dig deeper

- `typing.Protocol` docs: <https://docs.python.org/3/library/typing.html#typing.Protocol>
- dataclasses docs: <https://docs.python.org/3/library/dataclasses.html>
