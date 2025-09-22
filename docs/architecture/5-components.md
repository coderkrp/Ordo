# 5. Components

## 5.1. Request Orchestrator — Specification

**Purpose:** The central brain that accepts validated API requests and executes end-to-end business logic (fan-out to brokers, resilience, idempotency, collation, auditing) while keeping responsibilities bounded and testable.

**1. High-level responsibilities (summary)**
*   Check global safety gates (kill-switch, authorization context).
*   Handle idempotency for write operations (orders).
*   Perform pre-trade validation (instrument, margin/funds) before any broker calls.
*   Fan out requests concurrently to selected broker adapters.
*   Enforce per-broker timeouts, per-call retries with exponential backoff + jitter, and circuit breaker checks.
*   Collate per-broker results into a UnifiedResponse that captures overall status and per-broker detail.
*   Emit audit events at well-defined lifecycle points.
*   Delegate session/login flows to SessionManager (not handle low-level OTP logic itself).
*   Expose an interface testable in isolation from adapters (dependency injection/mocks).

**2. Key design principles**
*   Small surface area: Orchestrator coordinates, it does not implement broker logic (adapters do).
*   Deterministic outcomes: Idempotency & clear error codes so clients and automation can react reliably.
*   Fail-fast safety: Check kill-switch and pre-trade validations early to avoid unnecessary side-effects.
*   Observable: Correlation IDs, structured audit points, and metrics for latency/ success rates.
*   Configurable resilience: Per-adapter timeout, retry, and circuit breaker config.
*   Testable: All external dependencies injected, with strong unit/integration test coverage using HTTPX/respx mocks.

**3. API / Public Interfaces (types)**
*   Use Pydantic DTOs for request/response shapes.
  *   `execute_order(order: OrderRequest, brokers: list[str], context: RequestContext) -> UnifiedResponse`
  *   `get_portfolio(accounts: list[Account], context: RequestContext) -> UnifiedResponse`
  *   `initiate_login(account: Account) -> LoginInitiationResult` (delegates to SessionManager)
  *   `submit_otp(account: Account, otp: str) -> SessionStatus` (delegates to SessionManager)

**UnifiedResponse (Pydantic)**
```python
class BrokerResult(BaseModel):
    broker_id: str
    status: Literal["success","failed","pending"]
    code: Optional[str]  # standardized error code e.g., INSUFFICIENT_FUNDS
    message: Optional[str]
    payload: Optional[dict]  # broker-specific details (order id, etc.)
    latency_ms: Optional[int]

class UnifiedResponse(BaseModel):
    overall_status: Literal["success","partial_success","failure"]
    results: List[BrokerResult]      # one entry per targeted broker
    correlation_id: str
    elapsed_ms: int
    errors: Optional[List[ApiError]] # aggregated errors if any
```

**4. Execution flow (detailed, step-by-step)**
*   Receive request with validated OrderRequest and RequestContext (includes correlation id, authenticated principal).
*   Check Kill-Switch (persistent store or in-memory): if active, return `overall_status: failure` with `error_code: KILL_SWITCH_ACTIVE`.
*   Idempotency check (for write ops):
    *   If `Idempotency-Key` header present, consult `DbIdempotencyRecord`.
    *   If found and within TTL → return cached `UnifiedResponse`.
    *   Else reserve key (atomic insert) and continue.
*   Pre-trade validation (orders only): instrument existence/tradability + margin/funds check per account. If validation fails → return fast rejection (no broker calls).
*   Compute target adapter list based on `brokers` parameter and adapters' session status. Skip adapters that are offline/unavailable (annotate result as failed with code `ADAPTER_UNAVAILABLE`).
*   Per-broker operation pipeline (executed concurrently, but each adapter call follows this pattern):
    a. Check circuit breaker state; if OPEN → short-circuit to failed `BrokerResult` code `CB_OPEN`.
    b. Perform call with per-broker timeout (configurable). Use `httpx` with timeout.
    c. Retries: use exponential backoff + jitter for retriable error codes (e.g., 429, 5xx). Limit retries per broker (configurable).
    d. Collect broker response; map to `BrokerResult` with normalized code/message and latency.
*   Collation: gather all `BrokerResult` objects. Compute `overall_status`:
    *   `success` = all success;
    *   `partial_success` = at least one success and at least one failure;
    *   `failure` = all failed.
