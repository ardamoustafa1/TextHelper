import time
import uuid
from typing import Any, Dict

from fastapi import Request


_METRICS: Dict[str, Any] = {
    "total_requests": 0,
    "total_errors": 0,
    "total_duration_ms": 0.0,
    "last_request_ts": None,
}


async def observability_middleware(request: Request, call_next):
    """
    Middleware to attach a correlation ID and collect lightweight metrics.
    """
    start = time.time()
    _METRICS["total_requests"] += 1

    request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    request.state.request_id = request_id

    try:
        response = await call_next(request)
        return response
    except Exception:
        _METRICS["total_errors"] += 1
        raise
    finally:
        duration_ms = (time.time() - start) * 1000.0
        _METRICS["total_duration_ms"] += duration_ms
        _METRICS["last_request_ts"] = time.time()


def get_metrics_snapshot() -> Dict[str, Any]:
    """Return a shallow copy of current in-memory metrics."""
    snapshot = dict(_METRICS)
    # Derive avg latency if possible
    total = snapshot.get("total_requests") or 1
    snapshot["avg_duration_ms"] = snapshot.get("total_duration_ms", 0.0) / total
    return snapshot

