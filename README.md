# SME Financial & Supply-Chain Intelligence Platform

Monorepo scaffold. See `PROJECT_PLAN.md` for the canonical architecture and roadmap.

## Services
- frontend  → React + Vite + TS + MUI   (http://localhost:5173)
- backend   → FastAPI                   (http://localhost:8000)
- postgres  → PostgreSQL 16             (localhost:5432)

## Boot
```bash
cp .env.example .env
docker compose up --build