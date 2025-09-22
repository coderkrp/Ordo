# 3. Tech Stack

| Category | Technology | Version | Purpose | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Language** | Python | 3.12 | Core application language | Modern, async-capable, strong community, and specified in PRD. |
| **Runtime** | Uvicorn | 0.36.0 | ASGI server | High-performance server required to run FastAPI. |
| **Framework** | FastAPI | 0.117.1 | Backend web framework | High performance, built-in data validation, and dependency injection. |
| **Dependency Mgmt** | Poetry | 2.2.1 | Dependency management & packaging | Manages dependencies, virtual envs, and packaging; specified in PRD. |
| **HTTP Client** | HTTPX | 0.28.1 | Asynchronous HTTP requests | Required for performing non-blocking, concurrent fan-out requests to brokers. |
| **Default Database** | SQLite | 3.38+ | Default persistence layer | File-based, no external service needed, perfect for minimal footprint goal. |
| **Optional Database** | PostgreSQL | 15+ | Optional scalable persistence | Robust, open-source SQL database for users needing to scale. |
| **ORM / Persistence Toolkit** | SQLModel | 0.0.8+ | Async ORM + Pydantic-based models | Unifies SQLAlchemy and Pydantic, async support, simplifies repo pattern. |
| **Optional Cache** | Redis | 7.0+ | Optional caching layer | Industry standard for caching and can be used for kill-switch/state stores. |
| **Crypto / Security** | cryptography | 41.0+ | Encrypt sensitive secrets and tokens at rest | Battle-tested Python crypto library; needed for session token encryption. |
| **Linting** | Ruff | 0.1+ | Code linting | Extremely fast linter, ensures code quality and consistency; specified in PRD. |
| **Formatting** | Black | 23.9+ | Code formatting | Enforces a consistent, non-negotiable code style; specified in PRD. |
| **Testing** | Pytest | 7.4+ | Test framework | Standard for Python testing; enables clear, scalable tests for all components. |
| **Testing Utilities** | respx, pytest-asyncio, pytest-cov | latest | Mocking, async testing, coverage | Enable robust async HTTP testing and coverage metrics. |
| **Logging** | structlog | 23.1+ | Structured JSON logging | Provides machine-readable logs for observability and audit requirements. |
| **Metrics / Monitoring** | Prometheus FastAPI Instrumentator | 6.0+ | Metrics collection | Lightweight instrumentation for Prometheus-compatible monitoring. |
| **CLI Framework** | Typer | 0.9+ | CLI for helper scripts (e.g., OTP) | Consistent with FastAPI/SQLModel, provides modern CLI experience. |
| **Containerization** | Docker | 24.0+ | Container runtime | Packages the application and its dependencies for portable deployment. |
| **Local Orchestration** | Docker Compose | 2.20+ | Local orchestration of multi-service setup | Allows developers to spin up Ordo with Postgres/Redis easily. |
| **CI/CD** | GitHub Actions | hosted | Continuous Integration and Delivery | Runs linting, tests, build, and publishing pipelines; automates Docker Hub and PyPI publishing. |
| **DB Migrations** | Alembic | 1.12+ | **Post-MVP:** Database schema migrations | Standard tool for SQLAlchemy/SQLModel for managing schema evolution. |

---
