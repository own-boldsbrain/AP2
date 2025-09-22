# Makefile para PRE Orchestrator Agent

# Variáveis
DOCKER_COMPOSE = docker-compose
PYTHON = python
PIP = pip
DOCKER = docker
IMAGE_NAME = pre-orchestrator-agent
IMAGE_TAG = latest
FULL_IMAGE_NAME = yellowsolar/$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: help build run test lint clean docker-build docker-push install dev start-services stop-services

help:
	@echo "Comandos disponíveis:"
	@echo "  make help            - Exibe este menu de ajuda"
	@echo "  make install         - Instala as dependências de desenvolvimento"
	@echo "  make dev             - Executa o servidor em modo de desenvolvimento"
	@echo "  make lint            - Executa verificação de estilo de código"
	@echo "  make test            - Executa os testes unitários"
	@echo "  make build           - Constrói o pacote Python"
	@echo "  make docker-build    - Constrói a imagem Docker"
	@echo "  make docker-push     - Envia a imagem Docker para o registro"
	@echo "  make start-services  - Inicia os serviços com docker-compose"
	@echo "  make stop-services   - Interrompe os serviços com docker-compose"
	@echo "  make clean           - Remove arquivos temporários e caches"

install:
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

dev:
	uvicorn pkg.pre_orchestrator.server:app --reload --host 0.0.0.0 --port 8020

lint:
	black pkg/pre_orchestrator
	flake8 pkg/pre_orchestrator
	mypy pkg/pre_orchestrator

test:
	pytest pkg/pre_orchestrator/tests -v

build:
	$(PYTHON) -m build

docker-build:
	$(DOCKER) build -t $(FULL_IMAGE_NAME) -f apps/pre_orchestrator/Dockerfile .

docker-push:
	$(DOCKER) push $(FULL_IMAGE_NAME)

start-services:
	cd apps/pre_orchestrator && $(DOCKER_COMPOSE) up -d

stop-services:
	cd apps/pre_orchestrator && $(DOCKER_COMPOSE) down

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name ".pytest_cache" -exec rm -rf {} +
	find . -name ".coverage" -delete
	find . -name ".mypy_cache" -exec rm -rf {} +