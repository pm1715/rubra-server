from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import require_api_key
from app.dependencies import get_storage
from app.schemas import EvalRequest, EvalReportOut, MetricResultOut

router = APIRouter(prefix="/api/v1/eval", tags=["eval"])


def _report_to_out(report) -> EvalReportOut:
    return EvalReportOut(
        trace_id=report.trace_id,
        agent_name=report.agent_name,
        task=report.task,
        results=[
            MetricResultOut(
                metric_name=r.metric_name,
                score=r.score,
                passed=r.passed,
                reason=r.reason,
                category=r.category,
                is_deterministic=r.is_deterministic,
            )
            for r in report.results
        ],
        total_metrics=report.total_metrics,
        passed=report.passed,
        failed=report.failed,
        not_applicable=report.not_applicable,
        average_score=report.average_score,
        rubra_score=report.rubra_score,
        tool_intelligence_score=report.tool_intelligence_score,
        agentic_efficiency_score=report.agentic_efficiency_score,
        evaluation_ms=report.evaluation_ms,
    )


@router.post("", response_model=EvalReportOut)
async def run_eval(
    req: EvalRequest,
    _: None = Depends(require_api_key),
    storage=Depends(get_storage),
):
    """
    Run evaluation metrics against a stored trace.

    Returns an EvalReport with all metric scores, composite Rubra Score,
    Tool Intelligence Score, and Agentic Efficiency Score.
    """
    from rubra.core.evaluator.evaluator import evaluate

    trace = storage.get_trace(req.trace_id)
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace {req.trace_id} not found",
        )

    # persist=False — we handle persistence ourselves via the server's storage
    report = evaluate(
        trace,
        metrics=req.metrics,
        max_steps=req.max_steps,
        target_ms=req.target_ms,
        target_tokens=req.target_tokens,
        budget_usd=req.budget_usd,
        min_output_length=req.min_output_length,
        judge_model=req.judge_model,
        persist=False,
    )

    if req.persist:
        for r in report.results:
            storage.save_metric_result(
                trace_id=req.trace_id,
                metric_name=r.metric_name,
                score=r.score,
                passed=r.passed,
                reason=r.reason,
                category=r.category,
                is_deterministic=r.is_deterministic,
                metadata=r.metadata,
            )

    return _report_to_out(report)


@router.get("/{trace_id}", response_model=list[MetricResultOut])
async def get_stored_results(
    trace_id: str,
    _: None = Depends(require_api_key),
    storage=Depends(get_storage),
):
    """
    Retrieve previously persisted metric results for a trace.
    Returns empty list if the trace has never been evaluated.
    """
    trace = storage.get_trace(trace_id)
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace {trace_id} not found",
        )

    rows = storage.get_metric_results(trace_id)
    return [
        MetricResultOut(
            metric_name=r["metric_name"],
            score=r["score"],
            passed=r["passed"],
            reason=r["reason"],
            category=r["category"] or "unknown",
            is_deterministic=r["is_deterministic"],
        )
        for r in rows
    ]
