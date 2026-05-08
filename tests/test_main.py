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
from main import app, counters

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


# ===========================================================================
# New tests for ticket #3 — in-memory request counter / /stats endpoint
# ===========================================================================

import pytest


@pytest.fixture
def reset_counters():
    """Zero all counter keys before the test. Opt-in only — NOT autouse."""
    for k in counters:
        counters[k] = 0
    yield


def test_stats_status_and_content_type(reset_counters):
    """AC3: GET /stats returns 200 with application/json."""
    response = client.get("/stats")
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")


def test_stats_response_shape(reset_counters):
    """AC7c: /stats response has exactly the right shape and key set."""
    response = client.get("/stats")
    body = response.json()
    assert set(body.keys()) == {"counters"}
    assert set(body["counters"].keys()) == {"GET /", "GET /health", "GET /stats"}
    for v in body["counters"].values():
        assert isinstance(v, int)


def test_stats_initial_state(reset_counters):
    """AC7a: After reset, /stats shows 0 for / and /health, 1 for /stats itself."""
    response = client.get("/stats")
    body = response.json()
    assert body["counters"]["GET /"] == 0
    assert body["counters"]["GET /health"] == 0
    assert body["counters"]["GET /stats"] == 1  # counts itself (AC5)


def test_stats_increments_on_root_and_health(reset_counters):
    """AC7b: After M hits to / and N hits to /health, /stats shows M and N."""
    for _ in range(3):
        client.get("/")
    for _ in range(2):
        client.get("/health")
    response = client.get("/stats")
    body = response.json()
    assert body["counters"]["GET /"] == 3
    assert body["counters"]["GET /health"] == 2
    assert body["counters"]["GET /stats"] == 1


def test_stats_counts_itself(reset_counters):
    """AC7d: Two consecutive /stats calls; second shows one more than first."""
    r1 = client.get("/stats")
    r2 = client.get("/stats")
    v1 = r1.json()["counters"]["GET /stats"]
    v2 = r2.json()["counters"]["GET /stats"]
    assert v2 == v1 + 1


def test_404_does_not_mutate_counters(reset_counters):
    """AC6 / specs Q1: GET /nonexistent does not add new keys."""
    keys_before = set(counters.keys())
    client.get("/nonexistent")
    assert set(counters.keys()) == keys_before


def test_405_does_not_increment_root(reset_counters):
    """AC6 / specs Q1: POST / returns 405 and does not increment GET / counter."""
    client.post("/")
    assert counters["GET /"] == 0


# ===========================================================================
# New tests for ticket #4 — /version endpoint
# ===========================================================================

from main import APP_VERSION


def test_version_status_code():
    """AC2: GET /version must return HTTP 200."""
    response = client.get("/version")
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}"
    )


def test_version_json_body():
    """AC3: GET /version must return exactly {\"version\": \"<string>\"}."""
    response = client.get("/version")
    body = response.json()
    assert set(body.keys()) == {"version"}, f"Unexpected keys: {body.keys()}"
    assert isinstance(body["version"], str), "version value must be a string"


def test_version_content_type():
    """AC4: GET /version Content-Type must include application/json."""
    response = client.get("/version")
    assert "application/json" in response.headers.get("content-type", ""), (
        f"Unexpected Content-Type: {response.headers.get('content-type')}"
    )


def test_version_post_returns_405():
    """AC6: POST /version is not defined; FastAPI must return 405."""
    response = client.post("/version")
    assert response.status_code == 405, (
        f"Expected 405 for POST /version, got {response.status_code}"
    )


def test_version_does_not_mutate_counters():
    """AC7: GET /version must not add new keys to the counters dict."""
    keys_before = set(counters.keys())
    client.get("/version")
    assert set(counters.keys()) == keys_before, (
        "GET /version added unexpected keys to counters"
    )


def test_version_reflects_constant():
    """AC5: GET /version body must reflect the APP_VERSION constant."""
    response = client.get("/version")
    assert response.json() == {"version": APP_VERSION}, (
        f"Endpoint returned {response.json()!r}, expected {{'version': {APP_VERSION!r}}}"
    )
