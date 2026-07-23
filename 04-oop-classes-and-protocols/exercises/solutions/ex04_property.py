"""SOLUTION 04-03 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

import math


class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius

    @property
    def diameter(self) -> float:
        return 2 * self.radius

    @diameter.setter
    def diameter(self, value: float) -> None:
        self.radius = value / 2

    @property
    def area(self) -> float:
        return math.pi * self.radius**2
