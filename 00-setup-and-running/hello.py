"""Hello world — the `public static void main` of Python.

Run it:
    uv run python 00-setup-and-running/hello.py
"""

import sys


def main() -> None:
    # No System.out.println, no semicolons, no class wrapper required.
    print("Hello from Python", sys.version.split()[0])

    # f-strings: the idiomatic String.format — full tour in module 01.
    name = "Java dev"
    print(f"Welcome, {name}. You already know 80% of this.")


if __name__ == "__main__":
    # True only when this file is executed directly, not when imported.
    main()
