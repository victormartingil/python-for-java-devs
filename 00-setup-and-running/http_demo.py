"""External dependencies with `uv add` — demonstrated with httpx.

httpx is the HTTP client this repo uses everywhere (≈ Java's HttpClient /
RestTemplate / WebClient). It was added to pyproject.toml with:

    uv add httpx

Run it:
    uv run python 00-setup-and-running/http_demo.py

The HTTP call is wrapped in try/except so the script still runs offline.
"""

import httpx

URL = "https://jsonplaceholder.typicode.com/todos/1"


def fetch_todo(url: str, timeout: float = 5.0) -> dict[str, object]:
    """GET a JSON resource and return it as a dict.

    Note the type hints: `dict[str, object]` ≈ `Map<String, Object>`.
    Hints are optional at runtime — they're documentation + fuel for mypy.
    """
    # `with` ≈ try-with-resources: the client is closed automatically (module 05).
    with httpx.Client(timeout=timeout) as client:
        response = client.get(url)
        response.raise_for_status()  # throws on 4xx/5xx — like an error decoder
        data: dict[str, object] = response.json()
        return data


def main() -> None:
    try:
        todo = fetch_todo(URL)
    except httpx.HTTPError as exc:
        # Offline? DNS blocked? Don't crash a teaching example for that.
        print(f"Network call failed ({exc.__class__.__name__}: {exc})")
        print("That's fine — the point was: `uv add httpx` + import. It works.")
        return
    print("Fetched over HTTP with httpx:")
    print(f"  title:     {todo['title']}")
    print(f"  completed: {todo['completed']}")


if __name__ == "__main__":
    main()
