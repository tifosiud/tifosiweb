PYTHON ?= python3

run:
	$(PYTHON) run.py both

bot:
	$(PYTHON) run.py bot

web:
	$(PYTHON) run.py web

test:
	$(PYTHON) -m unittest discover -s tests
