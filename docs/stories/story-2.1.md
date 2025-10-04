# Story 2.1: HDFC Securities Adapter

## Status
Approved

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
- [ ] Implement `place_order`.
- [ ] Add `HDFCConfig` to the configuration models.
- [ ] Write `respx`-based integration tests for all adapter methods.

## Dev Notes
- **External API:** HDFC Securities API documentation is at `https://developer.hdfcsec.com/`.
- **Complexity:** This adapter adds a second real broker, which will validate the robustness of the `IBrokerAdapter` interface.

### Testing
- A full suite of integration tests mocking the HDFC API is required to ensure compliance with the adapter contract.

## QA Notes
- Risk profile: docs/qa/assessments/2.1-risk-20251003.md

## File List
- src/ordo/adapters/hdfc.py

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
| 2025-10-03 | 1.1 | Risk profile added | Quinn (QA) |
