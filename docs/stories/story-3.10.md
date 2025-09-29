# Story 3.10: Background Jobs Runner

## Status
Draft

## Story
**As a** system operator,
**I want** a reliable background job runner,
**so that** periodic maintenance tasks like session refreshing and data cleanup can run automatically without manual intervention.

## Acceptance Criteria
1. An `asyncio` background task supervisor is implemented and started with the main application.
2. The supervisor runs jobs at configurable intervals.
3. The supervisor monitors jobs and restarts them with an exponential backoff policy if they fail.
4. A recurring job is created for proactive `session_refresh` for brokers that support it.
5. A recurring job is created for `idempotency_cleanup` to delete expired keys from the database.
6. Job health (e.g., last successful run, status) is logged and can be monitored.

## Tasks / Subtasks
- [ ] Create `src/ordo/jobs/runner.py` to house the job supervisor and scheduling logic.
- [ ] Implement the `session_refresh` job.
- [ ] Implement the `idempotency_cleanup` job.
- [ ] Integrate the job runner into the main application startup sequence in `main.py`.
- [ ] Add configuration for job intervals and timeouts in `config.py`.
- [ ] Write integration tests to verify that jobs run on schedule and that the supervisor handles failures correctly.

## Dev Notes
- **Architecture:** This story implements the "Background Jobs Runner" component specified in the Architecture document (Section 5.5).
- **Resilience:** The runner is critical for long-term stability. It must be resilient to individual job failures and prevent them from crashing the main application.
- **Dependencies:** The `idempotency_cleanup` job depends on Story 2.8 (Idempotency Key Support).

### Testing
- Integration tests should verify that the supervisor correctly starts, stops, and restarts jobs on schedule and on failure.
- The `idempotency_cleanup` job test should verify that expired keys are deleted while active keys remain untouched.
- The `session_refresh` job test should verify that it correctly interacts with the `SessionManager`.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-27 | 1.0 | Initial draft | John (PM) |
