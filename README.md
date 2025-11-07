# event-booking

Microservice-style Event Booking using Next.js (frontend) and FastAPI + PostgreSQL (backend).

This repo contains a FastAPI backend (in `backend/`) and a planned Next.js frontend (in `frontend/`). The backend currently implements Events CRUD, a Docker Compose setup for local PostgreSQL, OpenAPI spec, and smoke-test scripts.

## Quick start (Windows PowerShell)

Prerequisites:
- Docker & Docker Compose
- Python 3.11+
- git

1) Start the database (from repo root):

```powershell
# run Postgres in docker
docker-compose up -d
```

2) Backend: create & activate a venv, install dependencies, and run the app

```powershell
cd backend
python -m venv .venv
# PowerShell activation
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# run the FastAPI app
uvicorn app.main:app --reload --port 8000
```

Open the interactive API docs: http://localhost:8000/docs (Swagger) or http://localhost:8000/redoc

3) Run the included smoke tests (from `backend/`):

```powershell
# while server is running
.\.venv\Scripts\Activate.ps1
.\scripts\test_api.ps1
```