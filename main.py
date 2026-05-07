from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root() -> dict:
    return {"message": "Hello, World!"}


@app.get("/health")
def read_health() -> dict:
    return {"status": "ok"}
