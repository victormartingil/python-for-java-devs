"""Exercise 06-03 — bounded waiting with asyncio.timeout.

Implement fetch_with_timeout. The tests are the spec:

    uv run pytest 06-async-and-concurrency/exercises -v

Anchor: CompletableFuture.orTimeout / get(timeout) — except here the block
itself is bounded: `async with asyncio.timeout(budget):` cancels the body when
the budget expires, raising TimeoutError at the boundary (Python 3.11+).
"""

import asyncio


async def slow_service(name: str, latency: float) -> str:
    """A service that always takes `latency` seconds to answer (given)."""
    await asyncio.sleep(latency)
    return f"{name}: answer"


async def fetch_with_timeout(name: str, latency: float, budget: float) -> str:
    """Call slow_service(name, latency) but give up after `budget` seconds.

    - the answer arrives within budget -> return it
    - the budget expires               -> return f"{name}: timed out"

    Use asyncio.timeout(...) and catch TimeoutError — do NOT measure time
    yourself with loops or sleep-polling.
    """
    raise NotImplementedError("TODO(ex03): asyncio.timeout around the await, catch TimeoutError")
