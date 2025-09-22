# 2. Requirements

## 2.1. Functional Requirements

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

## 2.2. Non-Functional Requirements

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

## 2.3. Post-MVP & Operational Requirements

**User Feedback & Community**
*   **NFR26:** A public channel (e.g., GitHub Issues) must be established for users to submit bug reports, feature requests, and general feedback.

**Analytics & Monitoring**
*   **NFR27:** The system should incorporate basic, anonymous usage analytics to track feature adoption (e.g., number of orders placed, portfolio views) and system performance. This must be implemented with user privacy as a priority and be clearly documented.
*   **NFR28:** A baseline alerting strategy must be documented, defining critical events that require operator notification (e.g., circuit breakers remaining open, sustained high rate of failed requests, critical job failures).

---
