# Story 1.1: API Authentication Middleware

## Status
Approved

## Story
**As a** developer,
**I want** API endpoints to be protected by a static bearer token,
**so that** access to the service is secure from the start.

## Acceptance Criteria
1. A FastAPI middleware is created to check for an `Authorization: Bearer <token>` header.
2. The required token is loaded from an environment variable `ORDO_API_TOKEN`.
3. Requests without a valid token header receive an HTTP 401 Unauthorized error.
4. The error response follows the standard `ApiError` JSON schema.
5. Endpoints protected by the middleware can only be accessed when a valid token is provided.

## Tasks / Subtasks
- [ ] Create a new module for authentication/security.
- [ ] Implement the bearer token middleware.
- [ ] Integrate the middleware into the main FastAPI application.
- [ ] Add `ORDO_API_TOKEN` to the configuration model.
- [ ] Apply the middleware to a test endpoint to verify its function.

## Dev Notes
- **Security:** This is a foundational security feature (NFR9, NFR6). The implementation should be in its own module (`security.py` or similar) as per the architecture.
- **Configuration:** The token must be loaded from the environment, not hardcoded.

### Testing
- Unit tests should verify that the middleware correctly rejects requests with missing or invalid tokens and allows requests with valid tokens.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