*   Persistence: store idempotency record (with `UnifiedResponse` snapshot) before returning to client (ensure durable response for retries).
*   Audit: emit audit events for Request Received, Pre-trade validation result, Broker Calls (start/finish per broker), Final Result. These must include correlation id and truncated payloads (no secrets).
*   Return `UnifiedResponse` with HTTP status codes: 200 for success, 207 for partial success (recommended), 400/4xx/503 for final failure depending on cause.

**5. Resilience & retry semantics (concrete)**
*   Per-broker timeout default: 8s (configurable).
*   Retry policy default: 3 attempts max, exponential backoff base 0.5s, multiplier 2, jitter 0.1–0.5s. Retries apply to network timeouts, 5xx, 429.
*   Circuit breaker per adapter: open after N failures in M seconds (e.g., 5 failures in 60s). Half-open probe allowed after T seconds. Configurable thresholds. Circuit breaker state stored in memory and optionally backed by Redis for multi-instance.
*   Backpressure / rate limiting: enforce per-adapter concurrency limits (Semaphore) and per-adapter rate limiters (token bucket). Configurable in adapter config.

**6. Idempotency details**
*   Key source: client `Idempotency-Key` header (required for clients that want dedup guarantee).
*   Store: `DbIdempotencyRecord` persisted with `response_snapshot_json` and `expires_at`.
*   Atomic reservation: use DB unique constraint to avoid race conditions (insert only if not exists).
*   TTL: default 24 hours (configurable). Cleanup job to prune expired keys.
*   Behavior: If same key seen after expiration → treated as new request.

**7. Pre-trade validation rules (minimum for MVP)**
*   Verify instrument exists and is tradable on the broker (use adapter metadata).
*   Verify account has sufficient cash/margin (query adapter session or session cache). For multi-broker orders, ensure the specific account for that broker has required resources (if order targets specific accounts).
*   Return clear, standardized error codes: `INVALID_INSTRUMENT`, `INSUFFICIENT_FUNDS`, `BROKER_NOT_AUTHENTICATED`.

**8. Audit & observability (hook points)**
*   Emit audit entries at these points (include `correlation_id`, `actor`, brief payload, and non-sensitive metadata):
    *   `request.received` (incoming payload)
    *   `request.pretrade.validated` (pass/fail + reason)
    *   `broker.call.started` (broker_id, attempt_no)
    *   `broker.call.finished` (broker_id, status, latency_ms, mapped_code)
    *   `request.result` (final `UnifiedResponse`)
*   Metrics to emit (Prometheus): per-api latency histogram, per-broker success rate, retry counts, circuit breaker trips, idempotency cache hit rate.

**9. Error mapping & codes**
*   Use standardized error codes across Ordo (not raw broker strings): e.g., `INVALID_OTP`, `RATE_LIMIT`, `TIMEOUT`, `CB_OPEN`, `INSUFFICIENT_FUNDS`, `KILL_SWITCH_ACTIVE`.
*   Include `broker_raw_code` inside `BrokerResult.payload` for diagnostics.
*   All API errors must contain `correlation_id` so clients can share when reporting incidents.

**10. Security considerations**
*   Never log secrets or full tokens — redact in audit payloads.
*   All outbound calls use TLS and configured per-adapter client certificates if present.
*   Ensure persisted idempotency response snapshots do not include secrets.
*   Time sync: validate host clock at startup; warn if drift > threshold (some broker APIs require synced timestamp).

**11. Concurrency & performance guidance**
*   Use `asyncio.gather` with `return_exceptions=False` and per-task timeout wrappers.
*   Use per-adapter semaphores for concurrency control to avoid runaway parallelism on limited instances (1 vCPU/1GB). Example: limit to 4 concurrent calls per adapter by default.
*   Keep bridge overhead minimal: measuring only orchestration cost (exclude broker RTT) — aim for median orchestration overhead ≤50ms (NFR1). Instrument and optimize hot paths if approaching limits.
*   For heavy fan-out across many brokers, ensure orchestrator imposes a global response SLA (e.g., overall timeout of 12s) to keep caller experience bounded.

**12. Testing strategy (for orchestrator)**
*   Unit tests:
    *   Mock adapters with deterministic behaviors (success, transient 5xx, non-retriable 4xx).
    *   Test idempotency behavior (reserve + cached response).
    *   Test kill-switch behavior (reject early).
