.PHONY: help install install-frontend install-backend install-backend-dev \
	dev-frontend dev-backend build-frontend start-frontend \
	lint-frontend lint-backend test-backend test \
	db-up db-down db-logs seed db-check

PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
NPM ?= npm

help:
	@printf "%s\n" \
	"Targets:" \
	"  install              Install frontend + backend deps" \
	"  install-frontend      npm install" \
	"  install-backend       pip install -r backend/requirements.txt" \
	"  install-backend-dev   install backend deps + ruff" \
	"  dev-frontend          Next.js dev server" \
	"  dev-backend           FastAPI dev server (uvicorn)" \
	"  build-frontend        Next.js build" \
	"  start-frontend        Next.js start" \
	"  lint-frontend         ESLint" \
	"  lint-backend          Ruff (requires: make install-backend-dev)" \
	"  test-backend          Pytest agent/unit tests" \
	"  test                 Run all tests" \
	"  db-up                 Start Postgres via docker compose" \
	"  db-down               Stop Postgres via docker compose" \
	"  db-logs               Tail Postgres logs" \
	"  seed                  Seed database (backend/seed_data.py)" \
	"  db-check              Simple DB connectivity check (backend/test_db.py)"

install: install-frontend install-backend

install-frontend:
	$(NPM) install

install-backend:
	$(PIP) install -r backend/requirements.txt

install-backend-dev: install-backend
	$(PIP) install ruff

dev-frontend:
	$(NPM) run dev

dev-backend:
	$(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend

build-frontend:
	$(NPM) run build

start-frontend:
	$(NPM) run start

lint-frontend:
	$(NPM) run lint

lint-backend:
	ruff check backend

test-backend:
	PYTHONPATH=backend $(PYTHON) -m pytest backend/tests

test: test-backend

db-up:
	docker compose up -d db

db-down:
	docker compose down

db-logs:
	docker compose logs -f db

seed:
	PYTHONPATH=backend $(PYTHON) backend/seed_data.py

db-check:
	PYTHONPATH=backend $(PYTHON) backend/test_db.py
