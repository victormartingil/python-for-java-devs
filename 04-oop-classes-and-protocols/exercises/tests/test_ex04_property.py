"""Spec for ex04_property — make these pass."""

import math

import pytest
from ex04_property import Circle


def test_diameter_reads_from_radius() -> None:
    assert Circle(3).diameter == 6


def test_diameter_setter_updates_radius() -> None:
    circle = Circle(1)
    circle.diameter = 10
    assert circle.radius == 5
    assert circle.diameter == 10


def test_area_is_derived() -> None:
    assert Circle(2).area == pytest.approx(math.pi * 4)


def test_area_is_read_only() -> None:
    circle = Circle(2)
    with pytest.raises(AttributeError):
        circle.area = 99
