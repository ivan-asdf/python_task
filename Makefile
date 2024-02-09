# export CELERY_BROKER_URL := amqp://username:password@localhost
# export DB_HOST := localhost

#.ONESHELL:
# run-local:
	# docker-compose up -d --build db
	# docker-compose up -d --build rabbitmq
	# python manage.py runserver 0.0.0.0:80 &
	# celery -A python_task worker --loglevel=info
	# export DB_HOST=localhost && \
	# export CELERY_BROKER_URL=amqp://username:password@localhost && \
	# python manage.py runserver 0.0.0.0:80 && \
	# echo $$CELERY_BROKER_URL && \
	# # celery -A python_task worker --loglevel=info

run-dev:
	docker-compose up --build

run-prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build

migrate:
	DB_HOST=localhost \
	python manage.py migrate

makemigrations:
	DB_HOST=localhost \
	python manage.py makemigrations

squashmigrations:
	DB_HOST=localhost \
	python manage.py squashmigrations

stop-composer:
	docker-compose down

db-clean:
	docker-compose down -v

# Usage
help:
	@echo "Run dev configuration(code is mounted so django will autoload at runtime code changes"
	@echo "  make run-dev"
	@echo "Run prod configuration(code copied as part of image)"
	@echo "  make run-prod"

.PHONY: run-dev run-prod stop-composer db-clean migrate makemigrations squashmigrations help

