# Contributing

Thanks for considering a contribution — this repo is a learning resource, so **clarity beats cleverness** in every change.

## Before you start

- **Content in English.** Code, comments, READMEs, commit messages.
- **The audience is senior Java developers.** Explain deltas, not programming basics. Every concept should anchor to its Java/Spring equivalent where one exists.
- **Everything must run.** If it can't be executed and tested, it doesn't go in.

## Set up and run the quality gates

```bash
uv sync --all-groups           # full environment (all modules)
uv run ruff check .            # lint
uv run ruff format .           # format (CI runs --check)
uv run mypy                    # type check
uv run pytest                  # full suite (123 + conditional skips)
bash scripts/verify-solutions.sh   # prove every exercise solution passes
```

All six must be green before a PR. A lighter `uv sync` is enough to work on fundamentals modules (00–07).

## Repo conventions (enforced by CI + review)

1. **Module template**: `NN-kebab-name/` with `README.md` (≤ 300 lines), runnable `.py` examples, `tests/`. Module dirs start with digits, so they are not Python packages — tests use a per-dir `conftest.py` for `sys.path` wiring.
2. **Unique basenames repo-wide** for every `.py` file (duplicate basenames collide in pytest/mypy).
3. **`pyproject.toml` is append-only** for config: new module → add its dir to `[tool.mypy] files` and its `tests/` dir to `testpaths`. Register any new pytest marker.
4. **App code passes `disallow_untyped_defs`** (mypy); tests are excluded from mypy.
5. **Tests must degrade gracefully**: anything needing Docker/Postgres/API keys goes behind a registered marker and skips cleanly when unavailable. Bare `uv run pytest` must stay green on any machine, on any sync profile.
6. **Exercises**: stubs raise `NotImplementedError` with a precise docstring; tests are the spec; reference implementations live in `exercises/solutions/` and MUST pass (`scripts/verify-solutions.sh` runs in CI).
7. **No legacy tools presented as current practice.** If you mention pip/venv/python-jose/etc., label it explicitly as legacy context.
8. **No personal data.** Neutral examples (tasks, users).

## Proposing changes

- **Fixes** (typos, broken code, stale versions): open a PR directly.
- **New content** (a module, an exercise set, a new equivalence in CHEATSHEET.md): open an issue first with the outline — the editorial line (terse, Java-anchored, runnable) is curated.
- **Dependency updates**: explain the "why" and confirm the full gate suite + solutions script pass with the new lockfile.
