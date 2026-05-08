import os
import random
import socket
import time
from datetime import datetime, timezone

import psutil
from fastapi import FastAPI
from pydantic import BaseModel
import stats

APP_VERSION = "1.0.0"
START_TIME: float = time.time()


class VersionResponse(BaseModel):
    version: str
    uptime: int

app = FastAPI()
app.add_middleware(stats.StatsMiddleware)


@app.get("/")
def read_root() -> dict:
    return {"message": "Hello, World!"}


@app.get("/health")
def read_health() -> dict:
    return {"status": "ok"}


@app.get("/stats")
def read_stats() -> dict:
    return stats.snapshot()


@app.get(
    "/version",
    response_model=VersionResponse,
    tags=["meta"],
    summary="Application version and uptime",
)
def read_version() -> VersionResponse:
    return VersionResponse(
        version=APP_VERSION,
        uptime=int(time.time() - START_TIME),
    )


@app.get("/ping")
def read_ping(msg: str = "") -> dict:
    if msg:
        return {"message": "pong", "msg": msg}
    return {"message": "pong"}


@app.post("/reset")
def reset_counters() -> dict:
    stats.reset_counters()
    return {"reset": True}


@app.get("/hostname")
def read_hostname() -> dict:
    return {"hostname": socket.gethostname()}


@app.get("/env")
def read_env() -> dict:
    return {"environment": os.environ.get("APP_ENV", "development")}


@app.get("/memory")
def read_memory() -> dict:
    rss_mb = round(psutil.Process().memory_info().rss / (1024 ** 2), 1)
    return {"rss_mb": rss_mb}


@app.get("/echo")
def read_echo(message: str) -> dict:
    return {"message": message}


@app.get("/timestamp")
def read_timestamp() -> dict:
    return {"timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/random")
def read_random() -> dict:
    return {"number": random.randint(1, 1000)}


@app.get("/reverse")
def read_reverse(text: str) -> dict:
    return {"reversed": text[::-1]}


@app.get("/upper")
def read_upper(text: str) -> dict:
    return {"upper": text.upper()}


@app.get("/count")
def read_count(text: str) -> dict:
    return {"count": len(text)}


@app.get("/palindrome")
def read_palindrome(text: str) -> dict:
    normalized = text.replace(" ", "").lower()
    return {"is_palindrome": normalized == normalized[::-1]}


@app.on_event("startup")
def _populate_counters() -> None:
    stats.init_counters(app)


# Populate counters at import time so TestClient (without lifespan context
# manager) and any eager module-level code see a fully initialised counter map.
# init_counters is idempotent, so the startup hook above is a safe no-op when
# the server is started normally via uvicorn.
stats.init_counters(app)
