# TechShop — AI Shopping Assistant

TechShop is a **reference implementation** demonstrating how to design and ship **AI-powered systems** with streaming responses, tool calling, deterministic side effects, and evaluation loops.

The focus is not just on prompting, but on **agent reliability, UI state synchronization, and production-style guardrails** that are required in real-world AI/ML applications.

- The **frontend** (Next.js) provides a modern chat widget and a cart experience.
- The **backend** (FastAPI + Postgres) runs a **LangGraph agent** with tool-calling for product search and cart actions.
- The agent streams responses to the UI and emits **structured “actions”** (as JSON blocks) so the frontend can reliably update cart state and navigate.

## Features

- **Streaming chat UI** (token-by-token response streaming)
- **Tool calling / agentic workflow** (LangGraph)
- **Cart actions backed by Postgres** (`add_to_cart`, `remove_from_cart`, `update_cart_quantity`, `get_cart`)
- **Product search** with fuzzy matching
- **UI state sync**: backend tool outputs are injected into the stream as ` ```json ... ``` ` blocks, and the frontend parses them to:
  - navigate (e.g. `"/cart"`)
  - update cart (add/remove/update quantity)
- **Guardrails**: step limit, tool timeouts, basic sanitization
- **API protections**: rate limiting + concurrency limits
- **CI**: frontend lint/build + backend lint/tests

## Architecture (high level)

```
Next.js (UI)  --->  Next.js /api/chat (proxy, streaming)  --->  FastAPI /api/chat (StreamingResponse)
   |                                                                      |
   |<--- streamed tokens + ```json action blocks``` ----------------------|
   |
CartProvider (local state)  <--- action blocks --->  Postgres (cart/products)
```

## Key design decisions

- **Streaming + structured actions**  
  The agent streams natural language tokens while emitting explicit JSON action
  blocks for side effects (e.g. cart updates, navigation).  
  This avoids brittle text parsing and keeps frontend state updates deterministic.

- **LangGraph over ad-hoc agent loops**  
  LangGraph provides explicit control flow, step limits, and better debuggability
  compared to custom while-loop agents.

- **Postgres-backed cart state**  
  Cart state is persisted in the database instead of relying on model memory,
  preventing hallucinated state and enabling idempotent operations.

- **Opt-in real-LLM evals**  
  Tool-calling accuracy is validated against a real model to catch regressions,
  while remaining skipped by default to avoid unnecessary API cost.

## Tech stack

- **Frontend**: Next.js (App Router), TypeScript, Tailwind, shadcn/ui
- **Backend**: FastAPI, SQLAlchemy, Postgres, LangChain + LangGraph
- **Infra**: Docker Compose (Postgres)

## Prerequisites

- Node.js 20+
- Python 3.11+
- Docker (for Postgres)
- An OpenAI API key (for the agent)

## Quickstart (local)

### 1) Start Postgres

```bash
make db-up
```

Postgres will be available on `localhost:5433` (mapped to container `5432`).

### 2) Install dependencies

```bash
make install
```

### 3) Set environment variables

Copy the example environment file:

```bash
cp backend/template.env .env
```

Edit `.env` to set your keys.

Required:

```bash
export OPENAI_API_KEY="YOUR_KEY_HERE"
```

Optional (LangSmith Tracing):

```bash
# Enable LangSmith tracing (highly recommended for debugging agents)
export LANGSMITH_TRACING=true
export LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
export LANGSMITH_API_KEY="YOUR_LANGSMITH_KEY"
export LANGSMITH_PROJECT="techshop_agent"
```

Optional (defaults shown):

```bash
export DATABASE_URL="postgresql://user:password@localhost:5433/techshop"
```

### 4) Seed the database

Use the provided SQL file to insert products:

```bash
# If you have psql installed:
psql "postgresql://user:password@localhost:5433/techshop" -f data/products.sql

# OR using Docker:
docker compose exec -T db psql -U user -d techshop < data/products.sql
```

