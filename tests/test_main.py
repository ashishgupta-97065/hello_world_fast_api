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


# ===========================================================================
# New tests for ticket #6 — POST /reset endpoint
# ===========================================================================

def test_reset_status_code(reset_counters):
    """AC1: POST /reset must return HTTP 200."""
    response = client.post("/reset")
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}"
    )


def test_reset_response_body(reset_counters):
    """AC2: POST /reset must return exactly {\"reset\": true}."""
    response = client.post("/reset")
    assert response.json() == {"reset": True}, (
        f"Unexpected body: {response.text}"
    )


def test_reset_zeroes_counters(reset_counters):
    """AC3 + AC4: After hits to / and /health then POST /reset, GET /stats shows every counter 0 except GET /stats which is 1."""
    client.get("/")
    client.get("/")
    client.get("/health")
    client.post("/reset")
    response = client.get("/stats")
    body = response.json()
    assert body["counters"]["GET /"] == 0
    assert body["counters"]["GET /health"] == 0
    assert body["counters"]["GET /stats"] == 1


def test_reset_does_not_add_reset_key(reset_counters):
    """AC4 / resolved Open Question: POST /reset must not add a /reset or POST /reset key to counters."""
    client.post("/reset")
    response = client.get("/stats")
    body = response.json()
    assert set(body["counters"].keys()) == {"GET /", "GET /health", "GET /stats"}, (
        f"Unexpected keys in counters: {set(body['counters'].keys())}"
    )


def test_reset_does_not_increment_on_call(reset_counters):
    """AC4 strict: immediately after POST /reset only (no other requests), GET /stats shows
    all counters at 0 except GET /stats itself which is exactly 1."""
    client.post("/reset")
    response = client.get("/stats")
    body = response.json()
    assert body["counters"]["GET /"] == 0, (
        f"POST /reset must not increment GET /, found {body['counters']['GET /']}"
    )
    assert body["counters"]["GET /health"] == 0, (
        f"POST /reset must not increment GET /health, found {body['counters']['GET /health']}"
    )
    assert body["counters"]["GET /stats"] == 1, (
        f"GET /stats should be 1 (self-increment only), found {body['counters']['GET /stats']}"
    )


def test_reset_content_type(reset_counters):
    """POST /reset Content-Type must include application/json."""
    response = client.post("/reset")
    assert "application/json" in response.headers.get("content-type", ""), (
        f"Unexpected Content-Type: {response.headers.get('content-type')}"
    )


def test_reset_get_method_returns_405():
    """GET /reset is not defined; FastAPI must return 405 Method Not Allowed."""
    response = client.get("/reset")
    assert response.status_code == 405, (
        f"Expected 405 for GET /reset, got {response.status_code}"
    )


def test_existing_routes_unaffected_after_reset(reset_counters):
    """AC6: Existing routes still return correct responses after the /reset endpoint is added."""
    assert client.get("/").json() == {"message": "Hello, World!"}
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/version").json() == {"version": APP_VERSION}
    stats_body = client.get("/stats").json()
    assert "counters" in stats_body
    assert set(stats_body["counters"].keys()) == {"GET /", "GET /health", "GET /stats"}


def test_reset_idempotent(reset_counters):
    """POST /reset called twice in a row must still return 200 and leave all counters at 0."""
    client.get("/")
    client.get("/health")
    client.post("/reset")
    response = client.post("/reset")
    assert response.status_code == 200
    assert response.json() == {"reset": True}
    stats = client.get("/stats").json()
    assert stats["counters"]["GET /"] == 0
    assert stats["counters"]["GET /health"] == 0
    assert stats["counters"]["GET /stats"] == 1


# ===========================================================================
# New tests for ticket #7 — GET /ping endpoint with optional msg parameter
# ===========================================================================

def test_ping_no_msg_returns_pong():
    """AC1: GET /ping (no query param) returns HTTP 200, body {"message": "pong"},
    Content-Type application/json."""
    response = client.get("/ping")
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}"
    )
    assert response.json() == {"message": "pong"}, (
        f"Unexpected body: {response.text}"
    )
    assert "application/json" in response.headers.get("content-type", ""), (
        f"Unexpected Content-Type: {response.headers.get('content-type')}"
    )


def test_ping_with_msg_echoes():
    """AC2: GET /ping?msg=hello returns HTTP 200, body {"message": "pong", "msg": "hello"},
    Content-Type application/json."""
    response = client.get("/ping", params={"msg": "hello"})
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}"
    )
    assert response.json() == {"message": "pong", "msg": "hello"}, (
        f"Unexpected body: {response.text}"
    )
    assert "application/json" in response.headers.get("content-type", ""), (
        f"Unexpected Content-Type: {response.headers.get('content-type')}"
    )


