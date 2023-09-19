SHELL := /bin/sh

# Run a command in a new container
web-run = docker-compose run --rm web
# Run a command in an existing container
web-exec = docker-compose exec web
# run on existing container if available otherwise a new one
web := ${if $(shell docker ps -q -f name=web),$(web-exec),$(web-run)}

build:
	docker-compose build

bash:
	$(web) bash

compile-requirements:
	$(web) pip-compile --output-file requirements.txt requirements.in

down:
	docker-compose down

migrate:
	$(web) python manage.py migrate

shell:
	$(web) python manage.py shell

up:
	$(MAKE) migrate
	docker-compose up

up-detached:
	docker-compose up -d
