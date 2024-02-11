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

# squashmigrations:
# 	DB_HOST=localhost \
# 	python manage.py squashmigrations

db-clean:
	docker-compose down -v

run-dev-d:
	docker-compose up --build -d

db-clean-full: db-clean run-dev-d makemigrations migrate run-dev

# Usage
help:
	@echo "Run dev configuration(code is mounted so django will autoload at runtime code changes"
	@echo "  make run-dev"
	@echo "Run prod configuration(code copied as part of image)"
	@echo "  make run-prod"

.PHONY: run-dev run-prod stop \
				migrate migrate-local makemigrations makemigrations-local \
				db-clean run-dev-d db-clean-full