*   Integration tests:
    *   Use `respx` to mock HTTP responses from adapters.
    *   Validate backoff/retry counts and circuit breaker transitions.
*   Load tests (optional):
    *   Simulate N parallel `execute_order` requests to validate semaphores and orchestration latency.
*   Acceptance: Add tests asserting `UnifiedResponse` mapping and error code normalization.

**13. Configuration knobs (example)**
*   `orchestrator.global_timeout_ms = 12000`
*   `adapter.<broker>.timeout_s = 8`
*   `adapter.<broker>.retries = 3`
*   `adapter.<broker>.concurrency = 4`
*   `idempotency.ttl_hours = 24`
*   `circuit_breaker.failure_threshold = 5`
*   `circuit_breaker.window_seconds = 60`
*   `circuit_breaker.reset_seconds = 120`
*   All config surfaced via Pydantic Settings and overridable by ENV/YAML.

**14. Minimal pseudocode**
```python
async def execute_order(order, brokers, context):
    correlation_id = context.correlation_id
    start = now()
    if killswitch.is_active():
        return UnifiedResponse(... overall_status="failure", errors=[KILL_SWITCH_ACTIVE])

    if order.has_idempotency_key():
        cached = db.get_idempotency(order.idempotency_key)
        if cached:
            return cached.response

    valid, reason = pretrade_validator.validate(order)
    if not valid:
        return UnifiedResponse(... overall_status="failure", errors=[reason])

    # select and filter adapters
    adapters = [registry.get(b) for b in brokers if registry.is_available(b)]

    # fan-out
    tasks = [run_for_adapter(adapter, order, correlation_id) for adapter in adapters]
    results = await asyncio.gather(*tasks, return_exceptions=False)  # per adapter handles its own timeout/retries

    unified = collate_results(results, correlation_id, elapsed_ms=elapsed(start))
    if order.has_idempotency_key():
        db.store_idempotency(order.idempotency_key, unified, ttl=config.idempotency_ttl)

    audit.emit("request.result", unified)
    return unified
```
`run_for_adapter` wraps circuit breaker checks, per-adapter semaphore, retry with tenacity or custom backoff, and maps broker response to `BrokerResult`.

**15. Extensibility & separation of concerns**
*   SessionManager: handles login/OTP flows and session persistence; orchestrator calls it to check adapter authentication status.
*   Adapter contract: adapters only implement `place_order`, `get_portfolio`, etc., and map broker responses into standard `OrderResult`.
*   Orchestrator remains thin coordinator — easy to move into a separate process if load demands in future.

**16. Acceptance criteria (short)**
*   Orchestrator returns `UnifiedResponse` for representative order with one successful adapter and one transient failure → `overall_status = "partial_success"`.
*   Idempotency key reused within TTL returns cached response (no broker calls).
*   Kill-switch active leads to immediate `KILL_SWITCH_ACTIVE` error without any broker calls.
*   Circuit breaker trips after configured failures and causes short-circuit responses.
*   Audit events emitted at all lifecycle hooks listed.

---

## 5.2. Broker Adapter Interface (IBrokerAdapter)

**1. Purpose & Core Principles**

The `IBrokerAdapter` defines the contract that all broker-specific implementations must follow. It abstracts away broker quirks and provides Ordo with a consistent, reliable interface for trading operations, portfolio data, and session management.

*   **Abstraction** — Each adapter encapsulates broker-specific endpoints, request/response formats, and quirks.
*   **Standardization** — Adapters translate raw broker data into Ordo’s standardized Pydantic DTOs (Portfolio, OrderResult, ApiError).
*   **Isolation** — Adapters are independent. They do not know about the Orchestrator, SessionManager, or other adapters.
*   **Consistency** — Every adapter behaves predictably across login, portfolio fetch, and order placement.

