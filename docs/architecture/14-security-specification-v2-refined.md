# 14. Security Specification (v2 Refined)

This section defines the mandatory security requirements and practices for the Ordo project.

## 14.1. Input Validation

*   **Library:** **Pydantic** is the sole library for all data validation.
*   **Location:** Validation **must** occur at the API boundary. All incoming data must be parsed into a Pydantic model before use.
*   **Approach:** A "whitelist" approach is enforced; unknown fields in request bodies will cause validation to fail.

## 14.2. Authentication & Authorization

*   **Authentication Method:** For the MVP, API access is secured by a single, static **Bearer Token** (`ORDO_API_TOKEN`).
*   **Token Rotation:** The static bearer token is loaded at service startup. Rotating it requires restarting the container with a new value.
*   **Authorization Model:** The MVP uses an all-or-nothing authorization model. A valid token grants access to all protected endpoints.

## 14.3. Secrets Management

*   **Core Rule:** Secrets **must never** be hardcoded in the source code. They must only be loaded from the environment via the Pydantic `Settings` object.
*   **Encryption Key:** The master encryption key is loaded from the environment at startup. Key rotation is a manual operational process that is out of scope for the MVP specification but is a critical consideration for long-term production hardening.
*   **Secrets in Memory:** Decrypted broker tokens and other sensitive data are held in memory only for the duration of a single request (just-in-time) to fulfill an operation. They are not cached or stored in memory long-term.
*   **Production:** Secrets must be injected into the container's environment using the host system's capabilities (e.g., Docker secrets, systemd environment files).

## 14.4. API Security

*   **Rate Limiting:** A token-bucket rate limiter is applied **per token**, with a configurable default (e.g., 100 requests/min).
*   **HTTPS Enforcement:** Production deployments **must** be run behind a reverse proxy that terminates TLS/HTTPS.
*   **CORS:** CORS is **disabled by default** and must be explicitly enabled by providing a list of trusted origins. Wildcard origins are strictly forbidden.
*   **Security Headers:** The application should include standard security headers (e.g., `X-Content-Type-Options: nosniff`) in all responses.

## 14.5. Data Protection

*   **Encryption at Rest:** Sensitive credentials in the `DbSession` table **must** be encrypted using the `cryptography` library.
*   **Logging:** Sensitive data **must** be redacted from all logs via the central `redact()` utility.

## 14.6. Dependency & Container Security

*   **Scanning Cadence:** Automated vulnerability scans will run on every CI/CD build on the `main` branch:
    *   **`pip-audit`** for Python dependencies.
    *   **`Trivy`** for the final Docker container image.
*   **Update Policy:** Dependencies should be reviewed for security updates at least monthly.
