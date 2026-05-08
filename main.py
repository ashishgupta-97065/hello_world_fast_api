from fastapi import FastAPI

APP_VERSION = "1.0.0"

app = FastAPI()

counters: dict[str, int] = {
    "GET /": 0,
    "GET /health": 0,
    "GET /stats": 0,
}


@app.get("/")
def read_root() -> dict:
    counters["GET /"] += 1
    return {"message": "Hello, World!"}


@app.get("/health")
def read_health() -> dict:
    counters["GET /health"] += 1
    return {"status": "ok"}


@app.get("/stats")
def read_stats() -> dict:
    counters["GET /stats"] += 1
    return {"counters": counters}


@app.get("/version")
def read_version() -> dict:
    return {"version": APP_VERSION}


@app.post("/reset")
def reset_counters() -> dict:
    for key in counters:
        counters[key] = 0
    return {"reset": True}
