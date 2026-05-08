"""
Tests for Ticket #10: 10 Utility Endpoints

Covers all Acceptance Criteria (AC1–AC19) for the ten new stateless utility
endpoints. AC20 is structural and satisfied by the existence of this file.

Endpoints under test:
  GET /hostname   GET /env        GET /memory   GET /echo
  GET /timestamp  GET /random     GET /reverse  GET /upper
  GET /count      GET /palindrome
"""
import socket
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# Helpers / constants for AC18 & AC19 cross-cutting checks
# ---------------------------------------------------------------------------

_ENDPOINTS_NO_PARAMS = [
    "/hostname",
    "/env",
    "/memory",
    "/timestamp",
    "/random",
]

_ENDPOINTS_WITH_PARAMS = [
    ("/echo",      {"message": "test"}),
    ("/reverse",   {"text": "test"}),
    ("/upper",     {"text": "test"}),
    ("/count",     {"text": "test"}),
    ("/palindrome", {"text": "test"}),
]


# ===========================================================================
# AC1: GET /hostname
# ===========================================================================

def test_hostname_returns_200():
    response = client.get("/hostname")
    assert response.status_code == 200


def test_hostname_response_has_hostname_key():
    response = client.get("/hostname")
    assert "hostname" in response.json()


def test_hostname_value_matches_socket_gethostname():
    """The returned hostname must equal socket.gethostname()."""
    response = client.get("/hostname")
    assert response.json()["hostname"] == socket.gethostname()


# ===========================================================================
# AC2: GET /env
# ===========================================================================

def test_env_returns_200():
    response = client.get("/env")
    assert response.status_code == 200


def test_env_default_is_development(monkeypatch):
    """When APP_ENV is not set the value must be 'development'."""
    monkeypatch.delenv("APP_ENV", raising=False)
    response = client.get("/env")
    assert response.status_code == 200
    assert response.json()["environment"] == "development"


def test_env_uses_app_env_when_set(monkeypatch):
    """When APP_ENV is set its value is returned verbatim."""
    monkeypatch.setenv("APP_ENV", "production")
    response = client.get("/env")
    assert response.status_code == 200
    assert response.json()["environment"] == "production"


def test_env_arbitrary_value_returned_verbatim(monkeypatch):
    """Any string value of APP_ENV is echoed back."""
    monkeypatch.setenv("APP_ENV", "staging")
    response = client.get("/env")
    assert response.json()["environment"] == "staging"


# ===========================================================================
# AC3: GET /memory
# ===========================================================================

def test_memory_returns_200():
    response = client.get("/memory")
    assert response.status_code == 200


def test_memory_response_has_rss_mb_key():
    response = client.get("/memory")
    assert "rss_mb" in response.json()


def test_memory_rss_mb_is_positive():
    """rss_mb must be strictly greater than zero."""
    response = client.get("/memory")
    assert response.json()["rss_mb"] > 0


def test_memory_rss_mb_is_numeric():
    """rss_mb must be a numeric type (float or int)."""
    response = client.get("/memory")
    assert isinstance(response.json()["rss_mb"], (int, float))


def test_memory_rss_mb_is_reasonable():
    """rss_mb should be a sensible process memory value (< 10 GB)."""
    response = client.get("/memory")
    assert response.json()["rss_mb"] < 10_000


# ===========================================================================
# AC4 & AC5: GET /echo
# ===========================================================================

def test_echo_returns_200():
    response = client.get("/echo", params={"message": "hello"})
    assert response.status_code == 200


def test_echo_returns_message_key():
    response = client.get("/echo", params={"message": "hello"})
    assert "message" in response.json()


def test_echo_returns_exact_message():
    """AC4: the message value must equal the input exactly."""
    response = client.get("/echo", params={"message": "hello"})
    assert response.json()["message"] == "hello"


@pytest.mark.parametrize("msg", [
    "hello",
    "Hello, World!",
    "123 !@# special",
    " spaces around ",
    "unicode: café",
])
def test_echo_various_messages_returned_verbatim(msg):
    response = client.get("/echo", params={"message": msg})
    assert response.status_code == 200
    assert response.json()["message"] == msg


def test_echo_missing_message_returns_422():
    """AC5: missing required query param must yield 422."""
    response = client.get("/echo")
    assert response.status_code == 422


def test_echo_422_body_is_fastapi_validation_envelope():
    """422 body must follow FastAPI's validation-error shape."""
    response = client.get("/echo")
    data = response.json()
    assert "detail" in data


