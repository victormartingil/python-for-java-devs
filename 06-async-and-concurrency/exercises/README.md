# 06 — Exercises: async & concurrency

"Make the test pass" practice for [module 06](../README.md). TODO stubs + tests that fail until the implementation is right.

```bash
uv run pytest 06-async-and-concurrency/exercises -v
```

| Exercise | Stub | Goal |
|---|---|---|
| 01 | `ex06_gather.py` | Sequential awaits → `asyncio.gather` (≈ `CompletableFuture.allOf`) |
| 02 | `ex06_blocking.py` | Find-and-fix the blocking call — tests measure elapsed time and loop starvation |
| 03 | `ex06_timeout.py` | Bounded waiting with `asyncio.timeout` (≈ `orTimeout`) |

The timing assertions are part of the spec: a "correct" answer that awaits one by one still fails.

**Don't read `solutions/` until your tests pass — the tests are the spec.** Solutions are reference implementations, not the only correct answer.
