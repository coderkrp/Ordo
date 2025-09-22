# Story 2.2: Mirae m.Stock Adapter

## Status
Draft

## Story
**As a** developer,
**I want** a fully implemented adapter for Mirae m.Stock,
**so that** the service can connect to this broker.

## Acceptance Criteria
1. A `MiraeAdapter` class is created that implements the full `IBrokerAdapter` interface.
2. The adapter correctly handles Mirae-specific API data formats and workflows for authentication.
3. The adapter correctly fetches and maps portfolio data to the standard `Portfolio` DTO.
4. The adapter correctly maps and places orders.
5. The adapter respects the detailed rate limits specified in the Mirae API documentation.
6. Includes unit tests using mocked broker API responses for all functions.

## Tasks / Subtasks
- [ ] Create `src/ordo/adapters/mirae.py`.
- [ ] Implement the full `IBrokerAdapter` interface.
- [ ] Add `MiraeConfig` to the configuration models.
- [ ] Implement rate-limiting logic specific to Mirae's documented limits.
- [ ] Write `respx`-based integration tests for all adapter methods.

## Dev Notes
- **External API:** Mirae m.Stock API documentation is available on their website.
- **Rate Limiting:** This is a key requirement (FR23). The adapter must include logic (e.g., a token bucket algorithm) to avoid exceeding the API rate limits.

### Testing
- A full suite of integration tests mocking the Mirae API is required. Tests should also verify that the rate limiter works as expected.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
