# hello_world_fast_api

A minimal FastAPI application exposing a root greeting endpoint and a health check endpoint. Use this as a baseline scaffold to verify the Python/FastAPI toolchain is wired up correctly.

## Prerequisites

- Python 3.10 or newer

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --port 8000
```

The server will start and listen on `http://localhost:8000`.

## Verify

```bash
curl http://localhost:8000/
```

Expected output:

```json
{"message":"Hello, World!"}
```

```bash
curl http://localhost:8000/health
```

Expected output:

```json
{"status":"ok"}
```

## Test

```bash
pytest
```

## Interactive API Documentation

Once the server is running, open your browser to `http://localhost:8000/docs` for the auto-generated Swagger UI where you can explore and try out both endpoints interactively.