# ===========================================================================
# AC6: GET /timestamp
# ===========================================================================

def test_timestamp_returns_200():
    response = client.get("/timestamp")
    assert response.status_code == 200


def test_timestamp_response_has_timestamp_key():
    response = client.get("/timestamp")
    assert "timestamp" in response.json()


def test_timestamp_is_parseable_utc_iso8601():
    """AC6: timestamp must be a valid UTC ISO 8601 string.

    Accepts both 'Z' suffix and '+00:00' offset per the architecture contract.
    """
    response = client.get("/timestamp")
    raw = response.json()["timestamp"]
    # Normalise: replace trailing Z with +00:00 so fromisoformat handles both
    normalised = raw.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalised)
    assert parsed.tzinfo is not None
    assert parsed.utcoffset().total_seconds() == 0


def test_timestamp_is_recent():
    """The returned timestamp must fall between before/after bounds."""
    before = datetime.now(timezone.utc)
    response = client.get("/timestamp")
    after = datetime.now(timezone.utc)

    raw = response.json()["timestamp"]
    normalised = raw.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalised)

    # Strip tzinfo for comparison if parsed has utc offset already compared
    assert before <= parsed <= after


# ===========================================================================
# AC7: GET /random
# ===========================================================================

def test_random_returns_200():
    response = client.get("/random")
    assert response.status_code == 200


def test_random_response_has_number_key():
    response = client.get("/random")
    assert "number" in response.json()


def test_random_number_is_integer():
    """The number field must be an integer, not a float."""
    response = client.get("/random")
    assert isinstance(response.json()["number"], int)


@pytest.mark.parametrize("_attempt", range(5))
def test_random_number_in_range_1_to_1000_inclusive(_attempt):
    """AC7: number must be in [1, 1000] (sample multiple calls)."""
    response = client.get("/random")
    number = response.json()["number"]
    assert 1 <= number <= 1000


# ===========================================================================
# AC8 & AC9: GET /reverse
# ===========================================================================

def test_reverse_returns_200():
    response = client.get("/reverse", params={"text": "hello"})
    assert response.status_code == 200


def test_reverse_response_has_reversed_key():
    response = client.get("/reverse", params={"text": "hello"})
    assert "reversed" in response.json()


def test_reverse_hello_becomes_olleh():
    """AC8: 'hello' must reverse to 'olleh'."""
    response = client.get("/reverse", params={"text": "hello"})
    assert response.json()["reversed"] == "olleh"


@pytest.mark.parametrize("text, expected", [
    ("hello",       "olleh"),
    ("abcde",       "edcba"),
    ("a",           "a"),
    ("",            ""),
    ("racecar",     "racecar"),
    ("Hello World", "dlroW olleH"),
    ("12345",       "54321"),
])
def test_reverse_parametrized(text, expected):
    response = client.get("/reverse", params={"text": text})
    assert response.status_code == 200
    assert response.json()["reversed"] == expected


def test_reverse_missing_text_returns_422():
    """AC9: missing required query param must yield 422."""
    response = client.get("/reverse")
    assert response.status_code == 422


# ===========================================================================
# AC10 & AC11: GET /upper
# ===========================================================================

def test_upper_returns_200():
    response = client.get("/upper", params={"text": "hello"})
    assert response.status_code == 200


def test_upper_response_has_upper_key():
    response = client.get("/upper", params={"text": "hello"})
    assert "upper" in response.json()


def test_upper_hello_becomes_HELLO():
    """AC10: 'hello' must uppercase to 'HELLO'."""
    response = client.get("/upper", params={"text": "hello"})
    assert response.json()["upper"] == "HELLO"


@pytest.mark.parametrize("text, expected", [
    ("hello",         "HELLO"),
    ("Hello World",   "HELLO WORLD"),
    ("already UPPER", "ALREADY UPPER"),
    ("123abc",        "123ABC"),
    ("",              ""),
    ("café",          "CAFÉ"),
])
def test_upper_parametrized(text, expected):
    response = client.get("/upper", params={"text": text})
    assert response.status_code == 200
    assert response.json()["upper"] == expected


def test_upper_missing_text_returns_422():
    """AC11: missing required query param must yield 422."""
    response = client.get("/upper")
    assert response.status_code == 422


# ===========================================================================
# AC12 & AC13: GET /count
# ===========================================================================

def test_count_returns_200():
    response = client.get("/count", params={"text": "hello"})
    assert response.status_code == 200


def test_count_response_has_count_key():
    response = client.get("/count", params={"text": "hello"})
    assert "count" in response.json()


