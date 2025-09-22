# Story 2.6: Implement Order Placement

## Status
Draft

## Story
**As a** developer,
**I want** adapters to implement order placement,
**so that** the service can execute trades.

## Acceptance Criteria
1. The `FyersAdapter` implements the `place_order` method.
2. The `HDFCAdapter` implements the `place_order` method.
3. The `MiraeAdapter` implements the `place_order` method.
4. Each adapter correctly maps the standard `OrderRequest` to its broker-specific API format.
5. Each adapter correctly maps the broker's response back to the standard `OrderResult`.

## Tasks / Subtasks
- [ ] Implement `place_order` in `FyersAdapter`.
- [ ] Implement `place_order` in `HDFCAdapter`.
- [ ] Implement `place_order` in `MiraeAdapter`.
- [ ] Write integration tests for each implementation using `respx`.

## Dev Notes
- **Core Functionality:** This story implements the primary trading function of the application.
- **Dependencies:** Depends on Story 2.5.

### Testing
- Extensive integration testing is required for each adapter to ensure order placement is reliable and correct.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
