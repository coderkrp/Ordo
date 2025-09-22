# 2. High-Level Architecture

## 2.1. Technical Summary

Ordo is a lightweight, **modular monolithic** backend with clear component boundaries: a core **Orchestrator**, an **Adapter Layer**, an **Auth/Session Manager**, and services for **Persistence** and **Auditing**. It is built on an async Python stack (FastAPI, asyncio, httpx) for efficient fan-out concurrency and is optimized for small cloud instances (1 vCPU/1GB RAM).

The architecture favors pragmatic simplicity and progressive complexity. It starts as a single process with clear extension points to optionally evolve with external services like Redis (for caching) or PostgreSQL (for scaled persistence) as future needs dictate.

**Key Architectural Patterns:**
*   **Ports and Adapters (Hexagonal):** The core logic is isolated from external concerns. This is primarily implemented via the **Adapter Pattern** for the broker integration layer.
*   **Repository Pattern:** Decouples business logic from data storage, initially for file-based logs and later for optional database backends.
*   **Resilience Patterns:** Includes **Circuit Breaker**, **Retry**, and **Idempotency** patterns to ensure safe and reliable communication with external APIs.
*   **Observability:** Employs **Correlation IDs** for traceable logging across all system components.

This architecture directly supports the PRD goals by providing a secure, extensible, and reliable orchestration layer with clear operational controls (kill-switch, status), safety mechanisms (idempotency, audits), and a lightweight deployment model (Docker).

## 2.2. High-Level Overview

**Architecture Style**
*   **Primary Style:** Modular Monolith. This allows us to start small and fast while enforcing decoupling between internal components (e.g., orchestrator, adapters).
*   **Deployment:** A single Docker container per deployment. Optional external services like PostgreSQL and Redis are supported via configuration for users who need to scale.

**Repository & Service Structure**
*   **Repository:** A Monorepo will be used, with the single backend service located under `/src/ordo` (to be detailed in the Source Tree section).
*   **Service:** The service is a single-process FastAPI application. Its internal components are organized as distinct Python modules/packages (adapters, orchestrator, auth, persistence, audit, cli_tools).

**Primary Data & Request Flow (Conceptual)**
1.  A client calls the Ordo REST API (e.g., `/api/v1/orders`) with an `Authorization: Bearer <token>`.
2.  The API layer authenticates the request via the static token and validates the request payload against its schema.
3.  The **Orchestrator** receives the request and executes the core logic:
    *   Performs pre-trade validations (e.g., for funds, instrument tradability).
    *   Checks for an idempotency key to prevent duplicate write operations.
    *   Fans out requests concurrently to the chosen broker adapters using `asyncio` and `httpx`.
    *   Manages resilience patterns: retries (with exponential backoff) and circuit breakers.
    *   Collates results from all adapters.
4.  The **Audit/Logging** service records the request, all broker interactions, and the final outcome.
5.  A unified response is returned to the client, annotated per broker, with explicit handling for partial successes.
6.  **Background Tasks:** The application will manage recurring background tasks (like session token refreshes) using native `asyncio` background tasks.

**Key Architectural Decisions**
*   **Stack:** Python & FastAPI are chosen for high developer velocity, excellent performance in async I/O workloads, and strong community support.
*   **Architecture:** A Modular Monolith is chosen to minimize operational complexity at MVP while allowing for future evolution.
*   **Extensibility:** The `IBrokerAdapter` interface is the primary extension point for adding new brokers.
*   **Persistence:** **SQLite** is the default persistence layer for audit logs and idempotency keys. This provides robust, queryable storage without requiring an external database, perfectly aligning with the minimal footprint goal. PostgreSQL is supported as an optional, scalable backend.
*   **Scope Boundary:** The MVP is strictly for snapshot-based data (no WebSockets or real-time streaming).
*   **Security:** A "security-by-design" approach includes encryption for credentials at rest, TLS enforcement, a static bearer token for API access, and optional mTLS support.

## 2.3. High-Level Project Diagram

