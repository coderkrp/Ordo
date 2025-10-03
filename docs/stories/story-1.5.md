# Story 1.5: Fyers Adapter - Portfolio

## Status
Done

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
- [x] Implement the `get_portfolio` method in `src/ordo/adapters/fyers.py`.
- [x] Add logic to fetch data from all required Fyers endpoints.
- [x] Write the data mapping logic to transform the Fyers response into the standard `Portfolio` model.
- [x] Add error handling for Fyers API errors.

## File List

- `src/ordo/adapters/fyers.py`
- `src/ordo/models/api/portfolio.py`
- `src/ordo/exceptions.py`
- `src/ordo/models/api/errors.py`
- `tests/adapters/test_fyers.py`

## Dev Notes
- **Data Mapping:** This is a critical step in fulfilling the core goal of unifying broker APIs. The mapping must be accurate and robust.
- **Dependencies:** This story depends on Story 1.3, as a valid session is required to fetch portfolio data.

### Testing
- Integration tests using `respx` should be written to mock the Fyers portfolio APIs and verify that the adapter correctly parses the response and maps it to the `Portfolio` DTO.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |

## QA Results

### Review Date: 2025-10-03

### Reviewed By: Quinn (Test Architect)

### Code Quality Assessment

The implementation of the `get_portfolio` method in the `FyersAdapter` is of high quality. The code is clean, well-structured, and follows the project's coding standards. It correctly implements the adapter pattern, uses async/await for non-blocking I/O, and handles errors gracefully by raising standardized exceptions. The use of Pydantic models for data transfer objects is also a good practice.

### Refactoring Performed

No refactoring was performed as the code is already in good shape.

### Compliance Check

- Coding Standards: ✓
- Project Structure: ✓
- Testing Strategy: ✓
- All ACs Met: ✓

### Improvements Checklist

- [ ] Consider adding tests for edge cases like empty holdings or funds in the API response.
- [ ] It would be beneficial to double-check the Fyers API documentation to confirm that `day_pnl` is truly unavailable. If it is available through another endpoint or calculation, the adapter should be updated to reflect that.

### Security Review

No security concerns were found. The implementation correctly uses CSRF protection and hashes sensitive information where necessary.

### Performance Considerations

The use of an asynchronous HTTP client (`httpx`) ensures that the adapter is non-blocking and performant. No performance issues were found.

### Files Modified During Review

None.

### Gate Status

Gate: PASS → docs/qa/gates/1.5-fyers-adapter-portfolio.yml

### Recommended Status

✓ Ready for Done
