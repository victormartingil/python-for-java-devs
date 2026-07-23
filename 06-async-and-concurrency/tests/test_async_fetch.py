"""Async tests — with asyncio_mode=auto, plain `async def test_` just works."""

import asyncio
import time

from async_fetch import simulated_concurrent, simulated_fetch, simulated_sequential


async def simulated_sequential_timed(n: int, latency: float) -> float:
    start = time.perf_counter()
    for i in range(n):
        await simulated_fetch(str(i), latency)
    return time.perf_counter() - start


async def simulated_concurrent_timed(n: int, latency: float) -> float:
    start = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        for i in range(n):
            tg.create_task(simulated_fetch(str(i), latency))
    return time.perf_counter() - start


async def test_simulated_fetch_returns_result() -> None:
    assert await simulated_fetch("x", latency=0.01) == "x: simulated result"


async def test_concurrent_is_faster_than_sequential() -> None:
    n, latency = 5, 0.05
    # sequential ≈ sum of latencies; concurrent ≈ max of latencies
    t_seq = await simulated_sequential_timed(n, latency)
    t_conc = await simulated_concurrent_timed(n, latency)
    assert t_seq >= n * latency * 0.9
    assert t_conc < t_seq / 2


async def test_module_level_helpers_agree() -> None:
    # the module's own simulated functions show the same ordering
    assert await simulated_concurrent(3) < await simulated_sequential(3)
