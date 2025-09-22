# Story 3.9: Python Client SDK

## Status
Draft

## Story
**As a** developer,
**I want** a minimal Python client SDK,
**so that** I can easily integrate my application with the Ordo API.

## Acceptance Criteria
1. A basic Python package is created for interacting with the Ordo API.
2. The SDK provides simple methods for `get_portfolio` and `place_order`.
3. The SDK handles authentication and session management.
4. The package is published to PyPI for easy installation.
5. The repository includes clear documentation with installation and usage examples.

## Tasks / Subtasks
- [ ] Create a new directory for the client SDK (e.g., `clients/python`).
- [ ] Implement the SDK using `httpx`.
- [ ] Add packaging configuration (`pyproject.toml`).
- [ ] Write usage examples for the documentation.
- [ ] Add the SDK to the PyPI publishing workflow.

## Dev Notes
- **Adoption:** A client SDK significantly lowers the barrier to entry for new users (NFR18).

### Testing
- The SDK should have its own suite of unit tests that mock the Ordo API.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
