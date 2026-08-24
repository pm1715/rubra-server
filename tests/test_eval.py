"""Tests for POST /api/v1/eval and GET /api/v1/eval/{trace_id}."""
from __future__ import annotations


def test_run_eval_execution(client, completed_trace):
    r = client.post("/api/v1/eval", json={
        "trace_id": completed_trace.trace_id,
        "metrics": "execution",
        "persist": False,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["trace_id"] == completed_trace.trace_id
    assert data["agent_name"] == "test_agent"
    assert data["total_metrics"] > 0
    assert data["rubra_score"] is not None
    assert 0.0 <= data["rubra_score"] <= 1.0


def test_run_eval_tool_metrics(client, completed_trace):
    r = client.post("/api/v1/eval", json={
        "trace_id": completed_trace.trace_id,
        "metrics": "tool",
        "persist": False,
    })
    assert r.status_code == 200
    data = r.json()
    names = {m["metric_name"] for m in data["results"]}
    assert "tool_chain_validity" in names


def test_run_eval_not_found(client):
    r = client.post("/api/v1/eval", json={
        "trace_id": "00000000-0000-0000-0000-000000000000",
        "metrics": "execution",
    })
    assert r.status_code == 404


def test_run_eval_all_categories(client, completed_trace):
    r = client.post("/api/v1/eval", json={
        "trace_id": completed_trace.trace_id,
        "metrics": "all",
        "persist": False,
    })
    assert r.status_code == 200
    data = r.json()
    categories = {m["category"] for m in data["results"]}
    assert "execution" in categories
    assert "tool" in categories
    assert "safety" in categories
    assert "quality" in categories


def test_get_stored_results_empty(client, completed_trace):
    r = client.get(f"/api/v1/eval/{completed_trace.trace_id}")
    assert r.status_code == 200
    assert r.json() == []


def test_get_stored_results_after_persist(client, completed_trace, storage):
    # Run eval with persist=True
    client.post("/api/v1/eval", json={
        "trace_id": completed_trace.trace_id,
        "metrics": "execution",
        "persist": True,
    })

    r = client.get(f"/api/v1/eval/{completed_trace.trace_id}")
    assert r.status_code == 200
    results = r.json()
    assert len(results) > 0
    assert all("metric_name" in m for m in results)


def test_get_stored_results_trace_not_found(client):
    r = client.get("/api/v1/eval/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_eval_metric_result_structure(client, completed_trace):
    r = client.post("/api/v1/eval", json={
        "trace_id": completed_trace.trace_id,
        "metrics": "execution",
        "persist": False,
    })
    m = r.json()["results"][0]
    assert "metric_name" in m
    assert "score" in m
    assert "passed" in m
    assert "category" in m
    assert "is_deterministic" in m
