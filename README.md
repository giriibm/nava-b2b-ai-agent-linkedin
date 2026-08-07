# Nava AI Outbound Intelligence Platform

Working implementation of the Phase 1 MVP architecture described in the Master
Product & Development Prompt: an AI-assisted B2B prospect intelligence
platform with a mandatory human-approval gate before anything is sent.

```
nava-ai-platform/
├── backend/     FastAPI — LLM Gateway, AI agents, ICP/Prospect/Approval APIs
├── frontend/    Next.js — Dashboard, ICP Builder, Prospect Workspace, Approval Queue, Settings
└── docker-compose.yml
```

## Quickest path to running it (no Docker)

**Backend**
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
Runs on http://localhost:8000 against a local SQLite file — zero external
services required to explore the API (http://localhost:8000/docs).

**Frontend** (separate terminal)
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```
Runs on http://localhost:3000.

**Optional — real AI output**
The Research/Scoring/Personalization agents call whatever `LLM_PROVIDER` is
set in `backend/.env` (default `ollama`). Install [Ollama](https://ollama.com),
run `ollama pull llama3.1`, and agent runs will produce real output instead of
failing with a "provider unreachable" job error. Switching to OpenAI/Anthropic/
Gemini is a one-line env change — see `backend/app/services/llm_gateway.py`.

## Docker Compose (adds Postgres)

```bash
docker compose up --build
```

## What's real vs. stubbed

| Component | Status |
|---|---|
| ICP Builder, Prospect import, Prospect Workspace, Approval Queue, Dashboard | Fully working, end-to-end |
| Research / Scoring / Personalization AI agents | Fully working against any configured LLM provider |
| Async job queue (`jobs` table + polling) | Fully working |
| Human approval gate before any outreach | Fully enforced — only the Approval router can trigger send |
| Salesforce sync | Interface defined, REST calls are `TODO` — needs a Connected App |
| HeyReach send | Implemented against HeyReach's public API shape — needs `HEYREACH_API_KEY` |

## Why these tools

Matches the stack specified in the Master Spec §8 exactly: Next.js/React/
TypeScript/Tailwind/shadcn-style components on the frontend, Python/FastAPI on
the backend, Postgres in Docker Compose (SQLite locally for zero-friction
dev). The LLM Gateway and Integration Service are built as swappable
interfaces per §7/§11 — no agent or router imports a vendor SDK directly.

## Verified

- Backend: installs clean, boots, and a full ICP → import → trigger-agent →
  job-status flow was exercised against a live server (see commit history /
  test transcript). Agent failures (e.g. LLM unreachable) are caught and
  surface as a `failed` job with an error message, never a crash.
- Frontend: `npm run build` compiles all 6 routes with zero TypeScript errors.
