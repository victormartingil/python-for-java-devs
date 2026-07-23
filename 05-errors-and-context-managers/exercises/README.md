# 05 — Exercises: errors & context managers

"Make the test pass" practice for [module 05](../README.md). TODO stubs + tests that fail until the implementation is right.

```bash
uv run pytest 05-errors-and-context-managers/exercises -v
```

| Exercise | Stub | Goal |
|---|---|---|
| 01 | `ex05_config_error.py` | Custom exception + EAFP translation, chained with `from` (≈ `initCause`) |
| 02 | `ex05_timer.py` | A timing context manager with `@contextmanager` (≈ try-with-resources as a recipe) |
| 03 | `ex05_suppress.py` | A suppress-and-log context manager — catch scoped to one block |

**Don't read `solutions/` until your tests pass — the tests are the spec.** Solutions are reference implementations, not the only correct answer.
