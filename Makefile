.PHONY: setup start stop test e2e integration dashboard

PYTHON=.venv/bin/python

setup:
	./scripts/setup.sh

start: setup
	ENV=prod $(PYTHON) -m counter.entrypoints.webapp

stop:
	-docker stop tfserving
	-docker stop test-mysql
	-docker stop test-mongo

test:
	PYTHONPATH=. $(PYTHON) -m pytest tests/domain -v

integration:
	PYTHONPATH=. $(PYTHON) -m pytest tests/integration -v

e2e:
	PYTHONPATH=. $(PYTHON) -m pytest tests/e2e -v

entrypoints:
	PYTHONPATH=. $(PYTHON) -m pytest tests/entrypoints -v

dashboard:
	$(PYTHON) scripts/generate_dashboard.py 