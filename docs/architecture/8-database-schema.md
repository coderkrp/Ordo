# 8. Database Schema

This section provides the concrete Data Definition Language (DDL) for the project's SQLite database, based on the conceptual models defined previously.

## 8.1. SQLite Schema (v2 Refined)

```sql
-- =================================================================
-- Ordo Database Schema (SQLite) - v2 Refined
-- =================================================================

-- Stores active broker sessions.
CREATE TABLE IF NOT EXISTS DbSession (
    broker_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    access_token_encrypted TEXT NOT NULL,
    refresh_token_encrypted TEXT,
    access_expires_at DATETIME NOT NULL,
    refresh_expires_at DATETIME,
    metadata_json TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (broker_id, account_id)
);

-- Trigger to auto-update updated_at on row update
CREATE TRIGGER IF NOT EXISTS trg_session_updated
AFTER UPDATE ON DbSession
FOR EACH ROW
BEGIN
    UPDATE DbSession SET updated_at = CURRENT_TIMESTAMP
    WHERE broker_id = OLD.broker_id AND account_id = OLD.account_id;
END;

-- Stores idempotency keys to prevent duplicate write operations.
CREATE TABLE IF NOT EXISTS DbIdempotencyRecord (
    key TEXT PRIMARY KEY,
    response_snapshot_json TEXT NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Stores the state of the global kill-switch.
-- This table is expected to have only a single row (id=1).
CREATE TABLE IF NOT EXISTS DbKillSwitch (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    is_active BOOLEAN NOT NULL DEFAULT 0,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Trigger to auto-update updated_at when kill-switch changes
CREATE TRIGGER IF NOT EXISTS trg_killswitch_updated
AFTER UPDATE ON DbKillSwitch
FOR EACH ROW
BEGIN
    UPDATE DbKillSwitch SET updated_at = CURRENT_TIMESTAMP WHERE id = 1;
END;

-- (Optional) Persists the state of circuit breakers to survive restarts.
-- NOTE: For MVP, this may be left unused and managed in-memory only.
CREATE TABLE IF NOT EXISTS DbCircuitBreakerState (
    adapter_id TEXT PRIMARY KEY,
    state TEXT NOT NULL CHECK(state IN ('CLOSED', 'OPEN', 'HALF_OPEN')),
    failure_count INTEGER NOT NULL DEFAULT 0,
    last_failure_at DATETIME,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Trigger to auto-update updated_at on row update
CREATE TRIGGER IF NOT EXISTS trg_circuitbreaker_updated
AFTER UPDATE ON DbCircuitBreakerState
FOR EACH ROW
BEGIN
    UPDATE DbCircuitBreakerState SET updated_at = CURRENT_TIMESTAMP
    WHERE adapter_id = OLD.adapter_id;
END;

-- (Optional) Persists audit logs to the database if file-based logging is disabled.
-- IMPORTANT: Sensitive fields (tokens, PII) must be masked before insertion.
CREATE TABLE IF NOT EXISTS DbAuditLogEntry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    correlation_id TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    component TEXT NOT NULL,
    action TEXT NOT NULL,
    outcome TEXT,
    payload_json TEXT -- Redacted / masked payload only
);

-- =================================================================
-- Indexes
-- =================================================================

-- Idempotency cleanup optimization
CREATE INDEX IF NOT EXISTS idx_idempotency_expires_at
ON DbIdempotencyRecord(expires_at);

-- Session lookup optimization
CREATE INDEX IF NOT EXISTS idx_session_account
ON DbSession(account_id);

-- Audit log lookup optimizations
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp
ON DbAuditLogEntry(timestamp);

CREATE INDEX IF NOT EXISTS idx_audit_log_correlation_id
ON DbAuditLogEntry(correlation_id);

-- Circuit breaker monitoring
CREATE INDEX IF NOT EXISTS idx_circuitbreaker_updated
ON DbCircuitBreakerState(updated_at);
```

---
