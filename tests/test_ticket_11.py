"""
Tests for Ticket #11: Mini-Apps Menu and 10 Self-Contained One-Page Applications

Covers AC1–AC18 as defined in specs.md. All tests use the FastAPI TestClient
and operate at the HTTP response level (status codes, headers, HTML content).
App-specific JS behaviour (AC7–AC16) is verified by inspecting the HTML/JS
payload for required structural elements and JS logic — browser execution is
out of scope for a server-side test suite.
"""
import re
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

APP_ROUTES = [
    "/apps/todo",
    "/apps/pomodoro",
    "/apps/markdown",
    "/apps/palette",
    "/apps/bmi",
    "/apps/password",
    "/apps/word-counter",
    "/apps/unit-converter",
    "/apps/quote",
    "/apps/dice",
]

APP_NAMES = [
    "Todo List",
    "Pomodoro Timer",
    "Markdown Previewer",
    "Color Palette Generator",
    "BMI Calculator",
    "Password Generator",
    "Word Counter",
    "Unit Converter",
    "Random Quote",
    "Dice Roller",
]

ALL_ROUTES = ["/"] + APP_ROUTES


# ---------------------------------------------------------------------------
# AC1 — GET / returns 200 text/html with links to all 10 mini-app routes
# ---------------------------------------------------------------------------

class TestAC1MenuRoute:
    def test_root_returns_200(self):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_root_content_type_is_html(self):
        resp = client.get("/")
        assert resp.headers["content-type"].startswith("text/html"), (
            f"Expected text/html, got: {resp.headers['content-type']}"
        )

    @pytest.mark.parametrize("route", APP_ROUTES)
    def test_root_contains_link_to_each_app(self, route):
        body = client.get("/").text
        # Accept href with double or single quotes
        assert f'href="{route}"' in body or f"href='{route}'" in body, (
            f"Menu page missing link to {route}"
        )


# ---------------------------------------------------------------------------
# AC2 — Root menu page contains visible link text for each app
# ---------------------------------------------------------------------------

class TestAC2AppNames:
    @pytest.mark.parametrize("name", APP_NAMES)
    def test_menu_contains_app_name(self, name):
        resp = client.get("/")
        assert name in resp.text, f"Menu page missing app name: '{name}'"


# ---------------------------------------------------------------------------
# AC3 — Each /apps/* route returns 200 with Content-Type text/html
# ---------------------------------------------------------------------------

class TestAC3AppRoutes:
    @pytest.mark.parametrize("route", APP_ROUTES)
    def test_app_route_returns_200(self, route):
        resp = client.get(route)
        assert resp.status_code == 200, (
            f"{route} returned {resp.status_code}"
        )

    @pytest.mark.parametrize("route", APP_ROUTES)
    def test_app_route_content_type_is_html(self, route):
        resp = client.get(route)
        ct = resp.headers["content-type"]
        assert ct.startswith("text/html"), (
            f"{route} content-type: {ct}"
        )


# ---------------------------------------------------------------------------
# AC4 — Each app page contains <a href="/"> with "Home" or "Back to Menu" text
# ---------------------------------------------------------------------------

class TestAC4BackLink:
    @pytest.mark.parametrize("route", APP_ROUTES)
    def test_app_page_has_root_href_link(self, route):
        body = client.get(route).text
        assert 'href="/"' in body or "href='/'" in body, (
            f"{route}: no element with href='/' found"
        )

    @pytest.mark.parametrize("route", APP_ROUTES)
    def test_app_page_back_link_has_home_or_menu_text(self, route):
        body = client.get(route).text
        # Find anchor elements with href="/" and check their text content
        anchors = re.findall(
            r'<a[^>]*href=["\'][/]["\'][^>]*>(.*?)</a>',
            body,
            re.IGNORECASE | re.DOTALL,
        )
        has_nav_text = any(
            re.search(r'home|menu|back', a, re.IGNORECASE)
            for a in anchors
        )
        assert has_nav_text, (
            f"{route}: <a href='/'> exists but contains neither 'Home', 'Menu', nor 'Back'"
        )


