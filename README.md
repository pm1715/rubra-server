<p align="center">
  <img src="assets/wordmark.svg" alt="Rubra" width="380"/>
</p>

**Server — REST API + live dashboard for [Rubra](https://github.com/pm1715/rubra-sdk).**

[![PyPI](https://img.shields.io/pypi/v/rubra-server.svg)](https://pypi.org/project/rubra-server/)
[![Docker](https://img.shields.io/badge/ghcr.io-rubra--server-blue?logo=docker)](https://github.com/pm1715/rubra-server/pkgs/container/rubra-server)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![CI](https://github.com/pm1715/rubra-server/actions/workflows/ci.yml/badge.svg)](https://github.com/pm1715/rubra-server/actions)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/pm1715/rubra-server)

Self-host a backend for your Rubra traces: browse them, run evaluations, and generate HTML reports from a browser — no notebook required.

---

## Try the full stack now — zero cost, zero setup

Click **Open in GitHub Codespaces** above (or go to `codespaces.new/pm1715/rubra-server`). The devcontainer automatically:

- Clones `rubra-sdk` and `rubra-deploy` as sibling repos and installs everything
- Installs and starts **Ollama** with a small local model — no OpenAI key needed
- Installs `kubectl`, `helm`, and `kind` for testing the [rubra-deploy](https://github.com/pm1715/rubra-deploy) Helm chart against a real (throwaway) Kubernetes cluster

Once it's ready:

```bash
# 1. Generate a real trace — a tool-calling agent, judged by a free local model
python examples/full_stack_demo.py

# 2. Start the server
uvicorn app.main:app --reload
```

Open the forwarded port-8000 URL for the dashboard, select the trace, and hit **Evaluate** — the judge-model field defaults to `gpt-4o-mini` but works with any [litellm](https://docs.litellm.ai/docs/providers)-supported model, including the free `ollama/llama3.2:1b` already running in the Codespace.

To also test the Kubernetes deployment for real:

```bash
cd ../rubra-deploy
./scripts/test-in-kind.sh
```

This builds the actual `Dockerfile`, loads it into a `kind` cluster, installs the Helm chart, and port-forwards it — a genuine deploy test with no registry or cloud cluster required.

---

## Quickstart

### Docker (recommended)

```bash
docker run -p 8000:8000 ghcr.io/pm1715/rubra-server:latest
```

Or with `docker compose` for persistent storage:

```bash
git clone https://github.com/pm1715/rubra-server
cd rubra-server
docker compose up
```

- Dashboard → http://localhost:8000
- API docs → http://localhost:8000/docs

### From PyPI

```bash
pip install rubra-server
rubra-server
```

### From source

```bash
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

By default the server uses SQLite at `.rubra/rubra.db` and runs in open dev mode (no API key required).

---

## Configuration

Copy `.env.example` to `.env` and adjust:

| Variable | Default | Description |
|---|---|---|
| `RUBRA_API_KEY` | unset | If set, all endpoints require an `X-Rubra-API-Key` header matching this value. Unset = open dev mode. |
| `RUBRA_DATABASE_URL` | `sqlite:///./data/rubra.db` | SQLite or PostgreSQL connection string. |
| `RUBRA_HOST` | `0.0.0.0` | Bind host. |
| `RUBRA_PORT` | `8000` | Bind port. |
| `RUBRA_DEBUG` | `false` | Enables uvicorn auto-reload. |
| `RUBRA_CORS_ORIGINS` | `["*"]` | Restrict to your frontend origin in production. |

---

## API

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/traces` | List traces (`?agent_name=`, `?limit=`, `?offset=`) |
| `GET` | `/api/v1/traces/{trace_id}` | Full trace detail including spans |
| `DELETE` | `/api/v1/traces/{trace_id}` | Delete a trace and its stored metric results |
| `POST` | `/api/v1/eval` | Evaluate a trace (`{"trace_id": "...", "metrics": "all", "judge_model": "gpt-4o-mini"}`) |
| `GET` | `/api/v1/eval/{trace_id}` | Fetch previously computed metric results |
| `GET` | `/api/v1/report/{trace_id}` | Self-contained HTML report |
| `GET` | `/api/v1/health` | Health check + storage backend info |
| `GET` | `/api/v1/version` | Server + SDK version |

Full interactive docs at `/docs` (Swagger) and `/redoc`.

---

## Dashboard

The `/` route serves a single-page dashboard: a trace list on the left, and on selection — trace metadata, span timeline, and an inline **Evaluate** button that runs any metric category and renders pass/fail results without leaving the page. The judge-model field next to it accepts any litellm model string, so goal metrics can run against a free local Ollama model instead of a paid API.

It polls `/api/v1/traces` every 30s, so traces produced by an instrumented agent elsewhere show up automatically.

---

## Getting traces into the server

The server only reads traces — it doesn't instrument your agent. Point your app's storage at the same database, or use the SDK's Postgres/shared-SQLite backend:

```python
import os
os.environ["RUBRA_DATABASE_URL"] = "postgresql://rubra:rubra@localhost:5432/rubra"

import rubra

@rubra.agent(task="Answer questions")
def my_agent(question: str) -> str:
    ...
```

As long as `rubra-server` points at the same `RUBRA_DATABASE_URL`, traces appear in the dashboard as soon as the agent finishes.

---

## Security & Code of Conduct

This repo follows the same [Security Policy](https://github.com/pm1715/rubra-sdk/blob/main/SECURITY.md) and [Code of Conduct](https://github.com/pm1715/rubra-sdk/blob/main/CODE_OF_CONDUCT.md) as rubra-sdk.

## License

Apache 2.0 — see [LICENSE](LICENSE).
