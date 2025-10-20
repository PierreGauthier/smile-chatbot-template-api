# SMILE Chatbot Template API

FastAPI service that exposes a Bot Framework-compatible chat endpoint backed by a Retrieval-Augmented Generation (RAG) pipeline for the SMILE virtual assistant. It orchestrates Azure OpenAI, Azure Cosmos DB, Azure AI Search, and LangChain components to deliver grounded responses while emitting telemetry through Azure Monitor.

## Features
- `/api/messages` endpoint ready for Azure Bot Emulator or Bot Service channels.
- RAG pipeline combining Azure Search vector retrieval, Cosmos DB history persistence, and Azure/OpenAI language models.
- Application-level telemetry via Azure Monitor OpenTelemetry exporter.
- Health probes at `/` and `/health` plus production-ready Docker and Compose definitions.

## Project Structure
- `src/app.py` – FastAPI entry point, lifespan hooks, CORS, and global exception handling.
- `src/routers/` – Bot Framework routing and conversation logic wiring.
- `src/domain/` & `src/application/` – Domain models and RAG orchestration services.
- `src/infrastructure/` – Azure integrations (Cosmos, Search, configuration, telemetry).
- `docs/` – Supplementary guides for local setup, configuration, and deployment.
- `data/` – Example seed data and embeddings utilities.

## Prerequisites
- Python 3.10+ (3.11 used in the Docker image) with `pip` and `python3-venv`.
- Azure resources (OpenAI, AI Search, Cosmos DB, App Configuration, Key Vault) with credentials exposed through environment variables.
- Optional: Docker 24+ and Docker Compose v2 for containerised runs.

## Quick Start
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
2. Provide configuration secrets in a `.env` file (see below) or export them as environment variables.
3. Launch the API locally:
   ```bash
   uvicorn src.app:app --host 0.0.0.0 --port 3978 --reload
   ```
4. Connect the Azure Bot Emulator to `http://localhost:3978/api/messages` to exchange messages.

## Configuration
The service resolves settings from `.env`, process environment variables, Azure App Configuration, and Key Vault (in that order). Core values include:
- `AZURE_OPENAI_*` and `OPENAI_*` – model deployments and API keys.
- `AZURE_SEARCH_*` – Azure AI Search endpoint, key, and index metadata.
- `AZURE_COSMOS_*` – Cosmos DB account, database, and container names.
- `LANGCHAIN_*` / `LANGSMITH_*` – LangChain tracing and hosted prompt references.
- `CORS_ALLOWED_ORIGINS` – Optional comma-separated list for browser clients.

Refer to `docs/setup.md` for the detailed configuration matrix and `docs/deployment.md` for production guidance.

## Docker
Run the service in a container with the provided assets:
```bash
docker compose up --build
```
Ensure a `.env` file sits beside `docker-compose.yml`; the API exposes port `3978` and includes an HTTP health check.

## Useful Commands
- `pytest` – Add and run tests as you extend the service.
- `uvicorn src.app:app --reload` – Fast reload loop for local development.
- `python -m pip install -r requirements.txt` – Re-install dependencies after updates.

## Additional Resources
- `docs/setup.md` – Environment provisioning, configuration flow, and secrets management.
- `docs/deployment.md` – Azure deployment checklist and operational tips.
