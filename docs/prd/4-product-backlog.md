# 4. Product Backlog

**Note on Documentation:** At the end of each epic, the project's documentation (README, Quickstart, etc.) must be updated to reflect the new features and changes.

## Sprint 0: Project Setup & Infrastructure Prep
**Goal:** Lay down the groundwork for development with project scaffolding, core API server, and health endpoint.

*   **Story 0.1: Project Scaffolding:** As a developer, I want a standardized project structure with git, dependency management, and linting configured, so that I can start developing in a clean and consistent environment.
*   **Story 0.2: Core API Server & Health Endpoint:** As a developer, I want a basic, runnable FastAPI server with a health check endpoint, so that I can confirm the application is running and deployable.
*   **Story 0.3: Initial Project Documentation:** As a new user, I want a clear README and Quickstart guide, so that I can understand the project and run it quickly.

## Epic 1: Foundation & Validated Single-Broker Workflow
**Goal:** Establish the core app, API auth, OTP helper, and a complete end-to-end workflow with a single real broker (Fyers), plus a mock adapter to prove extensibility.

*   **Story 1.1: API Authentication Middleware:** As a developer, I want API endpoints to be protected by a static bearer token, so that access to the service is secure from the start.
*   **Story 1.2: Broker Adapter Interface & Mock Adapter:** As an architect, I want a clearly defined broker adapter interface and a mock implementation, so that the core application can be developed and tested independently of real broker APIs.
*   **Story 1.3: Fyers Adapter - Authentication:** As a developer, I want to implement the authentication portion of the Fyers adapter, so that the application can connect to a real broker.
*   **Story 1.4: OTP Helper Script:** As a user, I want a CLI script that initiates the login process and prompts me to enter my OTP, so that I can complete the daily authentication flow easily.
*   **Story 1.5: Fyers Adapter - Portfolio:** As a developer, I want to implement portfolio fetching in the Fyers adapter, so that the application can retrieve user account data.
*   **Story 1.6: Portfolio API Endpoint:** As a user, I want a secure API endpoint to view my consolidated portfolio, so that I can see my primary account data.
    *   **Acceptance Criteria:**
        *   The endpoint is protected by the API Authentication Middleware.
        *   It returns a consolidated view of the user's portfolio from the requested broker.
        *   Errors must follow the standardized JSON schema (`{status, error_code, message}`).

## Epic 2: Multi-Broker Orchestration & Safe Order Placement
**Goal:** Add HDFC and Mirae adapters, implement orchestrator for multi-broker requests, and introduce order placement with idempotency and audit logging.

*   **Story 2.1: HDFC Securities Adapter:** As a developer, I want a fully implemented adapter for HDFC Securities, so that the service can connect to this broker.
    *   **Acceptance Criteria:**
        *   The adapter implements the full `IBrokerAdapter` interface (auth, portfolio, orders).
        *   It correctly handles HDFC-specific API data formats and workflows.
        *   Includes unit tests using mocked broker API responses to cover successful and failed scenarios.
*   **Story 2.2: Mirae m.Stock Adapter:** As a developer, I want a fully implemented adapter for Mirae m.Stock, so that the service can connect to this broker.
    *   **Acceptance Criteria:**
        *   The adapter implements the full `IBrokerAdapter` interface (auth, portfolio, orders).
        *   It correctly handles Mirae-specific API data formats and workflows.
        *   Includes unit tests using mocked broker API responses to cover successful and failed scenarios.
*   **Story 2.3: Request Orchestrator Service:** As a developer, I want a central orchestrator service, so that multi-broker requests are centralized and reusable.
*   **Story 2.4: Asynchronous Fan-Out & Collation:** As a developer, I want orchestrator requests to fan out concurrently and collate results, so that multi-broker requests are efficient.
*   **Story 2.5: Extend Adapter Interface for Orders:** As an architect, I want to extend IBrokerAdapter for order placement, so that all adapters can support trading functions.
*   **Story 2.6: Implement Order Placement:** As a developer, I want adapters to implement order placement, so that the service can execute trades.
*   **Story 2.7: Order Placement API Endpoint:** As a user, I want a secure endpoint to place orders across brokers, so that I can execute my strategies.
    *   **Acceptance Criteria:**
        *   The endpoint is protected by the API Authentication Middleware.
        *   It accepts order requests and routes them through the orchestrator.
        *   Errors must follow the standardized JSON schema (`{status, error_code, message}`).
        *   API response time overhead must meet the defined NFRs (median ≤50ms, 95th percentile ≤100ms).
*   **Story 2.8: Idempotency Key Support:** As a developer, I want to provide an idempotency key for orders, so that retries are safe and don’t create duplicates.
*   **Story 2.9: Audit Logging:** As a compliance officer, I want detailed audit logs, so that trading activity is traceable.
    *   **Acceptance Criteria:**
        *   All API requests and broker interactions are logged in a structured JSON format.
        *   Logs include timestamps, request details, broker responses, and final outcomes.
        *   Logs are persisted to local storage and survive application/container restarts.
*   **Story 2.10: Pre-Trade Validation & Retries:** As a trader, I want Ordo to validate trades and retry failures, so that my orders have the best chance of success.

## Epic 3: Resilience, Operations & Community Enablement
**Goal:** Make the app production-ready and OSS-friendly with resilience features, monitoring tools, and community adoption enablers.

*   **Story 3.1: Circuit Breaker Service:** As a developer, I want a circuit breaker for broker calls, so that repeated failures don’t overload the system.
*   **Story 3.2: Global Kill-Switch:** As a trader, I want a global kill-switch, so that I can instantly halt all trading activity in emergencies.
*   **Story 3.3: Status Endpoint:** As a user, I want a detailed status endpoint, so that I can monitor Ordo and broker connectivity.
    *   **Acceptance Criteria:**
        *   The endpoint returns the overall system status.
        *   It includes the connection status, last login time, and circuit breaker state for each configured broker.
        *   Access requires bearer token authentication by default.
        *   A configuration option (e.g., environment variable) can be set to make the endpoint public.
*   **Story 3.4: Configurable & Structured Logging:** As a developer, I want structured logs with configurable levels, so that I can debug effectively.
*   **Story 3.5: Optional Postgres Support:** As a sysadmin, I want Postgres support, so that I can scale Ordo for larger workloads.
*   **Story 3.6: Contribution Guide & Adapter SDK:** As a contributor, I want clear docs and SDK examples, so that I can add new brokers easily.
*   **Story 3.8: PyPI & Docker Hub Publishing:** As a developer, I want Ordo on PyPI and Docker Hub, so that I can install and run it easily.
*   **Story 3.9: Python Client SDK:** As a developer, I want a minimal Python client SDK, so that I can easily integrate my application with the Ordo API.
    *   **Acceptance Criteria:**
        *   A basic Python package is created for interacting with the Ordo API.
        *   The SDK includes clear documentation with installation and usage examples.
        *   The package is published to PyPI for easy installation.
