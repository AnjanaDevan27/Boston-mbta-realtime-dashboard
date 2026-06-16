.PHONY: setup test lint run deploy clean help

setup:
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v

coverage:
	pytest tests/ --cov=pipeline --cov-report=term-missing

lint:
	flake8 pipeline/ tests/ dags/ config/ --max-line-length=120

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
	find . -type f -name "*.pyc" -delete 2>/dev/null
	echo "Cleaned up cache files"

help:
	@echo "make setup    - Install dependencies"
	@echo "make test     - Run all tests"
	@echo "make coverage - Run tests with coverage"
	@echo "make lint     - Check code style"
	@echo "make clean    - Remove cache files"