```mermaid
graph TD
    %% --- User Environment ---
    subgraph User's Environment
        Client["Client (Script / Dashboard)"]
        OTPScript["OTP Helper CLI"]
    end

    %% --- Ordo Service ---
    subgraph Ordo Service (Docker Container)
        OrdoAPI["Ordo API (FastAPI)"]
        
        Auth["Auth Middleware"]
        Orchestrator["Request Orchestrator"]
        
        subgraph Adapters
            AdapterInterface["IBrokerAdapter Interface"]
            Adapter1["Fyers Adapter"]
            Adapter2["HDFC Adapter"]
            Adapter3["Mirae Adapter"]
            MockAdapter["Mock Adapter"]

            SessionManager["Session Manager (per Adapter)"]
        end

        subgraph Persistence & State Stores
            DB["SQLite / Postgres"]
            IdempotencyStore["Idempotency Store (persistent)"]
            KillSwitchStore["Kill-Switch Store (persistent)"]
            SessionStore["Session Tokens (encrypted, persistent)"]
            AuditLog["Audit Log (JSON file and/or DB)"]
        end

        subgraph In-Memory State
            CircuitBreakerStore["Circuit Breaker State (ephemeral)"]
        end
    end

    %% --- External Services ---
    subgraph External Services
        BrokerAPIs["External Broker APIs"]
    end

    %% --- Primary Flows ---
    Client --> |API Requests (TLS)| OrdoAPI
    OTPScript --> |Initiates login & submits OTP via API| OrdoAPI

    OrdoAPI --> Auth
    Auth --> Orchestrator

    Orchestrator --> AdapterInterface
    AdapterInterface --> Adapter1
    AdapterInterface --> Adapter2
    AdapterInterface --> Adapter3
    AdapterInterface --> MockAdapter

    Adapter1 --> SessionManager
    Adapter2 --> SessionManager
    Adapter3 --> SessionManager

    Adapter1 --> |HTTPS| BrokerAPIs
    Adapter2 --> |HTTPS| BrokerAPIs
    Adapter3 --> |HTTPS| BrokerAPIs

    %% --- Internal Data Flows ---
    Orchestrator --> IdempotencyStore
    Orchestrator --> KillSwitchStore
    Orchestrator --> CircuitBreakerStore
    Orchestrator --> AuditLog
    SessionManager --> SessionStore
```

## 2.4. Architectural and Design Patterns

*   **Hexagonal Architecture (Ports & Adapters):** The core application logic is isolated from external concerns. This is primarily implemented via the `IBrokerAdapter` interface, which defines methods like `login`, `place_order`, and `get_portfolio`.
    *   *Rationale:* Decouples the core system from volatile external APIs, simplifies testing by allowing mock adapters, and enables community contributions for new brokers (NFR12).
*   **Repository Pattern:** Data persistence and access (for sessions, idempotency keys, etc.) will be handled through a repository layer that abstracts the underlying database (SQLite or Postgres).
    *   *Rationale:* Provides flexibility to swap database backends with minimal code changes and simplifies unit testing by allowing mock repositories (NFR5).
*   **Dependency Injection:** The application will leverage FastAPI's built-in DI container to provide services and repository implementations to the components that need them.
    *   *Rationale:* Promotes loose coupling, enhances testability by making it easy to inject mock dependencies, and manages the lifecycle of components.
*   **Resilience Patterns (Circuit Breaker & Retry):** Each adapter will be protected by its own circuit breaker. API calls will use a retry strategy with exponential backoff and jitter.
    *   *Rationale:* Prevents cascading failures from a single faulty broker and gracefully handles transient network or API errors, a core resilience requirement (FR10, FR18).
*   **Idempotency Pattern:** All write operations, especially order placement, will support an idempotency key that is checked against a persistent store.
    *   *Rationale:* Critical for safe trading operations, guaranteeing that retried requests do not result in duplicate orders (FR16).
*   **Immutable, Append-Only Logging:** Audit records will be treated as immutable events and written to a structured (JSON) log in an append-only fashion.
    *   *Rationale:* Ensures a tamper-resistant trail for traceability, debugging, and potential compliance needs (FR19).

---
