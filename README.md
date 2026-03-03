# Airlock: Software Assurance Gateway
**Airlock** is a proactive "digital airlock" designed to vet third-party software before it enters a controlled environment. By generating a **Software Bill of Materials (SBOM)** and cross-referencing it with the **National Vulnerability Database (NVD)**, Airlock identifies supply chain risks before installation.

This project directly addresses **NIST SP 800-53** controls (CM-8, SI-2) and **Executive Order 14028** requirements for federal executive agencies.

---

# Project Flow & Architecture
Airlock operates as a distributed suite of applications coordinated via Docker Compose:

1. **Frontend (Vue 3):** A modern dashboard for uploading software artifacts and visualizing risk scores.
2. **API Gateway (FastAPI):** A high-performance Python backend that orchestrates the scanning and vetting logic.
3. **Analysis Engine (Syft):** An internal CLI worker that deconstructs software to generate a CycloneDX SBOM.
4. **Enrichment Layer (NVD API 2.0):** An automated service that queries NIST for real-time CVE data and CVSS severity scores.

---

# Git & Contribution Rules
To maintain code integrity and meet federal audit standards, all contributors must follow these rules:

### 1. Branching Strategy 
   - `master`: Protected. Only contains production-ready, audited code.
   - `staging`: Used for Final Integration Testing (UAT) before a release. 
   - `develop`: The main integration branch. All features must merge here first. 
   - `feature/[name]`: Create short-lived branches from `develop` for specific tasks (e.g., `feature/nvd-api-logic`).

### 2. Development Standards
   - **No Secrets in Git:** Never commit `.env` files or API keys. Use the provided `.gitignore`.
   - **Type Safety:** Use Pydantic models for all data structures to ensure "Clean OOP" and auto-generated documentation.
   - **Async First:** All external network calls (NVD API) must be handled asynchronously using `HTTPX` to prevent blocking the scanner.

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
2. **Setup Environment:** Create a `.env file` in the root with your `NVD_KEY`.
3. **Install Dependencies:** `pip install -r requirements.txt` (_ensure your `.venv` is active_).
4. **Launch:** `docker-compose up --build`