# Story 2.4: Asynchronous Fan-Out & Collation

## Status
Draft

## Story
**As a** developer,
**I want** orchestrator requests to fan out concurrently and collate results,
**so that** multi-broker requests are efficient.

## Acceptance Criteria
1. The orchestrator uses `asyncio.gather` to make calls to multiple adapters concurrently.
2. The orchestrator waits for all adapter calls to complete.
3. The results from each adapter are collected and collated into a single `UnifiedResponse` object.
4. The `UnifiedResponse` correctly reflects the `overall_status` (`success`, `partial_success`, `failure`) based on the individual broker results.

## Tasks / Subtasks
- [ ] Modify the orchestrator methods to use `asyncio.gather` for concurrent execution.
- [ ] Implement the `UnifiedResponse` and `BrokerResult` Pydantic models.
- [ ] Add the collation logic to determine the `overall_status`.
- [ ] Handle exceptions from individual adapters gracefully so that one failure doesn't stop all others.

## Dev Notes
- **Performance:** This is a key performance requirement (NFR2). The implementation should be non-blocking.
- **Resilience:** The collation logic must correctly handle partial failures, a core feature of the system (FR12).

### Testing
- Integration tests should verify the fan-out and collation logic. Use mock adapters that simulate success, failure, and slow responses to test the orchestrator's behavior under various conditions.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
