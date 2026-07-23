# 00 — Setup & running

**Goal:** install Python + uv, run your first script, add a dependency. 15 minutes.

## The toolchain, in Java terms

| Java | Python (2026) |
|---|---|
| JDK | Python 3.12+ interpreter |
| Maven/Gradle (`pom.xml` + lockfile) | **uv** (`pyproject.toml` + `uv.lock`) |
| `mvn install` | `uv sync` |
| `mvn exec:java` / `java -jar` | `uv run python script.py` |
| `.mvn/jvm.config`, toolchains | `.python-version` |

This repo uses **uv** throughout. It is a strong modern choice for project and dependency management: it can install Python, create virtual environments, resolve and lock dependencies, and run tools from one fast CLI. `pip` and `venv` remain widely used and worth recognizing; you just don't need to start with them for this course.

> **Ecosystem context (5 min):** you'll still see `pip install X`, `python -m venv .venv` and `requirements.txt` in tutorials, existing projects and Stack Overflow answers. That traditional workflow still works and is everywhere. This repo chooses uv's project workflow because it gives us one reproducible path from setup to CI.

## Install

```bash
# macOS
brew install uv

# Linux / macOS (official script)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
winget install astral-sh.uv
# or: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

You do **not** need to install Python separately. `uv sync` (or `uv python install 3.12`) fetches a managed interpreter for you, pinned by the `.python-version` file at the repo root (≈ Maven toolchains).

## The uv workflow

```bash
uv init my-project      # scaffold a new project (≈ mvn archetype:generate)
uv add httpx            # add a dependency (≈ adding to <dependencies> + resolving)
uv add --dev pytest     # add a dev/test dependency (≈ scope=test)
uv remove httpx         # remove it
uv sync                 # install everything from pyproject + uv.lock (≈ mvn install)
uv run python hello.py  # run inside the project environment
uv run pytest           # run any tool the project has installed
uv lock --upgrade       # upgrade dependencies (≈ versions:use-latest-releases)
```

Rules of thumb:

- **Never** edit `uv.lock` by hand (like you wouldn't hand-edit a `package-lock.json`).
- **Commit both** `pyproject.toml` and `uv.lock` — reproducible builds, same as a lockfile in Gradle.
- Dependencies are declared with version ranges in `pyproject.toml`; exact pins live in `uv.lock`.

## The venv, in one paragraph

Python isolates each project's dependencies in a **virtual environment** — a directory (`.venv/`) with its own interpreter and site-packages, roughly like a per-project local Maven repo combined with the JDK. In the traditional workflow you create and activate it by hand (`python -m venv .venv && source .venv/bin/activate`). **With this repo's uv workflow you normally don't touch it**: `uv sync` creates it, `uv run` uses it. If `.venv` gets corrupted, delete it and run `uv sync` again.

## How a script runs

There is no `public static void main`. A `.py` file executes top-to-bottom when you run it. The idiom:

```python
def main() -> None:
    print("hello")

if __name__ == "__main__":
    main()
```

`__name__` is `"__main__"` only when the file is executed directly — when imported as a module, it's the module name. So this guard means "only run when executed, not when imported" — the closest thing to a `main` method entry point. Get used to typing it; every script in this repo has one.

Run it:

```bash
uv run python 00-setup-and-running/hello.py
```

Two more execution forms you'll meet:

```bash
uv run python -m pytest        # -m runs a *module* as a script (≈ java -cp ... pkg.Main)
uv run python -m http.server   # stdlib modules work too
```

## Try it now

```bash
uv run python 00-setup-and-running/hello.py       # no dependencies at all
uv run python 00-setup-and-running/http_demo.py   # uses httpx (installed via uv add)
```

`http_demo.py` makes a real HTTP call to show that external dependencies *just work* after `uv add` — and it degrades gracefully if you're offline.

## IDE setup

- **VS Code:** install the *Python* extension (Microsoft). Point it at the project interpreter: `Cmd/Ctrl+Shift+P` → "Python: Select Interpreter" → pick `./.venv/bin/python`. Ruff extension for lint/format on save. Pyright comes bundled (that's the type checker in your editor; mypy runs in CI — module 07).
- **PyCharm:** it detects `.venv` automatically (Settings → Project → Python Interpreter). Enable the *Ruff* plugin.

Either way: **format on save with ruff**, and stop thinking about style forever.

## Dig deeper

- uv docs: <https://docs.astral.sh/uv/>
- Python official tutorial, "Modules" (how imports and `__name__` work): <https://docs.python.org/3/tutorial/modules.html>
