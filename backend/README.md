# TechShop Backend

The backend service for TechShop, built with **FastAPI**, **LangGraph**, and **PostgreSQL**.

It provides the AI agent runtime, product catalog management, and shopping cart persistence.

## Features

- **LangGraph Agent**: A stateful agent that manages conversation history and tool execution.
- **Streaming Response**: Tokens and structured action blocks are streamed to the frontend.
- **Tool Calling**:
  - `search_products`: Fuzzy search over the product catalog.
  - `add_to_cart`, `remove_from_cart`, `update_cart_quantity`: Persistent cart management.
  - `get_cart`: Retrieval of current cart state.
- **Postgres Persistence**: All cart operations and product data are stored in a relational database.
- **Guardrails**: Input sanitization (PII redaction), step limits, and tool timeouts.

## Setup & Installation

### 1. Requirements

- Python 3.11+
- PostgreSQL (or Docker)

### 2. Environment Variables

Copy the template:

```bash
cp template.env .env
```

Configure the following in `.env`:

```bash
# Database Connection
DATABASE_URL="postgresql://user:password@localhost:5433/techshop"

# OpenAI
OPENAI_API_KEY="sk-..."
OPENAI_MODEL="gpt-4-turbo-preview"  # Optional

# LangSmith (Optional - for tracing)
LANGSMITH_TRACING=true
LANGSMITH_API_KEY="..."
LANGSMITH_PROJECT="techshop_agent"
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

For development (includes linting/testing tools):

```bash
pip install -r requirements.txt && pip install ruff pytest
```

### 4. Database Setup

Ensure your Postgres instance is running. Then seed the data:

```bash
# Using psql
psql "postgresql://user:password@localhost:5433/techshop" -f ../data/products.sql
```

## Running the Server

Start the development server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.
Docs: `http://localhost:8000/docs`

## API Endpoints

### Chat

- `POST /api/chat/stream`: The main entry point for the AI agent. Accepts messages and returns a streaming response containing text tokens and JSON action blocks.

### Products

- `GET /api/products`: List products (with pagination).
- `GET /api/products/{product_id}`: Get details for a specific product.
- `GET /api/products/search`: Search products by name/description.

## Architecture

### Agent (`app/agent.py`)
The `TechShopAgent` uses **LangGraph** to define a graph where:
1.  **Agent Node**: Calls the LLM to decide the next step.
2.  **Tools Node**: Executes requested tools (search, cart operations).
3.  **Cycle**: The graph cycles until the LLM produces a final answer or hits the `MAX_TOOL_STEPS` limit.

### Tools (`app/tools.py`)
Encapsulate business logic and database interactions. They are exposed to the LLM as function schemas.

### Database (`app/models.py`)
SQLAlchemy models for:
- `Product`: Catalog items (JSONB specs, embeddings support prepared).
- `Cart` / `CartItem`: User shopping sessions.

## Testing

Run unit and integration tests:

```bash
PYTHONPATH=. pytest tests/
```

### Real-LLM Evaluation
To run accuracy tests against the real OpenAI API (costs money):

```bash
export RUN_REAL_LLM_EVAL=1
PYTHONPATH=. pytest tests/test_real_llm_tool_accuracy.py
```
