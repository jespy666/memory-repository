REVISION_CMD = poetry run alembic revision --autogenerate -m

.PHONY: migrations run

migrations:
	$(REVISION_CMD) "$(shell read -p 'Enter migration name: ' msg; echo $$msg)"

migrate:
	poetry run alembic upgrade head

dev:
	poetry run python3 -m src.app