**2. Interface Definition (Python `abc`)**
```python
from abc import ABC, abstractmethod
from typing import Optional
from schemas import (
    OrderRequest,
    OrderResult,
    Portfolio,
    SessionStatus,
    LoginInitiationResult,
    ApiError,
)
from config import BrokerConfig


class IBrokerAdapter(ABC):
    """
    Formal contract for all broker adapters.
    """

    def __init__(self, config: BrokerConfig):
        """
        Initialize adapter with validated configuration.
        Each adapter instance is typically bound to a single account.
        """
        self.config = config

    @property @abstractmethod
    def broker_id(self) -> str:
        """Unique slug for the broker (e.g., 'fyers', 'hdfc_sec')."""

    # --- Trading Operations ---
    @abstractmethod
    async def place_order(self, order: OrderRequest, context: dict) -> OrderResult:
        """
        Place an order with the broker.
        Must map Ordo order fields (e.g., symbol, type, side) to broker-specific API fields.
        Should raise BrokerError on unrecoverable failures.
        """

    # --- Portfolio & Data ---
    @abstractmethod
    async def get_portfolio(self, context: dict) -> Portfolio:
        """
        Retrieve the user's full portfolio (positions, holdings, balances).
        Should map broker-specific response into Ordo's standardized Portfolio DTO.
        """

    # --- Session Lifecycle ---
    @abstractmethod
    async def initiate_login(self) -> LoginInitiationResult:
        """
        Start the broker’s login flow (e.g., generate login URL, OTP request).
        Typically called by SessionManager.
        """

    @abstractmethod
    async def complete_login(self, auth_code: str) -> SessionStatus:
        """
        Complete login with OTP or auth code.
        Should return a standardized SessionStatus object containing access token
        and expiry information.
        """

    async def refresh_session(self) -> Optional[SessionStatus]:
        """
        (Optional) Refresh session using a refresh token.
        Default implementation raises NotImplementedError if broker does not support it.
        """
        raise NotImplementedError("This broker does not support refresh_session")

    @abstractmethod
    async def get_session_status(self) -> SessionStatus:
        """
        Return whether the current session is valid.
        Must detect expired or invalidated sessions.
        """
```

**3. Error Handling Strategy**

*   All adapter methods must raise `BrokerError` (a common Ordo exception) on unrecoverable failures.
*   Transient errors (timeouts, rate limits) should be raised with specific error codes so the Orchestrator can retry.
*   `ApiError` mapping: Adapters map broker error codes → Ordo’s standardized `ApiError` schema for consistency.

**4. Responsibilities of an Adapter Implementer**

When creating a new adapter (e.g., `ZerodhaAdapter`), the implementer must:
*   **Subclass `BrokerConfig`**: Define required credentials and broker-specific config.
*   **Implement `IBrokerAdapter`**: Provide working methods for login, portfolio, and order placement.
*   **Handle Authentication**: Correctly implement `initiate_login` / `complete_login`. Implement `refresh_session` only if supported.
*   **Map Data Models**: Translate broker responses → `Portfolio`, `OrderResult`.
*   **Map Errors**: Translate broker-specific HTTP and error codes → Ordo `ApiError`.
*   **Testing**: Provide unit tests using `respx` to mock broker APIs. Adapters must pass Ordo’s shared adapter contract test suite.

**5. Account Scoping**

*   Each adapter instance is typically bound to one broker account.
*   If a broker supports multi-account management, the adapter may internally multiplex, but this must be explicitly documented.

---

## 5.3. Session Manager

**1. Purpose and Core Responsibilities**

The Session Manager is the sole authority within Ordo for managing the lifecycle of broker authentication sessions.
*   **State Management** — Owns all reads/writes to `DbSession`.
*   **Flow Orchestration** — Drives login/refresh flows by invoking adapter methods (`initiate_login`, `complete_login`, `refresh_session`).
*   **Security** — Ensures tokens are encrypted at rest, decrypted only when required.
*   **Validation** — Provides a unified interface to check if a session is valid before broker calls.
*   **Concurrency Safety** — Ensures that refresh operations are not duplicated across concurrent requests.

**2. Key Design Principles**
*   **Encapsulation** — Other components never see raw tokens or persistence details.
*   **Coordination, Not Implementation** — Session Manager orchestrates flows; adapters implement broker specifics.
*   **Centralization** — Avoids scattered login/refresh logic.
*   **Resilience** — Handles session expiry gracefully and retries intelligently.
*   **Least Privilege** — Tokens decrypted only just-in-time for adapter use.

