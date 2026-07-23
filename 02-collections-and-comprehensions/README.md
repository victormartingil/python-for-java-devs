# 02 — Collections & comprehensions

**Goal:** stop writing loops. Python's answer to the Stream API is *comprehensions* — and they're the single most idiomatic construct in the language.

## The big four vs Java collections

| Python | Java | Notes |
|---|---|---|
| `list` | `ArrayList` | Ordered, mutable, duplicates. Your default. |
| `dict` | `LinkedHashMap` | Insertion-ordered since 3.7 (spec'd, not an accident). |
| `set` | `HashSet` | Unordered, unique. Fast membership: `x in s`. |
| `tuple` | `record`-ish / immutable `List` | Immutable, hashable. Use for fixed shapes: `(lat, lon)`. |

Literals you'll type daily: `[1, 2]`, `{"a": 1}`, `{1, 2}`, `(1, 2)`. Empty dict is `{}`; empty set must be `set()` (yes, this is a wart — `{}` is taken).

Two more worth knowing: `collections.defaultdict` (≈ `computeIfAbsent` built-in) and `collections.Counter` (a multiset — group-and-count in one line).

## Comprehensions vs Stream API — side by side

Same transformation, both languages:

```java
// Java: names of active users, uppercased, as a list
List<String> names = users.stream()
    .filter(User::isActive)
    .map(User::name)
    .map(String::toUpperCase)
    .toList();
```

```python
# Python
names = [u.name.upper() for u in users if u.is_active]
```

The mapping:

| Stream API | Comprehension |
|---|---|
| `.map(f)` | `f(x) for x in ...` |
| `.filter(p)` | `... if p(x)` |
| `.collect(toList())` | `[ ... ]` |
| `.collect(toSet())` | `{ ... }` |
| `.collect(toMap(k, v))` | `{k(x): v(x) for x in ...}` |
| `.flatMap(f)` | `y for x in xs for y in f(x)` |
| lazy stream | `( ... )` — generator expression (lazy!) |

When the pipeline gets long (3+ operations, multiple conditions), a plain `for` loop is *more* Pythonic than a nested comprehension. Readability wins; there's no "everything must be one expression" culture.

## Unpacking

```python
first, *rest = [1, 2, 3, 4]        # first=1, rest=[2,3,4]
lat, lon = (40.4, -3.7)            # no Pair<T>, no Map.Entry
for i, task in enumerate(tasks):   # index + element — never range(len(...))
```

## The top built-ins (memorize these)

| Function | Java equivalent |
|---|---|
| `sorted(xs, key=len, reverse=True)` | `stream().sorted(comparing(...))` — but returns a *new* list |
| `zip(a, b)` | no clean equivalent — iterate two sequences in lockstep |
| `enumerate(xs, start=1)` | indexed for-loop without an index variable |
| `any(xs)` / `all(xs)` | `stream().anyMatch(...)` / `allMatch(...)` |
| `min/max/sum(xs, key=...)` | collectors, but built-in |
| `itertools`: `groupby`, `chain`, `islice`, `batched` | the rest of the Stream API |

Full example — same problem twice — in `collections_demo.py`:

```bash
uv run python 02-collections-and-comprehensions/collections_demo.py
uv run pytest 02-collections-and-comprehensions/tests
```

## Common pitfalls for Java devs

- **Sorting in place vs returning new**: `list.sort()` mutates (returns `None` — calling `xs = xs.sort()` is a classic bug); `sorted(xs)` returns a new list. Prefer `sorted`.
- **Iterating a dict**: `for k in d` gives keys; `for k, v in d.items()` gives both. No `entrySet()` ceremony.
- **`zip` is lazy and stops at the shortest** — use `strict=True` (3.10+) when lengths must match; it raises otherwise, like an assertion.

## Dig deeper

- `itertools` docs — your missing Stream operations: <https://docs.python.org/3/library/itertools.html>
- Sorting HOWTO (key functions, `operator.itemgetter`): <https://docs.python.org/3/howto/sorting.html>
