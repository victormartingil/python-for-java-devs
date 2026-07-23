# 06 — Async & concurrency

**Goal:** the module Java devs get most wrong. Python concurrency is *not* Java concurrency with different keywords. Read this one twice.

## The GIL, in 5 lines

1. CPython has a **Global Interpreter Lock**: only one thread executes Python bytecode at a time.
2. So threads give you **concurrency, not parallelism** for CPU-bound Python code.
3. Threads are still fine for I/O (the GIL is released while waiting).
4. CPU-bound parallelism → `multiprocessing` (separate processes, separate GILs).
5. Java's "just add threads" mental model **does not transfer**.

**What's coming (3 lines):** Python 3.13 shipped an experimental *free-threaded* build (`python3.13t`) with the GIL optional. If it pans out, CPU-bound threading gets real parallelism — but it's opt-in and the ecosystem is still validating. For 2026 production code: asyncio for I/O, multiprocessing for CPU.

## `async`/`await` ≈ `CompletableFuture` — but single-threaded

```python
async def fetch(url: str) -> str:      # ≈ Supplier<CompletableFuture<String>>
    ...

results = await asyncio.gather(fetch(a), fetch(b))   # ≈ CompletableFuture.allOf
```

The crucial difference: `asyncio` runs on **one thread with an event loop**. Coroutines don't run in parallel — they *take turns*, yielding control at every `await` (while I/O is in flight). It's cooperative multitasking: closer to Project Loom's model of "cheap suspendable tasks" than to a thread pool, except suspension points are explicit (`await`) instead of automatic.

Consequences that surprise Java devs:

- **One blocking call stalls everything.** `time.sleep(1)` inside a coroutine freezes *all* coroutines for 1s — like blocking the only carrier thread. The async version is `await asyncio.sleep(1)`.
- **You can't mix sync libraries in.** A sync DB driver or `requests.get()` inside `async def` silently kills your throughput. Async code needs async libraries all the way down (`httpx.AsyncClient`, `asyncpg`, `aioredis`). This is why the repo pins `sqlalchemy[asyncio]` + `asyncpg` in module 10.
- No structured concurrency ceremony like `SupplyAsync` + executor — tasks are created with `asyncio.create_task()` and gathered.

## When async helps — and when it doesn't

| Workload | Tool | Java analogy |
|---|---|---|
| Many concurrent I/O calls (HTTP, DB, files) | `asyncio` | WebFlux / virtual threads |
| CPU-bound computation | `multiprocessing` | `ForkJoinPool` / parallel streams |
| A couple of blocking calls, simple script | threads or nothing | plain executor |
| One HTTP call | just call it synchronously | — |

Async is not "faster code". It's "more concurrent I/O per process". FastAPI uses it to serve thousands of concurrent requests on one process — that's the whole point (module 08+).

## The classic mistake, demonstrated

`async_fetch.py` fetches 3 URLs two ways and times both:

- **sequential** — one `await` after another ≈ calling `.join()` on each future in order
- **concurrent** — `asyncio.gather(...)` ≈ `allOf(...)`

Expected: concurrent ≈ max(latencies), sequential ≈ sum(latencies). Offline? The script catches the network failure and falls back to simulated latency (`asyncio.sleep`) so you can run it anywhere.

```bash
uv run python 06-async-and-concurrency/async_fetch.py
uv run pytest 06-async-and-concurrency/tests
```

## Common pitfalls for Java devs

- Forgetting `await` → you get a *coroutine object*, not a result. No compile error; it fails at runtime (mypy catches most of these — module 07).
- `asyncio.gather()` returns results **in argument order**, not completion order (same as `allOf`).
- Fire-and-forget: `asyncio.create_task(f())` without keeping a reference can be garbage-collected mid-flight. Keep the task, or use a `TaskGroup` (3.11+, ≈ structured concurrency — recommended).
- Reaching for threads because "async looks complicated". For I/O-heavy services, async *is* the Python answer — embrace it.

## Dig deeper

- `asyncio` docs: <https://docs.python.org/3/library/asyncio.html>
- `TaskGroup` (structured concurrency): <https://docs.python.org/3/library/asyncio-task.html#asyncio.TaskGroup>
