"""SOLUTION 06-02 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
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
    return list(await asyncio.gather(*(render_part(part) for part in PARTS)))
