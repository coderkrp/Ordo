# Story 2.5: Extend Adapter Interface for Orders

## Status
Draft

## Story
**As an** architect,
**I want** to extend IBrokerAdapter for order placement,
**so that** all adapters can support trading functions.

## Acceptance Criteria
1. The `IBrokerAdapter` interface is extended with a `place_order` method.
2. The `place_order` method accepts a standardized `OrderRequest` DTO and returns a standardized `OrderResult` DTO.
3. The `MockAdapter` is updated to implement the new `place_order` method, returning a successful mock response.

## Tasks / Subtasks
- [ ] Add `OrderRequest` and `OrderResult` Pydantic models.
- [ ] Add the abstract `place_order` method to the `IBrokerAdapter` class.
- [ ] Implement the `place_order` method on the `MockAdapter`.

## Dev Notes
- **Interface Stability:** This change extends the core adapter contract. It should be done carefully to ensure all existing and future adapters can adhere to it.

### Testing
- The contract tests for the `IBrokerAdapter` should be updated to include checks for the `place_order` method.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
