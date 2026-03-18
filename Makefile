.PHONY: build up down logs test clean-docs shell-app shell-ollama

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

test:
	docker compose run --rm tests pytest

clean-docs:
	rm -rf documents/*.pdf

shell-app:
	docker exec -it fortaleza-app /bin/bash

shell-ollama:
	docker exec -it fortaleza-ollama /bin/bash
