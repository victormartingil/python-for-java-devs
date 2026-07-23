"""Python essentials — a tour of everything that differs from Java.

Each section is short and runnable. Functions at the top are exercised
by tests/; the main() below just prints the tour.

Run it:
    uv run python 01-python-essentials/tour.py
"""


# ---------------------------------------------------------------------------
# Type hints: the "Java compromise". Not enforced at runtime — mypy enforces
# them in CI (module 07). `str | None` ≈ Optional<String>.
# ---------------------------------------------------------------------------
def greet(name: str, title: str | None = None) -> str:
    if title is not None:  # singletons compare with `is`, never `==`
        return f"Hello, {title} {name}"
    return f"Hello, {name}"


def classify_http_status(code: int) -> str:
    """match/case ≈ Java switch expressions — with guards and destructuring."""
    match code:
        case 200 | 201 | 204:  # multiple values, like case 200, 201, 204
            return "success"
        case 404:
            return "not found"
        case c if 400 <= c < 500:  # guard — no equivalent in classic switch
            return "client error"
        case c if c >= 500:
            return "server error"
        case _:  # default branch
            return "other"


def first_long_word(words: list[str], min_length: int = 5) -> str | None:
    """Walrus := : assign and test in one expression — avoids computing twice."""
    for word in words:
        if (n := len(word)) >= min_length:
            return f"{word} ({n} chars)"
    return None


def main() -> None:
    # --- 1. Dynamic typing: no declarations, types are hints -------------
    age = 42  # int, inferred by readers and mypy — no `int age = 42;`
    # age = "forty-two"  # would RUN (dynamic!), but mypy flags it in CI. Don't.
    print(f"0. age={age} — no type declaration, no semicolon")

    # --- 2. Indentation IS the block -------------------------------------
    tasks = ["write", "test", "ship"]
    if tasks:  # truthiness: non-empty list is truthy (≈ !tasks.isEmpty())
        print(f"1. {len(tasks)} tasks pending")

    # --- 3. None and `is` --------------------------------------------------
    nickname: str | None = None
    if nickname is None:
        print("2. nickname is None (≈ null; compared with `is`)")

    # --- 4. == vs is -------------------------------------------------------
    a = [1, 2]
    b = [1, 2]
    print(f"3. a == b: {a == b} (equals)  |  a is b: {a is b} (identity)")

    # --- 5. f-strings ------------------------------------------------------
    user, score = "ada", 9.456
    print(f"4. user={user} score={score:.1f}")  # expressions + formatting inline

    # --- 6. Mutability by default -----------------------------------------
    xs = [1, 2, 3]
    ys = xs  # NOT a copy — same object, like assigning a reference in Java
    ys.append(4)
    print(f"5. xs after ys.append(4): {xs} — no `final`, no defensive copies")

    # --- 7. Walrus + match -------------------------------------------------
    print(f"6. {first_long_word(['hi', 'hello', 'wonderful'])}")
    print(f"7. HTTP 503 -> {classify_http_status(503)}")

    # --- 8. Everything is an object ---------------------------------------
    shout = greet  # functions are values — assignable, passable, storable
    print(f"8. {shout('functions are objects too')}")


if __name__ == "__main__":
    main()
