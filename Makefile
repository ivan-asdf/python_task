run_local:
	docker-compose up -d db
	DB_HOST=localhost \
	python manage.py runserver 0.0.0.0:80

migrate:
	DB_HOST=localhost \
	python manage.py migrate

makemigrations:
	DB_HOST=localhost \
	python manage.py makemigrations

run_composer:
	docker-compose up

rebuild_composer:
	docker-compose up --build

stop_composer:
	docker-compose down

db_clean:
	docker-compose down -v
	make run_composer

# Usage
help:
	@echo "Local development:"
	@echo "  make run_local"
	@echo "Container development:"
	@echo "  make run_composer"

.PHONY: run_local run_composer rebuild_composer stop_composer db_clean help

