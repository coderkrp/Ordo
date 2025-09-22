# Story 3.5: Optional Postgres Support

## Status
Draft

## Story
**As a** sysadmin,
**I want** Postgres support,
**so that** I can scale Ordo for larger workloads.

## Acceptance Criteria
1. The application can connect to a PostgreSQL database when a `DATABASE_URL` for Postgres is provided.
2. All repository implementations (for sessions, idempotency, etc.) work correctly with the Postgres backend.
3. The application continues to work with SQLite when a SQLite `DATABASE_URL` is provided.
4. The `README` is updated with instructions on how to configure the service for Postgres.

## Tasks / Subtasks
- [ ] Add `psycopg2-binary` or a suitable async alternative as an optional dependency.
- [ ] Test all database operations against a live Postgres instance.
- [ ] Ensure the `SQLModel` definitions are compatible with both SQLite and Postgres.
- [ ] Update documentation with Postgres configuration details.

## Dev Notes
- **Scalability:** This is a key scalability feature (NFR5). The use of the Repository Pattern and `SQLModel` should make this straightforward.

### Testing
- The full integration test suite should be run against both a SQLite and a PostgreSQL database to ensure compatibility.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
