"""Exercise 06-01 — from sequential awaits to asyncio.gather.

fake_fetch simulates I/O latency WITHOUT blocking the event loop (given).
fetch_sequential is the "before" (given): total time ≈ SUM of latencies.
Write fetch_concurrent: same results, same order, total time ≈ MAX.

    uv run pytest 06-async-and-concurrency/exercises -v

Anchor: CompletableFuture.allOf — one thread, interleaved waits.
See fetch_concurrent in 06-async-and-concurrency/async_fetch.py.
"""

import asyncio


async def fake_fetch(name: str, latency: float = 0.1) -> str:
    """Simulated I/O: sleeps WITHOUT blocking the loop (asyncio.sleep — never time.sleep)."""
    await asyncio.sleep(latency)
    return f"{name}: done"


async def fetch_sequential(names: list[str], latency: float = 0.1) -> list[str]:
    """The "before": ≈ future.get() in a loop. Total time ≈ sum of latencies."""
    results = []
    for name in names:
        results.append(await fake_fetch(name, latency))
    return results


async def fetch_concurrent(names: list[str], latency: float = 0.1) -> list[str]:
    """TODO(ex01): same results IN INPUT ORDER, but start all fetches first and
    await them together — asyncio.gather. Total time ≈ ONE latency, not the sum.
    """
    raise NotImplementedError("TODO(ex01): asyncio.gather over the fake_fetch coroutines")
