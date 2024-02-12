run-dev:
	docker-compose up --build

run-prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build

stop:
	docker-compose down

migrate:
	docker-compose exec web python manage.py migrate

migrate-local:
	DB_HOST=localhost \
	python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

makemigrations-local:
	DB_HOST=localhost \
	python manage.py makemigrations

test:
	docker-compose exec web python manage.py test -v 2

db-clean:
	docker-compose down -v

run-dev-d:
	docker-compose up --build -d

db-clean-full: db-clean run-dev-d makemigrations migrate run-dev

# Usage
help:
	@echo "Run dev configuration (code is mounted so django will autoload at runtime code changes"
	@echo "  make run-dev"
	@echo
	@echo "Run prod configuration (code copied as part of image)"
	@echo "  make run-prod"
	@echo
	@echo "Stop services"
	@echo "  make stop"
	@echo
	@echo "Run migrations"
	@echo "  make migrate"
	@echo
	@echo "Run migrations by trying to connect to db locally"
	@echo "  make migrate-local"
	@echo
	@echo "Run tests"
	@echo "  make test"
	@echo
	@echo "Clean db and stop services"
	@echo "  make db-clean"
	@echo
	@echo "Clean db, do migrations, and run dev configuration (VERY USEFULL for just starting initial DEV configuration)"
	@echo "  make db-clean-full"

.PHONY: run-dev run-prod stop \
				migrate migrate-local makemigrations makemigrations-local test\
				db-clean run-dev-d db-clean-full
