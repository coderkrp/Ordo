# Story 1.3: Fyers Adapter - Authentication

## Status
Done

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
- [x] Create `src/ordo/adapters/fyers.py`.
- [x] Implement the `initiate_login` and `complete_login` methods for the Fyers API.
- [x] Add a `FyersConfig` model for the required credentials (`App ID`, `Secret ID`).
- [x] Integrate with the `SessionManager` to store the encrypted session tokens.
- [x] Use `httpx` for all outbound API calls.
- [x] Implement `get_session_status` to validate session tokens.
- [x] Add test coverage for CSRF protection.
- [x] Use custom `CSRFError` for security exceptions.

## Dev Notes
- **External API:** The Fyers API documentation is at `https://myapi.fyers.in/docsv3`. The logic must match this specification.
- **Security:** All secrets (`App ID`, `Secret ID`, tokens) must be handled securely and never logged.

### Testing
- Integration tests should be written using `respx` to mock the Fyers API endpoints and verify that the adapter correctly handles the authentication flow and token exchange.

## Dev Agent Record

### Completion Notes
- Integrated the `SessionManager` to securely store and retrieve session state and access tokens.
- Updated tests to mock the `SessionManager` and verify the integration.
- Implemented `get_session_status` in `FyersAdapter` to validate session tokens by making a profile API call.
- Added a test case for CSRF protection, ensuring `CSRFError` is raised on state mismatch.
- Created a custom `CSRFError` exception to provide more specific security error details.
- Added comprehensive tests for the new `get_session_status` method, covering active, inactive, and error states.

### File List
- `src/ordo/adapters/fyers.py` (modified)
- `tests/adapters/test_fyers.py` (modified)
- `src/ordo/models/api/errors.py` (modified)

## QA Notes
- risk profile: docs/qa/assessments/1.3-risk-20250927.md
- Test design matrix: docs/qa/assessments/1.3-test-design-20250927.md
- P0 tests identified: 4

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
| 2025-09-22 | 1.1 | QA Noes | Quinn (QA) |
| 2025-09-29 | 1.2 | Applied QA fixes for session status, CSRF testing, and custom exceptions. | James (Dev) |

## QA Results

### Review Date: 2025-09-29

### Reviewed By: Quinn (Test Architect)

### Code Quality Assessment
The implementation of the Fyers v3 adapter is clean, well-structured, and adheres to good programming practices. The code is readable and maintainable. The use of `httpx` for asynchronous requests and Pydantic for configuration management is appropriate.

### Refactoring Performed

- **File**: `src/ordo/adapters/fyers.py`
  - **Change**: Updated the Fyers adapter to use the v3 API for all authentication flows. This included changing the base URL, updating the `validate-authcode` payload to use `appIdHash`, and implementing a new method to refresh the access token.
  - **Why**: To align with the latest Fyers API and improve security and functionality.
  - **How**: By modifying the `FyersAdapter` class to use the v3 endpoints and authentication logic as per the user's request.

### Compliance Check

- Coding Standards: [✓]
- Project Structure: [✓]
- Testing Strategy: [✓]
- All ACs Met: [✓]

### Improvements Checklist

- [ ] Consider moving the Fyers API URLs to a centralized configuration file or constants module for even better maintainability.

### Security Review
The adapter correctly implements CSRF protection and securely handles secrets and tokens. The v3 API usage is aligned with the provided documentation.

### Performance Considerations
No performance issues were identified. The use of asynchronous requests is appropriate for a high-performance application.

### Files Modified During Review
- `src/ordo/adapters/fyers.py`
- `tests/adapters/test_fyers.py`

### Gate Status
Gate: PASS → qa.qaLocation/gates/1.3b-fyers-adapter-authentication.yml

### Recommended Status
[✓ Ready for Done]
