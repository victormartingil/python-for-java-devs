# 07 — A real project: uv + pytest + mypy

**Goal:** how a serious Python project is actually organized. This is the module that turns "I can write scripts" into "I can work on a Python codebase".

## The layout

```
07-real-project-uv-pytest-mypy/
├── src/
│   └── textutils/           # the package (≈ a Java package with classes)
│       ├── __init__.py      # makes it a package; holds the public API
│       └── core.py          # the implementation
└── tests/
    ├── conftest.py          # pytest config shared by the tests dir
    └── test_textutils.py
```

The **`src/` layout** (package under `src/`, tests outside) prevents the classic bug where tests import your *local* code instead of the *installed* package — like Maven's `src/main/java` vs `src/test/java`, it enforces the separation physically.

**`__init__.py`** marks a directory as a package (≈ `package-info.java`, but it can also *do* things: it typically re-exports the public API so users write `from textutils import slugify` instead of reaching into `textutils.core`). Modern note: `__init__.py`-less namespace packages exist; for application code, keep the file — explicit beats clever.

## `pyproject.toml` anatomy

One file replaces `pom.xml` (PEP 621 standard, tool-agnostic). The root of this repo has the real one — open it next to this table:

| Section | Maven analogy | What it does |
|---|---|---|
| `[project]` | `<groupId>/<artifactId>/<version>` + `<dependencies>` | name, version, `requires-python`, runtime deps |
| `[dependency-groups]` | `<scope>test</scope>` deps | dev-only deps (pytest, ruff, mypy) |
| `[tool.uv]` | build config | uv-specific behavior (`package = false` = not a publishable lib) |
| `[tool.ruff]` | Checkstyle + Spotless config | lint + format rules |
| `[tool.mypy]` | compiler warnings config | type-check strictness |
| `[tool.pytest.ini_options]` | surefire config | test discovery, async mode |
| `uv.lock` (generated) | a Gradle lockfile | exact pinned versions — **commit it** |

## The quality trio

```bash
uv run ruff check .        # lint (≈ Checkstyle): bugs, smells, import order
uv run ruff format .       # format (≈ Spotless/google-java-format): no arguments, ever
uv run mypy                # type check (≈ javac's type system, external tool)
uv run pytest              # tests (≈ mvn test)
```

- **ruff** is one binary replacing flake8 + black + isort. Configured with `line-length = 100`, `target-version = "py312"` in `pyproject.toml`.
- **mypy** with `disallow_untyped_defs = true` forces annotations on all functions — strict-but-pragmatic, like turning on compiler warnings that a senior team would.
- **Mentioned in 3 lines:** *pyright* is the type checker inside VS Code/Pylance (similar rules, different engine — your editor uses it while mypy runs in CI); *ty* is Astral's new, much faster type checker, emerging in 2026. Knowing mypy well transfers to both.

## Debugging & profiling — the "where's my IntelliJ debugger?" section

Same job, different tools. Four things cover 95% of a Java dev's debugging life:

**1. `breakpoint()` ≈ a breakpoint you commit to code.** Drop it anywhere; when execution hits it, you land in **pdb** (the built-in terminal debugger):

```python
def total(orders: list[Order]) -> Money:
    breakpoint()   # execution pauses here; try: pp orders — then n, s, c
```

Essential pdb commands: `n` (step over ≈ F8), `s` (step into ≈ F7), `c` (continue ≈ F9), `pp var` (print), `l` (list code), `q` (quit). Remove the line when done — ruff will flag a forgotten `breakpoint()` in CI (rule T100, if enabled), but the habit matters more than the linter.

**2. IDE debugging ≈ IntelliJ, one-to-one.** PyCharm: click the gutter, Debug — works out of the box. VS Code: Python extension, then F5; a minimal `launch.json` (you create `.vscode/launch.json` yourself, it's machine-local):

```json
{
  "version": "0.2.0",
  "configurations": [
    { "name": "Current file", "type": "debugpy", "request": "launch",
      "program": "${file}", "console": "integratedTerminal" },
    { "name": "FastAPI (module 11)", "type": "debugpy", "request": "launch",
      "module": "uvicorn", "args": ["app.main:app", "--reload"],
      "cwd": "${workspaceFolder}/11-project-architecture" }
  ]
}
```

**3. Debugging tests: `uv run pytest --pdb`.** The killer flag: drops you into pdb **at the exact failing assertion**. Add `-x` (stop at first failure) and `--lf` (re-run only last failures) and you have your IntelliJ "debug test" workflow in the terminal.

**4. Profiling ≈ JFR / async-profiler.** `python -m cProfile -s cumulative script.py` for deterministic CPU profiling (≈ JFR method sampling, built-in); `py-spy top --pid <pid>` or `py-spy record -o flame.svg -- python script.py` for sampling a *running* process without touching the code (≈ async-profiler — install with `uv tool install py-spy`, not into the project). Micro-benchmarks: `python -m timeit "..."`.

Try it: `debugging_demo.py` computes order stats and has a deliberate bug. Run it, then uncomment the `breakpoint()` line (or run `uv run pytest --pdb` on a failing test of your own) and inspect the state:

```bash
uv run python 07-real-project-uv-pytest-mypy/debugging_demo.py
```

## pytest — JUnit 5, minus the ceremony

```python
def test_slugify_basic():                      # no class, no @Test
    assert slugify("Hello World") == "hello-world"
```

The mappings:

| JUnit 5 | pytest |
|---|---|
| `@Test` on a method | any `test_*` function |
| `@BeforeEach` / DI into test params | **fixtures** — functions that return test resources, injected by name |
| `@ParameterizedTest` + `@ValueSource` | `@pytest.mark.parametrize("input,expected", [...])` |
| `@Tag("slow")` | `@pytest.mark.slow` (custom markers registered in config) |
| `@AfterEach` / cleanup | fixture with `yield` (teardown after the test) |
| AssertJ `assertThat(x).isEqualTo(y)` | plain `assert x == y` — pytest rewrites it to show rich diffs |

Open `tests/test_textutils.py`: one fixture (≈ `@BeforeEach`), one parametrize table, one marker. That's 90% of pytest for a Java dev.

## Run it

```bash
uv sync                                     # once, from the repo root
uv run pytest 07-real-project-uv-pytest-mypy/tests -v
uv run pytest -m "not slow"                 # markers as selectors
```

## Common pitfalls for Java devs

- Importing the package from a *different* working directory and getting `ModuleNotFoundError` — the fix is the `src/` layout + installed deps (in this repo, tests use a `conftest.py` that puts the module's code on `sys.path`; in a packaged project, `uv sync` installs it for real).
- `__pycache__` and `.pytest_cache` committed to git — they're in this repo's `.gitignore`; keep them there.
- Writing `setUp()` instance state in fixtures shared across tests — fixtures default to *function scope* (fresh per test), exactly like JUnit's default.

## Dig deeper

- pytest docs (fixtures, parametrize, markers): <https://docs.pytest.org/en/stable/>
- uv project docs: <https://docs.astral.sh/uv/concepts/projects/>