### 5) Run backend + frontend (two terminals)

Backend:

```bash
make dev-backend
```

Frontend:

```bash
make dev-frontend
```

Open:

- Frontend: `http://localhost:3000`
- Backend health: `http://localhost:8000/api/health`

## Run with Docker Compose (recommended for demo/deployment)

This repo includes a full-stack `docker-compose.yml` (Postgres + backend + frontend).

Required environment variables:

```bash
export OPENAI_API_KEY="YOUR_KEY_HERE"
```

Optional environment variables:

```bash
export OPENAI_MODEL="gpt-5-mini"
export CORS_ALLOW_ORIGINS="http://localhost:3000"
export BACKEND_URL="http://127.0.0.1:8000"
```

Start the stack:

```bash
docker compose up --build
```

Then open:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`

Notes:

- The frontend calls `POST /api/chat` which proxies to the backend using `BACKEND_URL`.
- In Docker Compose, the frontend container is configured with `BACKEND_URL=http://backend:8000`.

## Demo prompts

Try these in the chat widget:

- “Suggest me a phone.”
- “Show me some laptops.”
- “Increase the quantity to 2.”
- “Show my cart.”

## Repo layout
```
frontend/   # Next.js app, streaming chat UI, cart state handling  
backend/    # FastAPI app, LangGraph agent, tools, database logic  
data/       # SQL seed data for products
```
## Configuration

- **System prompt**: `backend/app/config/prompts.yaml`
- **Backend CORS**: `backend/app/main.py` reads `CORS_ALLOW_ORIGINS` (defaults to `http://localhost:3000`)
- **Frontend -> backend URL**: Next.js proxy (`src/app/api/chat/route.ts`) reads `BACKEND_URL` (defaults to `http://127.0.0.1:8000`)
- **Database URL**: `backend/app/database.py` reads `DATABASE_URL` and defaults to:
  - `postgresql://user:password@localhost:5433/techshop`

## Testing

Backend tests:

```bash
make test-backend
```

### Real-LLM tool-accuracy evals

These evals run against a real OpenAI model and validate **tool calling accuracy** (e.g., that the model actually calls `search_products`, `add_to_cart`, etc., with correct arguments).

They are **skipped by default** unless you explicitly enable them.

Required environment variables:

```bash
export RUN_REAL_LLM_EVAL=1
export OPENAI_API_KEY="YOUR_KEY_HERE"
export DATABASE_URL="postgresql://user:password@localhost:5433/techshop"
```

Optional:

```bash
export OPENAI_MODEL="gpt-5-mini"
```

Run:

```bash
PYTHONPATH=. pytest backend/tests/test_real_llm_tool_accuracy.py -q
```

Frontend lint:

```bash
make lint-frontend
```

Backend lint (requires dev deps):

```bash
make install-backend-dev
make lint-backend
```

## Troubleshooting

- **Database connection errors**
  - Ensure Postgres is running: `make db-up`
  - Confirm the port mapping is `5433:5432` in `docker-compose.yml`
  - The default local DSN is `postgresql://user:password@localhost:5433/techshop`

- **Chat can’t reach backend**
  - Ensure backend is running on `http://localhost:8000`
  - The chat widget calls `POST /api/chat` (Next.js), which proxies to the backend using `BACKEND_URL`
  - In Docker Compose, `BACKEND_URL` is set to `http://backend:8000` for the frontend container

- **Rate limiting**
  - The chat endpoint is rate limited (`10/minute`). If you hit limits, wait a bit and retry.

## Known limitations & future improvements

- Single-user cart model (no authentication)
- Demo-scale product catalog and search
- No embedding-based semantic retrieval yet
- Limited observability beyond logging and LangSmith tracing

Future improvements could include per-user carts, semantic search with embeddings,
retry/reconciliation logic for failed tool calls, and richer agent metrics for
tuning and evaluation.

## License

MIT (or replace with your preferred license)
