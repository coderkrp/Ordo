# Story 1.5: Fyers Adapter - Portfolio

## Status
Draft

## Story
**As a** developer,
**I want** to implement portfolio fetching in the Fyers adapter,
**so that** the application can retrieve user account data.

## Acceptance Criteria
1. The `get_portfolio` method is implemented in the `FyersAdapter`.
2. The adapter calls the appropriate Fyers API endpoint (e.g., `/profile`, `/funds`, `/holdings`).
3. The adapter successfully translates the Fyers-specific response into Ordo's standardized `Portfolio` DTO.
4. The implementation correctly handles API errors and returns a standardized `ApiError`.

## Tasks / Subtasks
- [ ] Implement the `get_portfolio` method in `src/ordo/adapters/fyers.py`.
- [ ] Add logic to fetch data from all required Fyers endpoints.
- [ ] Write the data mapping logic to transform the Fyers response into the standard `Portfolio` model.
- [ ] Add error handling for Fyers API errors.

## Dev Notes
- **Data Mapping:** This is a critical step in fulfilling the core goal of unifying broker APIs. The mapping must be accurate and robust.
- **Dependencies:** This story depends on Story 1.3, as a valid session is required to fetch portfolio data.

### Testing
- Integration tests using `respx` should be written to mock the Fyers portfolio APIs and verify that the adapter correctly parses the response and maps it to the `Portfolio` DTO.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
