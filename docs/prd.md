# Ordo Product Requirements Document (PRD)

## 1. Goals and Background Context

### 1.1. Goals

*   **Unify Broker Access:** Provide a single, resilient API for trades, portfolios, and market data to save developers **over 80% of time** spent on building and maintaining individual broker integrations.
*   **Automate Session Management:** Handle complex broker login, OTP, and session refresh workflows automatically.
*   **Ensure Trading Resilience:** Guarantee safe and reliable execution with features like idempotency keys, automatic retries, and a global kill-switch, targeting a **≥99% order request success rate**.
*   **Enable Fast Integration:** Design the API and documentation to allow a developer to integrate and execute their first trade within **one day**.
*   **Promote Open Source:** Establish Ordo as the go-to open-source foundation for Indian market integrations, eliminating repetitive work for the community.
*   **Support Lightweight Deployment:** Optimize for minimal infrastructure (1 vCPU + 1 GB RAM) to ensure accessibility and low operational cost.

### 1.2. Background Context

Indian algo developers and small trading desks face a fragmented ecosystem where each broker exposes its own inconsistent API. Building integrations is repetitive, error-prone, and risky for live trading. Ordo addresses this by providing a self-hostable, open-source backend that unifies multiple brokers under a single, resilient API.

Unlike existing platforms like Streak, Tradetron, or OpenAlgo, Ordo focuses narrowly on being a lightweight infrastructure layer: fast, reliable, and secure, without lock-in. It prioritizes transparency (open source), safety (idempotency, kill-switch), and simplicity (Dockerized deployment). This foundation accelerates development, reduces operational risk, and creates space for future SaaS opportunities.

### 1.3. Change Log

| Date       | Version | Description                                  | Author     |
| :--------- | :------ | :------------------------------------------- | :--------- |
| 2025-09-20 | 1.1     | Refined goals and context based on feedback. | John (PM)  |
| 2025-09-20 | 1.0     | Initial draft                                | John (PM)  |

---

## 2. Requirements

### 2.1. Functional Requirements

**Broker Adapters**
*   **FR1:** Support HDFC Securities, Mirae m.Stock, and Fyers at MVP.
*   **FR2:** Adapters must normalize broker-specific quirks (e.g., API endpoints, data formats) into a standard internal schema.
*   **FR3:** Adapters must expose consistent, unified data models for Orders (market and limit types at MVP), Portfolio & Positions, and Quotes.

**Authentication & Session Management**
*   **FR4:** The system must manage the daily broker login flow.
*   **FR5:** The system must provide a client-side helper script to initiate the daily login sequence for all configured brokers and prompt the user to enter the OTP received on their mobile device.
*   **FR6:** The system must securely persist session tokens and automatically refresh them where the broker API supports it.
*   **FR7:** The system must gracefully handle and report session expiry events.

**Request Orchestration**
*   **FR8:** The API must accept a single user request that can target one or more brokers simultaneously.
*   **FR9:** The system must fan out requests concurrently to all targeted brokers.
*   **FR10:** The system must automatically retry failed requests using an exponential backoff strategy before returning a final response.
*   **FR11:** The system must return a single, unified response that clearly annotates the result from each targeted broker.
*   **FR12:** The system must support partial success responses and return them in a standardized response schema, including broker-level status codes and error messages.

**Pre-Trade Validation**
*   **FR13:** The system must validate instrument existence and tradability with the broker before placing an order.
*   **FR14:** The system must check for sufficient margin/fund availability before sending an order.
*   **FR15:** The system must return a fast rejection with a clear error message if any pre-trade checks fail.

