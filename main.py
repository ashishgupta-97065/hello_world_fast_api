from fastapi import FastAPI
import stats

APP_VERSION = "1.0.0"

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


@app.get("/version")
def read_version() -> dict:
    return {"version": APP_VERSION}


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
