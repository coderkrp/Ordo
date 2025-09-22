# Story 1.2: Broker Adapter Interface & Mock Adapter

## Status
Draft

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
- [ ] Create `src/ordo/adapters/base.py` for the `IBrokerAdapter` interface.
- [ ] Define the abstract methods `initiate_login`, `complete_login`, `get_portfolio`, etc.
- [ ] Create `src/ordo/adapters/mock.py` for the `MockAdapter`.
- [ ] Implement the mock adapter with hardcoded data.
- [ ] Create a mechanism (e.g., in `config.py`) to select and load the desired adapter.

## Dev Notes
- **Architecture:** This is the core of the Hexagonal Architecture pattern (Architecture, Section 2.4, 5.2). Getting this interface right is critical for future extensibility (NFR12).
- **Testing:** The `MockAdapter` will be essential for unit and integration tests of the orchestrator and API endpoints without making live broker calls.

### Testing
- Unit tests should be written for the `MockAdapter` to ensure it correctly implements the interface and returns the expected mock data.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
