#!/usr/bin/env bash
set -euo pipefail

# Detener procesos anteriores del bot/web sin afectar a la ejecución actual.
for pattern in "python3 run.py both" "python3 run.py bot" "web_server.py" "src/bot/main.py"; do
  pids=$(pgrep -f "$pattern" || true)
  if [ -n "$pids" ]; then
    for pid in $pids; do
      if [ "$pid" != "$$" ] && [ "$pid" != "$PPID" ]; then
        kill "$pid" 2>/dev/null || true
      fi
    done
  fi
 done

sleep 1
