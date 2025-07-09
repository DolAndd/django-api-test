dev:
	uv run python3 manage.py runserver

migrate:
	uv run python3 manage.py migrate

install:
	@uv sync

build:
	./build.sh

render-start:
	gunicorn django_api_test.wsgi
