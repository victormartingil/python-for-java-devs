# 05 — Errors & context managers

**Goal:** two mindset shifts: (1) all exceptions are unchecked, and the culture is EAFP; (2) `with` replaces try-with-resources — and you can write your own in 5 lines.

## Exceptions: the hierarchy without `checked`

Java splits exceptions into checked (must declare/catch) and unchecked. Python has **only unchecked** — nothing is declared, the compiler forces nothing. The hierarchy you actually use:

```
BaseException
├── KeyboardInterrupt, SystemExit      # don't catch these
└── Exception                          # catch from here down
    ├── ValueError, TypeError          # bad data / bad types (≈ IllegalArgumentException)
    ├── KeyError, IndexError           # missing dict key / list index
    ├── RuntimeError                   # generic
    └── OSError (FileNotFoundError, ConnectionError, ...)
```

```python
try:
    task = tasks[task_id]
except KeyError:                    # be specific — bare `except:` is an anti-pattern
    raise EntityNotFoundError(task_id) from None   # `from` ≈ exception chaining
finally:
    cleanup()                       # same semantics as Java
```

Raise with `raise MyError("msg")`. Custom exceptions are one line: `class EntityNotFoundError(Exception): pass`. No `extends` ceremony, no checked-vs-unchecked debate — put the *domain meaning* in the name.

## EAFP vs LBYL — the cultural flip

Java culture: **LBYL** — Look Before You Leap. Check preconditions, then act.

```java
if (map.containsKey(key)) { value = map.get(key); }
```

Python culture: **EAFP** — Easier to Ask Forgiveness than Permission. Act, handle failure.

```python
try:
    value = mapping[key]
except KeyError:
    value = default
```

Why: checks and actions race (the key can vanish between them), and the happy path stays flat. This is why Python code has `try/except` in places where your Java instincts put `if` guards. Both styles exist in Python; EAFP is the idiomatic default when the failure is *exceptional*.

## `with` ≈ try-with-resources

```python
with open("data.txt") as f:        # f is closed even if an exception flies
    content = f.read()
```

Same guarantee as `try (var f = ...)`. Any object with `__enter__`/`__exit__` works — files, DB connections, locks, HTTP clients, transactions.

Writing your own is where it clicks. Two ways:

```python
# 1. The class way (≈ implementing AutoCloseable):
class FakeDbClient:
    def __enter__(self) -> "FakeDbClient": ...
    def __exit__(self, exc_type, exc, tb) -> None: self.close()

# 2. The generator way (usually what you want — see contextlib):
from contextlib import contextmanager

@contextmanager
def transaction(conn):
    conn.begin()
    try:
        yield conn        # the `as` target
        conn.commit()
    except Exception:
        conn.rollback()
        raise
```

The generator version turns "acquire / try / release" into straight-line code — this pattern is everywhere in FastAPI (module 09 uses it for DB sessions per request).

## Run it

```bash
uv run python 05-errors-and-context-managers/db_client.py
uv run pytest 05-errors-and-context-managers/tests
```

## Common pitfalls for Java devs

- **Bare `except:`** catches `KeyboardInterrupt` and `SystemExit` too. Always `except SpecificError:` — minimum `except Exception:`.
- `except` clauses are matched **in order** — specific before general, like Java multi-catch ordering.
- `__exit__` returning `True` **swallows the exception**. Almost never what you want; return `None`/`False`.
- Forgetting `raise ... from exc` (or `from None`) — the default chaining is fine, but `from None` hides noisy internal causes when re-raising as a domain exception, like a clean exception translation layer.

## Dig deeper

- Built-in exceptions: <https://docs.python.org/3/library/exceptions.html>
- `contextlib` docs: <https://docs.python.org/3/library/contextlib.html>
