PYTHON ?= python3

run:
	@SHELL_PID=$$; \
	ps -ef | grep -F 'python3 run.py both' | grep -v grep | awk -v sid=$$ '$$2 != sid {print $$2}' | xargs -r kill 2>/dev/null || true; \
	ps -ef | grep -F 'python3 run.py bot' | grep -v grep | awk -v sid=$$ '$$2 != sid {print $$2}' | xargs -r kill 2>/dev/null || true; \
	ps -ef | grep -F 'web_server.py' | grep -v grep | awk -v sid=$$ '$$2 != sid {print $$2}' | xargs -r kill 2>/dev/null || true; \
	ps -ef | grep -F 'src/bot/main.py' | grep -v grep | awk -v sid=$$ '$$2 != sid {print $$2}' | xargs -r kill 2>/dev/null || true; \
	sleep 1; \
	$(PYTHON) run.py both

bot:
	$(PYTHON) run.py bot

web:
	$(PYTHON) run.py web

test:
	$(PYTHON) -m unittest discover -s tests
