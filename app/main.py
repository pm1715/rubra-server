"""
Rubra Server — FastAPI REST API + dashboard.

Start:
    uvicorn app.main:app --reload
    # or:
    python -m app.main
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from importlib.metadata import version as _pkg_version

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.config import settings
from app.routers import eval as eval_router
from app.routers import report as report_router
from app.routers import traces as traces_router


# ---------------------------------------------------------------------------
# Lifespan — init storage once on startup
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.dependencies import get_storage
    get_storage()  # warm up storage singleton
    yield


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------


app = FastAPI(
    title="Rubra Server",
    description="REST API for the Rubra agentic evaluation framework.",
    version=_pkg_version("rubra-server"),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.rubra_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(traces_router.router)
app.include_router(eval_router.router)
app.include_router(report_router.router)


# ---------------------------------------------------------------------------
# Health / Version
# ---------------------------------------------------------------------------


@app.get("/api/v1/health", tags=["system"])
async def health():
    from app.dependencies import get_storage
    from app.schemas import HealthResponse
    storage = get_storage()
    db_url = storage._engine.url
    return HealthResponse(status="ok", storage=str(db_url))


@app.get("/api/v1/version", tags=["system"])
async def version():
    from rubra.__version__ import __version__ as sdk_version
    from app.schemas import VersionResponse
    return VersionResponse(server=_pkg_version("rubra-server"), sdk=sdk_version)


# ---------------------------------------------------------------------------
# Dashboard — self-contained single-page HTML served at /
# ---------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard():
    return HTMLResponse(content=_DASHBOARD_HTML)


_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rubra Dashboard</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjAwIDIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8ZGVmcz4KICAgIDxyYWRpYWxHcmFkaWVudCBpZD0iZ3JvdW5kIiBjeD0iNTAlIiBjeT0iNTAlIiByPSI1MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMDAwMDAwIiBzdG9wLW9wYWNpdHk9IjAuMzIiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMDAwMDAwIiBzdG9wLW9wYWNpdHk9IjAiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CgogICAgPHJhZGlhbEdyYWRpZW50IGlkPSJsb2JlQnJpZ2h0IiBjeD0iMzglIiBjeT0iMjIlIiByPSI4NSUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjZWFiNjhmIi8+CiAgICAgIDxzdG9wIG9mZnNldD0iMzglIiBzdG9wLWNvbG9yPSIjYzI0NjVhIi8+CiAgICAgIDxzdG9wIG9mZnNldD0iNzUlIiBzdG9wLWNvbG9yPSIjN2ExYjI4Ii8+CiAgICAgIDxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iIzNkMGMxMiIvPgogICAgPC9yYWRpYWxHcmFkaWVudD4KICAgIDxyYWRpYWxHcmFkaWVudCBpZD0ibG9iZU1lZCIgY3g9IjM4JSIgY3k9IjIyJSIgcj0iODUlIj4KICAgICAgPHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iI2M5OGE3NiIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjM4JSIgc3RvcC1jb2xvcj0iI2ExMjYzYSIvPgogICAgICA8c3RvcCBvZmZzZXQ9Ijc1JSIgc3RvcC1jb2xvcj0iIzYzMTMxZSIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMyZTA5MGQiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImxvYmVEYXJrIiBjeD0iMzglIiBjeT0iMjIlIiByPSI4NSUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjYTA1ZjVmIi8+CiAgICAgIDxzdG9wIG9mZnNldD0iMzglIiBzdG9wLWNvbG9yPSIjN2ExYjI4Ii8+CiAgICAgIDxzdG9wIG9mZnNldD0iNzUlIiBzdG9wLWNvbG9yPSIjNGEwZTE1Ii8+CiAgICAgIDxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iIzFmMDYwOSIvPgogICAgPC9yYWRpYWxHcmFkaWVudD4KCiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImhvbGUiIGN4PSI1MCUiIGN5PSIzMCUiIHI9IjgwJSI+CiAgICAgIDxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiMzYTEwMTUiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSI3MCUiIHN0b3AtY29sb3I9IiMxNTA0MDYiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMDUwMTAxIi8+CiAgICA8L3JhZGlhbEdyYWRpZW50PgogICAgPHJhZGlhbEdyYWRpZW50IGlkPSJob2xlU2hhZG93IiBjeD0iNTAlIiBjeT0iNTAlIiByPSI1MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMDAwMDAwIiBzdG9wLW9wYWNpdHk9IjAuNDUiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMDAwMDAwIiBzdG9wLW9wYWNpdHk9IjAiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgPC9kZWZzPgoKICA8ZWxsaXBzZSBjeD0iMTAwIiBjeT0iMTY2IiByeD0iNDgiIHJ5PSI5IiBmaWxsPSJ1cmwoI2dyb3VuZCkiLz4KCiAgPGVsbGlwc2UgY3g9IjEwMCIgY3k9IjEwMCIgcng9Ijk1IiByeT0iMzciIHRyYW5zZm9ybT0icm90YXRlKC0xMiAxMDAgMTAwKSIKICAgICAgICAgICBmaWxsPSJub25lIiBzdHJva2U9IiNhMzc5MmEiIHN0cm9rZS13aWR0aD0iMS44IiBvcGFjaXR5PSIwLjUiLz4KICA8ZWxsaXBzZSBjeD0iMTAwIiBjeT0iMTAwIiByeD0iOTUiIHJ5PSIzNyIgdHJhbnNmb3JtPSJyb3RhdGUoNTUgMTAwIDEwMCkiCiAgICAgICAgICAgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjYTM3OTJhIiBzdHJva2Utd2lkdGg9IjEuNiIgb3BhY2l0eT0iMC4zNSIvPgoKICA8ZyBzdHJva2UtbGluZWpvaW49InJvdW5kIj4KICAgIDxlbGxpcHNlIGN4PSIxMDAiIGN5PSI4MCIgcng9IjE2IiByeT0iMzMiIGZpbGw9InVybCgjbG9iZU1lZCkiICAgc3Ryb2tlPSIjMmUwOTBkIiBzdHJva2Utd2lkdGg9IjAuNzUiIG9wYWNpdHk9IjAuOTciIHRyYW5zZm9ybT0icm90YXRlKDAgMTAwIDEwMCkiLz4KICAgIDxlbGxpcHNlIGN4PSIxMDAiIGN5PSI4MCIgcng9IjE2IiByeT0iMzMiIGZpbGw9InVybCgjbG9iZURhcmspIiAgc3Ryb2tlPSIjMWYwNjA5IiBzdHJva2Utd2lkdGg9IjAuNzUiIG9wYWNpdHk9IjAuOTciIHRyYW5zZm9ybT0icm90YXRlKDUxLjQgMTAwIDEwMCkiLz4KICAgIDxlbGxpcHNlIGN4PSIxMDAiIGN5PSI4MCIgcng9IjE2IiByeT0iMzMiIGZpbGw9InVybCgjbG9iZURhcmspIiAgc3Ryb2tlPSIjMWYwNjA5IiBzdHJva2Utd2lkdGg9IjAuNzUiIG9wYWNpdHk9IjAuOTciIHRyYW5zZm9ybT0icm90YXRlKDEwMi44IDEwMCAxMDApIi8+CiAgICA8ZWxsaXBzZSBjeD0iMTAwIiBjeT0iODAiIHJ4PSIxNiIgcnk9IjMzIiBmaWxsPSJ1cmwoI2xvYmVEYXJrKSIgIHN0cm9rZT0iIzFmMDYwOSIgc3Ryb2tlLXdpZHRoPSIwLjc1IiBvcGFjaXR5PSIwLjk3IiB0cmFuc2Zvcm09InJvdGF0ZSgxNTQuMiAxMDAgMTAwKSIvPgogICAgPGVsbGlwc2UgY3g9IjEwMCIgY3k9IjgwIiByeD0iMTYiIHJ5PSIzMyIgZmlsbD0idXJsKCNsb2JlTWVkKSIgICBzdHJva2U9IiMyZTA5MGQiIHN0cm9rZS13aWR0aD0iMC43NSIgb3BhY2l0eT0iMC45NyIgdHJhbnNmb3JtPSJyb3RhdGUoMjA1LjYgMTAwIDEwMCkiLz4KICAgIDxlbGxpcHNlIGN4PSIxMDAiIGN5PSI4MCIgcng9IjE2IiByeT0iMzMiIGZpbGw9InVybCgjbG9iZUJyaWdodCkiIHN0cm9rZT0iIzNkMGMxMiIgc3Ryb2tlLXdpZHRoPSIwLjc1IiBvcGFjaXR5PSIwLjk3IiB0cmFuc2Zvcm09InJvdGF0ZSgyNTcuMCAxMDAgMTAwKSIvPgogICAgPGVsbGlwc2UgY3g9IjEwMCIgY3k9IjgwIiByeD0iMTYiIHJ5PSIzMyIgZmlsbD0idXJsKCNsb2JlQnJpZ2h0KSIgc3Ryb2tlPSIjM2QwYzEyIiBzdHJva2Utd2lkdGg9IjAuNzUiIG9wYWNpdHk9IjAuOTciIHRyYW5zZm9ybT0icm90YXRlKDMwOC40IDEwMCAxMDApIi8+CiAgPC9nPgoKICA8Y2lyY2xlIGN4PSIxMDAiIGN5PSIxMDAiIHI9IjEzIiBmaWxsPSJ1cmwoI2hvbGVTaGFkb3cpIi8+CiAgPGNpcmNsZSBjeD0iMTAwIiBjeT0iMTAwIiByPSI5IiBmaWxsPSJ1cmwoI2hvbGUpIi8+CiAgPGNpcmNsZSBjeD0iMTAwIiBjeT0iMTAwIiByPSI5IiBmaWxsPSJub25lIiBzdHJva2U9IiNhMzc5MmEiIHN0cm9rZS13aWR0aD0iMC44IiBvcGFjaXR5PSIwLjU1Ii8+Cjwvc3ZnPgo="/>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f3f4f6;color:#111;height:100vh;display:flex;flex-direction:column}
header{background:#dc2626;padding:14px 24px;display:flex;align-items:center;gap:16px;flex-shrink:0}
.logo-icon{width:30px;height:30px;flex-shrink:0}
.logo{font-size:20px;font-weight:800;color:#fff;letter-spacing:-.5px}
.logo-sub{color:#fca5a5;font-size:13px}
.header-right{margin-left:auto;display:flex;gap:12px;align-items:center}
.stat-pill{background:rgba(255,255,255,.15);color:#fff;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600}
.main{display:flex;flex:1;overflow:hidden}
.sidebar{width:380px;flex-shrink:0;background:#fff;border-right:1px solid #e5e7eb;display:flex;flex-direction:column;overflow:hidden}
.sidebar-header{padding:14px 16px;border-bottom:1px solid #e5e7eb;display:flex;align-items:center;gap:8px}
.sidebar-title{font-weight:600;font-size:14px}
.refresh-btn{margin-left:auto;background:#dc2626;color:#fff;border:none;padding:5px 12px;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600}
.refresh-btn:hover{background:#b91c1c}
.trace-list{overflow-y:auto;flex:1}
.trace-item{padding:12px 16px;border-bottom:1px solid #f3f4f6;cursor:pointer;transition:background .1s}
.trace-item:hover{background:#fef2f2}
.trace-item.selected{background:#fee2e2;border-left:3px solid #dc2626}
.trace-agent{font-weight:600;font-size:13px;margin-bottom:2px}
.trace-task{font-size:11px;color:#6b7280;margin-bottom:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.trace-meta{display:flex;gap:8px;font-size:11px;color:#9ca3af}
.badge{display:inline-block;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:700}
.badge-ok{background:#dcfce7;color:#166534}
.badge-fail{background:#fee2e2;color:#991b1b}
.badge-run{background:#fef9c3;color:#92400e}
.content{flex:1;overflow-y:auto;padding:24px}
.empty-state{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;color:#9ca3af}
.empty-icon{font-size:48px;margin-bottom:12px}
.panel{background:#fff;border-radius:10px;padding:20px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,.06)}
.panel-title{font-size:13px;font-weight:700;color:#dc2626;text-transform:uppercase;letter-spacing:.5px;margin-bottom:12px}
.kv-grid{display:grid;grid-template-columns:140px 1fr;gap:4px 12px;font-size:13px}
.kv-label{color:#6b7280;font-weight:500}
.kv-val{color:#111;word-break:break-all}
.score-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px}
.score-card{background:#fff;border-radius:8px;padding:16px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.06)}
.score-num{font-size:28px;font-weight:700;color:#dc2626}
.score-label{font-size:11px;color:#6b7280;margin-top:4px;text-transform:uppercase;letter-spacing:.3px}
.metrics-table{width:100%;border-collapse:collapse;font-size:12px}
.metrics-table th{padding:6px 10px;text-align:left;color:#6b7280;font-weight:600;border-bottom:1px solid #e5e7eb}
.metrics-table td{padding:6px 10px;border-bottom:1px solid #f9fafb}
.metrics-table tr:hover td{background:#fafafa}
.pass{color:#16a34a;font-weight:700}
.fail{color:#dc2626;font-weight:700}
.na{color:#9ca3af}
.eval-bar{display:flex;gap:8px;margin-bottom:16px}
.eval-select{border:1px solid #d1d5db;border-radius:6px;padding:6px 10px;font-size:13px;flex:1}
.eval-btn{background:#dc2626;color:#fff;border:none;padding:6px 18px;border-radius:6px;cursor:pointer;font-weight:600;font-size:13px}
.eval-btn:hover{background:#b91c1c}
.eval-btn:disabled{background:#d1d5db;cursor:not-allowed}
.report-btn{background:#111;color:#fff;border:none;padding:6px 14px;border-radius:6px;cursor:pointer;font-size:12px}
.report-btn:hover{background:#374151}
.spinner{display:inline-block;width:14px;height:14px;border:2px solid #fff;border-top-color:transparent;border-radius:50%;animation:spin .6s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.span-list{max-height:300px;overflow-y:auto}
.span-row{display:flex;gap:8px;align-items:center;padding:4px 0;border-bottom:1px solid #f3f4f6;font-size:12px}
.span-type{background:#f3f4f6;padding:1px 6px;border-radius:4px;font-family:monospace;font-size:10px;color:#374151;flex-shrink:0}
.span-name{color:#6b7280;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.span-dur{color:#9ca3af;flex-shrink:0;font-family:monospace}
</style>
</head>
<body>

<header>
  <svg class="logo-icon" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="100" cy="100" rx="95" ry="37" transform="rotate(-12 100 100)"
             fill="none" stroke="#ffffff" stroke-width="2" opacity="0.7"/>
    <ellipse cx="100" cy="100" rx="95" ry="37" transform="rotate(55 100 100)"
             fill="none" stroke="#ffffff" stroke-width="1.8" opacity="0.55"/>
    <g fill="#ffffff" stroke="#7a1b28" stroke-width="0.5" stroke-linejoin="round">
      <ellipse cx="100" cy="80" rx="16" ry="33" opacity="0.85" transform="rotate(0 100 100)"/>
      <ellipse cx="100" cy="80" rx="16" ry="33" opacity="0.6"  transform="rotate(51.4 100 100)"/>
      <ellipse cx="100" cy="80" rx="16" ry="33" opacity="0.6"  transform="rotate(102.8 100 100)"/>
      <ellipse cx="100" cy="80" rx="16" ry="33" opacity="0.6"  transform="rotate(154.2 100 100)"/>
      <ellipse cx="100" cy="80" rx="16" ry="33" opacity="0.85" transform="rotate(205.6 100 100)"/>
      <ellipse cx="100" cy="80" rx="16" ry="33" opacity="1"    transform="rotate(257.0 100 100)"/>
      <ellipse cx="100" cy="80" rx="16" ry="33" opacity="1"    transform="rotate(308.4 100 100)"/>
    </g>
    <circle cx="100" cy="100" r="9" fill="#7a1b28" opacity="0.55"/>
  </svg>
  <div class="logo">Rubra</div>
  <div class="logo-sub">Agentic Eval Dashboard</div>
  <div class="header-right">
    <span class="stat-pill" id="stat-traces">— traces</span>
    <span class="stat-pill" id="stat-tokens">— tokens</span>
    <a href="/docs" style="color:#fca5a5;font-size:12px;text-decoration:none">API Docs →</a>
  </div>
</header>

<div class="main">
  <div class="sidebar">
    <div class="sidebar-header">
      <span class="sidebar-title">Traces</span>
      <button class="refresh-btn" onclick="loadTraces()">↺ Refresh</button>
    </div>
    <div class="trace-list" id="trace-list">
      <div style="padding:24px;text-align:center;color:#9ca3af;font-size:13px">Loading…</div>
    </div>
  </div>

  <div class="content" id="content">
    <div class="empty-state">
      <div class="empty-icon">📊</div>
      <div style="font-weight:600;margin-bottom:6px">Select a trace to inspect</div>
      <div style="font-size:13px">Run an instrumented agent, then refresh the list.</div>
    </div>
  </div>
</div>

<script>
const API = '/api/v1';
let selectedTraceId = null;

async function api(path, opts = {}) {
  const r = await fetch(API + path, opts);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

function badge(status) {
  if (status === 'completed') return '<span class="badge badge-ok">OK</span>';
  if (status === 'failed')    return '<span class="badge badge-fail">FAIL</span>';
  return '<span class="badge badge-run">RUNNING</span>';
}

function dur(ms) {
  if (ms == null) return '—';
  if (ms < 1000) return ms.toFixed(0) + 'ms';
  return (ms/1000).toFixed(2) + 's';
}

function fmt(v) { return v == null ? '—' : v.toFixed(3); }

async function loadTraces() {
  try {
    const data = await api('/traces?limit=50');
    const list  = document.getElementById('trace-list');
    const pill  = document.getElementById('stat-traces');
    const tok   = document.getElementById('stat-tokens');
    pill.textContent = data.total + ' traces';
    const totalTok = data.traces.reduce((a, t) => a + t.total_tokens, 0);
    tok.textContent = totalTok.toLocaleString() + ' tokens';

    if (!data.traces.length) {
      list.innerHTML = '<div style="padding:24px;text-align:center;color:#9ca3af;font-size:13px">No traces yet. Run a @rubra.agent first.</div>';
      return;
    }

    list.innerHTML = data.traces.map(t => `
      <div class="trace-item${t.trace_id === selectedTraceId ? ' selected' : ''}"
           onclick="selectTrace('${t.trace_id}')">
        <div class="trace-agent">${esc(t.agent_name)} ${badge(t.status)}</div>
        <div class="trace-task">${esc(t.task || 'No task description')}</div>
        <div class="trace-meta">
          <span>${dur(t.duration_ms)}</span>
          <span>${t.total_tool_calls} tools</span>
          <span>${t.total_llm_calls} llm</span>
          <span>$${t.estimated_cost_usd.toFixed(4)}</span>
        </div>
      </div>`).join('');
  } catch (e) {
    document.getElementById('trace-list').innerHTML =
      '<div style="padding:16px;color:#dc2626;font-size:12px">Failed to load: ' + e.message + '</div>';
  }
}

async function selectTrace(traceId) {
  selectedTraceId = traceId;
  document.querySelectorAll('.trace-item').forEach(el => {
    el.classList.toggle('selected', el.onclick.toString().includes(traceId));
  });

  const content = document.getElementById('content');
  content.innerHTML = '<div style="padding:40px;text-align:center;color:#9ca3af">Loading trace…</div>';

  try {
    const trace = await api('/traces/' + traceId);
    renderTrace(trace);
  } catch (e) {
    content.innerHTML = '<div style="padding:24px;color:#dc2626">' + e.message + '</div>';
  }
}

function renderTrace(trace) {
  const content = document.getElementById('content');
  const statusBadge = badge(trace.status);
  const spanRows = (trace.spans || []).map(s => `
    <div class="span-row">
      <span class="span-type">${s.span_type}</span>
      <span class="span-name">${esc(s.name)}</span>
      <span class="span-dur">${dur(s.duration_ms)}</span>
      ${s.status === 'error' ? '<span style="color:#dc2626">✕</span>' : ''}
    </div>`).join('');

  content.innerHTML = `
    <div class="panel">
      <div class="panel-title">Trace</div>
      <div class="kv-grid">
        <span class="kv-label">Agent</span><span class="kv-val">${esc(trace.agent_name)}</span>
        <span class="kv-label">Status</span><span class="kv-val">${statusBadge}</span>
        <span class="kv-label">Task</span><span class="kv-val">${esc(trace.task || '—')}</span>
        <span class="kv-label">Duration</span><span class="kv-val">${dur(trace.duration_ms)}</span>
        <span class="kv-label">Tokens</span><span class="kv-val">${trace.total_tokens.toLocaleString()} ($${trace.estimated_cost_usd.toFixed(4)})</span>
        <span class="kv-label">Tools / LLM calls</span><span class="kv-val">${trace.total_tool_calls} / ${trace.total_llm_calls}</span>
        <span class="kv-label">Trace ID</span><span class="kv-val" style="font-family:monospace;font-size:11px">${trace.trace_id}</span>
        ${trace.final_output ? `<span class="kv-label">Output</span><span class="kv-val">${esc(trace.final_output.slice(0,200))}</span>` : ''}
      </div>
    </div>

    <div class="panel">
      <div class="panel-title">Evaluate</div>
      <div class="eval-bar">
        <select class="eval-select" id="metrics-sel">
          <option value="all">All metrics</option>
          <option value="execution">Execution only</option>
          <option value="tool">Tool orchestration</option>
          <option value="safety">Safety</option>
          <option value="quality">Quality</option>
          <option value="goal">Goal (LLM-judge)</option>
        </select>
        <input class="eval-select" id="judge-model" style="flex:0 0 200px" value="gpt-4o-mini"
               title="litellm model for goal metrics — try ollama/llama3.2 for a free local judge">
        <button class="eval-btn" id="eval-btn" onclick="runEval('${trace.trace_id}')">▶ Evaluate</button>
        <button class="report-btn" onclick="openReport('${trace.trace_id}')">⬡ HTML Report</button>
      </div>
      <div id="eval-result"></div>
    </div>

    <div class="panel">
      <div class="panel-title">Spans (${trace.spans.length})</div>
      <div class="span-list">${spanRows || '<div style="color:#9ca3af;font-size:12px">No spans captured.</div>'}</div>
    </div>`;
}

async function runEval(traceId) {
  const btn = document.getElementById('eval-btn');
  const metrics = document.getElementById('metrics-sel').value;
  const judge_model = document.getElementById('judge-model').value || 'gpt-4o-mini';
  const out = document.getElementById('eval-result');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>';
  out.innerHTML = '';

  try {
    const report = await api('/eval', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ trace_id: traceId, metrics, judge_model }),
    });
    renderReport(report, out);
  } catch (e) {
    out.innerHTML = '<div style="color:#dc2626;font-size:12px;margin-top:8px">' + e.message + '</div>';
  } finally {
    btn.disabled = false;
    btn.innerHTML = '▶ Evaluate';
  }
}

function renderReport(r, container) {
  const scores = [
    { label: 'Rubra Score', val: r.rubra_score },
    { label: 'Tool Intelligence', val: r.tool_intelligence_score },
    { label: 'Agentic Efficiency', val: r.agentic_efficiency_score },
  ].filter(s => s.val != null);

  const scoreHtml = scores.length ? `
    <div class="score-grid" style="margin-bottom:16px">
      ${scores.map(s => `
        <div class="score-card">
          <div class="score-num">${s.val.toFixed(3)}</div>
          <div class="score-label">${s.label}</div>
        </div>`).join('')}
      <div class="score-card">
        <div class="score-num">${r.passed}</div>
        <div class="score-label">Passed</div>
      </div>
      <div class="score-card" style="color:#dc2626">
        <div class="score-num" style="color:#dc2626">${r.failed}</div>
        <div class="score-label">Failed</div>
      </div>
      <div class="score-card">
        <div class="score-num" style="color:#6b7280">${r.not_applicable}</div>
        <div class="score-label">N/A</div>
      </div>
    </div>` : '';

  const rows = r.results.map(m => {
    const sc = m.score != null ? m.score.toFixed(4) : '—';
    const res = m.passed === true ? '<span class="pass">PASS</span>'
              : m.passed === false ? '<span class="fail">FAIL</span>'
              : '<span class="na">N/A</span>';
    return `<tr>
      <td style="font-family:monospace;font-size:11px">${esc(m.metric_name)}</td>
      <td style="text-align:right;font-weight:600">${sc}</td>
      <td style="text-align:center">${res}</td>
      <td style="color:#6b7280">${esc(m.category)}</td>
      <td style="font-size:11px;color:#9ca3af">${esc((m.reason||'').slice(0,60))}</td>
    </tr>`;
  }).join('');

  container.innerHTML = scoreHtml + `
    <table class="metrics-table">
      <thead><tr>
        <th>Metric</th><th>Score</th><th>Result</th><th>Category</th><th>Reason</th>
      </tr></thead>
      <tbody>${rows}</tbody>
    </table>
    <div style="margin-top:8px;font-size:11px;color:#9ca3af">
      ${r.total_metrics} metrics · ${r.evaluation_ms ? r.evaluation_ms.toFixed(0)+'ms' : ''}
    </div>`;
}

function openReport(traceId) {
  window.open('/api/v1/report/' + traceId, '_blank');
}

function esc(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

loadTraces();
setInterval(loadTraces, 30000);
</script>
</body>
</html>
"""


def start() -> None:
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.rubra_host,
        port=settings.rubra_port,
        reload=settings.rubra_debug,
    )


if __name__ == "__main__":
    start()
