# Nava AI Outbound Intelligence Platform — Backend

FastAPI implementation of the architecture in the Master Spec (§8-§12): ICP/Prospect
Service, AI Agent Orchestrator (Research/Scoring/Personalization), LLM Gateway
(Ollama by default, OpenAI/Anthropic/Gemini pluggable), Approval & Workflow
Service, and Salesforce/HeyReach integration stubs.

## Run locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # defaults to local SQLite, no external services required
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

## Using a real LLM

By default `LLM_PROVIDER=ollama` and the gateway calls `http://localhost:11434`.
Install [Ollama](https://ollama.com), `ollama pull llama3.1`, and it'll work with
zero other config. To use OpenAI/Anthropic/Gemini instead, set `LLM_PROVIDER` and
the matching `*_API_KEY` in `.env` — no code changes needed anywhere else.

## What's stubbed vs. real

- **Research / Scoring / Personalization agents** — fully implemented, call the
  LLM Gateway, and write real rows to the database.
- **Job queue** — real (FastAPI BackgroundTasks + a `jobs` table), swap for
  Celery/Redis when volume requires it (see `app/services/job_queue.py`).
- **Salesforce sync** — interface only (`app/services/integrations/salesforce_service.py`).
  Needs a Connected App + credentials before the `TODO` REST calls can be filled in.
- **HeyReach send** — implemented against HeyReach's public API shape; needs a
  real `HEYREACH_API_KEY` to actually send. Only the Approval router is allowed
  to call it — no agent has access to this service.

## Production notes

- Point `DATABASE_URL` at Postgres and add Alembic migrations before `Base.metadata.create_all`
  is dropped from `main.py` (currently fine for MVP/dev).
- Put real secrets in a secrets manager, not `.env`, per Master Spec §11.
