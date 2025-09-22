# 6. External APIs

This section details the external broker APIs required for the MVP.

## 6.1. Fyers API

*   **Purpose:** Provides trading and user data access for Fyers accounts.
*   **Documentation:** `https://myapi.fyers.in/docsv3`
*   **Authentication:** OAuth 2.0-style flow requiring an `App ID` and `Secret ID` obtained from the Fyers developer dashboard.
*   **Rate Limits:** The API has rate limits which must be confirmed from the documentation during implementation.
*   **Key Endpoints Used (Logical):**
    *   Login & Session: `POST /login/otp`, `POST /login/pin`, `POST /validate-token`
    *   User Data: `GET /profile`, `GET /funds`, `GET /holdings`
    *   Trading: `POST /orders`, `GET /orders`, `DELETE /orders`
    *   Market Data: `GET /quotes`

## 6.2. HDFC Securities API

*   **Purpose:** Provides trading and user data access for HDFC Securities InvestRight clients.
*   **Documentation:** `https://developer.hdfcsec.com/`
*   **Authentication:** Requires an `API Key` and `Secret Key` obtained from the HDFC Securities developer portal.
*   **Rate Limits:** To be confirmed from documentation during implementation.
*   **Key Endpoints Used (Logical):**
    *   Login & Session: Endpoints for initiating and completing login.
    *   User Data: `GET /portfolio`, `GET /holdings`, `GET /positions`
    *   Trading: `POST /orders`, `GET /orders`

## 6.3. Mirae Asset m.Stock API

*   **Purpose:** REST-like HTTP APIs for trading and investment with m.Stock.
*   **Documentation:** Available on the `mstock.com` website.
*   **Authentication:** Requires a long-lived `API Key` and a short-lived `Access Token` (JWT) that must be generated daily via an OTP flow.
*   **Rate Limits:** The documentation specifies detailed rate limits per API category (Order, Data, Quote) on a per-second, minute, hour, and day basis. These must be strictly adhered to by the adapter.
*   **Key Endpoints Used (Logical):**
    *   Login & Session: Endpoints for generating an access token via OTP.
    *   User Data: Endpoints for retrieving user profile and portfolio.
    *   Trading: `POST /orders`, `GET /orders`

---
