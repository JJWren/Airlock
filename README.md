# Airlock: Software Assurance Gateway

**Airlock** is a proactive "digital airlock" designed to vet third-party software before it enters a controlled environment. Users can **upload software artifacts** or point to a local directory, and Airlock will generate a **Software Bill of Materials (SBOM)**, cross-reference it with the **National Vulnerability Database (NVD)**, and produce a detailed risk report — including downloadable **PDF summaries**.

This project directly addresses **NIST SP 800-53** controls (CM-8, SI-2) and **Executive Order 14028** requirements for federal executive agencies.

---

# Project Flow & Architecture

Airlock operates as a distributed suite of applications coordinated via Docker Compose. The backend is built on a modular "Service-Pattern" architecture:

1. **Frontend (React):** A modern dashboard served on port `3000` for uploading software artifacts and visualizing risk scores. Communicates with the API via a configurable `VITE_API_BASE_URL`.
2. **API Gateway (FastAPI):** A high-performance gateway on port `8000` using the Factory Pattern for clean initialization and middleware (CORS) management. Exposes interactive Swagger docs at `/docs`. Supports **file uploads** via `python-multipart` and **real-time scan progress** streamed to the frontend via **Server-Sent Events (SSE)**.
3. **Correlation Service (The Brain):** An orchestration layer that bridges the SBOM generator and the vulnerability intelligence database. It aggressively cross-references multiple CPE guesses to ensure maximum detection accuracy.
4. **Analysis Engine (Syft):** Interacts with the [Anchore Syft](https://github.com/anchore/syft) binary (v1.0.1) to deconstruct software and generate CycloneDX SBOMs.
5. **Enrichment Layer (NVD via `nvdlib`):** Queries NIST for real-time CVE data and CVSS severity scores using the [`nvdlib`](https://github.com/vehemont/nvdlib) library, with retry logic powered by `tenacity` and async networking via `httpx`.
6. **Report Generator (`fpdf2`):** Produces downloadable PDF vulnerability reports summarizing scan findings.

**Structured logging** is handled throughout by [`loguru`](https://github.com/Delgan/loguru).

---

# CI/CD

The project includes a **GitHub Actions** workflow (`.github/workflows/`) for automated testing and validation on push/PR events.

---

# Development & Testing

To ensure parity between Windows development and Linux deployment (the "Airlock"), we utilize a Dual-Loop testing strategy:

## The Inner Loop (Local Development)

Run tests natively in PyCharm for a fast feedback loop. Ensure your `.env` points to the local Syft binary:

* **Variable:** `SYFT_BINARY_PATH=bin/syft.exe`
* **Command:** Run via the PyCharm pytest runner.

## The Outer Loop (Docker Deployment)

Run tests inside the Linux container to verify production parity:

```
docker compose exec -T -e PYTHONPATH=/app api pytest tests/
```

---

# Usage

## Uploading Software Artifacts

The primary workflow is to **upload a file** through the React dashboard (port `3000`) or via the API directly:

* **Endpoint:** `POST /api/v1/scan`
* Files are received by FastAPI and stored in the `/uploads` volume inside the container.
* Scan progress is streamed back to the client in real time via SSE.

## Scanning a Directory Path

You can also scan a directory already present in the container:

* **Endpoint:** `POST /api/v1/scan`
* **Payload:** `{ "target_path": "/app" }` (scans the Airlock codebase itself as a smoke test)

## Scanning External Host Projects

To scan a project on your host machine, configure the `SCAN_UPLOAD_PATH` variable in your `.env` file to point at the directory you want to scan, then reference `/uploads` as the target path inside the container:

1. **Set the env var:** `SCAN_UPLOAD_PATH=C:/Users/YourUser/Source/Project` (or the equivalent path on your OS)
2. **Rebuild:** `docker-compose up --build -d`
3. **Trigger the scan:** `{ "target_path": "/uploads" }`

---

# Git & Contribution Rules

To maintain code integrity and meet federal audit standards, all contributors must follow these rules:

### 1. Branching Strategy

* `master`: Protected. Only contains production-ready, audited code.
* `staging`: User Acceptance Testing (UAT) branch. Final stop for testing changes before deploying to the production-ready branch.
* `develop`: The main integration branch. All features must merge here first.
* `feature/[name]`: Create short-lived branches from `develop` for specific tasks (e.g., `feature/nvd-api-logic`).

### 2. Development Standards

* **No Secrets in Git:** Never commit `.env` files or API keys. Use the provided `.env.example`. Include a `.gitignore` and `.dockerignore`.
* **Type Safety:** Use Pydantic models for all data structures to ensure "Clean OOP" and auto-generated documentation.
* **Async First:** All external network calls (NVD API) must be handled asynchronously.

### 3. Commit Messages

Use descriptive, imperative labels:

* **feat:** (new feature)
* **fix:** (bug fix)
* **docs:** (documentation changes)
* **refactor:** (code change that neither fixes a bug nor adds a feature)

*Example Commit Message:*

```
fix: Fixed issue causing failed requests/responses.

- Corrected json object typo
- Cleaned up documentation
```

---

# Quick Start

1. **Clone:** `git clone https://github.com/JJWren/Airlock.git`
2. **Setup Environment:** Copy `.env.example` to `.env` and provide your `NVD_API_KEY`. Set `SCAN_UPLOAD_PATH` to a valid directory on your host.
3. **Launch:** `docker-compose up --build -d`
4. **Install Dependencies (local dev):** `pip install -r requirements.txt` (*ensure your `.venv` is active*).
5. **Interact:**
   * **React Dashboard:** [http://localhost:3000](http://localhost:3000) — upload artifacts, view scan results, and download PDF reports.
   * **Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs) — explore and test API endpoints directly.

---

# Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React |
| API | FastAPI, Uvicorn, Pydantic |
| SBOM Generation | Anchore Syft (v1.0.1, CycloneDX) |
| Vulnerability Data | NVD via `nvdlib`, `httpx`, `tenacity` |
| Real-Time Updates | SSE via `sse-starlette` |
| PDF Reports | `fpdf2` |
| Logging | `loguru` |
| Testing | `pytest`, `pytest-asyncio`, `anyio` |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
