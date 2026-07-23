"""Exercise 02-02 — dict + zip: parallel lists are a code smell, zip is the fix.

Implement to_lookup and invert. The tests are the spec:

    uv run pytest 02-collections-and-comprehensions/exercises -v

Hint: see the zip example in main() of
02-collections-and-comprehensions/collections_demo.py.
"""


def to_lookup(ids: list[int], names: list[str]) -> dict[int, str]:
    """Pair two parallel lists into a dict: ids[i] -> names[i].

    Java:    for (int i = 0; i < ids.size(); i++) map.put(ids.get(i), names.get(i));
    Python:  a dict comprehension over zip(ids, names, strict=True) — strict
             makes a length mismatch fail loudly instead of silently dropping
             trailing items (which is what plain zip does).
    """
    raise NotImplementedError("TODO(ex02): dict comprehension over zip(ids, names, strict=True)")


def invert(lookup: dict[int, str]) -> dict[str, int]:
    """Swap keys and values: {1: "ada"} -> {"ada": 1}.

    One dict comprehension over lookup.items().
    (Assumes values are unique — like a UNIQUE column in SQL.)
    """
    raise NotImplementedError("TODO(ex02): swap k/v in a dict comprehension")
