# Story 3.1: Circuit Breaker Service

## Status
Draft

## Story
**As a** developer,
**I want** a circuit breaker for broker calls,
**so that** repeated failures don’t overload the system or the external API.

## Acceptance Criteria
1. A circuit breaker is implemented for each broker adapter.
2. The circuit breaker opens (stops sending requests) after N consecutive failures.
3. The circuit breaker moves to a half-open state after a configured timeout, allowing one test request.
4. A successful test request closes the breaker; a failed one keeps it open.
5. The state of the circuit breaker (`OPEN`, `CLOSED`, `HALF-OPEN`) is exposed via the `/status` endpoint.

## Tasks / Subtasks
- [ ] Choose and add a circuit breaker library (e.g., `pybreaker`).
- [ ] Wrap the adapter calls within the orchestrator with the circuit breaker logic.
- [ ] Add configuration for failure thresholds and timeouts.
- [ ] Persist the circuit breaker state (optional, for surviving restarts).

## Dev Notes
- **Resilience:** This is a critical resilience pattern (FR18) to prevent cascading failures.
- **State:** The state of each breaker needs to be managed on a per-broker basis.

### Testing
- Integration tests must be written to verify the circuit breaker's state transitions. Simulate repeated failures from a mock adapter and check that the breaker opens, transitions to half-open, and eventually closes correctly.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
