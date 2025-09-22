# 7. Core Workflows

This section illustrates key system workflows using sequence diagrams.

## 7.1. Order Placement Workflow (v2)

This diagram details the end-to-end flow for placing an order, including all major components, safety checks, and resilience patterns.

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Ordo API
    participant O as Orchestrator
    participant S as SessionManager
    participant D as Idempotency DB
    participant K as KillSwitch
    participant CB as CircuitBreaker
    participant AU as Audit Service
    participant AD1 as Adapter Fyers
    participant AD2 as Adapter HDFC

    C->>A: POST /api/v1/orders (payload + Idempotency-Key)
    A->>A: Validate token + payload
    A->>AU: Log request received
    A->>O: execute_order(payload)

    O->>D: 1. Check idempotency key
    alt Key found
        D-->>O: Return cached result
        O-->>A: Cached unified response
        A-->>C: HTTP 200 (from cache)
    else Key not found
        D-->>O: Not found
    end

    O->>K: 2. Check killswitch
    alt KillSwitch active
        K-->>O: Active
        O->>AU: Log kill-switch reject
        O-->>A: ApiError (KILL_SWITCH_ACTIVE)
        A-->>C: HTTP 403
    else Inactive
        K-->>O: Inactive
    end

    O->>S: 3. Ensure sessions valid (Fyers, HDFC)
    S-->>O: Sessions valid (or refreshed)

    O->>O: 4. Perform global pre-trade validations (schema, supported type)

    par
        O->>CB: Check CircuitBreaker (Fyers)
        alt Breaker OPEN
            CB-->>O: Skip Fyers
            O->>AU: Log skipped broker (circuit open)
        else Breaker CLOSED
            CB-->>O: Closed
            O->>AD1: 5. place_order (with retries/backoff)
            AD1-->>O: OrderResult(success/broker_order_id)
        end
    and
        O->>CB: Check CircuitBreaker (HDFC)
        alt Breaker OPEN
            CB-->>O: Skip HDFC
            O->>AU: Log skipped broker (circuit open)
        else Breaker CLOSED
            CB-->>O: Closed
            O->>AD2: 5. place_order (with retries/backoff)
            AD2-->>O: OrderResult(error: RATE_LIMIT_EXCEEDED)
        end
    end

    O->>D: 6. Store idempotency result
    O->>AU: Log final per-broker results
    O-->>A: 7. Collate unified response (partial_success)
    note right of O: Unified schema with<br/>broker_id, status, order_id, error_code

    A-->>C: HTTP 207 Multi-Status (or 200 OK + per-broker results)
```

---
