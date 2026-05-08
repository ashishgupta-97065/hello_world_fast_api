import os
import random
import socket
import time
from datetime import datetime, timezone

import psutil
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import stats
import pages

APP_VERSION = "1.0.0"
START_TIME: float = time.time()

# Expose counters dict for tests that import it directly from main.
counters = stats._counters


class VersionResponse(BaseModel):
    version: str
    uptime: int

app = FastAPI()
app.add_middleware(stats.StatsMiddleware)


@app.get("/", response_class=HTMLResponse)
def read_root() -> HTMLResponse:
    return HTMLResponse(content=pages.render_menu())


@app.get("/apps/todo", response_class=HTMLResponse)
def app_todo() -> HTMLResponse:
    return HTMLResponse(content=pages.render_todo())


@app.get("/apps/pomodoro", response_class=HTMLResponse)
def app_pomodoro() -> HTMLResponse:
    return HTMLResponse(content=pages.render_pomodoro())


@app.get("/apps/markdown", response_class=HTMLResponse)
def app_markdown() -> HTMLResponse:
    return HTMLResponse(content=pages.render_markdown())


@app.get("/apps/palette", response_class=HTMLResponse)
def app_palette() -> HTMLResponse:
    return HTMLResponse(content=pages.render_palette())


@app.get("/apps/bmi", response_class=HTMLResponse)
def app_bmi() -> HTMLResponse:
    return HTMLResponse(content=pages.render_bmi())


@app.get("/apps/password", response_class=HTMLResponse)
def app_password() -> HTMLResponse:
    return HTMLResponse(content=pages.render_password())


@app.get("/apps/word-counter", response_class=HTMLResponse)
def app_word_counter() -> HTMLResponse:
    return HTMLResponse(content=pages.render_word_counter())


@app.get("/apps/unit-converter", response_class=HTMLResponse)
def app_unit_converter() -> HTMLResponse:
    return HTMLResponse(content=pages.render_unit_converter())


@app.get("/apps/quote", response_class=HTMLResponse)
def app_quote() -> HTMLResponse:
    return HTMLResponse(content=pages.render_quote())


@app.get("/apps/dice", response_class=HTMLResponse)
def app_dice() -> HTMLResponse:
    return HTMLResponse(content=pages.render_dice())


@app.get("/apps/finance", response_class=HTMLResponse)
def app_finance() -> HTMLResponse:
    return HTMLResponse(content=pages.render_finance())


@app.get("/apps/habits", response_class=HTMLResponse)
def app_habits() -> HTMLResponse:
    return HTMLResponse(content=pages.render_habits())


@app.get("/apps/flashcards", response_class=HTMLResponse)
def app_flashcards() -> HTMLResponse:
    return HTMLResponse(content=pages.render_flashcards())


@app.get("/apps/budget", response_class=HTMLResponse)
def app_budget() -> HTMLResponse:
    return HTMLResponse(content=pages.render_budget())


@app.get("/apps/stopwatch", response_class=HTMLResponse)
def app_stopwatch() -> HTMLResponse:
    return HTMLResponse(content=pages.render_stopwatch())


@app.get("/apps/json-formatter", response_class=HTMLResponse)
def app_json_formatter() -> HTMLResponse:
    return HTMLResponse(content=pages.render_json_formatter())


@app.get("/apps/diff", response_class=HTMLResponse)
def app_diff() -> HTMLResponse:
    return HTMLResponse(content=pages.render_diff())


@app.get("/apps/recipe", response_class=HTMLResponse)
def app_recipe() -> HTMLResponse:
    return HTMLResponse(content=pages.render_recipe())


@app.get("/apps/pomodoro-pro", response_class=HTMLResponse)
def app_pomodoro_pro() -> HTMLResponse:
    return HTMLResponse(content=pages.render_pomodoro_pro())


@app.get("/apps/kanban", response_class=HTMLResponse)
def app_kanban() -> HTMLResponse:
    return HTMLResponse(content=pages.render_kanban())


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
