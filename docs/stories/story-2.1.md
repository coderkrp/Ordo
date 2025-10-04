# Story 2.1: HDFC Securities Adapter

## Status
Done

## Story
**As a** developer,
**I want** a fully implemented adapter for HDFC Securities,
**so that** the service can connect to this broker.

## Acceptance Criteria
1. A `HDFCAdapter` class is created that implements the full `IBrokerAdapter` interface (auth, portfolio, orders).
2. The adapter correctly handles HDFC-specific API data formats and workflows for authentication.
3. The adapter correctly fetches and maps portfolio data to the standard `Portfolio` DTO.
4. The adapter correctly maps and places orders.
5. Includes unit tests using mocked broker API responses to cover successful and failed scenarios for all functions.

## Tasks / Subtasks
- [x] Create `src/ordo/adapters/hdfc.py`.
- [x] Implement `initiate_login` and `complete_login`.
- [x] Implement `get_portfolio`.
- [x] Implement `place_order`.
- [x] Add `HDFCConfig` to the configuration models.
- [x] Write `respx`-based integration tests for all adapter methods.

## Dev Notes
- **External API:** HDFC Securities API documentation is at `https://developer.hdfcsec.com/`.
- **Complexity:** This adapter adds a second real broker, which will validate the robustness of the `IBrokerAdapter` interface.

### Testing
- A full suite of integration tests mocking the HDFC API is required to ensure compliance with the adapter contract.

## QA Notes
- Risk profile: docs/qa/assessments/2.1-risk-20251003.md

## File List
- src/ordo/adapters/hdfc.py
- tests/adapters/test_hdfc.py

## Dev Agent Record

### Agent Model Used
Gemini

### Debug Log References
- `uv run ruff check . --fix`: Fixed unused imports.
- `uv run pytest`: All tests passed.

### Completion Notes
- Addressed the hardcoded consent issue by adding an optional `consent` parameter to the `complete_login` method.
- Added a comment to clarify the `day_pnl` limitation in the `get_portfolio` method.

### Change Log

- **2025-10-04**: Applied fixes based on QA feedback.
  - Modified `src/ordo/adapters/hdfc.py` to handle user consent dynamically.
  - Updated comments in `src/ordo/adapters/hdfc.py` regarding `day_pnl`.
  - Removed unused imports from `src/ordo/adapters/hdfc.py` and `tests/adapters/test_hdfc.py`.

## QA Results

### Review Date: 2025-10-04

### Reviewed By: Quinn (Test Architect)

### Code Quality Assessment

The initial implementation was functionally correct but the login methods in `HDFCAdapter` were long and complex, making them difficult to maintain. The code has been refactored to break down these methods into smaller, more manageable private methods. This improves readability and aligns with best practices.

### Refactoring Performed

- **File**: `src/ordo/adapters/hdfc.py`
  - **Change**: Refactored `initiate_login` and `complete_login` methods into smaller private methods (`_get_login_token`, `_validate_user`, `_validate_2fa`, `_authorize_session`, `_get_access_token`).
  - **Why**: To improve readability, maintainability, and testability of the code.
  - **How**: By breaking down the complex login logic into smaller, single-responsibility methods.

### Compliance Check

- Coding Standards: ✓
- Project Structure: ✓
- Testing Strategy: ✓
- All ACs Met: ✓

### Improvements Checklist

- [x] Refactored `HDFCAdapter` for better readability and maintainability.
- [x] The hardcoded `consent="true"` in `_authorize_session` should be replaced with a mechanism for explicit user consent.
- [x] The hardcoded `day_pnl=0.0` in `get_portfolio` should be verified against the HDFC API's capabilities. If the API provides this data, it should be used.

### Security Review

- The hardcoded `consent="true"` presents a potential security risk as it bypasses explicit user consent. This has been flagged as a concern.

### Performance Considerations

- No performance issues were identified.

### Files Modified During Review

- `src/ordo/adapters/hdfc.py`

### Gate Status

Gate: CONCERNS → qa/gates/2.1-hdfc-securities-adapter.yml

### Recommended Status

✗ Changes Required - See unchecked items above

### Review Date: 2025-10-04 (Follow-up)

### Reviewed By: Quinn (Test Architect)

### Code Quality Assessment

The developer has successfully addressed the concerns from the previous review. The hardcoded `consent` issue is resolved by introducing a parameter, and the `day_pnl` limitation is now clearly documented with a code comment. The refactoring of the login methods has significantly improved the code's readability and maintainability.

### Compliance Check

- Coding Standards: ✓
- Project Structure: ✓
- Testing Strategy: ✓
- All ACs Met: ✓

### Improvements Checklist

- [✓] Refactored `HDFCAdapter` for better readability and maintainability.
- [✓] The hardcoded `consent="true"` in `_authorize_session` should be replaced with a mechanism for explicit user consent.
- [✓] The hardcoded `day_pnl=0.0` in `get_portfolio` should be verified against the HDFC API's capabilities. If the API provides this data, it should be used.

### Security Review

- The consent issue has been addressed. No further security concerns were identified.

### Performance Considerations

- No performance issues were identified.

### Files Modified During Review

- None

### Gate Status

Gate: PASS → qa/gates/2.1-hdfc-securities-adapter.yml

### Recommended Status

✓ Ready for Done
