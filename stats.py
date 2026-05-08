import threading
from typing import Dict

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware

_counters: Dict[str, int] = {}
_lock: threading.Lock = threading.Lock()
_initialized: bool = False


def init_counters(app: FastAPI) -> None:
    """Populate _counters with one entry (value=0) per registered APIRoute on app.
    Must be called AFTER all routes are registered and BEFORE the first request.
    Idempotent: a second call has no effect."""
    global _initialized
    with _lock:
        if _initialized:
            return
        for route in app.routes:
            if isinstance(route, APIRoute):
                _counters[route.path] = 0
        _initialized = True


def snapshot() -> dict:
    """Return a copy of the current counter state, with keys in alphabetical order.
    Acquires _lock for the duration of the copy. Safe to serialize directly."""
    with _lock:
        return dict(sorted(_counters.items()))


def reset_counters() -> None:
    """Set every existing counter value to 0. Does NOT add or remove keys.
    Used by the existing POST /reset handler."""
    with _lock:
        for key in _counters:
            _counters[key] = 0


class StatsMiddleware(BaseHTTPMiddleware):
    """Starlette BaseHTTPMiddleware. After the downstream app finishes handling
    a request, inspects request.scope['route']. If the matched route's .path
    is a known counter key, increments its count by 1 under _lock.
    No-op for unmatched paths (404) and for paths not in _counters."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        route = request.scope.get("route")
        if route is not None:
            path = getattr(route, "path", None)
            if path is not None:
                with _lock:
                    if path in _counters:
                        _counters[path] += 1
        return response
