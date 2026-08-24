"""Tests for GET /api/v1/report/{trace_id}."""
from __future__ import annotations


def test_report_returns_html(client, completed_trace):
    r = client.get(f"/api/v1/report/{completed_trace.trace_id}")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "<!DOCTYPE html>" in r.text


def test_report_contains_agent_name(client, completed_trace):
    r = client.get(f"/api/v1/report/{completed_trace.trace_id}")
    assert "test_agent" in r.text


def test_report_contains_rubra_branding(client, completed_trace):
    r = client.get(f"/api/v1/report/{completed_trace.trace_id}")
    assert "Rubra" in r.text


def test_report_not_found(client):
    r = client.get("/api/v1/report/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_report_execution_metrics_only(client, completed_trace):
    r = client.get(f"/api/v1/report/{completed_trace.trace_id}?metrics=execution")
    assert r.status_code == 200
    assert "execution" in r.text.lower()


def test_dashboard_returns_html(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "Rubra Dashboard" in r.text


def test_health_endpoint(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "storage" in data


def test_version_endpoint(client):
    r = client.get("/api/v1/version")
    assert r.status_code == 200
    data = r.json()
    assert "server" in data
    assert "sdk" in data
    assert data["sdk"] == "0.1.0"
