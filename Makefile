.PHONY: install test lint backend frontend all

## Install all dependencies
install:
	pip install -r backend/requirements.txt
	cd frontend && npm install

## Run backend unit + integration tests
test:
	pytest backend/tests/ -v --tb=short

## Lint backend Python code
lint-py:
	flake8 backend/ --max-line-length=100 --exclude=backend/tests/

## Lint frontend JS/JSX
lint-js:
	cd frontend && npm run lint

## Start backend dev server
backend:
	cd backend && uvicorn main:app --reload --port 8000

## Start frontend dev server
frontend:
	cd frontend && npm start

## Run backend + frontend concurrently (requires 'make -j2')
all:
	$(MAKE) -j2 backend frontend
