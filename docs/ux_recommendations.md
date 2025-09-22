# UX Recommendations for the OTP Helper Script

This document provides UX guidance for the Command-Line Interface (CLI) `OTP Helper Script` (Story 1.4) to ensure it is clear, usable, and error-resilient.

## 1. Guiding Principles

- **Clarity is Key:** The user should always understand what is happening, what is expected of them, and whether an action succeeded or failed.
- **Provide Feedback:** Acknowledge every user input and provide immediate feedback on the result.
- **Guide, Don't Assume:** Guide the user through the process.
- **Design for Errors:** Errors are inevitable. The script should handle them gracefully and provide actionable advice.
- **Automation First:** A good CLI tool should be scriptable and usable by both humans and machines.

## 2. Visual and Interaction Design

### 2.1. Semantic Formatting
The script should use a combination of color and symbols for accessibility, ensuring that status is clear even for color-blind users.

- `[ℹ️ INFO]` (Blue/Default): General information.
- `[▶️ ACTION]` (Cyan): The script is performing an action.
- `[❓ PROMPT]` (Yellow): User input is required.
- `[✅ SUCCESS]` (Green): A successful operation.
- `[⚠️ WARN]` (Magenta): A non-critical issue or warning.
- `[❌ ERROR]` (Red): A failure.
- `[📋 DETAIL]` (Gray): Additional, less critical details.

### 2.2. Basic Interactive Workflow

The initial interactive workflow should be clear and guide the user step-by-step.

**Initial Scan:**
```bash
$ ./login.sh
[ℹ️ INFO] Scanning for configured brokers...
[ℹ️ INFO] Found 2 brokers: Fyers, HDFC Securities
```

**Login Process:**
```bash
[▶️ ACTION] Initiating login for Fyers (1 of 2)...
[✅ SUCCESS] Login process for Fyers initiated.
[❓ PROMPT] Please enter the OTP you received for Fyers: 123456

[▶️ ACTION] Verifying OTP for Fyers...
[✅ SUCCESS] Authentication successful for Fyers.
---
[▶️ ACTION] Initiating login for HDFC Securities (2 of 2)...
```

## 3. Error Handling and Edge Cases

### 3.1. Invalid or Expired OTP
The script must differentiate between an invalid OTP and an expired one, as the remedy is different.

```bash
[▶️ ACTION] Verifying OTP for Fyers...
[❌ ERROR] OTP for Fyers has expired.
[▶️ ACTION] Re-initiating login process for Fyers...
[✅ SUCCESS] New login process initiated.
[❓ PROMPT] Please enter the new OTP you received for Fyers:
```

### 3.2. Login Initiation Failure
Provide clear, actionable details if the login process can't even start.

```bash
[▶️ ACTION] Initiating login for Fyers...
[❌ ERROR] Failed to initiate login for Fyers.
[📋 DETAIL] Reason: Invalid client_id or secret in configuration.
[ℹ️ INFO] Please check your credentials for Fyers and try again.
[❓ PROMPT] Continue with next broker? (y/n): y
```

### 3.3. Timeouts
The script should not hang indefinitely.

```bash
[▶️ ACTION] Initiating login for Fyers...
[❌ ERROR] Timed out after 30 seconds waiting for a response from Fyers.
[ℹ️ INFO] The broker API may be down or experiencing issues.
[❓ PROMPT] Continue with next broker? (y/n): y
```

## 4. Advanced Features: Automation & Usability

To make the script a true power tool, the following features are recommended.

### 4.1. Automation-Friendly Mode
- **`--non-interactive` flag:** In this mode, the script will not prompt for input. If an expected environment variable is not set, it should fail for that broker. It should support two flexible formats:
    1.  Individual variables: `OTP_FYERS=123456`, `OTP_HDFC=789012`
    2.  A single composite variable: `ORDO_OTPS="fyers=123456,hdfc=789012"`
- **`--quiet` flag:** Suppresses all non-essential, human-readable output (e.g., `INFO`, `SUCCESS`). It will only print critical `ERROR` messages to `stderr` upon failure, making it ideal for cron jobs or other automated scripts where the exit code is the primary result.

### 4.2. Standardized Exit Codes
The script must use exit codes to signal its final state for scripting.
- `0`: All brokers authenticated successfully.
- `1`: Config error (e.g., file not found, invalid YAML).
- `2`: Authentication failed for all brokers.
- `3`: Partial success. At least one broker succeeded, but at least one failed.
- `4`: Prerequisite missing for non-interactive mode (e.g., `OTP_FYERS` not set).
- `5`: Network error or API timeout.
- `6`: Unexpected runtime error.

### 4.3. Partial Success Reporting
In interactive mode, if some brokers fail, the script should end with a clear summary report.

```bash
[ℹ️ INFO] Login process complete.
[✅ SUCCESS] Fyers
[❌ ERROR] HDFC Securities (Reason: Invalid OTP)
[✅ SUCCESS] Mirae m.Stock
[⚠️ WARN] Process finished with partial success. (Exit Code: 3)
```

### 4.4. Flexible Execution
- **`--broker <name>` flag:** Allows the user to run the login process for one or more specific brokers (e.g., `./login.sh --broker fyers --broker mirae`).
- **`--retry-failed` flag:** After a full run, automatically re-attempts the login process for any brokers that failed.
- **`--help` flag:** Prints a helpful usage message detailing all available commands, flags, and environment variables.

### 4.5. Configuration and Logging
- **`validate-config` command:** A subcommand (`./login.sh validate-config`) to parse the config file and report any errors.
- **`--log-file <path>` flag:** Writes structured JSON logs to a specified file. The schema should be:
  `{ "timestamp": "...", "broker": "...", "action": "...", "status": "...", "detail": "..." }`
- **`--verbose` flag:** Prints detailed diagnostic information, such as API request/response data, to the console for debugging.

## 5. Configuration Details

- The script should expect a configuration file in **YAML format**.
- The default path should be `~/.config/ordo/config.yaml`, but it should be overridable with an `ORDO_CONFIG` environment variable.

## 6. Security Considerations
 
- A clear warning should be included in the `--help` output and the main README regarding the use of environment variables for secrets.
- **Warning Text Example:** "Storing secrets or OTPs in environment variables can be insecure and may leak to shell history or system logs. For sensitive production use, prefer the interactive mode or manage environment variables with a secure vault system."