def test_count_hello_has_5_chars():
    """AC12: 'hello' must count to 5."""
    response = client.get("/count", params={"text": "hello"})
    assert response.json()["count"] == 5


def test_count_result_is_integer():
    response = client.get("/count", params={"text": "hello"})
    assert isinstance(response.json()["count"], int)


@pytest.mark.parametrize("text, expected_count", [
    ("hello",       5),
    ("a",           1),
    ("Hello World", 11),
    ("   ",         3),
    ("12345",       5),
    ("",            0),
])
def test_count_parametrized(text, expected_count):
    response = client.get("/count", params={"text": text})
    assert response.status_code == 200
    assert response.json()["count"] == expected_count


def test_count_missing_text_returns_422():
    """AC13: missing required query param must yield 422."""
    response = client.get("/count")
    assert response.status_code == 422


# ===========================================================================
# AC14, AC15, AC16, AC17: GET /palindrome
# ===========================================================================

def test_palindrome_returns_200():
    response = client.get("/palindrome", params={"text": "racecar"})
    assert response.status_code == 200


def test_palindrome_response_has_is_palindrome_key():
    response = client.get("/palindrome", params={"text": "racecar"})
    assert "is_palindrome" in response.json()


def test_palindrome_true_for_racecar():
    """AC14: 'racecar' is a palindrome."""
    response = client.get("/palindrome", params={"text": "racecar"})
    assert response.json()["is_palindrome"] is True


def test_palindrome_false_for_hello():
    """AC15: 'hello' is not a palindrome."""
    response = client.get("/palindrome", params={"text": "hello"})
    assert response.json()["is_palindrome"] is False


def test_palindrome_case_insensitive_with_spaces():
    """AC16: 'Race Car' (mixed case, space) must be recognised as a palindrome."""
    response = client.get("/palindrome", params={"text": "Race Car"})
    assert response.status_code == 200
    assert response.json()["is_palindrome"] is True


@pytest.mark.parametrize("text, expected", [
    # Basic palindromes
    ("racecar",       True),
    ("level",         True),
    ("noon",          True),
    ("madam",         True),
    # Basic non-palindromes
    ("hello",         False),
    ("python",        False),
    ("world",         False),
    # Case-insensitive (AC16)
    ("Race Car",      True),
    ("Madam",         True),
    ("AbBa",          True),
    # Space-insensitive
    ("race car",      True),
    ("a man a plan a canal Panama", True),
    # Edge cases
    ("a",             True),
    ("",              True),   # empty string is trivially a palindrome
])
def test_palindrome_parametrized(text, expected):
    response = client.get("/palindrome", params={"text": text})
    assert response.status_code == 200
    assert response.json()["is_palindrome"] is expected


def test_palindrome_missing_text_returns_422():
    """AC17: missing required query param must yield 422."""
    response = client.get("/palindrome")
    assert response.status_code == 422


# ===========================================================================
# AC18: All 10 endpoints return Content-Type: application/json
# ===========================================================================

@pytest.mark.parametrize("endpoint", _ENDPOINTS_NO_PARAMS)
def test_content_type_application_json_no_params(endpoint):
    """AC18: endpoints without required params must return application/json."""
    response = client.get(endpoint)
    ct = response.headers["content-type"]
    # Substring check — do NOT use equality; future FastAPI may add charset suffix
    assert "application/json" in ct


@pytest.mark.parametrize("endpoint,params", _ENDPOINTS_WITH_PARAMS)
def test_content_type_application_json_with_params(endpoint, params):
    """AC18: endpoints with required params must return application/json."""
    response = client.get(endpoint, params=params)
    ct = response.headers["content-type"]
    assert "application/json" in ct


# ===========================================================================
# AC19: None of the 10 endpoints require authentication
# ===========================================================================

@pytest.mark.parametrize("endpoint", _ENDPOINTS_NO_PARAMS)
def test_no_auth_required_no_params(endpoint):
    """AC19: must return 200 with no Authorization header."""
    response = client.get(endpoint)
    # Explicit: no headers= kwarg → no Authorization sent
    assert response.status_code == 200
    assert response.status_code not in (401, 403)


@pytest.mark.parametrize("endpoint,params", _ENDPOINTS_WITH_PARAMS)
def test_no_auth_required_with_params(endpoint, params):
    """AC19: must return 200 with no Authorization header."""
    response = client.get(endpoint, params=params)
    assert response.status_code == 200
    assert response.status_code not in (401, 403)
