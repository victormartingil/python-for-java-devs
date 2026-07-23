# CHEATSHEET — Java ↔ Python master table

The one page to bookmark. Every row is expanded in the linked module.

## Toolchain & frameworks

| Java / Spring | Python | Module |
|---|---|---|
| Maven / Gradle (`pom.xml`) | `uv` + `pyproject.toml` + `uv.lock` | [00](00-setup-and-running/), [07](07-real-project-uv-pytest-mypy/) |
| `mvn spring-boot:run` | `uv run uvicorn app.main:app --reload` | [08](08-fastapi-crud/) |
| Spring Boot | FastAPI | [08](08-fastapi-crud/)–[11](11-project-architecture/) |
| `@RestController` / `@GetMapping` | `APIRouter` / `@router.get` | [08](08-fastapi-crud/) |
| `@Service` / UseCase | Plain functions/classes in `services/` (no annotations) | [08](08-fastapi-crud/), [11](11-project-architecture/) |
| DI with `@Autowired` | `Depends(...)` | [09](09-fastapi-pro-di-auth-config/) |
| DTOs / records + Bean Validation | Pydantic `BaseModel` + `Field(...)` | [08](08-fastapi-crud/) |
| `application.yml` + `@ConfigurationProperties` | `pydantic-settings` + `.env` | [09](09-fastapi-pro-di-auth-config/) |
| Spring Security (JWT) | `OAuth2PasswordBearer` + **PyJWT** + pwdlib (Argon2) | [09](09-fastapi-pro-di-auth-config/) |
| Spring Data JPA / Hibernate | SQLAlchemy 2.0 ORM (async) | [10](10-persistence-sqlalchemy-alembic/) |
| JdbcTemplate | SQLAlchemy Core | [10](10-persistence-sqlalchemy-alembic/) |
| Flyway / Liquibase | Alembic | [10](10-persistence-sqlalchemy-alembic/) |
| Hexagonal architecture (ports & adapters) | Layered-by-domain architecture + DI; `typing.Protocol` when you want explicit contracts | [04](04-oop-classes-and-protocols/), [11](11-project-architecture/) |
| `@Async` / JMS queues | `BackgroundTasks` / Dramatiq + Redis | [14](14-production-docker-ci/) |
| SLF4J + Logback | `logging` / `structlog` | [14](14-production-docker-ci/) |
| Actuator `/health` | Hand-rolled endpoint + middlewares | [14](14-production-docker-ci/) |
| Spring AI | Official SDK / LangChain / LangGraph / MCP | [13](13-ai-llms-rag-agents/) |

## Language constructs

| Java | Python | Module |
|---|---|---|
| `interface` / `implements` | `typing.Protocol` + duck typing | [04](04-oop-classes-and-protocols/) |
| Lombok `@Data` / records | `@dataclass` / Pydantic | [04](04-oop-classes-and-protocols/) |
| `Optional<T>` | `T \| None` | [01](01-python-essentials/) |
| `List` / `Map` / `Set` | `list` / `dict` / `set` (+ `tuple`) | [02](02-collections-and-comprehensions/) |
| Stream API (`map`/`filter`/`collect`) | Comprehensions + `itertools` | [02](02-collections-and-comprehensions/) |
| Lambdas / functional interfaces | First-class functions, `lambda` | [03](03-functions-and-decorators/) |
| AOP / annotations with behavior | Decorators | [03](03-functions-and-decorators/) |
| Checked exceptions | All exceptions unchecked; EAFP style | [05](05-errors-and-context-managers/) |
| try-with-resources | `with` (context managers) | [05](05-errors-and-context-managers/) |
| `CompletableFuture` / virtual threads | `asyncio` / `await` (single-threaded event loop; GIL + 3.13 free-threading explained) | [06](06-async-and-concurrency/) |
| switch expressions | `match` / `case` | [01](01-python-essentials/) |
| `public static void main` | `if __name__ == "__main__":` | [00](00-setup-and-running/) |
| JUnit 5 + Mockito | pytest + fixtures + `unittest.mock` | [07](07-real-project-uv-pytest-mypy/), [12](12-advanced-testing/) |
| `@BeforeEach` | pytest fixtures | [07](07-real-project-uv-pytest-mypy/) |
| `@ParameterizedTest` | `@pytest.mark.parametrize` | [07](07-real-project-uv-pytest-mypy/) |
| MockMvc / WebTestClient | FastAPI `TestClient` (built on **httpx2** in starlette 1.3+); `httpx2.AsyncClient` + `ASGITransport` for async DB tests | [08](08-fastapi-crud/), [12](12-advanced-testing/) |
| Testcontainers | `testcontainers-python` | [12](12-advanced-testing/) |

## Gotchas for Java developers

The traps that bite everyone in week one:

| Gotcha | What happens | The rule |
|---|---|---|
| **Mutable default arguments** | `def f(x, acc=[])` — the list is created **once** at function definition and shared across calls. | Use `None` as default, create the object inside: `def f(x, acc=None): acc = acc or []` |
| **`==` vs `is`** | `==` compares values (like `.equals()`); `is` compares identity (like Java `==` on references). | Almost always want `==`. Exception: `x is None`. |
| **Indentation is syntax** | No braces. A misaligned block is a different program — or a syntax error. | 4 spaces, always. Let ruff format for you. |
| **No semicolons, no `new`, no type declarations** | `task = Task("x")`, not `Task task = new Task("x");` | Types live in *hints*: `def f(task: Task) -> None`. |
| **Everything is an object** | Functions, classes, modules — all can be assigned, passed, stored. | This is why decorators and `Depends` work. |
| **Mutability by default** | Lists/dicts are mutable and passed by reference — no `final`, no defensive copying culture. | Return new collections; use `tuple`/`frozenset` for immutability. |
| **Truthiness** | Empty list/dict/string, `0`, `None` are all *falsy* — no explicit `isEmpty()` needed. | `if tasks:` not `if len(tasks) > 0:`. But `if x is not None:` when `0`/`""` are valid values. |
