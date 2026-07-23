"""Spec for ex05_timer — make these pass."""

import time

import pytest
from ex05_timer import timer


def test_records_one_measurement() -> None:
    timings: list[float] = []
    with timer(timings):
        pass
    assert len(timings) == 1
    assert timings[0] >= 0


def test_measures_real_elapsed_time() -> None:
    timings: list[float] = []
    with timer(timings):
        time.sleep(0.05)
    assert timings[0] >= 0.05


def test_exception_still_records_then_propagates() -> None:
    timings: list[float] = []
    with pytest.raises(RuntimeError), timer(timings):
        raise RuntimeError("boom")
    assert len(timings) == 1, "the measurement must happen even when the block raises"


def test_separate_blocks_accumulate() -> None:
    timings: list[float] = []
    with timer(timings):
        pass
    with timer(timings):
        pass
    assert len(timings) == 2
