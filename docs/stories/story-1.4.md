# Story 1.4: OTP Helper Script

## Status
Draft

## Story
**As a** user,
**I want** a CLI script that initiates the login process and prompts me to enter my OTP,
**so that** I can complete the daily authentication flow easily.

## Acceptance Criteria
1. A Python CLI script is created using `Typer`.
2. The script can be called with a specific broker to log into (e.g., `python -m scripts.otp_cli --broker fyers`).
3. The script calls the Ordo API to initiate the login, which may involve printing a URL for the user to visit.
4. The script prompts the user to enter the OTP they receive on their device.
5. The script submits the OTP back to the Ordo API to complete the login.
6. The script provides clear feedback on success or failure.

## Tasks / Subtasks
- [ ] Create `scripts/otp_cli.py`.
- [ ] Use `Typer` to create the CLI command structure.
- [ ] Use `httpx` to make API calls to the Ordo service.
- [ ] Implement the interactive prompts for OTP entry.
- [ ] Add error handling for API failures.

## Dev Notes
- **User Experience:** This script is a key part of the daily user workflow (FR5). It should be simple and intuitive to use.
- **API Client:** The script will act as a client to the Ordo API. It will need to use the same bearer token for authentication.

### Testing
- Manual testing is required to verify the interactive flow.
- Automated tests can be written to check the script's non-interactive error handling and command-line argument parsing.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
