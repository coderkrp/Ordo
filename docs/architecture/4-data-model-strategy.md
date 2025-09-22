# 4. Data Model Strategy

## Definitive Data Architecture Strategy (v4)

### Part 1: Guiding Principles

1.  **Source of Truth:** The broker is the single source of truth for real-time data like portfolios and positions. The Ordo database **does not** persist this data, preventing staleness.
2.  **Standardization over Pass-Through:** The primary goal of the API models (DTOs) is to unify broker-specific data and error codes into a single, standard schema. This simplifies client-side logic.
3.  **Naming Convention:** All database-persisted models will be prefixed with `Db` (e.g., `DbSession`). All API and configuration models (Pydantic schemas) will reside in a dedicated `/schemas` directory.
4.  **API Versioning:** All API DTOs are considered part of the `v1` API contract. Any future breaking changes to a model will require a new API version.
5.  **Progressive Complexity:** The default persistence and state management will use the simplest, most lightweight options (in-memory, SQLite). More complex options (Redis, Postgres, DB-based circuit breakers) are available for users who need to scale.

### Part 2: Model Definitions

**A. Persistent Models (`Db*`)**

*   **`DbSession`**
    *   **Purpose:** Persists a single account's session with a single broker.
    *   **Primary Key:** Composite key of (`adapter_id`, `account_id`).
    *   **Attributes:** `access_token_encrypted`, `refresh_token_encrypted` (optional), `expires_at`, `metadata_json` (for other broker-specific fields).
*   **`DbIdempotencyRecord`**
    *   **Purpose:** Prevents duplicate write operations.
    *   **Attributes:** `key` (primary key), `response_snapshot_json`, `expires_at` (to enable TTL/cleanup).
*   **`DbCircuitBreakerState` (Optional)**
    *   **Purpose:** Optional persistence for circuit breaker state to survive restarts. The default is in-memory.
    *   **Attributes:** `adapter_id`, `state` (Enum: OPEN, HALF_OPEN, CLOSED), `failure_count`, `last_failure_at`.

**B. In-Memory / API Models (Pydantic Schemas)**

*   **`Portfolio`**
    *   **Purpose:** A unified summary of a user's account.
    *   **Attributes:** `cash_balance`, `margin_available`, `positions` (list[`Position`]), `holdings` (list[`Holding`]), `metadata_json` (optional escape hatch for broker-specific data).
*   **`Position` & `Holding`**: Separate DTOs representing daily and long-term holdings, respectively.
*   **`Quote`**
    *   **Purpose:** A minimal, standardized market data quote.
    *   **Attributes:** `instrument_token`, `last_price`, `timestamp`, `extended_fields_json` (optional).
*   **`ApiError`**
    *   **Purpose:** The standard structure for all error responses.
    *   **Attributes:** `error_code` (standardized Enum), `message` (human-readable), `details` ({`broker_id`: `fyers`, `native_error`: `...`}), `correlation_id`.

**C. Configuration Models (Pydantic Settings)**

*   **`BrokerConfig` (Base Class)**: An abstract base class for all broker configurations.
*   **`FyersConfig(BrokerConfig)` / `HDFCConfig(BrokerConfig)`**: Concrete, type-safe subclasses for each broker, defining the specific fields they require (e.g., `client_id`, `secret_key`).

### Part 3: Specific Strategies

*   **Portfolio Caching Strategy:** Portfolio data is fetched on demand from the broker and **is not persisted** in the Ordo database. An optional, short-lived (e.g., 1-5 seconds, configurable) in-memory or Redis cache can be enabled to reduce latency for high-frequency polling clients.
*   **Audit Strategy:** Auditing will be performed via structured, append-only JSON logs written to a file (`structlog`), which satisfies the MVP requirement. A `DbAuditLogEntry` table is out of scope for MVP but can be added later if required for advanced querying or compliance.
*   **Error Code Strategy:** Error codes returned in the `ApiError` model will be **standardized** across all brokers (e.g., `INSUFFICIENT_FUNDS`, `INVALID_SESSION`). The original broker-native error message will be available in the `details` field for debugging.

---