# ---------------------------------------------------------------------------
# AC5 — No external CDN dependencies on any page
# ---------------------------------------------------------------------------

class TestAC5NoCDN:
    @pytest.mark.parametrize("route", ALL_ROUTES)
    def test_no_external_script_src(self, route):
        body = client.get(route).text
        matches = re.findall(r'<script[^>]+src=["\']https?://', body, re.IGNORECASE)
        assert not matches, (
            f"{route}: found external <script src>: {matches}"
        )

    @pytest.mark.parametrize("route", ALL_ROUTES)
    def test_no_external_stylesheet_link(self, route):
        body = client.get(route).text
        # Attribute order may vary
        matches = re.findall(
            r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']https?://',
            body, re.IGNORECASE
        )
        matches2 = re.findall(
            r'<link[^>]+href=["\']https?://[^"\']+["\'][^>]+rel=["\']stylesheet["\']',
            body, re.IGNORECASE
        )
        assert not matches + matches2, (
            f"{route}: found external <link rel=stylesheet>"
        )

    @pytest.mark.parametrize("route", ALL_ROUTES)
    def test_no_external_img_src(self, route):
        body = client.get(route).text
        matches = re.findall(r'<img[^>]+src=["\']https?://', body, re.IGNORECASE)
        assert not matches, (
            f"{route}: found external <img src>: {matches}"
        )


# ---------------------------------------------------------------------------
# AC6 — All existing JSON endpoints are preserved unchanged
# ---------------------------------------------------------------------------

