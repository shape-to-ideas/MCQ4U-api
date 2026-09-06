# MCQ4U Backend — Project Details

## Overview

MCQ4U (Multiple Choice Questions for You) is a quiz/assessment backend. The
vision (from `wiki/Home.md`) is to let an educator add MCQs on any topic to a
portal, and let users (mostly students) attempt those questions. The repo was
bootstrapped from a generic Litestar starter template — the README, Sonar
project key, and static banner asset still reference the template
(`starlite-hello-world`) rather than MCQ4U, and should eventually be cleaned
up.

- **Local folder:** `mcq4u_backend`
- **Actual GitHub repo:** `shape-to-ideas/MCQ4U-api` (per deploy workflow)
- **Author:** `joshi51`

## Tech Stack

| Concern | Choice |
|---|---|
| Language | Python (`>=3.9,<4.0`; Docker image uses 3.11.4) |
| Web framework | [Litestar](https://litestar.dev) `2.0.0rc1` (ASGI) |
| App server | uvicorn / `litestar run` CLI |
| Package manager | Poetry (`pyproject.toml`, `poetry.lock`); `requirements.txt` exported for Docker |
| Database | MongoDB, accessed directly via `pymongo` (no ORM/ODM) |
| Validation/DTOs | Pydantic v2 |
| Auth | JWT (`pyjwt`, HS256) + `bcrypt` password hashing |
| Config | `.env` via `python-dotenv` |
| Lint/format | `ruff` (`ruff.toml`) |
| Type checking | `mypy` (strict, in `pyproject.toml`) |
| Tests | `pytest`, `pytest-asyncio`, `pytest-cov` |
| Static analysis | SonarCloud (`sonar-project.properties`), CodeQL (nightly) |
| Containerization | Docker + docker-compose |
| CI/CD | GitHub Actions — test workflow + SSH deploy to AWS EC2 |

## Project Structure

Feature-folder architecture; each domain module follows the same layering:
**controllers → services → domains (DTOs) → models (DB document shapes)**.

```
app/
  main.py            App factory (create_app), entry point
  db/                DatabaseService — Mongo client + per-collection accessors
  shared/             constants, logger, middlewares, types, utils (cross-cutting)
  user/
    controllers/      UserController (HTTP routes)
    domains/           Pydantic request/response DTOs
    models/            TypedDict Mongo document shapes
    services/           UserService (business logic + Mongo queries/aggregations)
  question/            Same 4-layer pattern, for questions/topics/answers
  stats/               Site-wide stats: StatsController → StatsService → StatsResponse DTO (no models/ — reads existing collections only)
tests/
  test_app.py          Single stub test (not real coverage — see Testing)
wiki/                  GitHub wiki mirror (mostly empty placeholders)
static/                Leftover Litestar template banner asset
.github/workflows/     ci.yaml.txt (disabled), test.yaml, deploy.yml, codeql.yaml, dependabot.yaml
Dockerfile, docker-compose.yml
pyproject.toml, poetry.lock, requirements.txt
pytest.ini, ruff.toml, .flake8, .pre-commit-config.yaml, sonar-project.properties
```

## Entry Point

`app/main.py::create_app()` builds the `Litestar` app:

- Single `Router` mounted at `/api/v1`, registering `UserController`, `QuestionController`, and `StatsController`.
- CORS wide open (`allow_origins=['*']`).
- Custom lifespan handler opens the MongoDB client on startup (`app.state.mongodb_client`) and closes it on shutdown.
- `debug=True` is hardcoded — **not environment-gated**.
- OpenAPI docs configured: title "MCQ4U API Documentation", version `1.0.0`.
- Module-level `app = create_app()`; run directly via `uvicorn.run(app)` (port not configurable — `# @TODO to configure port`) or via `litestar run --host 0.0.0.0 --port 80` in Docker.

## Database (MongoDB)

No ORM — raw `pymongo` driver with aggregation pipelines (`$lookup`, `$expr`)
for joins done at the application layer. Schema is enforced only implicitly
via `TypedDict` models and Pydantic DTOs; collections are created lazily on
first insert (no formal migrations).

`app/db/__init__.py` — `DatabaseService`:
- `get_db_client()` — `MongoClient` using `CONNECTION_URL` env var, TLS via `certifi.where()` (implies MongoDB Atlas).
- Collection accessors: `user_instance()` (`users`), `questions_instance()` (`questions`), `topics_instance()` (`topics`), `answers_instance()` (`answers`), `attempted_questions_instance()` (`attempted_questions`).

**Models (document shapes):**

- `app/user/models` — `Users` (`_id`, `email`, `phone`, `first_name`, `last_name`, `password`, `is_admin`, `attempted_questions`), `AttemptedQuestions` (`_id`, `question_id`, `selected_option`, `user_id`)
- `app/question/models` — `Questions` (`_id`, `title`, `options`, `tags`, `is_active`, `topic_id`, `answer`), `Topics` (`_id`, `name`), `Answers` (`_id`, `question_id`, `correct_option`), `Options` (`_id`, `title`, `key`)

Mongo `ObjectId` serialization is handled via `bson.json_util.dumps`/`json.loads` round-trips rather than a custom JSON encoder.

## API Surface

All routes under `/api/v1` (README's example URLs are stale template text).

**UserController** (tag "Users"):
- `POST /api/v1/user/register` — create a user
- `POST /api/v1/user/login` — `{phone, password}` → `{token}` (JWT)
- `GET /api/v1/user` *(auth)* — current user details from JWT
- `POST /api/v1/user/attempt-questions` *(auth)* — record `[{question_id, option}]`, skipping already-attempted ones
- `GET /api/v1/user/attempted-questions` *(auth)* — `?topic_id=` — attempted questions joined with topic, user's answer, and correct answer

**QuestionController** (tag "Question"):
- `POST /api/v1/questions/create` *(auth)* — bulk-create MCQs (title, options A–E, tags, is_active, topic_id, answer) + their `Answers` record
- `POST /api/v1/questions/topics` *(auth)* — create topics, deduped against existing
- `GET /api/v1/questions` *(auth)* — `?topic_id=&is_active=&question_id=` — fetch by id or topic
- `GET /api/v1/topics` *(auth)* — list all topics

**StatsController** (tag "Stats"):
- `GET /api/v1/stats` *(auth)* — site-wide counters for the frontend's dashboard banner: `total_topics` (count of `topics`), `total_users` (count of `users`), `questions_attempted` (distinct `question_id` in `attempted_questions`), `users_attempted` (distinct `user_id` in `attempted_questions`). Pure read-only aggregate, no new collections.

Core domain concepts: **Users**, **Topics**, **Questions** (with embedded `Options` keyed A–E), **Answers**, **AttemptedQuestions**. There is no dedicated scoring endpoint — a client can compute score by comparing attempted vs. correct answers, both of which `get_attempted-questions` returns together.

## Authentication & Authorization

- Stateless JWT auth (HS256, `pyjwt`). `UserService.login()` issues a token containing `id`, `is_admin`, `first_name`, `last_name`, `email`, `expiry` (30 days), signed with `JWT_SECRET`.
- Passwords hashed with `bcrypt`; salt rounds from `SALT_ROUNDS` env var.
- `app/shared/middlewares.py::AuthorizationMiddleware` — extracts `Authorization: Bearer <token>`, decodes/validates the JWT, manually checks expiry, re-confirms the user still exists in Mongo, injects `scope['user_auth_data']`. Applied per-route (register/login are public; most other routes require it).
- **Gap:** `is_admin` exists on the user model and JWT payload but is not currently enforced anywhere — no role-based route gating yet.

## Configuration

- Root `.env` with `CONNECTION_URL`, `JWT_SECRET`, `SALT_ROUNDS`.
- Loaded independently via `load_dotenv()` in several modules (`main.py`, `db/__init__.py`, both `services` modules) — mildly redundant but harmless.
- **Latent bug**: `app/db/__init__.py` builds its dotenv path as `join(dirname(__file__), '.env')`, i.e. it looks for `app/db/.env` (which doesn't exist) rather than the project-root `.env`. It currently works only because `main.py` imports `app.db` and then separately calls a path-less `load_dotenv()` early enough that `CONNECTION_URL` ends up set in `os.environ` before `DatabaseService` needs it in most run configurations. Running `db/__init__.py`'s module-level `os.getenv('CONNECTION_URL')` in a context where that hasn't happened yet (e.g. a different import order, or a script that imports `app.db` directly) raises `pymongo.errors.ConfigurationError: No default database defined`. Not yet fixed — flagging for whoever touches env loading next.
- No separate dev/staging/prod profiles; deploy workflow regenerates `.env` from GitHub Actions secrets on the EC2 host at deploy time.

## Testing

- `pytest` + `pytest-asyncio` + `pytest-cov`, configured across `pytest.ini` and `pyproject.toml` (`addopts = "--cov=app -v"`).
- Only `tests/test_app.py` exists, with a single test (`test_create_user`) that: hits a stale route not matching the real `/api/v1` prefix, is missing an `await` before `.json()`, and asserts a tautology (`1 == 1`).
- **Effectively no real test coverage** — this is leftover template scaffolding, not a genuine suite.

## Build & Deploy

- `Dockerfile`: `python:3.11.4-slim-bookworm`, installs `requirements.txt`, exposes port 80, runs `litestar run --host 0.0.0.0 --port 80`.
- `docker-compose.yml`: single `mcq4u-api` service, env/build-args for `CONNECTION_URL`/`JWT_SECRET`/`SALT_ROUNDS`, maps `80:80`.
- `.github/workflows/deploy.yml`: on push to `main` touching `app/**`, SSHes into an AWS EC2 host, pulls `shape-to-ideas/MCQ4U-api.git`, regenerates `.env` from secrets, runs `docker compose up --build -d`.
- `.github/workflows/test.yaml`: reusable pytest job (Poetry-based, configurable Python/OS matrix).
- `.github/workflows/ci.yaml.txt`: present but disabled (`.txt` extension).
- `.github/workflows/dependabot.yaml`, `codeql.yaml`: dependency updates and nightly security scanning.

## Known Gaps / TODOs

- No caching layer, queueing, email/notification service, or file storage, despite an `email` field existing on users.
- `debug=True` hardcoded in `create_app()` (should be env-gated for production).
- `# @TODO to configure port` in `app/main.py`.
- `# @TODO fix return type for all` in `app/question/controllers/__init__.py` — many methods return bare `Any`.
- `# @TODO need to be optimised` above `generate_options_list` in `app/question/services/__init__.py`.
- `is_admin` flag not enforced by any route — no real authorization tiers yet.
- `app/db/__init__.py`'s `load_dotenv()` call points at a non-existent `app/db/.env` instead of the project root `.env` (see Configuration) — currently masked by import order, but fragile.
- README, Sonar project key, and static banner still reference the original Litestar template, not MCQ4U.
- `wiki/Local_Setup.md` and `wiki/modules/Users.md` are empty placeholders.
- Test suite needs to be built essentially from scratch.