**3. Public Interface**
```python
from typing import Optional
from schemas import LoginInitiationResult, SessionStatus, SessionCheckResult

class SessionManager:
    """
    Manages the lifecycle of broker authentication sessions.
    """

    def __init__(self, repository: SessionRepository, crypto: CryptoService, adapter_registry: AdapterRegistry):
        self.repository = repository
        self.crypto = crypto
        self.adapter_registry = adapter_registry
        self._locks = {}  # concurrency control per (broker_id, account_id)

    async def initiate_login(self, account_id: str, broker_id: str) -> LoginInitiationResult:
        """
        Start the login flow for a given account by calling the adapter’s initiate_login().
        """
        ...

    async def complete_login(self, account_id: str, broker_id: str, auth_code: str) -> SessionStatus:
        """
        Complete the login flow, encrypt new tokens, and persist session.
        """
        ...

    async def ensure_valid_session(self, account_id: str, broker_id: str) -> SessionCheckResult:
        """
        High-level check for orchestrator:
          1. Retrieve persisted session.
          2. If expired, attempt refresh (with concurrency-safe lock).
          3. Return a SessionCheckResult with status and reason.
        """
        ...

    async def get_session_status(self, account_id: str, broker_id: str) -> SessionStatus:
        """
        Retrieve persisted session status for an account.
        """
        ...

    async def _get_decrypted_token(self, account_id: str, broker_id: str) -> str:
        """
        Internal: Retrieve and decrypt token for adapter use.
        Not intended for external calls; orchestrator should always use ensure_valid_session first.
        """
        ...
```

**4. Supporting Types**
```python
class SessionCheckResult(BaseModel):
    status: str  # "valid", "expired", "refresh_failed", "unsupported"
    reason: Optional[str] = None
    session_status: Optional[SessionStatus] = None
```
This makes Orchestrator decisions explicit:
*   `valid` → safe to proceed
*   `expired` / `refresh_failed` → fail fast or bubble up error
*   `unsupported` → only manual re-login possible

**5. High-Level Execution Flows**
*   **A. Initial Login Flow**
    *   API route `/api/v1/auth/{broker}/{account}/login` → `SessionManager.initiate_login`.
    *   Session Manager fetches adapter, calls `adapter.initiate_login()`.
    *   Returns a `LoginInitiationResult` (e.g., login URL).
    *   After OTP/auth, client calls `/api/v1/auth/callback`.
    *   API route → `SessionManager.complete_login(auth_code)`.
    *   Adapter returns tokens → encrypted → persisted as `DbSession`.
*   **B. Reactive Refresh Flow**
    *   Orchestrator → `ensure_valid_session`.
    *   If token valid → return `SessionCheckResult(status="valid")`.
    *   If expired → acquire lock for (`broker_id`, `account_id`).
    *   Call `adapter.refresh_session()`.
        *   If success → encrypt/persist → return `SessionCheckResult(status="valid")`.
        *   If not supported → return `SessionCheckResult(status="unsupported")`.
        *   If failed → return `SessionCheckResult(status="refresh_failed", reason=...)`.

**6. Error Handling Strategy**
*   Explicit Result Objects instead of `bool` → more diagnosable.
*   Transient vs unrecoverable errors bubble up via `SessionCheckResult.reason`.
*   Locking ensures refresh only happens once per account/broker at a time.

**7. Testing Expectations**
*   Unit tests must cover:
    *   Initial login flow success/failure.
    *   Expired token → refresh success.
    *   Expired token → refresh failure.
    *   Expired token → broker does not support refresh.
    *   Concurrency test → two refresh calls result in a single refresh attempt.

---

## Persistence Component — Final Specification

**1. Purpose and Core Responsibilities**

The Persistence Service implements the Repository Pattern, creating an abstraction layer between Ordo’s business logic and the underlying database (SQLite for default, PostgreSQL for scale).

*   **Responsibilities:**
    *   Decouple business logic from DB dialect (SQLite/Postgres).
    *   Provide a uniform contract for CRUD operations on session, idempotency, audit, and kill-switch data.
    *   Ensure encrypted-at-rest token storage.
    *   Support easy mocking for unit testing.

**2. Core Design & Implementation**

*   **ORM/Library:** `SQLModel` (Pydantic + SQLAlchemy) for schema + ORM.
*   **Async-first:** All repository methods are `async`.
*   **DI-friendly:** Repositories provided via FastAPI dependency injection.
*   **Security Boundary:** Repositories only ever persist encrypted tokens. Encryption/decryption happens at the `SessionManager` layer, not here.

**3. Repository Interfaces (ABC)**

All repository interfaces are defined as abstract base classes (ABCs).