class TestAC6ExistingJSONEndpoints:
    def test_health_returns_ok(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("application/json")
        assert resp.json() == {"status": "ok"}

    def test_ping_no_msg(self):
        resp = client.get("/ping")
        assert resp.status_code == 200
        assert resp.json()["message"] == "pong"
        assert "msg" not in resp.json()

    def test_ping_with_msg(self):
        resp = client.get("/ping?msg=hi")
        assert resp.status_code == 200
        data = resp.json()
        assert data["message"] == "pong"
        assert data["msg"] == "hi"

    def test_version_shape(self):
        resp = client.get("/version")
        assert resp.status_code == 200
        data = resp.json()
        assert "version" in data
        assert "uptime" in data
        assert isinstance(data["uptime"], int)
        assert isinstance(data["version"], str)

    def test_stats_returns_dict(self):
        resp = client.get("/stats")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("application/json")
        assert isinstance(resp.json(), dict)

    def test_reset_returns_reset_true(self):
        resp = client.post("/reset")
        assert resp.status_code == 200
        assert resp.json() == {"reset": True}

    def test_hostname_shape(self):
        resp = client.get("/hostname")
        assert resp.status_code == 200
        data = resp.json()
        assert "hostname" in data
        assert isinstance(data["hostname"], str)

    def test_env_shape(self):
        resp = client.get("/env")
        assert resp.status_code == 200
        data = resp.json()
        assert "environment" in data
        assert isinstance(data["environment"], str)

    def test_memory_shape(self):
        resp = client.get("/memory")
        assert resp.status_code == 200
        data = resp.json()
        assert "rss_mb" in data
        assert isinstance(data["rss_mb"], (int, float))

    def test_echo_returns_message(self):
        resp = client.get("/echo?message=testval")
        assert resp.status_code == 200
        assert resp.json() == {"message": "testval"}

    def test_timestamp_is_parseable_iso(self):
        resp = client.get("/timestamp")
        assert resp.status_code == 200
        ts = resp.json()["timestamp"]
        # Must parse as ISO datetime
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        assert dt is not None

    def test_random_in_range(self):
        resp = client.get("/random")
        assert resp.status_code == 200
        n = resp.json()["number"]
        assert 1 <= n <= 1000

    def test_reverse_reverses_text(self):
        resp = client.get("/reverse?text=hello")
        assert resp.status_code == 200
        assert resp.json() == {"reversed": "olleh"}

    def test_upper_uppercases(self):
        resp = client.get("/upper?text=hello")
        assert resp.status_code == 200
        assert resp.json() == {"upper": "HELLO"}

    def test_count_returns_length(self):
        resp = client.get("/count?text=hello")
        assert resp.status_code == 200
        assert resp.json() == {"count": 5}

    def test_palindrome_true(self):
        resp = client.get("/palindrome?text=racecar")
        assert resp.status_code == 200
        assert resp.json() == {"is_palindrome": True}

    def test_palindrome_false(self):
        resp = client.get("/palindrome?text=hello")
        assert resp.status_code == 200
        assert resp.json() == {"is_palindrome": False}

    def test_palindrome_with_spaces(self):
        resp = client.get("/palindrome?text=race car")
        assert resp.status_code == 200
        assert resp.json()["is_palindrome"] is True

    @pytest.mark.parametrize("path", [
        "/health", "/ping", "/version", "/stats", "/hostname",
        "/env", "/memory", "/echo?message=x", "/timestamp",
        "/random", "/reverse?text=a", "/upper?text=a",
        "/count?text=a", "/palindrome?text=a",
    ])
    def test_existing_endpoints_return_json_content_type(self, path):
        resp = client.get(path)
        assert resp.headers["content-type"].startswith("application/json"), (
            f"{path}: expected application/json, got {resp.headers['content-type']}"
        )


# ---------------------------------------------------------------------------
# AC7 — Todo List: input, Add, complete, delete controls present in HTML/JS
# ---------------------------------------------------------------------------

class TestAC7Todo:
    def setup_method(self):
        self.body = client.get("/apps/todo").text

    def test_has_text_input(self):
        # Must have an input for entering tasks
        assert "<input" in self.body, "Todo: missing <input> element"

    def test_has_add_button_or_text(self):
        assert re.search(r'\bAdd\b', self.body, re.IGNORECASE), (
            "Todo: missing 'Add' button/label text"
        )

    def test_has_delete_capability_in_js(self):
        assert re.search(r'delete|remove', self.body, re.IGNORECASE), (
            "Todo: missing delete/remove functionality"
        )

    def test_has_complete_or_toggle_in_js(self):
        assert re.search(r'complete|toggle|checked|strike|done', self.body, re.IGNORECASE), (
            "Todo: missing complete/toggle functionality"
        )

    def test_has_task_list_structure(self):
        # ul/li structure for task list
        assert re.search(r'<ul|<ol|<li', self.body, re.IGNORECASE), (
            "Todo: missing list structure (ul/ol/li)"
        )

    def test_enter_key_handling(self):
        # AC7: "press Enter" should add the task — JS must handle Enter/keydown/keypress
        assert re.search(r'Enter|keydown|keypress|keyCode|key\b', self.body, re.IGNORECASE), (
            "Todo: missing Enter key handling for task submission"
        )


# ---------------------------------------------------------------------------
# AC8 — Pomodoro Timer: 25:00 display, Start/Pause/Reset, break logic, setInterval
# ---------------------------------------------------------------------------

class TestAC8Pomodoro:
    def setup_method(self):
        self.body = client.get("/apps/pomodoro").text

    def test_shows_25_00_display(self):
        assert "25:00" in self.body, "Pomodoro: missing initial '25:00' display"

    def test_has_start_control(self):
        assert re.search(r'\bStart\b', self.body, re.IGNORECASE), (
            "Pomodoro: missing 'Start' control"
        )

    def test_has_pause_control(self):
        assert re.search(r'\bPause\b', self.body, re.IGNORECASE), (
            "Pomodoro: missing 'Pause' control"
        )

    def test_has_reset_control(self):
        assert re.search(r'\bReset\b', self.body, re.IGNORECASE), (
            "Pomodoro: missing 'Reset' control"
        )

    def test_has_break_timer_in_js(self):
        # 5-minute break: JS should reference 5:00 or 300 seconds
        assert re.search(r'5:00|300\b|break', self.body, re.IGNORECASE), (
            "Pomodoro: missing break timer logic (5-min / 300s)"
        )

    def test_has_setinterval(self):
        assert "setInterval" in self.body, (
            "Pomodoro: missing setInterval for per-second countdown"
        )

    def test_has_clearinterval(self):
        assert "clearInterval" in self.body, (
            "Pomodoro: missing clearInterval (needed for pause/reset)"
        )


# ---------------------------------------------------------------------------
# AC9 — Markdown Previewer: textarea + preview, subset parser in JS
# ---------------------------------------------------------------------------

class TestAC9Markdown:
    def setup_method(self):
        self.body = client.get("/apps/markdown").text

    def test_has_textarea(self):
        assert "<textarea" in self.body, "Markdown: missing <textarea>"

    def test_has_preview_area(self):
        assert re.search(r'preview|output', self.body, re.IGNORECASE), (
            "Markdown: missing preview/output area"
        )

    def test_live_update_on_input(self):
        assert "oninput" in self.body or "addEventListener" in self.body, (
            "Markdown: missing oninput or addEventListener for live preview"
        )

    def test_js_handles_h1_heading(self):
        # Parser replaces # ... with <h1>
        assert re.search(r'h1|<h1', self.body, re.IGNORECASE), (
            "Markdown JS: missing H1 heading support"
        )

    def test_js_handles_h2_heading(self):
        assert re.search(r'h2|<h2', self.body, re.IGNORECASE), (
            "Markdown JS: missing H2 heading support"
        )

    def test_js_handles_h3_heading(self):
        assert re.search(r'h3|<h3', self.body, re.IGNORECASE), (
            "Markdown JS: missing H3 heading support"
        )

    def test_js_handles_bold(self):
        # **text** -> <strong>
        assert re.search(r'strong|bold|\*\*', self.body, re.IGNORECASE), (
            "Markdown JS: missing bold (**text**) support"
        )

    def test_js_handles_italic(self):
        # *text* -> <em>
        assert re.search(r'<em>|italic|\bem\b', self.body, re.IGNORECASE), (
            "Markdown JS: missing italic (*text*) support"
        )

    def test_js_handles_inline_code(self):
        assert re.search(r'<code>|inline.{0,10}code|`', self.body, re.IGNORECASE), (
            "Markdown JS: missing inline code (`code`) support"
        )

    def test_js_handles_links(self):
        # [label](url) -> <a href="url">
        assert re.search(r'<a\b|href', self.body, re.IGNORECASE), (
            "Markdown JS: missing link ([label](url)) support"
        )

    def test_js_handles_unordered_list(self):
        # - item -> <li>/<ul>
        assert re.search(r'<ul|<li', self.body, re.IGNORECASE), (
            "Markdown JS: missing unordered list (- item) support"
        )


# ---------------------------------------------------------------------------
# AC10 — Color Palette Generator: Generate button, 5 swatches, Copy + clipboard
# ---------------------------------------------------------------------------

class TestAC10Palette:
    def setup_method(self):
        self.body = client.get("/apps/palette").text

    def test_has_generate_button(self):
        assert re.search(r'\bGenerate\b', self.body, re.IGNORECASE), (
            "Palette: missing 'Generate' button"
        )

    def test_generates_exactly_5_swatches(self):
        # JS should iterate 5 times or reference the number 5 for color count
        assert re.search(r'\b5\b', self.body), (
            "Palette: missing reference to 5 (swatch count)"
        )

    def test_generates_hex_rrggbb_format(self):
        # JS generates #RRGGBB — look for hex generation logic
        assert re.search(r'RRGGBB|[0-9A-Fa-f]{6}|toString\s*\(\s*16\s*\)|toUpperCase', self.body), (
            "Palette: missing #RRGGBB hex generation logic"
        )

    def test_has_copy_control(self):
        assert re.search(r'\bCopy\b', self.body, re.IGNORECASE), (
            "Palette: missing 'Copy' control"
        )

    def test_uses_clipboard_api(self):
        assert "clipboard" in self.body, (
            "Palette: missing navigator.clipboard usage"
        )

    def test_has_copied_feedback(self):
        # Visible feedback after copy: text changes to "Copied!" etc.
        assert re.search(r'Copied', self.body, re.IGNORECASE), (
            "Palette: missing 'Copied' feedback text"
        )


# ---------------------------------------------------------------------------
# AC11 — BMI Calculator: height/weight inputs, correct thresholds and categories
# ---------------------------------------------------------------------------

class TestAC11BMI:
    def setup_method(self):
        self.body = client.get("/apps/bmi").text

    def test_has_height_input(self):
        assert re.search(r'height', self.body, re.IGNORECASE), (
            "BMI: missing height input/label"
        )

    def test_has_weight_input(self):
        assert re.search(r'weight', self.body, re.IGNORECASE), (
            "BMI: missing weight input/label"
        )

    def test_shows_underweight_category(self):
        assert "Underweight" in self.body, "BMI: missing 'Underweight' category"

    def test_shows_normal_category(self):
        assert "Normal" in self.body, "BMI: missing 'Normal' category"

    def test_shows_overweight_category(self):
        assert "Overweight" in self.body, "BMI: missing 'Overweight' category"

    def test_shows_obese_category(self):
        assert "Obese" in self.body, "BMI: missing 'Obese' category"

    def test_threshold_18_5_present(self):
        assert "18.5" in self.body, "BMI: missing threshold 18.5"

    def test_threshold_25_present(self):
        assert "25" in self.body, "BMI: missing threshold 25"

    def test_threshold_30_present(self):
        assert "30" in self.body, "BMI: missing threshold 30"

    def test_bmi_formula_divides_by_height_squared(self):
        # weight / (height/100)^2 — look for /100 or height_m or similar
        assert re.search(r'/\s*100|\*\s*100|height_m|toFixed\s*\(\s*1', self.body, re.IGNORECASE), (
            "BMI: missing height->meters conversion or formula"
        )

    def test_has_validation_message_slot(self):
        assert re.search(r'valid|error|invalid|non.positive|non.numeric', self.body, re.IGNORECASE), (
            "BMI: missing validation message for invalid input"
        )

    def test_result_rounded_to_1_decimal(self):
        assert re.search(r'toFixed\s*\(\s*1\s*\)', self.body), (
            "BMI: result not rounded to 1 decimal (toFixed(1))"
        )


# ---------------------------------------------------------------------------
# AC12 — Password Generator: length 8–64, 4 char classes, validation, copy
# ---------------------------------------------------------------------------

class TestAC12Password:
    def setup_method(self):
        self.body = client.get("/apps/password").text

    def test_has_length_control_with_range(self):
        # Length 8 to 64
        assert re.search(r'\b8\b', self.body) and re.search(r'\b64\b', self.body), (
            "Password: missing length range 8–64"
        )

    def test_has_uppercase_toggle(self):
        assert re.search(r'uppercase|upper', self.body, re.IGNORECASE), (
            "Password: missing uppercase character class toggle"
        )

    def test_has_lowercase_toggle(self):
        assert re.search(r'lowercase|lower', self.body, re.IGNORECASE), (
            "Password: missing lowercase character class toggle"
        )

    def test_has_numbers_toggle(self):
        assert re.search(r'number|digit', self.body, re.IGNORECASE), (
            "Password: missing numbers character class toggle"
        )

    def test_has_symbols_toggle(self):
        assert re.search(r'symbol', self.body, re.IGNORECASE), (
            "Password: missing symbols character class toggle"
        )

    def test_symbol_set_documented_on_page(self):
        # At least some symbols from the required set must appear in the page text
        assert re.search(r'[!@#$%^&*()\-_=+\[\]{};:,\.?/]', self.body), (
            "Password: missing documented symbol set on page"
        )

    def test_has_generate_button(self):
        assert re.search(r'\bGenerate\b', self.body, re.IGNORECASE), (
            "Password: missing 'Generate' button"
        )

    def test_has_validation_for_no_class(self):
        assert re.search(r'valid|error|select|at least|one class', self.body, re.IGNORECASE), (
            "Password: missing validation message for no character class selected"
        )

    def test_has_copy_control(self):
        assert re.search(r'\bCopy\b', self.body, re.IGNORECASE), (
            "Password: missing 'Copy' control"
        )

    def test_uses_clipboard(self):
        assert "clipboard" in self.body, (
            "Password: missing navigator.clipboard usage"
        )

    def test_has_copied_feedback(self):
        assert re.search(r'Copied', self.body, re.IGNORECASE), (
            "Password: missing 'Copied' feedback text"
        )


# ---------------------------------------------------------------------------
# AC13 — Word Counter: textarea + 5 live stats updating without page reload
# ---------------------------------------------------------------------------

class TestAC13WordCounter:
    def setup_method(self):
        self.body = client.get("/apps/word-counter").text

    def test_has_textarea(self):
        assert "<textarea" in self.body, "Word Counter: missing <textarea>"

    def test_has_words_stat(self):
        assert re.search(r'\bwords?\b', self.body, re.IGNORECASE), (
            "Word Counter: missing words stat"
        )

    def test_has_characters_stat(self):
        assert re.search(r'characters?|chars?', self.body, re.IGNORECASE), (
            "Word Counter: missing characters stat"
        )

    def test_has_sentences_stat(self):
        assert re.search(r'sentences?', self.body, re.IGNORECASE), (
            "Word Counter: missing sentences stat"
        )

    def test_has_paragraphs_stat(self):
        assert re.search(r'paragraphs?', self.body, re.IGNORECASE), (
            "Word Counter: missing paragraphs stat"
        )

    def test_has_reading_time_stat(self):
        assert re.search(r'reading.{0,5}time|read.*min|min.*read', self.body, re.IGNORECASE), (
            "Word Counter: missing reading time stat"
        )

    def test_reading_time_uses_200_wpm(self):
        assert re.search(r'\b200\b', self.body), (
            "Word Counter: missing 200 WPM constant for reading time calculation"
        )

    def test_reading_time_uses_ceil(self):
        assert re.search(r'ceil|Math\.ceil', self.body, re.IGNORECASE), (
            "Word Counter: reading time should use Math.ceil"
        )

    def test_live_update_on_input(self):
        assert "oninput" in self.body or "addEventListener" in self.body, (
            "Word Counter: missing oninput/addEventListener for live updates"
        )


# ---------------------------------------------------------------------------
# AC14 — Unit Converter: 3 tabs, Length/Weight/Temperature units, tab switching
# ---------------------------------------------------------------------------

class TestAC14UnitConverter:
    def setup_method(self):
        self.body = client.get("/apps/unit-converter").text

    def test_has_length_tab(self):
        assert re.search(r'\bLength\b', self.body, re.IGNORECASE), (
            "Unit Converter: missing 'Length' tab"
        )

    def test_has_weight_tab(self):
        assert re.search(r'\bWeight\b', self.body, re.IGNORECASE), (
            "Unit Converter: missing 'Weight' tab"
        )

    def test_has_temperature_tab(self):
        assert re.search(r'\bTemperature\b', self.body, re.IGNORECASE), (
            "Unit Converter: missing 'Temperature' tab"
        )

    @pytest.mark.parametrize("unit", ["meters", "kilometers", "miles", "feet"])
    def test_length_units_present(self, unit):
        assert re.search(unit, self.body, re.IGNORECASE), (
            f"Unit Converter: missing length unit '{unit}'"
        )

    @pytest.mark.parametrize("unit", ["kilograms", "pounds", "grams", "ounces"])
    def test_weight_units_present(self, unit):
        assert re.search(unit, self.body, re.IGNORECASE), (
            f"Unit Converter: missing weight unit '{unit}'"
        )

    @pytest.mark.parametrize("unit", ["Celsius", "Fahrenheit", "Kelvin"])
    def test_temperature_units_present(self, unit):
        assert re.search(unit, self.body, re.IGNORECASE), (
            f"Unit Converter: missing temperature unit '{unit}'"
        )

    def test_tab_switching_js(self):
        # Tab switching changes visible form without page reload
        assert re.search(r'display|block|none|tab', self.body, re.IGNORECASE), (
            "Unit Converter: missing tab switching JS (display/block/none)"
        )

    def test_result_rounded_to_4_decimals(self):
        assert re.search(r'toFixed\s*\(\s*4\s*\)', self.body), (
            "Unit Converter: missing toFixed(4) for 4-decimal rounding"
        )


# ---------------------------------------------------------------------------
# AC15 — Random Quote: ≥20 quotes (hardcoded array), author, Next button
# ---------------------------------------------------------------------------

class TestAC15Quote:
    def setup_method(self):
        self.body = client.get("/apps/quote").text

    def test_has_next_button(self):
        assert re.search(r'\bNext\b', self.body, re.IGNORECASE), (
            "Quote: missing 'Next' button"
        )

    def test_has_at_least_20_text_fields(self):
        # Each quote object has a `text` field — count occurrences
        count = len(re.findall(r'"text"\s*:', self.body))
        assert count >= 20, (
            f"Quote: found only {count} 'text' fields in JS array (need ≥20)"
        )

    def test_has_at_least_20_author_fields(self):
        count = len(re.findall(r'"author"\s*:', self.body))
        assert count >= 20, (
            f"Quote: found only {count} 'author' fields in JS array (need ≥20)"
        )

    def test_has_js_array_of_quote_objects(self):
        # Inline JS array containing objects with text+author
        assert re.search(r'\[\s*\{', self.body), (
            "Quote: missing JS array of quote objects"
        )

    def test_has_author_display_element(self):
        assert re.search(r'author', self.body, re.IGNORECASE), (
            "Quote: missing author display"
        )


# ---------------------------------------------------------------------------
# AC16 — Dice Roller: D4–D20 types, count 1–6, Roll button, animation JS
# ---------------------------------------------------------------------------

class TestAC16Dice:
    def setup_method(self):
        self.body = client.get("/apps/dice").text

    @pytest.mark.parametrize("die", ["D4", "D6", "D8", "D10", "D12", "D20"])
    def test_all_die_types_present(self, die):
        assert re.search(die, self.body, re.IGNORECASE), (
            f"Dice: missing die type '{die}'"
        )

    def test_has_count_selector_1_to_6(self):
        # Count selector: values 1..6 should be selectable
        assert re.search(r'count|quantity|number.*die|die.*number|\bcount\b', self.body, re.IGNORECASE), (
            "Dice: missing count selector"
        )
        # Values 1 and 6 should be present for the count range
        assert re.search(r'\b1\b', self.body) and re.search(r'\b6\b', self.body), (
            "Dice: count range 1–6 not found"
        )

    def test_has_roll_button(self):
        assert re.search(r'\bRoll\b', self.body, re.IGNORECASE), (
            "Dice: missing 'Roll' button"
        )

    def test_has_animation_mechanism(self):
        # Animation: setInterval for flicker (≥300ms) or CSS animation/transition
        has_interval = "setInterval" in self.body
        has_css_anim = re.search(r'animation|transition|transform', self.body, re.IGNORECASE)
        assert has_interval or has_css_anim, (
            "Dice: missing animation (setInterval, CSS animation/transition)"
        )

    def test_animation_lasts_at_least_300ms(self):
        # Architecture specifies 400ms flicker; look for ≥300 in JS context
        ms_values = re.findall(r'\b(\d+)\b', self.body)
        durations = [int(v) for v in ms_values if int(v) >= 300 and int(v) <= 5000]
        assert durations, (
            "Dice: missing an animation duration value ≥300ms in JS"
        )

    def test_results_display_area(self):
        assert re.search(r'result|roll|total', self.body, re.IGNORECASE), (
            "Dice: missing results display area"
        )


# ---------------------------------------------------------------------------
# AC17 — All pages are valid HTML5 documents
# ---------------------------------------------------------------------------

class TestAC17ValidHTML5:
    @pytest.mark.parametrize("route", ALL_ROUTES)
    def test_starts_with_doctype_html(self, route):
        body = client.get(route).text.strip()
        assert body.lower().startswith("<!doctype html>"), (
            f"{route}: does not start with <!DOCTYPE html>"
        )

    @pytest.mark.parametrize("route", ALL_ROUTES)
    def test_contains_html_element(self, route):
        body = client.get(route).text
        assert re.search(r'<html[\s>]', body, re.IGNORECASE), (
            f"{route}: missing <html> element"
        )

    @pytest.mark.parametrize("route", ALL_ROUTES)
    def test_contains_head_element(self, route):
        body = client.get(route).text
        assert re.search(r'<head[\s>]', body, re.IGNORECASE), (
            f"{route}: missing <head> element"
        )

    @pytest.mark.parametrize("route", ALL_ROUTES)
    def test_contains_body_element(self, route):
        body = client.get(route).text
        assert re.search(r'<body[\s>]', body, re.IGNORECASE), (
            f"{route}: missing <body> element"
        )

    @pytest.mark.parametrize("route", ALL_ROUTES)
    def test_has_charset_meta(self, route):
        body = client.get(route).text
        assert re.search(r'charset\s*=\s*["\']?utf-8', body, re.IGNORECASE), (
            f"{route}: missing charset=utf-8 meta tag"
        )


# ---------------------------------------------------------------------------
# AC18 — No mini-app calls a backend endpoint added by this ticket
# ---------------------------------------------------------------------------

class TestAC18NoBackendCallsFromApps:
    @pytest.mark.parametrize("route", APP_ROUTES)
    def test_no_fetch_to_apps_routes(self, route):
        body = client.get(route).text
        # fetch() calls must not reference /apps/* backend paths
        matches = re.findall(r'fetch\s*\(\s*["\'][^"\']*\/apps\/', body, re.IGNORECASE)
        assert not matches, (
            f"{route}: found fetch() to /apps/ backend route: {matches}"
        )

    @pytest.mark.parametrize("route", APP_ROUTES)
    def test_no_xhr_open_to_apps_routes(self, route):
        body = client.get(route).text
        matches = re.findall(r'\.open\s*\([^)]*\/apps\/', body, re.IGNORECASE)
        assert not matches, (
            f"{route}: found XHR.open() to /apps/ route: {matches}"
        )

    def test_menu_page_is_static_html(self):
        # Menu page has no inline JS that POSTs/GETs any route
        body = client.get("/").text
        # It's acceptable (even expected) to have no fetch at all on the static menu
        # What must NOT happen: fetch("/apps/...")
        matches = re.findall(r'fetch\s*\(\s*["\'][^"\']*\/apps\/', body, re.IGNORECASE)
        assert not matches, f"Menu page: unexpected fetch() to /apps/ route"


# ---------------------------------------------------------------------------
# Extra: HTTP method constraints on new routes
# ---------------------------------------------------------------------------

class TestHTTPMethodConstraints:
    @pytest.mark.parametrize("route", APP_ROUTES)
    def test_post_to_app_routes_is_405(self, route):
        resp = client.post(route)
        assert resp.status_code == 405, (
            f"POST {route} returned {resp.status_code}, expected 405"
        )

    def test_unknown_app_slug_returns_404(self):
        resp = client.get("/apps/this-app-does-not-exist-xyz")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Extra: Root no longer returns JSON (contract changed per AC1 / architecture)
# ---------------------------------------------------------------------------

class TestRootContractChange:
    def test_root_no_longer_returns_json_message(self):
        resp = client.get("/")
        # The old contract was {"message": "Hello, World!"}; this ticket changes it to HTML
        ct = resp.headers["content-type"]
        assert not ct.startswith("application/json"), (
            f"GET / still returns application/json — expected text/html after ticket #11"
        )

    def test_root_body_is_html_not_hello_world_json(self):
        resp = client.get("/")
        # Body should be HTML, not the old JSON
        assert '{"message": "Hello, World!"}' not in resp.text, (
            "GET / still returns old JSON body"
        )
