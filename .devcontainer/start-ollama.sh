#!/usr/bin/env bash
# Runs on every container start. Starts the Ollama server if it isn't
# already running, and pulls the demo model on first start only.
set -euo pipefail

MODEL="${RUBRA_DEMO_MODEL:-llama3.2:1b}"

if ! pgrep -x "ollama" > /dev/null 2>&1; then
  echo "==> Starting Ollama server"
  nohup ollama serve > /tmp/ollama.log 2>&1 &
  sleep 3
fi

if ! ollama list 2>/dev/null | grep -q "$MODEL"; then
  echo "==> Pulling $MODEL (first run only, ~1.3GB)"
  ollama pull "$MODEL"
fi

echo "==> Ollama ready at http://localhost:11434 (model: $MODEL)"
