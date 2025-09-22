# 1. Introduction

This document outlines the backend architecture for **Ordo**, an open-source, self-hostable backend designed for **algo developers and small trading desks**. It unifies broker integrations for the Indian market (MVP: Fyers, HDFC Securities, Mirae m.Stock) into a single, resilient API.

The primary architectural goal is to handle complex workflows—authentication, request orchestration, retries, and safe order placement—while remaining lightweight enough to run on a modest 1 vCPU + 1 GB RAM instance. This architecture prioritizes **developer ergonomics**, **operational readiness**, and **extensibility**.

**Architectural Boundary:** Ordo is intentionally a backend-first infrastructure layer. Any dashboard or UX built on top is a separate concern and **requires** its own Frontend Architecture document. This document focuses exclusively on backend services, persistence, security, and observability.

**Starter Template:** N/A — this is a greenfield backend service using Python, FastAPI, and Poetry.

---
