.PHONY: install lint format typecheck arch test check

install:
	uv sync
	uv run pre-commit install

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .

typecheck:
	uv run mypy

arch:
	uv run lint-imports

test:
	uv run pytest

check: lint typecheck arch test
