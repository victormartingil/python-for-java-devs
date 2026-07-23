"""Collections & comprehensions — the same problem, Java-style vs Pythonic.

Problem: given a list of tasks, return the titles of the high-priority
pending tasks, uppercased, sorted by estimate descending.

Run it:
    uv run python 02-collections-and-comprehensions/collections_demo.py
"""

from collections import Counter
from itertools import groupby
from typing import TypedDict


class Task(TypedDict):
    """A dict with known keys, type-checked (in real code: dataclass or Pydantic)."""

    title: str
    priority: str
    done: bool
    estimate: int


TASKS: list[Task] = [
    {"title": "write docs", "priority": "high", "done": False, "estimate": 3},
    {"title": "fix login", "priority": "high", "done": False, "estimate": 5},
    {"title": "refactor dao", "priority": "low", "done": False, "estimate": 8},
    {"title": "ship release", "priority": "high", "done": True, "estimate": 2},
    {"title": "add tests", "priority": "high", "done": False, "estimate": 5},
]


def urgent_titles_java_style(tasks: list[Task]) -> list[str]:
    """How a Java dev writes it on day one: loops, temp lists, indexes.

    Correct — but nobody writes Python like this past week two.
    """
    result = []
    for task in tasks:
        if task["priority"] == "high" and not task["done"]:
            result.append(task["title"].upper())

    estimates = {t["title"].upper(): t["estimate"] for t in tasks}
    for i in range(len(result)):  # bubble-sort flavored sadness
        for j in range(i + 1, len(result)):
            if estimates[result[j]] > estimates[result[i]]:
                result[i], result[j] = result[j], result[i]
    return result


def urgent_titles_pythonic(tasks: list[Task]) -> list[str]:
    """The idiomatic version: filter as a comprehension, sorted() with a key."""
    pending = [t for t in tasks if t["priority"] == "high" and not t["done"]]
    by_estimate = sorted(pending, key=lambda t: t["estimate"], reverse=True)
    return [t["title"].upper() for t in by_estimate]


def counts_by_priority(tasks: list[Task]) -> Counter[str]:
    """Counter ≈ groupingBy + counting(), in one line."""
    return Counter(t["priority"] for t in tasks)


def titles_by_status(tasks: list[Task]) -> dict[bool, list[str]]:
    """itertools.groupby ≈ Collectors.groupingBy — but input must be sorted first."""
    ordered = sorted(tasks, key=lambda t: t["done"])
    return {
        done: [t["title"] for t in group]
        for done, group in groupby(ordered, key=lambda t: t["done"])
    }


def main() -> None:
    print("Java-style:  ", urgent_titles_java_style(TASKS))
    print("Pythonic:    ", urgent_titles_pythonic(TASKS))
    assert urgent_titles_java_style(TASKS) == urgent_titles_pythonic(TASKS)

    print("By priority: ", dict(counts_by_priority(TASKS)))
    print("By status:   ", titles_by_status(TASKS))

    # Unpacking, enumerate, zip, any/all — the daily vocabulary:
    first, *rest = ["a", "b", "c"]
    print(f"Unpack:      first={first!r} rest={rest}")
    print("Enumerate:   ", list(enumerate(["x", "y"], start=1)))
    print("Zip:         ", list(zip(["id", "name"], [7, "ada"], strict=True)))
    print("any/all:     ", any(t["done"] for t in TASKS), all(t["estimate"] for t in TASKS))


if __name__ == "__main__":
    main()
