"""
Shared fixtures for rubra-server tests.
Uses an in-memory SQLite DB so tests are fast and isolated.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from rubra.core.storage.db import RubraStorage


@pytest.fixture(autouse=True)
def reset_storage_singleton():
    """Each test gets a fresh in-memory DB via monkeypatched dependency."""
    yield
    # reset lru_cache so next test gets a clean instance
    from app.dependencies import get_storage
    get_storage.cache_clear()


@pytest.fixture()
def storage() -> RubraStorage:
    return RubraStorage("sqlite:///:memory:")


@pytest.fixture()
def client(storage) -> TestClient:
    from app.dependencies import get_storage
    from app.main import app

    get_storage.cache_clear()
    app.dependency_overrides[get_storage] = lambda: storage
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def completed_trace(storage):
    """A completed trace with one tool span, saved to storage."""
    from rubra.core.tracer.models import (
        Span, SpanType, ToolCallData, ToolResponseData, Trace,
    )

    trace = Trace(
        agent_name="test_agent",
        task="Answer a question about capitals",
        expected_tool_calls=["search"],
    )
    call = Span(
        trace_id=trace.trace_id,
        span_type=SpanType.TOOL_CALL,
        name="tool:search",
        tool_call_data=ToolCallData(tool_name="search", arguments={"q": "France capital"}),
    )
    call.finish()
    trace.add_span(call)

    resp = Span(
        trace_id=trace.trace_id,
        parent_span_id=call.span_id,
        span_type=SpanType.TOOL_RESPONSE,
        name="tool_response:search",
        tool_response_data=ToolResponseData(tool_name="search", output="Paris is the capital of France."),
    )
    resp.finish()
    trace.add_span(resp)
    trace.finish(output="Paris")

    storage.save_trace(trace)
    return trace
