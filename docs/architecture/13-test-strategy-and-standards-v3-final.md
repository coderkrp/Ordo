# 13. Test Strategy and Standards (v3 Final)

This section defines the comprehensive testing strategy for the Ordo project, ensuring reliability, correctness, and adherence to the architecture.

## 13.1. Testing Philosophy

*   **Approach:** We will follow a pragmatic "Test-After-Development" approach, with a strong emphasis on automated testing to ensure a robust safety net.
*   **Test Pyramid:** Our strategy is centered on the test pyramid model: a large base of fast unit and contract tests, a focused layer of integration and resilience tests, and a small, critical set of E2E smoke tests.
*   **Coverage Goal:** The automated test suite **must** maintain **≥80% line coverage**. For critical components like the Orchestrator, SessionManager, and Adapters, a high **branch/path coverage** will also be manually reviewed and prioritized.

## 13.2. Test Types and Organization

*   **Framework:** **`pytest`** is the sole framework for all test types.
*   **Location:** All tests reside in the root `/tests` directory, which mirrors the `src/ordo` package structure.

### 13.2.1. Unit Tests
*   **Scope:** Test a single function or class in complete isolation.
*   **Mocking:** Use `unittest.mock` for internal dependencies.

### 13.2.2. Contract Tests
*   **Scope:** A dedicated, shared test suite that every broker adapter implementation **must** pass.
*   **Purpose:** To enforce the `IBrokerAdapter` contract, ensuring every adapter behaves identically with respect to data mapping and error translation.
*   **Location:** `tests/contracts/`.

### 13.2.3. Integration Tests
*   **Scope:** Verify the interaction between internal components (e.g., a service and its repository) and the behavior of background jobs.
*   **Infrastructure:** Use ephemeral databases (e.g., via Docker or Testcontainers). External APIs remain mocked with `respx`.

### 13.2.4. Resilience Tests
*   **Scope:** A special category of integration tests designed to prove our resilience patterns (retries, circuit breakers, timeouts) work as specified.

### 13.2.5. End-to-End (E2E) Smoke Tests
*   **Scope:** A small suite of tests run against a fully containerized application to verify critical user workflows, including the partial success and kill-switch scenarios.

## 13.3. Test Data and Environment

*   **Test Data Generation:** Test data will be generated using `pytest` fixtures and the **`factory-boy`** library.
*   **Canonical Datasets:** A shared **`tests/testdata/`** directory will hold reusable JSON files representing mock API responses (e.g., `fyers_portfolio_response.json`). This ensures that contract and integration tests are working against a stable, canonical dataset.
*   **Mocking External APIs:** All external HTTP APIs **must** be mocked using **`respx`**.

## 13.4. Observability and Security Testing

*   **Observability Tests:** The test suite will include specific tests to verify that the `correlation_id` is present in structured log outputs and that key Prometheus metrics are incremented correctly.
*   **Basic Security Tests:** The test suite will verify that protected API endpoints require authentication and that sensitive data is redacted from logs.

## 13.5. Continuous Testing (CI/CD)

*   **Execution:** The full test suite will be run by the GitHub Actions pipeline on every push to `main`.
*   **Parallelization:** The CI pipeline will be configured to run test suites in parallel (e.g., unit/contract tests run separately from slower integration/E2E tests) to minimize feedback time.
*   **Gating:** A merge will be blocked if any test fails or if the code coverage drops below the 80% threshold.
*   **Out of Scope for MVP:** Dedicated performance and load tests are explicitly out of scope for the MVP but are a key item on the post-MVP roadmap.

---
