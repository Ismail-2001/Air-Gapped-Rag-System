.PHONY: build up down logs test shell ollama-sh clean save load status

# Variables
PROJECT_NAME = airgap-rag
DOCKER_COMPOSE = docker compose

build:      ## Build all containers
	$(DOCKER_COMPOSE) build

up:         ## Start the stack in background
	$(DOCKER_COMPOSE) up -d

down:       ## Stop the stack
	$(DOCKER_COMPOSE) down

logs:       ## Tail all logs
	$(DOCKER_COMPOSE) logs -f

test:       ## Run air-gap verification tests
	$(DOCKER_COMPOSE) exec app python tests/test_airgap.py
	$(DOCKER_COMPOSE) exec app python tests/test_rag.py

shell:      ## Shell into app container
	$(DOCKER_COMPOSE) exec app bash

ollama-sh:  ## Shell into ollama container
	$(DOCKER_COMPOSE) exec ollama bash

clean:      ## Remove all containers, volumes, images, and data
	$(DOCKER_COMPOSE) down -v --rmi all --remove-orphans
	rm -rf app/chroma_data/
	rm -rf models/*
	rm -rf documents/*

save:       ## Export Docker images to tar for offline transfer
	mkdir -p ./exports
	docker save airgap-app:latest > ./exports/airgap-app.tar
	docker save airgap-ollama:latest > ./exports/airgap-ollama.tar
	@echo "Images exported to ./exports directory."

load:       ## Import Docker images from tar files
	docker load < ./exports/airgap-app.tar
	docker load < ./exports/airgap-ollama.tar

status:     ## Show container health and stats
	$(DOCKER_COMPOSE) ps
	docker stats --no-stream

help:       ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