def test_ping_empty_msg_treated_as_no_msg():
    """AC3: GET /ping?msg= (param present but empty string) returns {"message": "pong"}
    with no "msg" key — identical to the no-param case."""
    response = client.get("/ping?msg=")
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}"
    )
    body = response.json()
    assert body == {"message": "pong"}, (
        f"Expected exactly {{\"message\": \"pong\"}}, got {body}"
    )
    assert "msg" not in body, (
        f"'msg' key must not appear when msg is empty string; body={body}"
    )


def test_ping_does_not_increment_counters(reset_counters):
    """AC4: Multiple /ping calls (with and without msg) must not touch counters["GET /"]
    or counters["GET /health"]. Verified by reading the counters dict directly to avoid
    the side-effect of calling GET /stats."""
    client.get("/ping")
    client.get("/ping", params={"msg": "test"})
    client.get("/ping?msg=")
    client.get("/ping")
    client.get("/ping", params={"msg": "another"})
    assert counters["GET /"] == 0, (
        f"/ping must not increment counters['GET /'], found {counters['GET /']}"
    )
    assert counters["GET /health"] == 0, (
        f"/ping must not increment counters['GET /health'], found {counters['GET /health']}"
    )
    assert counters["GET /stats"] == 0, (
        f"/ping must not increment counters['GET /stats'], found {counters['GET /stats']}"
    )


def test_ping_does_not_add_new_counter_key(reset_counters):
    """AC5: After multiple /ping calls, GET /stats counters key set is exactly
    {"GET /", "GET /health", "GET /stats"} — no "GET /ping" or any other new key."""
    client.get("/ping")
    client.get("/ping", params={"msg": "foo"})
    client.get("/ping?msg=")
    client.get("/ping")
    response = client.get("/stats")
    assert response.status_code == 200
    body = response.json()
    assert set(body["counters"].keys()) == {"GET /", "GET /health", "GET /stats"}, (
        f"Unexpected keys in counters after /ping calls: {set(body['counters'].keys())}"
    )


def test_ping_post_returns_405():
    """AC8: POST /ping is not defined; FastAPI must return 405 Method Not Allowed."""
    response = client.post("/ping")
    assert response.status_code == 405, (
        f"Expected 405 for POST /ping, got {response.status_code}"
    )


@pytest.mark.parametrize("msg,expected_body", [
    ("world", {"message": "pong", "msg": "world"}),
    ("foo bar", {"message": "pong", "msg": "foo bar"}),
    ("123", {"message": "pong", "msg": "123"}),
    ("special!@#", {"message": "pong", "msg": "special!@#"}),
])
def test_ping_msg_echoed_verbatim(msg, expected_body):
    """AC2 (parameterised): Various non-empty msg values are echoed back verbatim."""
    response = client.get("/ping", params={"msg": msg})
    assert response.status_code == 200, (
        f"Expected 200 for msg={msg!r}, got {response.status_code}"
    )
    assert response.json() == expected_body, (
        f"Unexpected body for msg={msg!r}: {response.text}"
    )


def test_ping_no_msg_body_is_byte_identical_to_empty_msg():
    """AC3 (structural): Confirm that /ping and /ping?msg= produce exactly the same JSON body."""
    r_no_param = client.get("/ping")
    r_empty_param = client.get("/ping?msg=")
    assert r_no_param.json() == r_empty_param.json(), (
        f"No-param body {r_no_param.text!r} != empty-param body {r_empty_param.text!r}"
    )


def test_ping_counter_values_unchanged_after_mixed_traffic(reset_counters):
    """AC4 (extended): Interleaved /ping calls among real traffic must not inflate /ping
    contribution into existing counters."""
    client.get("/")            # GET / counter = 1
    client.get("/ping")        # must not affect anything
    client.get("/health")      # GET /health counter = 1
    client.get("/ping", params={"msg": "probe"})  # must not affect anything
    client.get("/")            # GET / counter = 2
    client.get("/ping?msg=")   # must not affect anything
    # Read counters directly — do NOT call /stats here to avoid its own side-effect.
    assert counters["GET /"] == 2, (
        f"Expected GET / counter=2, got {counters['GET /']}"
    )
    assert counters["GET /health"] == 1, (
        f"Expected GET /health counter=1, got {counters['GET /health']}"
    )
    assert counters["GET /stats"] == 0, (
        f"Expected GET /stats counter=0, got {counters['GET /stats']}"
    )


def test_existing_routes_unaffected_after_ping_added():
    """AC6: All five pre-existing endpoints return their expected responses after /ping is
    introduced — no regressions."""
    # GET /
    root = client.get("/")
    assert root.status_code == 200
    assert root.json() == {"message": "Hello, World!"}
    # GET /health
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    # GET /version
    version = client.get("/version")
    assert version.status_code == 200
    assert version.json() == {"version": APP_VERSION}
    # GET /stats — shape and key set
    stats = client.get("/stats")
    assert stats.status_code == 200
    stats_body = stats.json()
    assert "counters" in stats_body
    assert set(stats_body["counters"].keys()) == {"GET /", "GET /health", "GET /stats"}
    # POST /reset
    reset = client.post("/reset")
    assert reset.status_code == 200
    assert reset.json() == {"reset": True}
