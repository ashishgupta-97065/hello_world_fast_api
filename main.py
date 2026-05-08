import time

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


@app.on_event("startup")
def _populate_counters() -> None:
    stats.init_counters(app)


# Populate counters at import time so TestClient (without lifespan context
# manager) and any eager module-level code see a fully initialised counter map.
# init_counters is idempotent, so the startup hook above is a safe no-op when
# the server is started normally via uvicorn.
stats.init_counters(app)
