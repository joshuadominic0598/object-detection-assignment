.PHONY: setup start test e2e

setup:
	./scripts/setup.sh

start: setup
	. .venv/bin/activate && ENV=prod python -m counter.entrypoints.webapp

stop:
	-docker stop tfserving
	-docker stop test-mysql
	-docker stop test-mongo

test:
	pytest

e2e:
	pytest tests/e2e -v