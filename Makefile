.PHONY: bootstrap api web worker test lint demo

bootstrap:
	python -m pip install -e ".[dev]"
	pnpm --dir frontend install

api:
	uvicorn backend.app.main:app --reload --port 8000

web:
	pnpm --dir frontend dev

worker:
	celery -A backend.app.worker.celery_app worker --loglevel=INFO

test:
	pytest
	pnpm --dir frontend test

lint:
	ruff check backend sim tests scripts
	pnpm --dir frontend lint

demo:
	python scripts/run_demo.py

