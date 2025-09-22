# 11. Error Handling Strategy (v2 Refined)

This section defines the comprehensive error handling, logging, and propagation strategy for the Ordo application.

## 11.1. General Approach & Exception Hierarchy

The application's error strategy is built on a clear distinction between user-correctable errors (4xx status codes) and internal system errors (5xx status codes).

*   **Custom Exception Hierarchy:** All application-specific exceptions will inherit from a common `OrdoError` base class. This hierarchy is split into two main branches:
    *   `UserError`: Represents client-side problems (e.g., invalid input, insufficient funds, invalid session). These will be mapped to **4xx HTTP status codes**.
    *   `SystemError`: Represents server-side or upstream problems (e.g., database connection failure, unexpected broker API error). These will be mapped to **5xx HTTP status codes**.

    ```python
    # In ordo/security/exceptions.py
    class OrdoError(Exception):
        """Base class for all application exceptions."""
        def __init__(self, message: str, code: str):
            self.message = message
            self.code = code

    class UserError(OrdoError): ...
    class SystemError(OrdoError): ...

    # Examples of specific exceptions
    class ValidationError(UserError): ...
    class InsufficientFundsError(UserError): ...
    class InvalidSessionError(UserError): ...
    class BrokerError(SystemError): ...
    class PersistenceError(SystemError): ...
    ```

*   **Global Exception Handling:** A global FastAPI exception handler will be responsible for catching all `OrdoError` subclasses and unhandled Python exceptions. It will:
    1.  Log the error with the appropriate severity and full context (including `correlation_id`).
    2.  Map the exception to the standard `ApiError` JSON response schema.
    3.  Return the correct HTTP status code (4xx for `UserError`, 5xx for `SystemError` and unhandled exceptions).

## 11.2. Error Code Registry

To ensure consistency, all error codes will be centralized in a single file.

*   **Location:** `ordo/error_codes.py`
*   **Implementation:** A Python `Enum` will be used to define all canonical error codes, serving as the single source of truth.
*   **Example:**
    ```python
    from enum import Enum

    class OrdoErrorCode(str, Enum):
        # User Errors
        VALIDATION_ERROR = "VALIDATION_ERROR"
        INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
        INVALID_SESSION = "INVALID_SESSION"
        # System Errors
        BROKER_UNAVAILABLE = "BROKER_UNAVAILABLE"
        PERSISTENCE_ERROR = "PERSISTENCE_ERROR"
        # ... etc.
    ```

## 11.3. Exception to HTTP Status Code Mapping

| Exception Type | HTTP Status Code | Description |
| :--- | :--- | :--- |
| `ValidationError` | 400 Bad Request | Invalid input from the client. |
| `InvalidSessionError` | 401 Unauthorized | The broker session is invalid or expired. |
| `PermissionError` | 403 Forbidden | The user is not authorized to perform the action. |
| `NotFoundError` | 404 Not Found | The requested resource does not exist. |
| `RateLimitError` | 429 Too Many Requests | The client has exceeded the rate limit. |
| `BrokerError` | 503 Service Unavailable | An upstream broker API is unavailable or failed. |
| `PersistenceError` | 500 Internal Server Error | A database operation failed. |
| `SystemError` (generic) | 500 Internal Server Error | A generic internal system failure. |

## 11.4. Handling Specific Scenarios

*   **Partial Failures (Multi-Broker Requests):** If a request to multiple brokers results in a mix of success and failure, the API will **not** return a top-level error. Instead, it will return an **HTTP 207 Multi-Status** code, and the `UnifiedResponse` body will detail the success or failure of each individual broker in its `results` array.
*   **Background Jobs & CLI:**
    *   **Background Jobs:** The job supervisor will wrap each job execution in a `try...except` block. Any unhandled exception will be logged as CRITICAL, and a Prometheus counter (`ordo_job_failures_total`) will be incremented. The job will then be restarted according to its backoff policy.
    *   **CLI Tool:** The OTP helper CLI will catch exceptions from the Ordo API and translate them into user-friendly messages and specific exit codes for automation.

## 11.5. Security: Redaction

*   **Mandatory Redaction:** It is a strict requirement that **no sensitive data** (tokens, API keys, secrets, PII) ever appears in logs or `ApiError` responses.
*   **Central Utility:** A central `redact()` utility will be implemented and must be applied to all data payloads before they are passed to the logging framework or included in an error response.

## 11.6. Observability: Error Metrics

*   **Prometheus Counter:** In addition to logging, a Prometheus counter will track error occurrences.
*   **Metric Name:** `ordo_errors_total`
*   **Labels:** The metric will be labeled to provide dimensions for analysis:
    *   `error_code`: The canonical code from our registry (e.g., `INSUFFICIENT_FUNDS`).
    *   `component`: The part of the system where the error originated (e.g., `orchestrator`, `fyers_adapter`).

---
