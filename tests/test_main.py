"""
Test suite for hello_world_fast_api.

Covers all 9 Acceptance Criteria from specs.md:
  AC1  - GET / returns HTTP 200
  AC2  - GET / returns {"message": "Hello, World!"} with Content-Type application/json
  AC3  - GET /health returns HTTP 200
  AC4  - GET /health returns {"status": "ok"} with Content-Type application/json
  AC5  - uvicorn start command is present in README (documented)
  AC6  - requirements.txt exists and contains fastapi and uvicorn
  AC7  - requirements.txt is parseable and lists all needed packages
  AC8  - README exists with venv creation, pip install, and server start instructions
  AC9  - This test suite itself exercises AC1-AC4 (satisfied by the tests below)
"""

import pathlib

import pytest
from fastapi.testclient import TestClient
from main import app

# ---------------------------------------------------------------------------
# Shared test client (module-scope so the ASGI lifespan runs once)
# ---------------------------------------------------------------------------

client = TestClient(app)

# Paths used in file-existence tests, anchored to the repo root.
REPO_ROOT = pathlib.Path(__file__).parent.parent


# ===========================================================================
# AC1 + AC2: GET /
# ===========================================================================

def test_root_status_code():
    """AC1: GET / must return HTTP 200."""
    response = client.get("/")
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}"
    )


def test_root_json_body():
    """AC2: GET / must return exactly {\"message\": \"Hello, World!\"}."""
    response = client.get("/")
    assert response.json() == {"message": "Hello, World!"}, (
        f"Unexpected body: {response.text}"
    )


def test_root_content_type():
    """AC2: GET / Content-Type must include application/json."""
    response = client.get("/")
    assert "application/json" in response.headers.get("content-type", ""), (
        f"Unexpected Content-Type: {response.headers.get('content-type')}"
    )


# ===========================================================================
# AC3 + AC4: GET /health
# ===========================================================================

def test_health_status_code():
    """AC3: GET /health must return HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}"
    )


def test_health_json_body():
    """AC4: GET /health must return exactly {\"status\": \"ok\"}."""
    response = client.get("/health")
    assert response.json() == {"status": "ok"}, (
        f"Unexpected body: {response.text}"
    )


def test_health_content_type():
    """AC4: GET /health Content-Type must include application/json."""
    response = client.get("/health")
    assert "application/json" in response.headers.get("content-type", ""), (
        f"Unexpected Content-Type: {response.headers.get('content-type')}"
    )


# ===========================================================================
# AC6 + AC7: requirements.txt
# ===========================================================================

def _read_requirements() -> str:
    req_path = REPO_ROOT / "requirements.txt"
    return req_path.read_text(encoding="utf-8").lower()


def test_requirements_txt_exists():
    """AC6: requirements.txt must exist at repo root."""
    req_path = REPO_ROOT / "requirements.txt"
    assert req_path.is_file(), f"requirements.txt not found at {req_path}"


def test_requirements_txt_has_fastapi():
    """AC6: requirements.txt must list fastapi."""
    content = _read_requirements()
    assert "fastapi" in content, (
        "requirements.txt does not contain 'fastapi'"
    )


def test_requirements_txt_has_uvicorn():
    """AC6: requirements.txt must list an ASGI server (uvicorn)."""
    content = _read_requirements()
    assert "uvicorn" in content, (
        "requirements.txt does not contain 'uvicorn'"
    )


def test_requirements_txt_has_pytest():
    """AC7: requirements.txt must list pytest so the test suite is runnable."""
    content = _read_requirements()
    assert "pytest" in content, (
        "requirements.txt does not contain 'pytest'"
    )


def test_requirements_txt_has_httpx():
    """AC7: requirements.txt must list httpx (required by FastAPI TestClient)."""
    content = _read_requirements()
    assert "httpx" in content, (
        "requirements.txt does not contain 'httpx' (needed by TestClient)"
    )


def test_requirements_txt_is_parseable():
    """AC7: requirements.txt must be non-empty and parseable (no binary content)."""
    req_path = REPO_ROOT / "requirements.txt"
    content = req_path.read_text(encoding="utf-8").strip()
    assert len(content) > 0, "requirements.txt is empty"
    # Each non-blank, non-comment line should look like a package specifier.
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        assert line[0].isalpha() or line.startswith("-"), (
            f"Unexpected line in requirements.txt: {line!r}"
        )


# ===========================================================================
# AC8: README with setup instructions
# ===========================================================================

def _read_readme() -> str:
    for name in ("README.md", "README.rst", "README.txt", "README"):
        candidate = REPO_ROOT / name
        if candidate.is_file():
            return candidate.read_text(encoding="utf-8")
    return ""


def test_readme_exists():
    """AC8: A README file must exist at repo root."""
    found = any(
        (REPO_ROOT / name).is_file()
        for name in ("README.md", "README.rst", "README.txt", "README")
    )
    assert found, "No README file found at repo root"


def test_readme_has_venv_instructions():
    """AC8: README must contain virtualenv creation instructions (python -m venv)."""
    content = _read_readme().lower()
    assert "venv" in content, (
        "README does not mention venv creation"
    )


def test_readme_has_pip_install():
    """AC8: README must contain pip install instructions."""
    content = _read_readme().lower()
    assert "pip install" in content, (
        "README does not contain 'pip install' instructions"
    )


def test_readme_has_uvicorn_start_command():
    """AC8: README must document the uvicorn server start command."""
    content = _read_readme().lower()
    assert "uvicorn" in content, (
        "README does not contain a uvicorn start command"
    )


def test_readme_has_port_8000():
    """AC5/AC8: README must reference port 8000 (documents the binding per AC5)."""
    content = _read_readme()
    assert "8000" in content, (
        "README does not mention port 8000 (required by AC5)"
    )


# ===========================================================================
# Additional robustness: wrong-method and unknown-path behaviour
# (FastAPI defaults — not custom, but worth asserting so regressions are caught)
# ===========================================================================

def test_root_post_returns_405():
    """POST / is not defined; FastAPI must return 405 Method Not Allowed."""
    response = client.post("/")
    assert response.status_code == 405, (
        f"Expected 405 for POST /, got {response.status_code}"
    )


def test_unknown_path_returns_404():
    """GET /nonexistent must return 404 Not Found."""
    response = client.get("/nonexistent")
    assert response.status_code == 404, (
        f"Expected 404 for unknown path, got {response.status_code}"
    )
