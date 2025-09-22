# Project Brief — Core Unified Backend API

## Executive Summary
- **Product Concept:** A lightweight, open-source backend that unifies broker integrations for Indian markets, providing a standardized API for order execution, portfolio tracking, and market data across brokers like HDFC Securities, Mirae’s m.Stock, and Fyers.  
- **Primary Problem Being Solved:** Developers and businesses waste time writing and maintaining duplicate integrations for each broker’s unique API, while traders suffer from inconsistent workflows and reliability issues.  
- **Target Market:** Initially built for internal use, later targeting independent algo developers, small proprietary desks, and fintech startups seeking a reliable broker-agnostic API.  
- **Key Value Proposition:** Instead of reinventing integrations repeatedly, the Core API offers a single, consistent, resilient orchestration layer — handling logins, retries, margin checks, and unified responses, while keeping credentials secure.  

---

## Problem Statement
Developers and traders in India face significant friction when working with multiple broker APIs:  
- Each broker uses different endpoints, auth flows, and quirks.  
- Building stable integrations requires **20–40 hours per broker**, plus ongoing maintenance.  
- Rate limits, session expirations, and retries must be handled manually.  
- Errors in execution (missed orders, duplicate placements) can cause **real financial losses**.  
- Small desks lack a consolidated execution API and must manage multiple trading terminals simultaneously.  

Existing solutions don’t fully solve this:  
- **Broker APIs** are fragmented and force repeated work.  
- **Streak/Tradetron** focus on strategy layers but don’t expose a reusable, transparent backend.  
- **OpenAlgo** provides multi-broker support but is heavier, more UI-oriented, and less optimized as a lightweight, embeddable API service.  

This leaves a clear gap: a **lean, reliable, and extensible backend orchestration layer** that developers and desks can trust to unify broker interactions.  

---

## Proposed Solution
The **Core Unified Backend API** is a standalone, self-hostable service providing:  

- **Unified REST API:** For placing orders, fetching portfolios, and managing broker sessions.  
- **Authentication Management:** Daily broker login flows, OTP relay endpoints/scripts, session persistence, and auto-refresh.  
- **Request Orchestration:**  
  - Async fan-out of requests across brokers.  
  - Automatic retries with exponential backoff before returning results.  
  - Unified response structures that clearly annotate per-broker outcomes.  
  - Graceful degradation via partial success reporting if some brokers remain unreachable.  
- **Pre-Trade Validations:** Best-effort checks for margin/fund availability and instrument validity before sending orders.  
- **Resilience & Safety:**  
  - Idempotency keys to prevent duplicate submissions.  
  - Circuit breakers for failing brokers.  
  - Global kill-switch for instant halt.  
  - Audit logging for all requests.  
- **Security-First Design:** Encrypted credential storage, TLS transport, optional mTLS.  
- **Lightweight Deployment:** Optimized for 1 vCPU + 1 GB RAM instances using FastAPI async and HTTP/2.  
- **Extensibility:** Modular broker adapters with a standard interface for new brokers.  

Positioned as **infrastructure, not a dashboard**, the Core API is designed to power dashboards, algos, or fintech products while staying transparent, reliable, and trust-focused.  

---

## Target Users
- **Primary:**  
  1. **Independent Algo Developers** — seeking a unified API to avoid duplicating broker logic.  
  2. **Small Proprietary Trading Desks** — needing a reliable execution backend to build their own dashboards or tools.  

- **Secondary:**  
  1. **Fintech Startups** — early-stage teams needing faster time-to-market with a stable execution layer.  
  2. **Retail Multi-Broker Traders (technical users)** — advanced individuals willing to self-host and connect trading scripts.  

---

## MVP Features
1. **Broker Adapters:** HDFC, Mirae m.Stock, Fyers.  
2. **Authentication & Session Lifecycle:**  
   - Daily login flow.  
   - OTP relay endpoint/helper script.  
   - Session persistence + refresh.  
3. **Unified API Models:** Orders, portfolios, quotes.  
4. **Request Orchestration Layer:**  
   - Async fan-out across selected brokers.  
   - Automatic retries with exponential backoff before responding.  
   - Unified collated response with per-broker results.  
   - Partial success handling (with clear annotations).  
