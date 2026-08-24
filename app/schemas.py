"""
API-layer Pydantic schemas.
Kept separate from SDK models so the HTTP contract can evolve independently.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Traces
# ---------------------------------------------------------------------------


class TokenUsageOut(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float


class SpanOut(BaseModel):
    span_id: str
    span_type: str
    name: str
    status: str
    duration_ms: float | None
    error_message: str | None
    tool_name: str | None = None
    llm_model: str | None = None
    llm_tokens: int | None = None


class TraceSummary(BaseModel):
    trace_id: str
    agent_name: str
    task: str | None
    status: str
    total_tool_calls: int
    total_llm_calls: int
    total_tokens: int
    estimated_cost_usd: float
    duration_ms: float | None
    started_at: datetime
    ended_at: datetime | None
    tags: list[str]
    had_errors: bool


class TraceDetail(TraceSummary):
    task_description: str | None
    final_output: str | None
    error_message: str | None
    expected_output: str | None
    expected_tool_calls: list[str] | None
    spans: list[SpanOut]
    token_usage: TokenUsageOut
    metadata: dict[str, Any]


class TraceListResponse(BaseModel):
    traces: list[TraceSummary]
    total: int
    limit: int
    offset: int


# ---------------------------------------------------------------------------
# Eval
# ---------------------------------------------------------------------------


class EvalRequest(BaseModel):
    trace_id: str
    metrics: str = Field(
        default="all",
        description="Metric set: all, execution, tool, safety, quality, goal",
    )
    max_steps: int = 10
    target_ms: float = 5000.0
    target_tokens: int = 4096
    budget_usd: float = 0.10
    min_output_length: int = 10
    persist: bool = True


class MetricResultOut(BaseModel):
    metric_name: str
    score: float | None
    passed: bool | None
    reason: str | None
    category: str
    is_deterministic: bool


class EvalReportOut(BaseModel):
    trace_id: str
    agent_name: str
    task: str | None
    results: list[MetricResultOut]
    total_metrics: int
    passed: int
    failed: int
    not_applicable: int
    average_score: float | None
    rubra_score: float | None
    tool_intelligence_score: float | None
    agentic_efficiency_score: float | None
    evaluation_ms: float | None


# ---------------------------------------------------------------------------
# Health / Version
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    status: str = "ok"
    storage: str


class VersionResponse(BaseModel):
    server: str
    sdk: str
