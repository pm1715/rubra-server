from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import require_api_key
from app.dependencies import get_storage
from app.schemas import TraceDetail, TraceListResponse, TraceSummary, SpanOut, TokenUsageOut

router = APIRouter(prefix="/api/v1/traces", tags=["traces"])


def _to_summary(trace) -> TraceSummary:
    return TraceSummary(
        trace_id=trace.trace_id,
        agent_name=trace.agent_name,
        task=trace.task,
        status=trace.status.value,
        total_tool_calls=trace.total_tool_calls,
        total_llm_calls=trace.total_llm_calls,
        total_tokens=trace.token_usage.total_tokens,
        estimated_cost_usd=trace.token_usage.estimated_cost_usd,
        duration_ms=trace.duration_ms,
        started_at=trace.started_at,
        ended_at=trace.ended_at,
        tags=trace.tags,
        had_errors=trace.had_errors,
    )


def _to_span_out(span) -> SpanOut:
    tool_name = None
    llm_model = None
    llm_tokens = None
    if span.tool_call_data:
        tool_name = span.tool_call_data.tool_name
    elif span.tool_response_data:
        tool_name = span.tool_response_data.tool_name
    elif span.llm_data:
        llm_model = span.llm_data.model
        llm_tokens = span.llm_data.total_tokens
    return SpanOut(
        span_id=span.span_id,
        span_type=span.span_type.value,
        name=span.name,
        status=span.status.value,
        duration_ms=span.duration_ms,
        error_message=span.error_message,
        tool_name=tool_name,
        llm_model=llm_model,
        llm_tokens=llm_tokens,
    )


def _to_detail(trace) -> TraceDetail:
    return TraceDetail(
        trace_id=trace.trace_id,
        agent_name=trace.agent_name,
        task=trace.task,
        task_description=trace.task_description,
        status=trace.status.value,
        total_tool_calls=trace.total_tool_calls,
        total_llm_calls=trace.total_llm_calls,
        total_tokens=trace.token_usage.total_tokens,
        estimated_cost_usd=trace.token_usage.estimated_cost_usd,
        duration_ms=trace.duration_ms,
        started_at=trace.started_at,
        ended_at=trace.ended_at,
        tags=trace.tags,
        had_errors=trace.had_errors,
        final_output=trace.final_output,
        error_message=trace.error_message,
        expected_output=trace.expected_output,
        expected_tool_calls=trace.expected_tool_calls,
        spans=[_to_span_out(s) for s in trace.spans],
        token_usage=TokenUsageOut(
            prompt_tokens=trace.token_usage.prompt_tokens,
            completion_tokens=trace.token_usage.completion_tokens,
            total_tokens=trace.token_usage.total_tokens,
            estimated_cost_usd=trace.token_usage.estimated_cost_usd,
        ),
        metadata=trace.metadata,
    )


@router.get("", response_model=TraceListResponse)
async def list_traces(
    agent_name: str | None = Query(None),
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _: None = Depends(require_api_key),
    storage=Depends(get_storage),
):
    """List recent traces, newest first."""
    traces = storage.list_traces(agent_name=agent_name, limit=limit, offset=offset)
    return TraceListResponse(
        traces=[_to_summary(t) for t in traces],
        total=len(traces),
        limit=limit,
        offset=offset,
    )


@router.get("/{trace_id}", response_model=TraceDetail)
async def get_trace(
    trace_id: str,
    _: None = Depends(require_api_key),
    storage=Depends(get_storage),
):
    """Get a single trace with all spans."""
    trace = storage.get_trace(trace_id)
    if not trace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trace {trace_id} not found")
    return _to_detail(trace)


@router.delete("/{trace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trace(
    trace_id: str,
    _: None = Depends(require_api_key),
    storage=Depends(get_storage),
):
    """Delete a trace and its stored metric results."""
    from sqlalchemy import delete as sql_delete
    from rubra.core.storage.db import TraceRow, MetricResultRow

    trace = storage.get_trace(trace_id)
    if not trace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trace {trace_id} not found")

    with storage._Session() as session:
        session.execute(sql_delete(MetricResultRow).where(MetricResultRow.trace_id == trace_id))
        session.execute(sql_delete(TraceRow).where(TraceRow.trace_id == trace_id))
        session.commit()