**`ISessionRepository`**
```python
class ISessionRepository(ABC):
    """
    Interface for storing and retrieving broker sessions.
    Tokens passed to persistence are always encrypted.
    """
    @abstractmethod
    async def get_session(self, broker_id: str, account_id: str) -> Optional[DbSession]: ...
    @abstractmethod
    async def save_session(self, session: DbSession) -> DbSession: ...
    @abstractmethod
    async def delete_session(self, broker_id: str, account_id: str) -> None: ...
```

**`IIdempotencyRepository`**
```python
class IIdempotencyRepository(ABC):
    """ Interface for idempotency records. """
    @abstractmethod
    async def get_record(self, key: str) -> Optional[DbIdempotencyRecord]: ...
    @abstractmethod
    async def create_record(self, record: DbIdempotencyRecord) -> DbIdempotencyRecord:
        """ Must raise IntegrityError if key already exists. Handled at service layer. """
        ...
```

**`IAuditLogRepository`**
```python
class IAuditLogRepository(ABC):
    """
    Interface for optional audit log persistence to a database.
    The application supports both 'file' and 'database' audit backends,
    configurable at runtime. 'file' is the default for MVP.
    """
    @abstractmethod
    async def save_entry(self, entry: DbAuditLogEntry) -> DbAuditLogEntry: ...
```

**`IKillSwitchRepository`**
```python
class IKillSwitchRepository(ABC):
    """ Interface for kill-switch persistence. """
    @abstractmethod
    async def get_state(self) -> bool: ...
    @abstractmethod
    async def set_state(self, enabled: bool) -> None: ...
```

**3.1. Supporting Data Models**

While most data models are defined in the global Data Model Strategy, the `KillSwitch` is a simple state managed here.

```python
from sqlmodel import SQLModel, Field

class DbKillSwitch(SQLModel, table=True):
    """ A simple model to hold the global kill-switch state. """
    id: Optional[int] = Field(default=1, primary_key=True)
    is_active: bool = Field(default=False)
```

**4. Concrete Implementations (SQLite Default)**

The `SqliteKillSwitchRepository` will operate on the `DbKillSwitch` model, typically on the single row where `id=1`. Other repos (SqliteSessionRepository, SqliteIdempotencyRepository, etc.) follow the patterns previously discussed.

**Example: `SqliteSessionRepository`**
```python
class SqliteSessionRepository(ISessionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_session(self, broker_id: str, account_id: str) -> Optional[DbSession]:
        statement = select(DbSession).where(DbSession.broker_id == broker_id, DbSession.account_id == account_id)
        result = await self.session.exec(statement)
        return result.one_or_none()

    async def save_session(self, session: DbSession) -> DbSession:
        self.session.add(session)
        await self.session.commit()
        await self.session.refresh(session)
        return session

    async def delete_session(self, broker_id: str, account_id: str) -> None:
        db_session = await self.get_session(broker_id, account_id)
        if db_session:
            await self.session.delete(db_session)
            await self.session.commit()
```

**5. Database Engine & Session Management**

*   The `DATABASE_URL` will be loaded from the application's configuration (e.g., environment variables) to allow easy switching between SQLite and PostgreSQL.
*   A single `AsyncEngine` is created at startup.
*   A new `AsyncSession` is provided per-request via a FastAPI dependency.

```python
# In database.py
from sqlmodel import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from collections.abc import AsyncGenerator
from app.config import settings # Example of loading config

# The DATABASE_URL is loaded from configuration
engine = create_async_engine(settings.DATABASE_URL, echo=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session
```

**6. Migration & Schema Evolution**

*   **SQLite (MVP):** For simplicity, MVP assumes dropping/rebuilding the schema if models change.
*   **Postgres (scale-up):** Future migration support via Alembic is expected.

**7. Concurrency & Transactionality**

*   Idempotency records must rely on DB uniqueness constraints (`key UNIQUE`).
*   Session writes must use transactions to avoid race conditions.
*   The `SqliteKillSwitchRepository` will use a transaction to ensure atomic updates to the state.

**8. Testing Strategy**

*   Provide in-memory repositories (e.g., `InMemorySessionRepository`) for fast unit tests.
*   Integration tests will cover both SQLite and (optionally) Postgres backends.
*   Contract tests will ensure all repository implementations satisfy their ABCs.

---

## 5.5. Other System Components — Final Specification

This section defines the remaining high-level components that support the core application logic.

### **1) API Server (FastAPI) — Refined Spec**

