# Story 3.4: Configurable & Structured Logging

## Status
Draft

## Story
**As a** developer,
**I want** structured logs with configurable levels,
**so that** I can debug effectively in production.

## Acceptance Criteria
1. The logging level (`DEBUG`, `INFO`, `ERROR`) can be configured via an environment variable.
2. All log output is in a structured JSON format.
3. The application correctly uses different log levels for different types of events (e.g., `INFO` for requests, `ERROR` for failures).

## Tasks / Subtasks
- [ ] Refine the `structlog` configuration from Story 2.9.
- [ ] Add logic to parse the log level from the application config.
- [ ] Review the codebase and ensure appropriate log levels are used everywhere.

## Dev Notes
- **Observability:** This enhances the audit logging from Story 2.9 and makes the system much easier to operate (NFR21).

### Testing
- Tests should check that setting the log level environment variable correctly changes the volume of log output.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
