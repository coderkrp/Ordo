# 1. Goals and Background Context

## 1.1. Goals

*   **Unify Broker Access:** Provide a single, resilient API for trades, portfolios, and market data to save developers **over 80% of time** spent on building and maintaining individual broker integrations.
*   **Automate Session Management:** Handle complex broker login, OTP, and session refresh workflows automatically.
*   **Ensure Trading Resilience:** Guarantee safe and reliable execution with features like idempotency keys, automatic retries, and a global kill-switch, targeting a **≥99% order request success rate**.
*   **Enable Fast Integration:** Design the API and documentation to allow a developer to integrate and execute their first trade within **one day**.
*   **Promote Open Source:** Establish Ordo as the go-to open-source foundation for Indian market integrations, eliminating repetitive work for the community.
*   **Support Lightweight Deployment:** Optimize for minimal infrastructure (1 vCPU + 1 GB RAM) to ensure accessibility and low operational cost.

## 1.2. Background Context

Indian algo developers and small trading desks face a fragmented ecosystem where each broker exposes its own inconsistent API. Building integrations is repetitive, error-prone, and risky for live trading. Ordo addresses this by providing a self-hostable, open-source backend that unifies multiple brokers under a single, resilient API.

Unlike existing platforms like Streak, Tradetron, or OpenAlgo, Ordo focuses narrowly on being a lightweight infrastructure layer: fast, reliable, and secure, without lock-in. It prioritizes transparency (open source), safety (idempotency, kill-switch), and simplicity (Dockerized deployment). This foundation accelerates development, reduces operational risk, and creates space for future SaaS opportunities.

## 1.3. Change Log

| Date       | Version | Description                                  | Author     |
| :--------- | :------ | :------------------------------------------- | :--------- |
| 2025-09-20 | 1.1     | Refined goals and context based on feedback. | John (PM)  |
| 2025-09-20 | 1.0     | Initial draft                                | John (PM)  |

---
