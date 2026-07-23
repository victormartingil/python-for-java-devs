"""Spec for ex06_gather — make these pass."""

import time

from ex06_gather import fetch_concurrent, fetch_sequential

NAMES = ["a", "b", "c", "d"]


async def test_results_match_sequential_and_keep_order() -> None:
    expected = await fetch_sequential(NAMES, latency=0.01)
    assert await fetch_concurrent(NAMES, latency=0.01) == expected


async def test_result_content() -> None:
    assert await fetch_concurrent(["x"], latency=0.01) == ["x: done"]


async def test_total_time_is_max_not_sum() -> None:
    start = time.perf_counter()
    await fetch_concurrent(NAMES, latency=0.1)
    elapsed = time.perf_counter() - start
    # 4 sequential fetches would take ≈ 0.4s; concurrent ≈ 0.1s.
    assert elapsed < 0.3, f"took {elapsed:.2f}s — you awaited the fetches one by one"


async def test_empty_input() -> None:
    assert await fetch_concurrent([], latency=0.01) == []
