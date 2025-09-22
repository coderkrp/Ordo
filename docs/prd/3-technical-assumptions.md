# 3. Technical Assumptions

## 3.1. Repository Structure: Monorepo
*   All code for the core service, broker adapters, and helper scripts will reside in a single repository (Monorepo) to simplify dependency management and initial development.

## 3.2. Service Architecture: Monolith
*   The service will be built as a single, deployable monolithic application based on Python's `asyncio` model, using FastAPI and Uvicorn. This is the simplest and fastest approach for the defined MVP scope.

## 3.3. Testing Requirements: Unit + Integration
*   The project will require a combination of unit tests and integration tests. All contributed broker adapters must include a suite of unit tests and demonstrate interface compliance.

## 3.4. Additional Technical Assumptions and Requests

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
