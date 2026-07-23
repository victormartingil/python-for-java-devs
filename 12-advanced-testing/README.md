# 12 — Advanced testing

**The question this module answers:** *"I have JUnit 5 + Mockito + Testcontainers muscle memory. Where's the equivalent test pyramid for the module 11 app — and what are the non-obvious differences?"*

This module tests **module 11's actual app** — nothing here is rebuilt. The suite imports `app/` from `11-project-architecture/` and adds the two layers the repo hasn't shown yet: mocks and real containers.

## Run it

*Requires: `uv sync --group web`*

```bash
# Everything that doesn't need Docker (mocks + module 11's in-memory tests):
uv run pytest 12-advanced-testing/tests -v

# The testcontainers tests (starts a real Postgres 16 container, destroys it after):
uv run pytest -m docker -v          # skips cleanly if Docker isn't running

# Coverage over module 11's app, with the threshold from pyproject.toml:
uv run pytest 11-project-architecture/tests 12-advanced-testing/tests --cov
```

## The pyramid, applied to a layered app

```
        ╱  few: testcontainers   ╲     repository + real Postgres
       ╱   repo tests (docker)    ╲    — this module, test_repository_with_testcontainers.py
      ╱   some: API tests with     ╲   — module 11, test_layered_api.py
     ╱   in-memory repos (DI swap)  ╲
    ╱   many: pure service tests     ╲  — module 11, test_task_service.py
   ╱   (no framework, no DB, no mocks)╲ + this module, test_service_with_mocks.py
```

The architecture from module 11 is what makes the pyramid cheap: services don't import FastAPI or SQLAlchemy, so most tests are plain function calls over a `Protocol`-shaped repository.

## The JUnit/Mockito/Testcontainers ↔ pytest mapping

| Java / Spring | Python (this repo) | Notes |
|---|---|---|
| `@ExtendWith(MockitoExtension.class)` | nothing — mocks are plain objects | no extension model |
| `@Mock TaskRepository repo` | `AsyncMock(spec=TaskRepository)` | **`AsyncMock`** for async methods — a plain `Mock` returns a `Mock` when awaited, the #1 migration bug |
| `when(repo.get(1)).thenReturn(t)` | `repo.get.return_value = record` | stubbing is attribute assignment |
| `when(...).thenThrow(e)` / `.thenReturn(a, b)` | `repo.get.side_effect = e` / `= [a, b]` | exception instance, or a sequence of per-call results |
| `verify(repo).delete(1)` | `repo.delete.assert_awaited_once_with(1)` | `assert_awaited_*` for async, `assert_called_*` for sync |
| `ArgumentCaptor` | `repo.update.await_args.args` | the recorded call is inspectable directly |
| `InOrder` / `verify(inOrder)` | `repo.mock_calls == [call.create(...), call.delete(1)]` | the full conversation, in order |
| `@InjectMocks` | `TaskService(repo)` — a plain constructor | DI by constructor means no framework magic anywhere |
| `@MockBean` (Spring Boot test) | `app.dependency_overrides[...]` (module 11) | replace the wiring, keep everything real |
| `@BeforeEach` | fixtures (`@pytest.fixture`) | module 07 |
| `@ParameterizedTest` | `@pytest.mark.parametrize` | module 07 |
| `@DataJpaTest` + `@Testcontainers` + `@Container` | `testcontainers-python` + session fixture | `test_repository_with_testcontainers.py` |
| `WireMock` / `MockRestServiceServer` | `patch("module.function")` or `httpx2.MockTransport` | patch **where the name is looked up**, not where it's defined |
| JaCoCo + `mvn verify` | `pytest-cov` + `[tool.coverage]` in pyproject | `--cov` flag; threshold = `fail_under` |

## Mock vs real container: the senior rule

**Repositories → real database via testcontainers.** A mocked repository can only prove your service calls it correctly; it can't prove your SQL, your mappings, your constraints, your flush/commit behavior. Those are exactly the bugs repositories have. `PostgresContainer` boots in ~2 s on a warm machine (the image is the same `postgres:16` the repo's compose files use). Mocking SQLAlchemy sessions is a trap — you end up asserting that mocks call mocks.

**External services → mocks.** HTTP calls to things you don't own (payment gateways, Slack webhooks, other teams' APIs): patch the seam. `notify.py` shows the pattern — one isolated function does the I/O, everything around it is unit-tested by replacing that function. Contract testing (Pact) is the next step when the external API is someone else's and stability matters; out of scope here.

**Services → mostly neither.** A pure service + `InMemoryTaskRepository` (module 11) is a *hand-written fake*, not a mock: no call verification, real behavior. Reach for `AsyncMock` only when you're testing *interaction* ("does the service pass the DTO through untouched?") rather than *outcome*.

## What's in `tests/`

| File | Layer | Technique |
|---|---|---|
| `test_service_with_mocks.py` | service | `AsyncMock` stubbing, call verification, `side_effect`, `patch` vs `patch.object`, the "patch where it's used" rule |
| `test_repository_with_testcontainers.py` | repository | real Postgres 16 in a container, per-test schema reset, flush/commit boundaries — marked **`docker`** |
| `conftest.py` | wiring | sys.path to module 11 + skips `docker` tests when no daemon is up (same pattern as module 10's `postgres` marker) |

The `docker` marker is registered in `pyproject.toml`. In CI (GitHub Actions `ubuntu-latest` has Docker) these tests **run**; on a laptop without Docker they skip with a clear reason.

## Coverage with a threshold

`pyproject.toml` now carries:

```toml
[tool.coverage.run]     # ≈ JaCoCo's <includes>
source = ["11-project-architecture/app"]
branch = true           # branch coverage, not just line coverage

[tool.coverage.report]
fail_under = 80         # the build fails below 80% — like jacoco:check
show_missing = true
```

80% with *branch* coverage on a layered app is a sane floor, not a goal. The number that matters is "are the service's branches and the repository's SQL covered" — which the pyramid above gives you. 100% coverage on this app would mean testing framework plumbing, which is JaCoCo-on-getters energy.

## Common pitfalls for Java devs

- **Awaiting a plain `Mock`.** `Mock()()` returns a `Mock`; `await` on it explodes with a confusing `TypeError: object Mock can't be used in 'await' expression`. Use `AsyncMock` (or `Mock(spec=...)` on a sync protocol). Rule: the mock type matches the *method*, not the class.
- **Patching where it's defined.** `patch("httpx2.post")` doesn't help if the module did `from httpx2 import post` — the consumer has its own reference. Patch `"consumer_module.post"`. This trips up every Java dev once.
- **Mocking what you should containerize.** If the test's value is "does the SQL work", a mock makes the test worthless *and* brittle. Container or nothing.
- **`return_value` vs `side_effect` with async.** Both work on `AsyncMock`; `side_effect = [a, b]` gives per-call results, `side_effect = SomeException()` raises. Setting an *async function* as side_effect is for when you need logic in the fake.
- **Fixture scope mismatch.** The container fixture is `scope="session"` (boot once); the session fixture is per-test (truncate). Making the container per-test would work but turn 2 s into 2 s × N.

## Dig deeper

- unittest.mock — the "where to patch" section is mandatory reading: <https://docs.python.org/3/library/unittest.mock.html#where-to-patch>
- testcontainers-python: <https://testcontainers-python.readthedocs.io/>
- pytest-cov / coverage.py config: <https://coverage.readthedocs.io/en/latest/config.html>
