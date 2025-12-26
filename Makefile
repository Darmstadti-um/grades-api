.PHONY: up down logs itest

up:
	docker compose up --build -d db
	docker compose up --build migrate
	docker compose up --build -d app

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

itest:
	docker compose -f docker-compose.test.yml up --build -d
	POSTGRES_HOST=localhost POSTGRES_PORT=55432 POSTGRES_DB=grades POSTGRES_USER=grades POSTGRES_PASSWORD=grades \
	pytest -q
	docker compose -f docker-compose.test.yml down -v
