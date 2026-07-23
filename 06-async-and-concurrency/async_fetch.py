"""Async & concurrency — 3 fetches, sequential vs concurrent, with timing.

Online: real HTTP via httpx.AsyncClient. Offline: falls back to simulated
latency via asyncio.sleep so the demo always runs.

Run it:
    uv run python 06-async-and-concurrency/async_fetch.py
"""

import asyncio
import time

import httpx

URLS = [
    "https://jsonplaceholder.typicode.com/todos/1",
    "https://jsonplaceholder.typicode.com/todos/2",
    "https://jsonplaceholder.typicode.com/todos/3",
]
SIMULATED_LATENCY = 0.3  # seconds, used when the network is unavailable


async def fetch_one(client: httpx.AsyncClient, url: str) -> str:
    """One async HTTP GET. Every `await` is a yield point for the event loop."""
    response = await client.get(url)
    response.raise_for_status()
    data = response.json()
    return f"{url.rsplit('/', 1)[-1]}: {data['title']}"


async def simulated_fetch(name: str, latency: float = SIMULATED_LATENCY) -> str:
    """Offline stand-in: sleeps WITHOUT blocking the event loop."""
    await asyncio.sleep(latency)  # time.sleep() here would freeze everything
    return f"{name}: simulated result"


async def fetch_sequential(urls: list[str]) -> tuple[list[str], float]:
    """≈ future.get() in a loop: total time ≈ SUM of latencies."""
    start = time.perf_counter()
    results = []
    async with httpx.AsyncClient(timeout=5.0) as client:
        for url in urls:
            results.append(await fetch_one(client, url))
    return results, time.perf_counter() - start


async def fetch_concurrent(urls: list[str]) -> tuple[list[str], float]:
    """≈ CompletableFuture.allOf: total time ≈ MAX of latencies."""
    start = time.perf_counter()
    async with httpx.AsyncClient(timeout=5.0) as client:
        results = await asyncio.gather(*(fetch_one(client, url) for url in urls))
    return list(results), time.perf_counter() - start


async def simulated_sequential(n: int) -> float:
    start = time.perf_counter()
    for i in range(n):
        await simulated_fetch(str(i))
    return time.perf_counter() - start


async def simulated_concurrent(n: int) -> float:
    start = time.perf_counter()
    async with asyncio.TaskGroup() as tg:  # 3.11+ structured concurrency
        for i in range(n):
            tg.create_task(simulated_fetch(str(i)))
    return time.perf_counter() - start


async def main() -> None:
    try:
        seq, t_seq = await fetch_sequential(URLS)
        conc, t_conc = await fetch_concurrent(URLS)
        print("sequential:", *seq, f"({t_seq:.2f}s)", sep="\n  ")
        print("concurrent:", *conc, f"({t_conc:.2f}s)", sep="\n  ")
        print(f"\nspeedup: {t_seq / t_conc:.1f}x — same thread, interleaved I/O waits")
    except httpx.HTTPError as exc:
        print(f"No network ({exc.__class__.__name__}) — falling back to simulated latency\n")
        t_seq = await simulated_sequential(3)
        t_conc = await simulated_concurrent(3)
        print(f"simulated sequential: {t_seq:.2f}s  (≈ 3 × {SIMULATED_LATENCY}s)")
        print(f"simulated concurrent: {t_conc:.2f}s  (≈ 1 × {SIMULATED_LATENCY}s)")
        print("\nSame machine, same thread — concurrency, not parallelism.")


if __name__ == "__main__":
    asyncio.run(main())  # the entry point: creates and runs the event loop
