PICCOLO_CONF := core.database

# ── Docker ───────────────────────────────────────────────────────────────────

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f api

# ── Dev local ─────────────────────────────────────────────────────────────────

install:
	pip install -r requirements.txt

dev:
	PICCOLO_CONF=$(PICCOLO_CONF) uvicorn app:app --reload --host 0.0.0.0 --port 8000

worker:
	huey_consumer core.worker.huey -w 2 -k thread

# ── Migrations ────────────────────────────────────────────────────────────────

# Exemple : make migration app=auth
migration:
	PICCOLO_CONF=$(PICCOLO_CONF) piccolo migrations new $(app) --auto

migrate:
	PICCOLO_CONF=$(PICCOLO_CONF) piccolo migrations forwards all

# ── Tests ─────────────────────────────────────────────────────────────────────

test:
	pytest tests/ -v

# ── Scaffolding ───────────────────────────────────────────────────────────────

# Exemple : make feature name=clients
feature:
	@python3 scripts/new_feature.py $(name)

.PHONY: up down logs install dev worker migration migrate test feature
