"""Spec for ex06_blocking — make these pass."""

import asyncio
import inspect
import time

from ex06_blocking import PARTS, load_dashboard


async def test_renders_all_parts_in_order() -> None:
    assert await load_dashboard() == [f"{part} rendered" for part in PARTS]


def test_is_a_coroutine_function() -> None:
    # `def` instead of `async def` fails here — the signature is part of the contract.
    assert inspect.iscoroutinefunction(load_dashboard)


async def test_does_not_block_the_loop() -> None:
    # The watchdog coroutine runs alongside load_dashboard; if the loop is
    # blocked (time.sleep) or renders are sequential, it starves / time grows.
    ticks = 0

    async def watchdog() -> None:
        nonlocal ticks
        for _ in range(4):
            await asyncio.sleep(0.05)
            ticks += 1

    start = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        tg.create_task(load_dashboard())
        tg.create_task(watchdog())
    elapsed = time.perf_counter() - start
    assert ticks == 4, "the event loop was blocked — the watchdog could not run"
    assert elapsed < 0.45, f"took {elapsed:.2f}s — sequential or blocking (≈0.6s) suspected"
