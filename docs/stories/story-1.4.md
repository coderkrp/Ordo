# Story 1.4: OTP Helper Script

## Status
Approved

## Story
**As a** user,
**I want** a CLI script that initiates the login process and prompts me to enter my OTP,
**so that** I can complete the daily authentication flow easily.

## Acceptance Criteria
1. A Python CLI script is created using `Typer`.
2. The script can be called with a specific broker to log into (e.g., `python -m scripts.otp_cli --broker fyers`).
3. The script calls the Ordo API to initiate the login, which may involve printing a URL for the user to visit.
4. The script prompts the user to enter the OTP/URL they receive on their device.
5. The script submits the OTP back to the Ordo API to complete the login.
6. The script provides clear feedback on success or failure.

## Tasks / Subtasks
- [x] Create `scripts/otp_cli.py`.
- [x] Use `Typer` to create the CLI command structure.
- [x] Use `httpx` to make API calls to the Ordo service.
- [x] Implement the interactive prompts for OTP entry.
- [x] Add error handling for API failures.
- [x] Refactor URL parsing logic into a separate utility function in `scripts/otp_cli.py`.

## File List
- `scripts/otp_cli.py`
- `scripts/__init__.py`
- `tests/scripts/test_otp_cli.py`

## Dev Notes
- **User Experience:** This script is a key part of the daily user workflow (FR5). It should be simple and intuitive to use.
- **API Client:** The script will act as a client to the Ordo API. It will need to use the same bearer token for authentication.
- **Development Notes:**
  - Initial implementation used `async-typer`, but was migrated to `typer` directly as modern `typer` supports async commands.
  - Encountered issues with `typer[all]` extra in `pyproject.toml` which was resolved by removing `[all]`.
  - Testing required mocking `typer.echo` and `typer.prompt` directly due to `CliRunner` not awaiting async commands.

### Testing
- Manual testing is required to verify the interactive flow.
- Automated tests can be written to check the script's non-interactive error handling and command-line argument parsing.

## Dev Agent Record
- **Agent Model Used:** Gemini
- **Debug Log References:**
  - Initial test failures due to `async-typer` and `CliRunner` incompatibility.
  - `typer[all]` extra causing dependency resolution issues.
  - `fixture 'mocker' not found` due to missing `pytest-mock` dependency.
  - Whitespace issue in `typer.echo` assertion.
- **Completion Notes List:**
  - All story tasks are implemented and verified by passing tests.
  - Code adheres to project standards and structure.
  - Dependencies are correctly managed.
  - Testing strategy is applied.
- **File List:**
  - `scripts/otp_cli.py`
  - `scripts/__init__.py`
  - `tests/scripts/test_otp_cli.py`
- **Change Log:**
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
| 2025-09-30 | 1.1 | Implemented and verified OTP Helper Script. Migrated from `async-typer` to `typer`. | James (Dev Agent) |

## Status
Ready for Review

## QA Results

### Review Date: 2025-10-01

### Reviewed By: Quinn (Test Architect)

### Code Quality Assessment

The `otp_cli.py` script is well-implemented, adhering to modern Python practices with `Typer` and `httpx`. The separation of API calls is good. Error handling is robust for API and network issues. The use of `ordo.config` for settings is appropriate.

### Refactoring Performed

None.

### Compliance Check

- Coding Standards: ✓
- Project Structure: ✓
- Testing Strategy: ✓
- All ACs Met: ✓

### Improvements Checklist

- [ ] Consider refactoring the `login` function to extract URL parsing logic into a separate utility function for improved modularity and readability.

### Security Review

The script handles authentication flow and relies on the Ordo API for secure credential management. No direct security vulnerabilities were identified within the script itself. Proper configuration of `ORDO_API_BASE_URL` and secure implementation of the Ordo API are critical.

### Performance Considerations

The script is interactive and not performance-critical. Current implementation is efficient enough for its purpose.

### Files Modified During Review

None.

### Gate Status

Gate: CONCERNS → docs/qa/gates/1.4-otp-helper-script.yml
Risk profile: Not generated (no specific risk-profile task executed)
NFR assessment: Not generated (no specific nfr-assess task executed)

### Recommended Status

✗ Changes Required - See unchecked items above

