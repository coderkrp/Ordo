# Ordo
### One API. All brokers. Unified.

**Ordo** is an open-source backend that unifies multiple Indian broker APIs into a single, consistent, and resilient trading interface.  
Instead of juggling different broker endpoints and quirks, Ordo gives developers and trading teams one reliable API for order execution, portfolio tracking, and market data.

- 🔗 **Unified API** — trade across brokers like HDFC Securities, Mirae m.Stock, and Fyers through one standard interface.  
- 🔄 **Resilient by Design** — built-in retries, rate limits, idempotency, and circuit breakers.  
- 🔐 **Secure & Transparent** — open-source, credential encryption, TLS transport.  
- ⚡ **Lightweight** — deploy in minutes on a 1 vCPU / 1 GB RAM instance.  
- 🛠️ **Extensible** — modular broker adapters, easy to add new brokers.  

**Use Ordo to bring order to your trading infrastructure.**

## Quickstart

Get started with Ordo by following our comprehensive [Quickstart Guide](docs/quickstart.md).

## Fyers Login Guide for Ordo CLI

This guide will walk you through the process of authenticating with Fyers using the Ordo CLI.

### Prerequisites

1.  **Fyers Developer Account:** You need a Fyers developer account and an app created with the following details:
    *   **App Name:** Choose a name for your application.
    *   **Redirect URL:** This is the URL that Fyers will redirect to after you log in. For this CLI-based flow, you can use your ngrok URL. For example: `https://hardly-wilted-urchin.ngrok-free.app`
2.  **Ordo API Server Running:** Your Ordo API server must be running and accessible.
3.  **ngrok:** You need ngrok to expose your local Ordo API server to the internet.

### Step 1: Set Your Credentials

You can provide your Fyers credentials to the CLI in two ways:

1.  **Environment Variables:** Set the following environment variables in your `.env` file:
    ```
    FYERS_APP_ID="your_fyers_app_id"
    FYERS_SECRET_ID="your_fyers_secret_id"
    FYERS_REDIRECT_URI="your_ngrok_url"
    ```
2.  **Command-Line Arguments:** You can pass the credentials as arguments when you run the script.

### Step 2: Run the Login Script

Open your terminal and run the following command:

```bash
python -m scripts.otp_cli login --broker fyers
```

If you are not using environment variables, you can pass the credentials as arguments:

```bash
python -m scripts.otp_cli login --broker fyers --app-id "your_fyers_app_id" --secret-id "your_fyers_secret_id" --redirect-uri "your_ngrok_url"
```

### Step 3: Authenticate with Fyers

1.  The script will output a **login URL**. Copy this URL and paste it into your web browser.
2.  Log in with your Fyers credentials.
3.  After a successful login, Fyers will redirect you to the `Redirect URL` you configured in your Fyers app. You will likely see a "not found" error in your browser because the ngrok URL is pointing to your backend server, which doesn't serve a webpage at that path. **This is expected.**

### Step 4: Capture the Redirect URL

1.  The URL in your browser's address bar will look something like this:

    ```
    https://hardly-wilted-urchin.ngrok-free.app/?s=ok&code=200&message=&auth_code=eyJ...&state=your_state
    ```

2.  Copy the **entire URL** from your browser's address bar.

### Step 5: Complete the Login

1.  Go back to your terminal where the `otp_cli.py` script is running.
2.  The script will prompt you to "Enter the full redirect URL".
3.  Paste the URL you copied from your browser and press Enter.

The script will then complete the authentication process, and you will receive an access token.
