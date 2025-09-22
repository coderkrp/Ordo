# Story 1.3: Fyers Adapter - Authentication

## Status
Draft

## Story
**As a** developer,
**I want** to implement the authentication portion of the Fyers adapter,
**so that** the application can connect to a real broker.

## Acceptance Criteria
1. A `FyersAdapter` class is created that implements the `IBrokerAdapter` interface.
2. The adapter correctly handles the Fyers OAuth 2.0-style login flow.
3. It can successfully generate a login URL, accept an auth code, and retrieve an access token.
4. The retrieved session token is securely persisted using the Session Manager component.
5. The adapter can report a valid session status after a successful login.

## Tasks / Subtasks
- [ ] Create `src/ordo/adapters/fyers.py`.
- [ ] Implement the `initiate_login` and `complete_login` methods for the Fyers API.
- [ ] Add a `FyersConfig` model for the required credentials (`App ID`, `Secret ID`).
- [ ] Integrate with the `SessionManager` to store the encrypted session tokens.
- [ ] Use `httpx` for all outbound API calls.

## Dev Notes
- **External API:** The Fyers API documentation is at `https://myapi.fyers.in/docsv3`. The logic must match this specification.
- **Security:** All secrets (`App ID`, `Secret ID`, tokens) must be handled securely and never logged.

### Testing
- Integration tests should be written using `respx` to mock the Fyers API endpoints and verify that the adapter correctly handles the authentication flow and token exchange.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
