"""Exercise 06-02 — find and fix the blocking call.

load_dashboard_naive (given) "works" — but it calls time.sleep() inside an
async function, freezing the whole event loop, and renders parts one by one.
Rewrite it as load_dashboard: same output, non-blocking, well under 0.45s.

    uv run pytest 06-async-and-concurrency/exercises -v

Anchor: calling a blocking JDBC driver inside @Async — the thread is stuck for
the duration. render_part (given) is the async twin: asyncio.sleep yields the
loop. See the warning in simulated_fetch, 06-async-and-concurrency/async_fetch.py.
"""

import asyncio
import time

PARTS = ("header", "body", "footer")
RENDER_TIME = 0.2  # seconds per part


def render_part_blocking(part: str) -> str:
    """The legacy SYNC renderer: time.sleep freezes the loop. Do not call it."""
    time.sleep(RENDER_TIME)
    return f"{part} rendered"


async def render_part(part: str) -> str:
    """The async twin (given): same latency, but the loop stays free."""
    await asyncio.sleep(RENDER_TIME)
    return f"{part} rendered"


async def load_dashboard_naive() -> list[str]:
    """The bug on display: a blocking call + sequential rendering ≈ 0.6s of stuck loop."""
    return [render_part_blocking(part) for part in PARTS]


async def load_dashboard() -> list[str]:
    """TODO(ex02): return the three rendered parts, non-blocking, in ≈0.2s.

    Use render_part (never the blocking one) and start all three renders BEFORE
    awaiting them — asyncio.gather or asyncio.TaskGroup, your pick.
    """
    raise NotImplementedError("TODO(ex02): gather/TaskGroup over render_part coroutines")
