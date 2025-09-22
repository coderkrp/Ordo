# Story 1.6: Portfolio API Endpoint

## Status
Draft

## Story
**As a** user,
**I want** a secure API endpoint to view my consolidated portfolio,
**so that** I can see my primary account data.

## Acceptance Criteria
1. A GET endpoint is created at `/api/v1/portfolio`.
2. The endpoint is protected by the API Authentication Middleware (from Story 1.1).
3. It accepts an optional `brokers` query parameter to specify which brokers to query.
4. The endpoint uses the orchestrator to fetch portfolio data from the specified brokers.
5. The returned data is a `UnifiedResponse` containing the standardized `Portfolio` DTO for each broker.
6. Errors from the orchestrator or adapters are handled gracefully and returned in the standard `ApiError` format.

## Tasks / Subtasks
- [ ] Create a new API endpoint in `src/ordo/api/v1/endpoints/portfolio.py`.
- [ ] Implement the logic to call the (yet to be created) orchestrator service.
- [ ] Add request and response models (Pydantic schemas).
- [ ] Ensure the endpoint is protected by the auth dependency.

## Dev Notes
- **Orchestration:** This is the first endpoint to use the orchestrator pattern. While the full orchestrator is not built yet, this story lays the groundwork for it by establishing the API-to-service communication pattern.
- **Dependencies:** Depends on Story 1.1 (Auth), Story 1.2 (Adapter Interface), and Story 1.5 (Fyers Portfolio).

### Testing
- Integration tests should be written for the endpoint, using the `MockAdapter` to provide data and verifying that the endpoint returns the correct `UnifiedResponse` structure.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
