# Story 2.7: Order Placement API Endpoint

## Status
Draft

## Story
**As a** user,
**I want** a secure endpoint to place orders across brokers,
**so that** I can execute my strategies.

## Acceptance Criteria
1. A POST endpoint is created at `/api/v1/orders`.
2. The endpoint is protected by the API Authentication Middleware.
3. The endpoint accepts a standardized `OrderRequest` payload.
4. The endpoint delegates the request to the `RequestOrchestrator`.
5. The endpoint returns a `UnifiedResponse` with the results from each broker.
6. The endpoint meets the performance NFRs (median overhead ≤50ms).

## Tasks / Subtasks
- [ ] Create `src/ordo/api/v1/endpoints/orders.py`.
- [ ] Implement the POST endpoint and its Pydantic models.
- [ ] Integrate the endpoint with the `RequestOrchestrator`.
- [ ] Add performance instrumentation to measure latency overhead.

## Dev Notes
- **Dependencies:** Depends on Story 2.3, 2.5, and 2.6.

### Testing
- Integration tests should be written for the endpoint, using mock adapters to simulate different success and failure scenarios from the orchestrator.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