5. **Pre-Trade Validation:**  
   - Margin/fund availability checks.  
   - Instrument validation before sending.  
6. **Resilience & Safety:**  
   - Idempotency keys.  
   - Kill-switch.  
   - Audit logging.  
   - Circuit breakers for failing brokers.  
7. **Security:** Encrypted secrets storage, TLS transport.  
8. **Deployment:** Dockerized, config-driven, minimal footprint.  

**Stretch Goals (post-MVP):**  
- Adapter health monitoring endpoints.  
- Broker adapter SDK for community contributions.  
- Historical data caching.  

---

## Goals & Success Metrics

### Business Objectives
1. Eliminate duplicated work by building a reusable broker integration layer within 3 months.  
2. Establish trust and credibility via open-source release, attracting early adopters.  
3. Lay the foundation for monetization (e.g., Dashboard project) by enabling reliable multi-broker execution.  
4. Prove resilience and reliability on constrained infra (1 vCPU + 1 GB RAM).  

### User Success Metrics
1. Developers integrate Core API into scripts within **1 day**.  
2. Saves **80%+ development time** compared to direct broker APIs.  
3. Achieves **≥99% order request success rate** after retries.  
4. Provides confidence via kill-switch, retries, and idempotency (no duplicate orders).  

### KPIs
- **Latency Overhead (Bridge):** ≤50ms target, ≤100ms acceptable, ≤250ms upper limit.  
- **Adapter Uptime:** ≥99.5% (excluding broker outages).  
- **Retry Success Rate:** ≥90% of failed requests succeed on retry.  
- **Memory Footprint:** <300 MB baseline usage.  
- **Adoption Proxies:** GitHub stars/forks, Docker pulls, PyPI downloads, community discussions.  
- **Reliability Metrics:** Kill-switch activations, duplicate order prevention rate, adapter health checks.  

---

## Dependencies

### Broker APIs
- HDFC Securities, Mirae m.Stock, Fyers.  
- Extensible for future brokers.  

### Frameworks & Libraries
- FastAPI, Pydantic, httpx/aiohttp, cryptography, uvicorn.  

### Persistence
- SQLite (default), Postgres optional.  
- Optional Redis for caching/distributed rate-limiting.  

### Deployment
- Docker container, config-driven (ENV/.yaml).  
- Poetry/pip for dependency management.  

### Optional Integrations (Post-MVP)
- Prometheus/Grafana for monitoring.  
- Vault/SOPS for enterprise-grade secret management.  

---

## Risks & Mitigations
1. **Python Performance Limits:** Mitigate with async I/O, caching, and potential Rust rewrites for hot paths.  
2. **Broker API Quirks/Downtime:** Mitigate with retries, circuit breakers, modular adapters.  
3. **Security Concerns:** Encrypt credentials, TLS transport, open-source transparency.  
4. **Community Adoption Uncertainty:** Mitigate with open-source release, documentation, examples.  
5. **Solo Developer Maintenance Load:** Mitigate with modular adapters + SDK for community contributions.  
6. **Regulatory Ambiguity:** Position as a **self-hosted developer tool**, not a third-party trading service.  

---

## Roadmap

### Phase 1 — MVP (0–3 months)
- Adapters for HDFC, Mirae, Fyers.  
- Auth/OTP relay + session persistence.  
- Fan-out orchestration + retries.  
- Margin/instrument pre-trade checks.  
- Kill-switch, audit logs, Docker deployment.  

### Phase 2 — Hardening & Community Release (3–6 months)
- Adapter health monitoring.  
- More order types (SL, BO where supported).  
- Stress/performance testing.  
- Open-source release (GitHub, Docker Hub, PyPI SDK).  

### Phase 3 — Business-Grade Features (6–12 months)
- Adapter SDK for new brokers.  
- Optional Postgres/Redis integrations.  
- Alert hooks (webhooks/email).  
- Multi-account routing.  

### Phase 4 — Expansion (12+ months)
- More brokers (Zerodha, AngelOne, ICICI Direct).  
- Advanced order types (GTT, OCO).  
- Enterprise-grade security (mTLS, Vault).  
- Community-driven adapter maintenance.  
