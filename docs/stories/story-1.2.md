# Story 1.2: Broker Adapter Interface & Mock Adapter

## Status
Done

## Story
**As an** architect,
**I want** a clearly defined broker adapter interface and a mock implementation,
**so that** the core application can be developed and tested independently of real broker APIs.

## Acceptance Criteria
1. An abstract base class `IBrokerAdapter` is created defining the methods for authentication and portfolio retrieval.
2. A `MockAdapter` class is created that implements the `IBrokerAdapter` interface.
3. The `MockAdapter` returns hardcoded, valid data for portfolio requests.
4. The `MockAdapter` simulates a successful login and returns a valid session status.
5. The core application can be configured to use the `MockAdapter` for testing purposes.

## Tasks / Subtasks
- [x] Create `src/ordo/adapters/base.py` for the `IBrokerAdapter` interface.
- [x] Define the abstract methods `initiate_login`, `complete_login`, `get_portfolio`, etc.
- [x] Create `src/ordo/adapters/mock.py` for the `MockAdapter`.
- [x] Implement the mock adapter with hardcoded data.
- [x] Create a mechanism (e.g., in `config.py`) to select and load the desired adapter.

## Dev Agent Record

### Completion Notes
- Created the `IBrokerAdapter` interface with the required abstract methods.
- Implemented a `MockAdapter` with hardcoded Indian portfolio data.
- Added a factory function in `config.py` to select and load the appropriate adapter based on the `BROKER_ADAPTER` setting.
- Wrote unit tests for the `MockAdapter` and the adapter loading mechanism.
- All tests are passing.

### File List
- `src/ordo/adapters/base.py` (created)
- `src/ordo/adapters/mock.py` (created)
- `src/ordo/config.py` (modified)
- `tests/adapters/test_mock.py` (created)
- `tests/test_config.py` (created)


## Dev Notes
- **Architecture:** This is the core of the Hexagonal Architecture pattern (Architecture, Section 2.4, 5.2). Getting this interface right is critical for future extensibility (NFR12).
- **Testing:** The `MockAdapter` will be essential for unit and integration tests of the orchestrator and API endpoints without making live broker calls.

### Testing
- Unit tests should be written for the `MockAdapter` to ensure it correctly implements the interface and returns the expected mock data.

## QA Results
- Risk profile: docs/qa/assessments/1.2-risk-20250924.md
- Test design matrix: docs/qa/assessments/1.2-test-design-20250924.md
- P0 tests identified: 2

### Review Date: 2025-09-26

### Reviewed By: Quinn (Test Architect)

### Code Quality Assessment

The implementation is of high quality. The code is clean, well-structured, and adheres to the project's coding standards. The use of an abstract base class for the adapter is a good design pattern that will make the application more extensible.

### Refactoring Performed

- **File**: `tests/adapters/test_mock.py`
  - **Change**: Refactored the `test_mock_adapter_get_rich_portfolio_data` test to use a separate mock adapter for rich portfolio data.
  - **Why**: To improve the maintainability and readability of the test.
  - **How**: By creating a new `RichMockAdapter` class that inherits from `MockAdapter` and overrides the `get_portfolio` method.

### Compliance Check

- Coding Standards: [✓]
- Project Structure: [✓]
- Testing Strategy: [✓]
- All ACs Met: [✓]

### Improvements Checklist

- [x] Refactored `test_mock_adapter_get_rich_portfolio_data` for better maintainability.
- [x] Added a test to ensure `IBrokerAdapter` is abstract.

### Security Review

No security concerns found.

### Performance Considerations

Not applicable for the mock adapter.

### Files Modified During Review

- `tests/adapters/test_mock.py`

### Gate Status

Gate: PASS → qa.qaLocation/gates/1.2-broker-adapter-interface.yml

### Recommended Status

[✓ Ready for Done]

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
