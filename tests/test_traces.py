"""Tests for GET /api/v1/traces and GET /api/v1/traces/{trace_id}."""
from __future__ import annotations

import pytest
from rubra.core.tracer.models import Trace


def test_list_traces_empty(client):
    r = client.get("/api/v1/traces")
    assert r.status_code == 200
    data = r.json()
    assert data["traces"] == []
    assert data["total"] == 0


def test_list_traces_returns_summaries(client, completed_trace):
    r = client.get("/api/v1/traces")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    t = data["traces"][0]
    assert t["trace_id"] == completed_trace.trace_id
    assert t["agent_name"] == "test_agent"
    assert t["status"] == "completed"
    assert t["total_tool_calls"] == 1


def test_list_traces_filter_by_agent(client, storage):
    for name in ["alpha", "alpha", "beta"]:
        t = Trace(agent_name=name, task="task")
        t.finish()
        storage.save_trace(t)

    r = client.get("/api/v1/traces?agent_name=alpha")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert all(t["agent_name"] == "alpha" for t in data["traces"])


def test_list_traces_limit(client, storage):
    for i in range(5):
        t = Trace(agent_name="agent", task=f"task {i}")
        t.finish()
        storage.save_trace(t)

    r = client.get("/api/v1/traces?limit=3")
    assert r.status_code == 200
    assert len(r.json()["traces"]) == 3


def test_get_trace_by_id(client, completed_trace):
    r = client.get(f"/api/v1/traces/{completed_trace.trace_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["trace_id"] == completed_trace.trace_id
    assert data["agent_name"] == "test_agent"
    assert len(data["spans"]) == 2


def test_get_trace_not_found(client):
    r = client.get("/api/v1/traces/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_delete_trace(client, completed_trace, storage):
    r = client.delete(f"/api/v1/traces/{completed_trace.trace_id}")
    assert r.status_code == 204

    # Verify deleted
    assert storage.get_trace(completed_trace.trace_id) is None


def test_delete_nonexistent_trace(client):
    r = client.delete("/api/v1/traces/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
