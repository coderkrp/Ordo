# Story 2.8: Idempotency Key Support

## Status
Draft

## Story
**As a** developer,
**I want** to provide an idempotency key for orders,
**so that** retries are safe and don’t create duplicates.

## Acceptance Criteria
1. The order placement endpoint (`/api/v1/orders`) accepts an `Idempotency-Key` header.
2. The orchestrator checks for the existence of this key in a persistent store (SQLite/Postgres).
3. If the key is found, the orchestrator immediately returns the cached response from the original request without calling the adapters.
4. If the key is not found, the orchestrator proceeds with the request and stores the key and the final `UnifiedResponse` upon completion.
5. The stored keys have a configurable TTL (e.g., 24 hours).

## Tasks / Subtasks
- [ ] Create a `DbIdempotencyRecord` model and a repository for it.
- [ ] Add logic to the orchestrator to check for and store idempotency records.
- [ ] Modify the API endpoint to read the `Idempotency-Key` header.
- [ ] Implement a background job or cleanup mechanism for expired keys.

## Dev Notes
- **Safety:** This is a critical safety feature (FR16). The implementation must be atomic to prevent race conditions.
- **Persistence:** The idempotency records must be stored in the database to survive restarts.

### Testing
- Integration tests must verify that providing the same key twice returns the cached response and only results in one actual broker call.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
