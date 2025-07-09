dev:
	uv run python3 manage.py runserver

migrate:
	uv run python3 manage.py migrate

install:
	@uv sync
