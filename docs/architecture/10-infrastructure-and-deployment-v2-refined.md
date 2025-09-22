# 10. Infrastructure and Deployment (v2 Refined)

This section defines the infrastructure, containerization, CI/CD pipeline, and operational strategy for Ordo.

## 10.1. Infrastructure as Code (IaC)

*   **Tooling:**
    *   **Local Environment:** Docker & Docker Compose are the required tools for local development.
    *   **Production:** The core application is delivered as a Docker image. Users are responsible for providing a Docker host.
*   **Location:** A `Dockerfile`, `docker-compose.yml`, and `.env.example` file will be located at the project root.
*   **Future-Proofing:** While out of scope for MVP, a natural evolution for scaled deployments would be to provide Kubernetes manifests or a Helm chart.

## 10.2. Configuration Management

*   **Method:** For MVP, configuration is managed exclusively via environment variables, loaded by Pydantic's settings management.
*   **Developer Experience:** An `.env.example` file will be provided to list all available environment variables.
*   **Local Secrets:** For local development, it is recommended that developers use a `docker-compose.override.yml` file (which is git-ignored) to inject sensitive secrets (broker credentials, API tokens), preventing them from being checked into source control.
*   **Production Secrets:** In a production environment, secrets should be injected into the container using the host system's capabilities (e.g., Docker secrets, systemd environment files, or cloud provider services). Advanced tools like Vault are explicitly out of scope for the MVP specification.

## 10.3. CI/CD Pipeline (GitHub Actions)

The pipeline, defined in `.github/workflows/main.yml`, will execute on pushes to the `main` branch and perform the following steps:
1.  **Lint & Format Check:** Ensure code quality with `ruff` and `black`.
2.  **Security Scanning:**
    *   Scan dependencies for known vulnerabilities using `pip-audit`.
    *   Scan the final Docker image for OS-level vulnerabilities using a tool like `Trivy`.
3.  **Run Automated Tests:** Execute the full `pytest` suite.
4.  **Build & Push Docker Image:**
    *   Build the production Docker image using multi-stage builds and layer caching for efficiency.
    *   Tag the image with the Git SHA and `latest`.
    *   Push the image to a container registry (e.g., Docker Hub, GitHub Container Registry).

## 10.4. Running in Production

*   **Process Management:** To handle concurrent requests effectively, the application should be run with a process manager like **Gunicorn**, using Uvicorn-compatible workers.
    *   *Example Command:* `gunicorn "ordo.main:app" -w 4 -k uvicorn.workers.UvicornWorker`
*   **Supervision & Resilience:** The Docker container should be run under a supervisor to ensure it restarts automatically on failure.
    *   *Recommended Method:* Use Docker's built-in restart policies (e.g., `restart: always`) in a `docker-compose` file or a systemd service unit on the host.

## 10.5. Observability

*   **Logging:** The application will log structured JSON to `stdout`. This allows a container log aggregator (like Fluentd, Logstash, or Promtail) to collect, parse, and forward logs to a centralized system (e.g., Loki, Elasticsearch).
*   **Metrics:** The application will expose a `/metrics` endpoint (via an optional dependency) for a Prometheus server to scrape.

## 10.6. Database Lifecycle

*   **SQLite (Default):** The schema is managed directly by the application. For MVP, schema changes are destructive (requiring a database file reset).
*   **PostgreSQL (Optional):** For users deploying with PostgreSQL, database migrations will be managed by **Alembic**. The configuration and migration scripts will reside in the root `migrations/` directory.

## 10.7. Rollback Strategy

*   **Method:** The recommended manual rollback strategy is to re-deploy the previously known stable Docker image tag.
*   **Best Practice:** Production hosts should be encouraged to keep at least one previous stable image tag pulled locally. This ensures that a rollback can be performed immediately without depending on the availability of the external container registry.

---
