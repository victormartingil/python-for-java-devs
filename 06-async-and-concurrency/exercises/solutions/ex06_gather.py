"""SOLUTION 06-01 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
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
    return list(await asyncio.gather(*(fake_fetch(name, latency) for name in names)))