**1. Responsibility (concise)**
*   1.1. Expose versioned REST endpoints (`/api/v1/*`) implementing the Ordo contract.
*   1.2. Validate input with Pydantic DTOs and enforce the standardized `ApiError` response schema on all errors.
*   1.3. Inject security context (via Auth Middleware) and `correlation_id` into each request.
*   1.4. Route validated requests to the service layer (Orchestrator, SessionManager).
*   1.5. Provide size limits, request rate limits, and response time SLAs.

**2. Key Endpoints (initial)**
*   2.1. `GET /health`: An unauthenticated liveness probe that returns a simple HTTP 200 OK if the server is running.
*   2.2. `GET /api/v1/status`: An authenticated readiness probe that provides detailed system health, including adapter connectivity status.
*   2.3. `GET /api/v1/portfolio`: Unified portfolio (query param `brokers=` optional).
*   2.4. `POST /api/v1/orders`: Place orders; accepts `Idempotency-Key` header.
*   2.5. `POST /api/v1/killswitch`: Admin toggle (auth required).
*   2.6. `POST /api/v1/auth/{broker}/{account}/login` and callback endpoints for login flows.
*   2.7. `POST /api/v1/auth/report` (Optional): Receives and logs the final summary report from the OTP Helper CLI for audit purposes.

**3. Error contract (mandatory)**
*   3.1. All errors must serialize to `ApiError` JSON: `{"error_code": "STRING", "message": "Human friendly", "details": {...}, "correlation_id": "UUID"}`
*   3.2. Use consistent canonical codes (e.g., `INVALID_REQUEST`, `KILL_SWITCH_ACTIVE`, `IDEMPOTENCY_VIOLATION`, `INVALID_SESSION`, `RATE_LIMIT`, `TIMEOUT`, `PARTIAL_SUCCESS`).

**4. Rate limiting & size limits**
*   4.1. Per-instance config: `API_MAX_REQ_SIZE_BYTES` (default 256KB).
*   4.2. Lightweight token-bucket rate limiter per client token/IP (e.g., 60 req/min by default).
*   4.3. Reject with `ApiError` code `RATE_LIMIT` and HTTP 429 when exceeded.

**5. Timeouts & SLAs**
*   5.1. API-level global timeout: `ORCHESTRATOR_GLOBAL_TIMEOUT_MS` (default 12000ms).
*   5.2. For long-running operations, asynchronous job endpoints are noted as a post-MVP feature.

**6. Observability & Metrics**
*   6.1. Emit Prometheus metrics: `http_requests_total{endpoint,method,status}`, `http_request_duration_seconds` histogram per endpoint.
*   6.2. Correlate logs and metrics via `correlation_id`.

**7. Security & Best Practices**
*   7.1. Force TLS in deployment.
*   7.2. Validate and sanitize all inputs via Pydantic.
*   7.3. Enforce CORS disabled by default.
*   7.4. Do not leak internal stack traces in responses.

---

### **2) Auth Middleware — Refined Spec**

**1. Responsibility (concise)**
*   1.1. Validate `Authorization: Bearer <token>` header.
*   1.2. Populate `request.state` with `security_context` and `correlation_id`.
*   1.3. Emit auth success/failure metrics.
*   1.4. Support live token reload without restart.

**2. MVP Behavior**
*   2.1. Default: single static bearer token `ORDO_API_TOKEN`.
*   2.2. Support token reload (e.g., via a secured admin endpoint like `/admin/reload-config` protected by a separate admin-only token).

**3. Rate-limiting & brute-force defense**
*   3.1. Track failed auth attempts per token/IP and enforce short-term throttling.
*   3.2. Emit metric `auth_failed_total{reason,client}`.

**4. Correlation ID**
*   4.1. If client provides `X-Correlation-ID`, propagate it; else generate UUIDv4.
*   4.2. Attach `correlation_id` to all logs/metrics for the request.

**5. Observability**
*   5.1. Emit metrics for successful and failed auth events.
*   5.2. Log attempts at INFO (success) and WARN (failure).

---

### **3) Audit & Logging — Refined Spec**

**1. Responsibility (concise)**
*   1.1. Emit structured JSON logs for all important lifecycle events.
*   1.2. Provide optional persistence of audit logs to DB via `IAuditLogRepository`. Default is append-only JSON files with rotation.
*   1.3. Ensure PII and secrets are never persisted or emitted in logs.