**Resilience & Safety Controls**
*   **FR16:** The system must support idempotency keys on all order placement requests to prevent duplicate submissions.
*   **FR17:** The system must provide a global kill-switch API endpoint that immediately halts all new order placements.
*   **FR18:** The system must implement circuit breakers that temporarily halt requests to brokers that fail more than N consecutive times within M seconds (configurable).
*   **FR19:** The system must create a detailed audit log for all requests, broker interactions, and final outcomes. At MVP, logs must be persisted to local storage with optional support for structured logs (JSON format).
*   **FR20:** The system must provide a `/status` API endpoint that returns the overall system health and, for each adapter, its connection status, last successful login time, last API call timestamp, and current circuit breaker state (`OPEN`, `CLOSED`, `HALF-OPEN`).
*   **FR21:** The system must use a standardized JSON schema for all API responses, including errors, which clearly distinguishes between global errors and broker-specific errors.
*   **FR22:** The audit log (FR19) must be persisted to a local file that is automatically rotated to prevent unbounded growth.
*   **FR23:** The system must internally manage and respect per-broker rate limits, queuing or delaying requests as needed to avoid API bans.

### 2.2. Non-Functional Requirements

**Performance**
*   **NFR1:** The API’s median latency overhead must be ≤50ms, with 95th percentile ≤100ms and absolute upper limit ≤250ms.
*   **NFR2:** The system must handle concurrent fan-out requests with minimal latency overhead.
*   **NFR3:** The system must run comfortably on a 1 vCPU + 1 GB RAM instance.

**Scalability**
*   **NFR4:** The architecture must scale from a single-user self-hosted deployment to small desk deployments with multiple accounts.
*   **NFR5:** The system must provide optional support for an external database (Postgres) and cache (Redis) to handle heavier loads.

**Security**
*   **NFR6:** All API keys, secrets, and session tokens must be encrypted at rest.
*   **NFR7:** All API transport must be enforced over TLS.
*   **NFR8:** The system must provide optional support for mutual TLS (mTLS) authentication.
*   **NFR9:** The OTP relay mechanism must not store OTPs beyond their transient use in the login flow.
*   **NFR19:** Access to the API must be secured by a configurable, static bearer token that clients must provide in an `Authorization` header.

**Reliability**
*   **NFR10:** Individual broker adapters must maintain ≥99.5% uptime, excluding broker-side outages.
*   **NFR11:** The request retry mechanism should achieve a ≥90% success rate for recoverable, transient failures.
*   **NFR25:** The system requires the host machine's clock to be accurately synchronized via a service like NTP, as timestamps are critical for logging and potential future trading logic.

**Maintainability & Extensibility**
*   **NFR12:** The system must have a modular architecture that isolates broker-specific logic into adapters.
*   **NFR13:** The project must define a clear adapter interface and require adapter-specific unit tests to ensure stability as brokers change APIs.
*   **NFR24:** All broker adapters must be accompanied by a suite of automated unit tests that mock the external broker API to ensure stability.

**Deployment & Configuration**
*   **NFR14:** The system must be distributable as a lightweight Docker image.
*   **NFR15:** All system behavior (e.g., broker selection, credentials, retry policies) must be configurable via environment variables or a YAML file.
*   **NFR23:** At MVP, any changes to the system's configuration will require a service restart to take effect. Dynamic configuration reloading is out of scope.

**Transparency & Adoption**
*   **NFR16:** The project must be fully open-source under a permissive license (e.g., MIT, Apache 2.0).
*   **NFR17:** The project must be published to Docker Hub and PyPI to ensure easy adoption.
*   **NFR18:** The repository must include a README, quickstart guide, contribution guidelines, and at least one sample client SDK (Python at MVP).
*   **NFR20:** All API endpoints must be versioned, with the initial version being `v1` (e.g., `/api/v1/orders`).
*   **NFR21:** The system must support configurable log levels (`DEBUG`, `INFO`, `ERROR`) and output structured (JSON) logs for diagnostics.
*   **NFR22:** Real-time or streaming market data (e.g., via WebSockets) is explicitly out of scope for the MVP. The API will only provide snapshot-based data on request.

