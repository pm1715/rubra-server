from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse

from app.auth import require_api_key
from app.dependencies import get_storage

router = APIRouter(prefix="/api/v1/report", tags=["report"])


@router.get("/{trace_id}", response_class=HTMLResponse)
async def get_html_report(
    trace_id: str,
    metrics: str = "all",
    _: None = Depends(require_api_key),
    storage=Depends(get_storage),
):
    """
    Generate and stream a self-contained HTML evaluation report.

    Evaluates the trace on the fly using the requested metric set and
    returns a browser-ready HTML page — no separate eval call needed.
    """
    from rubra.core.evaluator.evaluator import evaluate

    trace = storage.get_trace(trace_id)
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace {trace_id} not found",
        )

    report = evaluate(trace, metrics=metrics, persist=False)
    html = report.to_html()
    return HTMLResponse(content=html, status_code=200)
