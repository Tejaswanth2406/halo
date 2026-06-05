.PHONY: help install dev lint test clean build docker-build docker-up

help:
	@echo "RAG Production System - Available Commands"
	@echo "==========================================="
	@echo "make install        - Install dependencies"
	@echo "make dev            - Setup development environment"
	@echo "make lint           - Run code linters"
	@echo "make format         - Format code with black/isort"
	@echo "make test           - Run all tests"
	@echo "make test-unit      - Run unit tests only"
	@echo "make test-integration - Run integration tests"
	@echo "make test-coverage  - Run tests with coverage"
	@echo "make clean          - Clean build artifacts"
	@echo "make docker-build   - Build Docker images"
	@echo "make docker-up      - Start Docker containers"
	@echo "make docker-down    - Stop Docker containers"
	@echo "make eval           - Run RAGAS evaluation"

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt
	pip install -e ".[dev]"

lint:
	flake8 src tests
	mypy src
	pylint src

format:
	black src tests
	isort src tests

test:
	pytest tests/ -v

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-coverage:
	pytest tests/ --cov=src --cov-report=html

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov dist build

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

eval:
	python scripts/run_evaluation.py

freeze:
	pip freeze > requirements.txt
