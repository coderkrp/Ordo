# Story 2.10: Pre-Trade Validation & Retries

## Status
Draft

## Story
**As a** trader,
**I want** Ordo to validate trades and retry failures,
**so that** my orders have the best chance of success.

## Acceptance Criteria
1. The orchestrator performs pre-trade validation checks (instrument tradability, funds) before placing an order (FR13, FR14).
2. If validation fails, the request is rejected immediately with a clear error (FR15).
3. The orchestrator automatically retries failed broker calls for transient errors (e.g., network issues, 5xx errors) using an exponential backoff strategy (FR10).
4. The number of retries and backoff factor are configurable.

## Tasks / Subtasks
- [ ] Implement pre-trade validation logic in the orchestrator.
- [ ] Add retry logic (e.g., using the `tenacity` library) around the adapter calls in the orchestrator.
- [ ] Add configuration options for retry policies.

## Dev Notes
- **Resilience:** This story implements core resilience patterns defined in the architecture (Section 2.4).

### Testing
- Integration tests should be created to verify the retry behavior. Use `respx` to simulate transient and permanent API failures from mock adapters and assert that the orchestrator retries correctly.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
