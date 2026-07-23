# 04 — Exercises: OOP, classes & protocols

"Make the test pass" practice for [module 04](../README.md). TODO stubs + tests that fail until the implementation is right.

```bash
uv run pytest 04-oop-classes-and-protocols/exercises -v
```

| Exercise | Stub | Goal |
|---|---|---|
| 01 | `ex04_protocol.py` | Satisfy a `Protocol` structurally — no `implements`, no inheritance |
| 02 | `ex04_dataclass.py` | Frozen dataclass with `__post_init__` validation (≈ a record's compact constructor) |
| 03 | `ex04_property.py` | `@property` getter/setter instead of Java-style accessors |

**Don't read `solutions/` until your tests pass — the tests are the spec.** Solutions are reference implementations, not the only correct answer.
