"""SOLUTION 06-03 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

import asyncio


async def slow_service(name: str, latency: float) -> str:
    """A service that always takes `latency` seconds to answer (given)."""
    await asyncio.sleep(latency)
    return f"{name}: answer"


async def fetch_with_timeout(name: str, latency: float, budget: float) -> str:
    try:
        async with asyncio.timeout(budget):
            return await slow_service(name, latency)
    except TimeoutError:
        return f"{name}: timed out"
