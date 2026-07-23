# 01 — Exercises: Python essentials

"Make the test pass" practice for [module 01](../README.md). Same format you know from JUnit: TODO stubs + tests that fail until the implementation is right.

```bash
uv run pytest 01-python-essentials/exercises -v
```

| Exercise | Stub | Goal |
|---|---|---|
| 01 | `ex01_fstrings.py` | f-string format specs (`:.1f`, `:03d`) instead of `String.format` |
| 02 | `ex01_truthiness.py` | `is not None` vs falsy — the `or` trap with `0`; truthiness for emptiness |
| 03 | `ex01_match.py` | `match/case` with OR patterns and a guard (≈ switch expressions) |

**Don't read `solutions/` until your tests pass — the tests are the spec.** Solutions are reference implementations, not the only correct answer.
