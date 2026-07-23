"""Spec for ex06_timeout — make these pass."""

import time

from ex06_timeout import fetch_with_timeout


async def test_fast_answer_comes_back() -> None:
    assert await fetch_with_timeout("users", latency=0.01, budget=1.0) == "users: answer"


async def test_slow_answer_times_out() -> None:
    assert await fetch_with_timeout("users", latency=5.0, budget=0.05) == "users: timed out"


async def test_giving_up_is_prompt() -> None:
    start = time.perf_counter()
    await fetch_with_timeout("billing", latency=5.0, budget=0.05)
    elapsed = time.perf_counter() - start
    # Without a timeout this test would take 5 seconds.
    assert elapsed < 1.0, f"took {elapsed:.2f}s — the budget was not enforced"
