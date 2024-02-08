run-local:
	docker-compose up -d db
	DB_HOST=localhost \
	python manage.py runserver 0.0.0.0:80

migrate:
	DB_HOST=localhost \
	python manage.py migrate

makemigrations:
	DB_HOST=localhost \
	python manage.py makemigrations

squashmigrations:
	DB_HOST=localhost \
	python manage.py squashmigrations

run-composer:
	docker-compose up

rebuild-composer:
	docker-compose up --build

stop-composer:
	docker-compose down

db-clean:
	docker-compose down -v

# Usage
help:
	@echo "Local development:"
	@echo "  make run-local"
	@echo "Container development:"
	@echo "  make run-composer"

.PHONY: run-local run-composer rebuild-composer stop-composer db-clean help squashmigrations