### 2.3. Post-MVP & Operational Requirements

**User Feedback & Community**
*   **NFR26:** A public channel (e.g., GitHub Issues) must be established for users to submit bug reports, feature requests, and general feedback.

**Analytics & Monitoring**
*   **NFR27:** The system should incorporate basic, anonymous usage analytics to track feature adoption (e.g., number of orders placed, portfolio views) and system performance. This must be implemented with user privacy as a priority and be clearly documented.
*   **NFR28:** A baseline alerting strategy must be documented, defining critical events that require operator notification (e.g., circuit breakers remaining open, sustained high rate of failed requests, critical job failures).

---

## 3. Technical Assumptions

### 3.1. Repository Structure: Monorepo
*   All code for the core service, broker adapters, and helper scripts will reside in a single repository (Monorepo) to simplify dependency management and initial development.

### 3.2. Service Architecture: Monolith
*   The service will be built as a single, deployable monolithic application based on Python's `asyncio` model, using FastAPI and Uvicorn. This is the simplest and fastest approach for the defined MVP scope.

### 3.3. Testing Requirements: Unit + Integration
*   The project will require a combination of unit tests and integration tests. All contributed broker adapters must include a suite of unit tests and demonstrate interface compliance.

### 3.4. Additional Technical Assumptions and Requests

**Broker API Stability**
*   It is assumed that HDFC Securities, Mirae m.Stock, and Fyers expose stable, functioning APIs accessible to retail users with documented daily login flows.
*   It is assumed that any undocumented API changes or outages are outside Ordo’s control and responsibility.

**Environment & Infrastructure**
*   Ordo is designed for deployment in a Linux container environment (Docker).
*   The host system clock is assumed to be synchronized via NTP or an equivalent service.
*   Reliable outbound internet connectivity is assumed to be available from the host environment.

**Data and Persistence**
*   The database schema is considered fixed for the MVP. A database migration tool is not in scope.

**Security and Configuration**
*   System secrets (e.g., broker credentials, API tokens) are assumed to be managed via environment variables. Advanced secret management systems are out of scope.
*   The user is responsible for generating their own cryptographically secure random string to use as the API's bearer token.

**Development and Maintainability**
*   The project will use `Poetry` for Python dependency management.
*   The project will enforce `Black` for code formatting and `Ruff` for linting to ensure code quality and consistency.

**User Responsibilities**
*   Users are responsible for securely configuring their own broker credentials, managing their OTP inputs, and ensuring their use of the tool complies with broker agreements.
*   Users are responsible for deploying Ordo in a secure environment where secrets and configuration are protected.

**Scope Boundaries**
*   The service provides snapshot-based market data only; real-time streaming is out of scope for MVP.
*   The service does not guarantee order fulfillment, as rejections can occur at the broker or exchange level for reasons beyond its control.
*   Historical market data storage and analytics are out of scope for MVP.

---

## 4. Product Backlog

**Note on Documentation:** At the end of each epic, the project's documentation (README, Quickstart, etc.) must be updated to reflect the new features and changes.

### Sprint 0: Project Setup & Infrastructure Prep
**Goal:** Lay down the groundwork for development with project scaffolding, core API server, and health endpoint.

*   **Story 0.1: Project Scaffolding:** As a developer, I want a standardized project structure with git, dependency management, and linting configured, so that I can start developing in a clean and consistent environment.
*   **Story 0.2: Core API Server & Health Endpoint:** As a developer, I want a basic, runnable FastAPI server with a health check endpoint, so that I can confirm the application is running and deployable.
*   **Story 0.3: Initial Project Documentation:** As a new user, I want a clear README and Quickstart guide, so that I can understand the project and run it quickly.

### Epic 1: Foundation & Validated Single-Broker Workflow
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

### Epic 2: Multi-Broker Orchestration & Safe Order Placement
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

### Epic 3: Resilience, Operations & Community Enablement
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
