"""Exercise 04-03 — @property: accessors that don't look like accessors.

Finish Circle. The tests are the spec:

    uv run pytest 04-oop-classes-and-protocols/exercises -v

Hint: see Task.is_big in 04-oop-classes-and-protocols/notifiers.py — called
WITHOUT parens. A setter lets callers write circle.diameter = 10 while radius
stays the single source of truth. You'll need `import math` for the area.
"""


class Circle:
    """radius is stored; diameter and area are derived.

    TODO(ex03):
    - diameter: property — get returns 2 * radius; set updates radius
    - area:     read-only property returning math.pi * radius ** 2
    """

    def __init__(self, radius: float) -> None:
        self.radius = radius

    @property
    def diameter(self) -> float:
        raise NotImplementedError("TODO(ex03): return 2 * self.radius")

    # TODO(ex03): add the @diameter.setter and the read-only area property
