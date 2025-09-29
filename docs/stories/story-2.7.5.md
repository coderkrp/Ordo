# Story 2.7.5: Foundational Database Layer

## Status
Ready

## Story
**As a** developer,
**I want** a foundational database layer using the repository pattern,
**so that** the application can persist data for features like idempotency and the kill-switch.

## Acceptance Criteria
1. `SQLModel` is added as a dependency for ORM.
2. A database connection manager is created for SQLite.
3. A base repository pattern is established to abstract data access.
4. The database is initialized on application startup.
5. Unit tests verify the database connection and basic repository functionality.

## Tasks / Subtasks
- [ ] Add `sqlmodel` to dependencies.
- [ ] Create `src/ordo/db.py` to manage the database engine and sessions.
- [ ] Implement a `BaseRepository` class.
- [ ] Integrate the database setup into the main FastAPI app.
- [ ] Create `tests/test_db.py`.

## Dev Notes
- **Architecture:** This story establishes the core data persistence pattern for the application, which is a prerequisite for several key features.
- **Dependencies:** This story unblocks Story 2.8 (Idempotency) and Story 3.2 (Kill-Switch).

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-27 | 1.0 | Initial draft | John (PM) |
