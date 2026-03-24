# Airlock: Software Assurance Gateway
**Airlock** is a proactive "digital airlock" designed to vet third-party software before it enters a controlled environment. By generating a **Software Bill of Materials (SBOM)** and cross-referencing it with the **National Vulnerability Database (NVD)**, Airlock identifies supply chain risks before installation.

This project directly addresses **NIST SP 800-53** controls (CM-8, SI-2) and **Executive Order 14028** requirements for federal executive agencies.

---

# Project Flow & Architecture
Airlock operates as a distributed suite of applications coordinated via Docker Compose. The backend is built on a modular "Service-Pattern" architecture:

1. **Frontend (Vue 3):** A modern dashboard for uploading software artifacts and visualizing risk scores.
2. **API Gateway (FastAPI):** A high-performance gateway using the Factory Pattern for clean initialization and middleware (CORS) management.
3. **Correlation Service (The Brain):** An orchestration layer that bridges the SBOM generator and the vulnerability intelligence database. It aggressively cross-references multiple CPE guesses to ensure maximum detection accuracy.
4. **Analysis Engine (Syft):** Interacts with the Syft binary to deconstruct software and generate CycloneDX SBOMs.
5  **Enrichment Layer (NVD API 2.0):** An asynchronous service that queries NIST for real-time CVE data and CVSS severity scores.

---

# Development & Testing

To ensure parity between Windows development and Linux deployment (the "Airlock"), we utilize a Dual-Loop testing strategy:

## The Inner Loop (Local Development)
Run tests natively in PyCharm for a fast feedback loop. Ensure your `.env` points to the local Syft binary:

- **Variable:** `SYFT_BINARY_PATH=bin/syft.exe`
- **Command:** Run via the PyCharm pytest runner.

## The Outer Loop (Docker Deployment)
Run tests inside the Linux container to verify production parity:
```bash
docker compose exec -T -e PYTHONPATH=/app api pytest tests/
```

---

# Usage: Scanning Projects

## Scanning the Airlock (Internal)
To verify the API and scanner are working, you can scan the code inside the container:

- **Endpoint:** `POST /api/v1/scan`
- **Payload:** `{ "target_path": "/app" }`

## Scanning External Host Projects
To scan a project on your Windows machine, map it as a Bind Mount in docker-compose.yml:

1. **Map the volume:** `- C:/Users/YourUser/Source/Project:/mnt/external_scan:ro`

2. **Trigger the scan:**
```json
{ "target_path": "/mnt/external_scan" }
```

---

# Git & Contribution Rules
To maintain code integrity and meet federal audit standards, all contributors must follow these rules:

### 1. Branching Strategy 
   - `master`: Protected. Only contains production-ready, audited code.
   - `develop`: The main integration branch. All features must merge here first. 
   - `feature/[name]`: Create short-lived branches from `develop` for specific tasks (e.g., `feature/nvd-api-logic`).

### 2. Development Standards
   - **No Secrets in Git:** Never commit `.env` files or API keys. Use the provided `.env.example`. Include a `.gitignore` and `.dockerignore`.
   - **Type Safety:** Use Pydantic models for all data structures to ensure "Clean OOP" and auto-generated documentation.
   - **Async First:** All external network calls (NVD API) must be handled asynchronously.

### 3. Commit Messages
Use descriptive, imperative labels:
   - **feat:** (new feature)
   - **fix:** (bug fix)
   - **docs:** (documentation changes)
   - **refactor:** (code change that neither fixes a bug nor adds a feature)

_Example Commit Message:_
```bash
fix: Fixed issue causing failed requests/responses.

- Corrected json object typo
- Cleaned up documentation
```

---

# Quick Start
1. **Clone:** `git clone [repo-url]`
2. **Setup Environment:** Copy `.env.example` to `.env` and provide your `NVD_API_KEY`.
3. **Launch:** `docker-compose up --build -d`
4. **Install Dependencies:** `pip install -r requirements.txt` (_ensure your `.venv` is active_).
5. **Interact:** Visit http://localhost:8000/docs for the interactive Swagger UI and Health Check.
