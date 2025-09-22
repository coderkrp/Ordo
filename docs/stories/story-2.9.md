# Story 2.9: Audit Logging

## Status
Draft

## Story
**As a** compliance officer,
**I want** detailed audit logs,
**so that** trading activity is traceable.

## Acceptance Criteria
1. All API requests and their outcomes are logged in a structured (JSON) format.
2. All interactions with broker APIs (requests and responses) are logged.
3. Logs include a `correlation_id` to trace a single request through the system.
4. Logs are written to a local file that is automatically rotated.
5. Sensitive information (tokens, secrets) is redacted from the logs.

## Tasks / Subtasks
- [ ] Configure `structlog` for structured JSON logging.
- [ ] Add a logging middleware to FastAPI to log all incoming requests.
- [ ] Add explicit log statements in the orchestrator and adapters for key events.
- [ ] Implement a redaction utility for sensitive data.
- [ ] Configure file rotation for the log output.

## Dev Notes
- **Observability:** This is a key observability and compliance feature (FR19, NFR21).
- **Security:** The redaction of secrets is non-negotiable.

### Testing
- Tests should check that log output is structured JSON and that sensitive fields in logged payloads are correctly redacted.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
