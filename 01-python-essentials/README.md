# 01 — Python essentials

**Goal:** only what collides with your Java instincts. You already know what a variable is — this is where Python's rules *differ*.

## Dynamic typing + type hints: the Java compromise

Java checks types at compile time. Python checks them **never** (at runtime you just get `AttributeError` when you're wrong). The modern compromise: **type hints everywhere**, checked by mypy in CI (module 07). Same safety net as `javac`, just external to the language.

```python
def greet(name: str) -> str:        # ≈ String greet(String name)
    return f"hi {name}"

age: int = 42                       # declared, but not enforced at runtime
nickname: str | None = None         # ≈ Optional<String>, but honest about null
```

Notes:

- `str | None` (3.10+) is the idiomatic `Optional<String>`. You check it with `if nickname is not None:` — there's no `.map()`/`.orElseThrow()` ceremony (though nothing stops you from writing helpers).
- Hints don't change runtime behavior. `greet(123)` *runs*. Your safety is mypy + tests, exactly like your safety in Java is javac + tests.

## Indentation is syntax

No braces. The block *is* the indentation:

```python
if age >= 18:
    print("adult")      # 4 spaces — always 4 spaces
else:
    print("minor")
```

This feels wrong for about two days. Then Java starts looking noisy. Let ruff handle formatting.

## `None`, truthiness, and emptiness

- `None` ≈ `null`, but it's a singleton object — compare with `is None`, never `== None`.
- **Truthiness**: `""`, `0`, `[]`, `{}`, `None` are all *falsy*. So `if tasks:` replaces `if (!tasks.isEmpty())`.
- ⚠️ Trap: `0` and `""` are falsy too. When zero/empty are *valid values*, write `if count is not None:` explicitly. This is the #1 source of "works in my Java mental model" bugs.

## `==` vs `is`

| Python | Java |
|---|---|
| `a == b` | `a.equals(b)` — value comparison |
| `a is b` | `a == b` on references — identity |

You almost always want `==`. Use `is` only for singletons: `None`, `True`, `False`, enum members.

## Mutability by default

`list` and `dict` are mutable, passed by reference, and there's no `final`. Defensive copying is not the culture; the culture is *don't mutate what you don't own* — return new collections instead. Constants are `SCREAMING_SNAKE_CASE` by convention only (no enforcement).

## f-strings

`String.format` done right. Expressions allowed inside:

```python
f"user {user.name} has {len(tasks)} tasks, total {sum(t.estimate for t in tasks)}"
```

## The walrus `:=`

Assignment as an expression (≈ Java's `if ((m = matcher.find()))` pattern, but first-class):

```python
if (n := len(items)) > 10:
    print(f"too many: {n}")
```

Use it to avoid computing twice. Don't use it to be clever.

## `match` / `case` — switch expressions, but destructuring

Looks like Java's modern `switch`, but it *destructures*:

```python
match response.status_code:
    case 200:
        ...
    case 404:
        ...
    case code if code >= 500:   # guard clause
        ...
    case _:                      # default
        ...
```

See `classify_http_status` in `tour.py` — and note it can match on shapes (`case {"id": int() as id, **rest}`), which Java's pattern matching for switch only recently started approaching.

## Run it

```bash
uv run python 01-python-essentials/tour.py
uv run pytest 01-python-essentials/tests
```

## Dig deeper

- Official docs — built-in types & truthiness: <https://docs.python.org/3/library/stdtypes.html>
- `match` tutorial (PEP 636): <https://peps.python.org/pep-0636/>
