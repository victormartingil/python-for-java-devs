# 02 — Exercises: collections & comprehensions

"Make the test pass" practice for [module 02](../README.md). TODO stubs + tests that fail until the implementation is right.

```bash
uv run pytest 02-collections-and-comprehensions/exercises -v
```

| Exercise | Stub | Goal |
|---|---|---|
| 01 | `ex02_comprehension.py` | Refactor a Java-style loop into one comprehension + `sorted()` |
| 02 | `ex02_dict_zip.py` | `zip(..., strict=True)` + dict comprehensions to build and invert lookups |
| 03 | `ex02_pipeline.py` | Translate `stream().filter().collect(groupingBy(..., summingInt()))` |

**Don't read `solutions/` until your tests pass — the tests are the spec.** Solutions are reference implementations, not the only correct answer.
