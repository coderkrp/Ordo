# Quickstart Guide

This guide provides step-by-step instructions to get the Ordo application up and running quickly.

## 1. Development Setup

This project requires **Python 3.12+** and uses [Poetry](https://python-poetry.org/) for dependency management.

### 1.1. Install Dependencies
```bash
# Ensure you are using Python 3.12
python --version

# Install Poetry if not already installed
pip install poetry

# Install dependencies
poetry install
```

### 1.2. Run the Application
```bash
# Start the FastAPI app with Uvicorn (hot reload enabled)
poetry run uvicorn ordo.main:app --reload --port 8000
```
The API will be available at: http://localhost:8000

Interactive API docs:

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

### 1.3. Run Tests
```bash
# Run all tests with pytest
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/ordo --cov-report=term-missing
```

### 1.4. Linting & Formatting
```bash
# Check linting
poetry run ruff check src tests

# Auto-fix linting issues
poetry run ruff check src tests --fix

# Format code
poetry run black src tests
```

## 2. Configuration with .env

Ordo uses environment variables for configuration. A `.env.example` file is provided in the project root.

1.  **Create your `.env` file:**
    ```bash
    cp .env.example .env
    ```
2.  **Edit `.env`:** Open the newly created `.env` file and update the values as needed. For local development, you might only need to set `DATABASE_URL` or other specific settings.

## 3. Using Docker

For a more isolated and production-like environment, you can run Ordo using Docker.

### 3.1. Build the Docker Image
```bash
# Build the image
docker build -t ordo:dev .
```

### 3.2. Run with Docker
```bash
# Run with Docker, mounting your .env file for configuration
docker run -p 8000:8000 --env-file .env ordo:dev
```

### 3.3. Verification
After running the Docker container, you can verify the application is running by accessing the health endpoint:
```bash
curl http://localhost:8000/health
```
You should receive a JSON response: `{"status": "ok"}`.

---

✅ Note:

Uvicorn runs with HTTP/1.1 by default. For production, Ordo should be deployed behind a reverse proxy (e.g., Nginx, Traefik, or Caddy) which will handle TLS termination and enable HTTP/2/3 for clients.

All configuration is managed via environment variables (see .env.example).