**2. Log content & schema**
*   2.1. Each entry must include: `timestamp`, `level`, `service`, `component`, `correlation_id`, `actor`, `action`, `payload` (truncated & redacted), `outcome`.

**3. PII & secret handling**
*   3.1. Enforce a redaction policy: tokens, API keys, etc., must be replaced with `[REDACTED]`.
*   3.2. Implement a centralized `redact()` utility.

**4. Log sinks & rotation**
*   4.1. File-based default with size/time rotation.
*   4.2. Optional sinks (Loki, ELK) configurable via environment variables.

**5. Audit DB (optional)**
*   5.1. If DB persistence is enabled, write asynchronously to avoid blocking.
*   5.2. Requires a configurable retention policy.

**6. Observability hooks**
*   6.1. Emit metrics for key audit outcomes: `orders_placed_total`, `sessions_refreshed_total`, etc.

---

### **4) OTP Helper CLI — Refined Spec**

**1. Purpose & modes**
*   1.1. A thin CLI to assist daily login flows: interactive and non-interactive.
*   1.2. The CLI communicates with the Ordo HTTP API.

**2. UX & automation features**
*   2.1. Interactive mode with prompts and progress indicators.
*   2.2. Non-interactive mode via flags (`--otp`) or environment variables.
*   2.3. Flags: `--broker`, `--non-interactive`, `--quiet`, `--log-file`, etc.
*   2.4. Granular exit codes for automation (e.g., `0`=success, `2`=auth failure, `4`=missing OTP).
*   2.5. A final summary report can be posted back to Ordo via the optional `/api/v1/auth/report` endpoint.

**3. Security considerations**
*   3.1. Warn prominently about storing OTPs in environment variables.
*   3.2. Do not log OTPs.

**4. Observability & automation UX**
*   4.1. Support structured JSON logging via `--log-file`.
*   4.2. Provide `validate-config` subcommand to preflight configuration.

**5. Implementation notes**
*   5.1. Lightweight Python CLI using `Typer`.

---

### **5) Background Jobs Runner — Refined Spec**

**1. Purpose & job types**
*   1.1. Run periodic maintenance and health tasks inside the same process (MVP).
*   1.2. Key jobs: `session_refresh`, `adapter_health_check`, `idempotency_cleanup`.

**2. Job architecture (robustness)**
*   2.1. Use `asyncio` background tasks started at app startup and monitored by a Watchdog supervisor.
*   2.2. Each job wrapped with error handling, retry/backoff, and circuit-breaker awareness.
*   2.3. If a job fails repeatedly, emit an alert metric.

**3. Concurrency & scheduling knobs**
*   3.1. Per-job config: `interval_seconds`, `timeout_seconds`, `max_retries`.
*   3.2. Allow disabling job types via environment variables.

**4. Crash recovery & monitoring**
*   4.1. Supervisor restarts failed jobs with exponential backoff.
*   4.2. Track `last_successful_run` timestamp in metrics.
*   4.3. Provide an admin HTTP endpoint `/api/v1/jobs` (auth only) reporting job health.

**5. Idempotency cleanup & DB pressure**
*   5.1. `idempotency_cleanup` uses batched deletes to avoid DB pressure.
*   5.2. Provide a dry-run mode.

**6. Observability & metrics**
*   6.1. Emit per-job metrics: `job_last_success_timestamp`, `job_runs_total`, `job_failures_total`, `job_duration_seconds`.

---

### **6) Cross-component Notes & Policies**

*   **ApiError Canonicalization:** A single, documented enum file will be the source of truth for all error codes.
*   **Correlation ID Policy:** Every external request and broker call must include a `correlation_id`.
*   **PII & Secrets:** A central redaction utility is mandatory. Repositories must never accept plaintext secrets.
*   **Config & Feature Flags:** Expose toggles for key features (e.g., `ENABLE_DB_AUDIT_LOGS`). We recommend a standard convention for environment variables, such as prefixing all with `ORDO_` (e.g., `ORDO_API_TOKEN`).
*   **Operational Guidance:** Document minimal resource recommendations and TLS enforcement for public deployments.

---

### **7) Acceptance Criteria (minimal)**

*   API endpoints conform to the `ApiError` contract for all failure cases.
*   Auth middleware supports token reload without a restart.
*   OTP CLI returns specified exit codes for all major outcomes.
*   Background jobs restart on failure and emit metrics for the last successful run.
*   All logs are structured JSON with secrets redacted by default.

---
