# 12. Coding Standards (Ordo Project)

These standards are mandatory for all code contributions to the Ordo project. They ensure consistency, quality, and adherence to the project’s architecture, while remaining practical for a solo developer.

## 12.1. Core Standards & Tooling

*   **Language:** Python 3.12 (async-first).
*   **Formatting:** All code must be formatted with `black` (default config).
*   **Linting:** All code must pass linting with `ruff`. Rules defined in `pyproject.toml`.
*   **Type Checking:** All code must pass `mypy` static type checks.
*   **Dependency Management:**
    *   Use Poetry for all dependencies.
    *   Pin versions in `pyproject.toml`.
    *   No direct imports of broker SDKs in core logic — all external APIs must go through adapters.
*   **Automation:** CI/CD (GitHub Actions) will enforce linting, formatting, typing, and testing on every push.

## 12.2. Naming Conventions

| Element | Convention | Example |
| :--- | :--- | :--- |
| Packages & Modules | `snake_case` | `src/ordo/core/orchestrator.py` |
| Classes & Type Aliases | `PascalCase` | `class BrokerError(OrdoError):` |
| Functions & Variables | `snake_case` | `def get_portfolio(...):` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_TIMEOUT = 8` |
| Database Models | `PascalCase` | `class DbSession(SQLModel):` |
| API Schemas (DTOs) | `PascalCase` | `class OrderRequest(BaseModel):` |

## 12.3. Critical Implementation Rules

1.  **Isolate External Calls:**
    *   Core services (e.g., Orchestrator) must not call external APIs directly.
    *   All external communication goes through an `IBrokerAdapter` implementation.
2.  **Use the Repository Pattern:**
    *   Core services must not query databases directly.
    *   All persistence goes through repository interfaces (`persistence/interfaces.py`).
3.  **Strict DTO Usage:**
    *   API endpoints must only expose Pydantic schemas from `models/api_schemas.py`.
    *   Never expose raw database models to clients.
4.  **Centralized Configuration:**
    *   No hardcoded secrets or config values.
    *   All config must be loaded via the `Settings` class in `config.py`.
5.  **Mandatory Redaction:**
    *   No sensitive data (tokens, keys, PII) in logs.
    *   Always pass log payloads through the central `redact()` utility before logging.
6.  **Async Discipline:**
    *   All external I/O must be `async` (`httpx`, `aiosqlite`, etc.).
    *   Blocking calls (`requests`, `time.sleep`) are forbidden.
7.  **Error Handling:**
    *   All raised exceptions must inherit from `OrdoError`.
    *   Do not raise raw Python exceptions from core services.

## 12.4. Testing Standards

*   **Framework:** `pytest`.
*   **Structure:** Tests live under `/tests`, mirroring `src/ordo`. Files named `test_*.py`.
*   **Types of Tests:**
    *   Unit tests for adapters (mock broker APIs).
    *   Integration tests for orchestrator + persistence.
    *   Smoke tests for API endpoints (`/health`, `/status`) in Docker.
*   **Coverage:** Aim for ≥80% coverage (enforced via CI).

## 12.5. Logging & Observability

*   **Library:** `structlog` with JSON formatting.
*   **Context:** Every log entry must include `correlation_id` and, where applicable, `broker_id` and `account_id`.
*   **Levels:**
    *   `INFO`: Request lifecycle events.
    *   `WARNING`: Transient failures (auto-retry, session refresh failed).
    *   `ERROR`: Request failures after retries.
    *   `CRITICAL`: Unexpected system failures.

## 12.6. Documentation & Comments

*   **Docstrings:** Required for all public classes, methods, and functions. Follow Google style for consistency.
*   **When to Comment:**
    *   Business rules or domain-specific quirks.
    *   Workarounds for external limitations.
    *   Non-obvious edge case handling.
*   **When Not to Comment:**
    *   Avoid redundant comments (“increment i by 1”).

## 12.7. Contribution & Workflow

*   **Solo Workflow:** Since this is a solo project, CI/CD automation enforces quality instead of human reviewers.
*   **Contribution Gate:** A commit can only be merged to `main` if:
    *   It passes linting (`ruff`).
    *   It passes formatting (`black --check`).
    *   It passes type checking (`mypy`).
    *   It passes all tests (`pytest`).
*   **Branching:** Use feature branches (`feature/*`, `fix/*`). Merge to `main` only after CI passes.

---
