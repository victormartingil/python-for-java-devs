# 03 — Functions & decorators

**Goal:** functions are values, and decorators are Python's AOP. Understanding decorators *now* is what makes FastAPI obvious later — `@app.get("/tasks")` is just a decorator.

## Functions are objects

No `Function<T,R>`, no `@FunctionalInterface`, no method references. A function is a value you assign, pass, return, and store in collections:

```python
handlers = {"email": send_email, "slack": send_slack}   # strategy map, zero ceremony
handler = handlers[channel]
handler(message)
```

Lambdas exist too — but **one expression only**: `lambda t: t.estimate`. Anything longer gets a `def`. (Yes, Java lambdas are more powerful here. Python's answer is: just name the function.)

## `*args` and `**kwargs`

Varargs, both positional and keyword:

```python
def find_tasks(status: str, *tags: str, limit: int = 10, **filters: object) -> list[Task]:
```

- `*tags` ≈ `String... tags`
- `**filters` collects extra named args into a dict — no Java equivalent; it's how flexible APIs and decorator forwarding work
- Parameters after `*` are **keyword-only** — callers must name them. Great for readability, impossible in Java.

## The mutable default trap — the #1 Python gotcha

```python
def add_tag(task: Task, tags: list[str] = []) -> list[str]:   # NEVER
    tags.append(...)
```

Default values are evaluated **once, at function definition**, and shared across calls — like a `static` field you didn't ask for. The idiom:

```python
def add_tag(task: Task, tags: list[str] | None = None) -> list[str]:
    tags = [] if tags is None else tags
```

ruff (rule B006) flags this automatically. We enable it in this repo.

## Decorators = AOP without the framework

A decorator is a function that wraps a function. Think `@Transactional`, `@Cacheable`, `@Around` — but written in 10 lines of plain code, no proxy magic:

```python
@timed                     # ≈ @Around with a stopwatch
@retry(times=3)            # ≈ Spring Retry
def call_external_api(): ...
```

- `@timed` is sugar for `timed(call_external_api)` — rebinding the name.
- `@retry(times=3)` is sugar for `retry(times=3)(call_external_api)` — a decorator *factory* (like an annotation with attributes).
- Always use `@functools.wraps` inside, or you lose the wrapped function's name/docstring (the equivalent of a proxy hiding the target's metadata — it breaks FastAPI and pytest).

Open `decorators.py` and read `@timed` and `@retry` built from scratch. Once you can *write* one, every `@app.get`, `@pytest.fixture`, `@dataclass` in the rest of this repo stops being magic.

## Full type hints

Annotate everything public — mypy (module 07) is configured to require it:

```python
from collections.abc import Callable

def timed[**P, R](func: Callable[P, R]) -> Callable[P, R]: ...  # 3.12 generics
```

Python generics (the `[**P, R]` inline syntax, 3.12+) are close to Java's `<T>`; `Callable[[A], R]` ≈ `Function<A, R>`. Older code uses `TypeVar`/`ParamSpec` from `typing` — same idea, more boilerplate.

## Run it

```bash
uv run python 03-functions-and-decorators/decorators.py
uv run pytest 03-functions-and-decorators/tests
```

## Common pitfalls for Java devs

- Forgetting `@functools.wraps` → wrapped function loses `__name__`; tools that introspect (FastAPI!) misbehave.
- Decorating with side effects at import time — decorators run when the module is *imported*, not when the function is called. (This is exactly how FastAPI's route registration works.)
- `lambda` overuse — if it needs a name in a comment, it needed a `def`.

## Dig deeper

- `functools` docs (`wraps`, `lru_cache`, `partial`): <https://docs.python.org/3/library/functools.html>
- Real Python's decorator primer: <https://realpython.com/primer-on-python-decorators/>
