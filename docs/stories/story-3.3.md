# Story 3.3: Status Endpoint

## Status
Draft

## Story
**As a** user,
**I want** a detailed status endpoint,
**so that** I can monitor Ordo and broker connectivity.

## Acceptance Criteria
1. A GET endpoint is created at `/api/v1/status`.
2. The endpoint is protected by the API authentication middleware.
3. The endpoint returns the overall system status, version, and uptime.
4. For each configured broker, the endpoint returns its connection status, last successful login time, and current circuit breaker state.

## Tasks / Subtasks
- [ ] Create `src/ordo/api/v1/endpoints/status.py`.
- [ ] Implement the logic to gather status information from the `SessionManager` and the circuit breaker service.
- [ ] Define the `StatusResponse` Pydantic model.

## Dev Notes
- **Observability:** This endpoint is crucial for operational monitoring and debugging (FR20).

### Testing
- Integration tests should call the status endpoint and verify that the response structure is correct and reflects the state of mock components (e.g., a mock adapter with a failed session).

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
