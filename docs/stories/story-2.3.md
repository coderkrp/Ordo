# Story 2.3: Request Orchestrator Service

## Status
Draft

## Story
**As a** developer,
**I want** a central orchestrator service,
**so that** multi-broker requests are centralized and reusable.

## Acceptance Criteria
1. A `RequestOrchestrator` class is created in the `core` module.
2. The orchestrator has methods for `get_portfolio` and `place_order`.
3. The orchestrator takes a list of target broker IDs.
4. The orchestrator dynamically loads the required adapter implementations.
5. The API endpoints (e.g., for portfolio) are refactored to use the orchestrator instead of calling adapters directly.

## Tasks / Subtasks
- [ ] Create `src/ordo/core/orchestrator.py`.
- [ ] Implement the `RequestOrchestrator` class structure.
- [ ] Add logic to select and instantiate adapters based on broker IDs.
- [ ] Implement the initial `get_portfolio` method.
- [ ] Refactor the `/api/v1/portfolio` endpoint to delegate to the orchestrator.

## Dev Notes
- **Architecture:** This service is the "central brain" of the application (Architecture, Section 5.1). It will encapsulate the fan-out and resilience logic.
- **Dependencies:** This story is a prerequisite for true multi-broker functionality.

### Testing
- Unit tests should be written for the orchestrator, using mock adapters to verify that it correctly selects and calls the right adapters.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
