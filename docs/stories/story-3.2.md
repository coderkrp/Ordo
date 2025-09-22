# Story 3.2: Global Kill-Switch

## Status
Draft

## Story
**As a** trader,
**I want** a global kill-switch,
**so that** I can instantly halt all trading activity in emergencies.

## Acceptance Criteria
1. A secure API endpoint (e.g., POST `/api/v1/killswitch`) is created to enable or disable the kill-switch.
2. When the kill-switch is active, all new order placement requests are immediately rejected with an HTTP 423 Locked status and a clear error message.
3. Existing in-flight requests are allowed to complete.
4. The state of the kill-switch is persisted to the database to survive application restarts.
5. The current state of the kill-switch is reported in the `/status` endpoint.

## Tasks / Subtasks
- [ ] Create a `DbKillSwitch` model and repository.
- [ ] Create the `/api/v1/killswitch` endpoint with admin-level protection.
- [ ] Add a check at the very beginning of the order placement logic in the orchestrator.
- [ ] Update the `/status` endpoint to include the kill-switch state.

## Dev Notes
- **Safety:** This is the ultimate safety control (FR17). It must be the very first check for any trading-related operation.

### Testing
- Integration tests must verify that when the kill-switch is enabled, order placement calls are rejected, and when disabled, they proceed.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
