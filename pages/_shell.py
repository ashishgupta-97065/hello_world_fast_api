"""Shared design-system shell for all Mini-App pages."""
from html import escape

BASE_STYLES: str = """
:root {
  --bg: #0f1117;
  --surface: #1a1d2e;
  --border: #2d3150;
  --text: #e8eaf6;
  --text-muted: #7986a3;
  --accent: #5c6bc0;
  --accent-hover: #7986cb;
  --success: #26a69a;
  --warning: #ffa726;
  --danger: #ef5350;
  --info: #42a5f5;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  min-height: 100vh;
}
a { color: var(--accent); text-decoration: none; }
a:hover { color: var(--accent-hover); text-decoration: underline; }

/* Top bar */
.top-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1.5rem;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}
.top-bar-link {
  color: var(--accent);
  font-size: 0.9rem;
  white-space: nowrap;
}
.top-bar-link:hover { color: var(--accent-hover); }
.top-bar-title {
  font-weight: 600;
  font-size: 1rem;
  color: var(--text);
}

/* Container */
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

/* Menu */
.menu-container {
  max-width: 960px;
  margin: 0 auto;
  padding: 3rem 1.5rem 2rem;
}
.menu-hero { text-align: center; margin-bottom: 2.5rem; }
.menu-hero h1 { font-size: 2.2rem; font-weight: 700; color: var(--text); margin-bottom: 0.5rem; }
.menu-hero p { color: var(--text-muted); font-size: 1.1rem; }
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.25rem;
}
.card {
  display: block;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  text-decoration: none;
  color: var(--text);
  transition: transform 0.15s ease, border-color 0.15s ease;
}
.card:hover {
  transform: translateY(-3px);
  border-color: var(--accent);
  text-decoration: none;
  color: var(--text);
}
.card-emoji { font-size: 2rem; margin-bottom: 0.75rem; }
.card-name { font-weight: 600; font-size: 1rem; margin-bottom: 0.35rem; }
.card-desc { font-size: 0.85rem; color: var(--text-muted); }
.menu-footer { text-align: center; margin-top: 3rem; color: var(--text-muted); font-size: 0.85rem; }

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.55rem 1.2rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  transition: background 0.15s ease, opacity 0.15s ease;
}
.btn:disabled { opacity: 0.45; cursor: not-allowed; }
.btn-primary { background: var(--accent); color: #fff; border-color: var(--accent); }
.btn-primary:hover:not(:disabled) { background: var(--accent-hover); }
.btn-secondary { background: var(--surface); color: var(--text); border-color: var(--border); }
.btn-secondary:hover:not(:disabled) { border-color: var(--accent); }
.btn-ghost { background: transparent; color: var(--accent); border-color: var(--accent); }
.btn-ghost:hover:not(:disabled) { background: rgba(92,107,192,0.12); }

/* Inputs */
input[type="text"], input[type="number"], input[type="range"], textarea, select {
  width: 100%;
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.55rem 0.85rem;
  font-size: 0.9rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.15s ease;
}
input[type="range"] { padding: 0; cursor: pointer; }
input:focus, textarea:focus, select:focus { border-color: var(--accent); }
textarea { resize: vertical; min-height: 120px; }

/* Badge */
.badge {
  display: inline-block;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
}
.badge-success { background: rgba(38,166,154,0.2); color: var(--success); }
.badge-warning { background: rgba(255,167,38,0.2); color: var(--warning); }
.badge-danger  { background: rgba(239,83,80,0.2);  color: var(--danger);  }
.badge-info    { background: rgba(66,165,245,0.2);  color: var(--info);    }

/* Validation */
.validation {
  color: var(--danger);
  font-size: 0.85rem;
  margin-top: 0.4rem;
  display: none;
}
.validation.visible { display: block; }

/* Utility */
.muted { color: var(--text-muted); }
.mono { font-family: 'Courier New', Courier, monospace; }

/* Tabs */
.tab-strip {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0;
}
.tab {
  padding: 0.5rem 1rem;
  border-radius: 8px 8px 0 0;
  cursor: pointer;
  font-size: 0.9rem;
  background: none;
  color: var(--text-muted);
  border: 1px solid transparent;
  border-bottom: none;
  margin-bottom: -1px;
}
.tab.active {
  color: var(--text);
  background: var(--surface);
  border-color: var(--border);
  border-bottom-color: var(--surface);
}
.tab:hover:not(.active) { color: var(--text); }
"""


def page(title: str, body_html: str, extra_css: str = "", extra_js: str = "") -> str:
    """Return a full HTML5 document for a /apps/<slug> page."""
    safe_title = escape(title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{safe_title} — Mini-Apps</title>
  <style>{BASE_STYLES}{extra_css}</style>
</head>
<body>
  <header class="top-bar">
    <a class="top-bar-link" href="/">← Back to Menu</a>
    <span class="top-bar-title">{safe_title}</span>
  </header>
  <main class="container">{body_html}</main>
  <script>(()=>{{ {extra_js} }})();</script>
</body>
</html>"""


def render_menu() -> str:
    """Return the home menu HTML5 document."""
    originals = [
        ("todo",          "✅", "Todo List",               "Manage tasks with add, complete, and delete"),
        ("pomodoro",      "⏱️", "Pomodoro Timer",          "25-min work sessions with 5-min breaks"),
        ("markdown",      "📝", "Markdown Previewer",      "Live two-column Markdown-to-HTML preview"),
        ("palette",       "🎨", "Color Palette Generator", "Generate five random hex colour swatches"),
        ("bmi",           "⚖️", "BMI Calculator",          "Calculate BMI from height and weight"),
        ("password",      "🔒", "Password Generator",      "Strong passwords with custom character sets"),
        ("word-counter",  "🔤", "Word Counter",            "Live word, character, and reading-time stats"),
        ("unit-converter","🔁", "Unit Converter",          "Convert length, weight, and temperature"),
        ("quote",         "💬", "Random Quote",            "Inspiring quotes from a curated collection"),
        ("dice",          "🎲", "Dice Roller",             "Roll D4–D20 with animated results"),
    ]
    batch3 = [
        ("finance",        "💰", "Personal Finance",  "Track income and expenses with category breakdown"),
        ("habits",         "✅", "Habit Tracker",     "7-day grid with streaks and completion %"),
        ("flashcards",     "🃏", "Flashcards",        "Build a deck and run a study session"),
        ("budget",         "📊", "Budget Planner",    "Per-category budgets with progress bars"),
        ("stopwatch",      "⏱️", "Stopwatch",         "Lap splits with best/worst markers"),
        ("json-formatter", "{ }", "JSON Formatter",   "Format, minify, validate, and copy JSON"),
        ("diff",           "🔀", "Text Diff",         "Line-by-line diff between two texts"),
        ("recipe",         "🍳", "Recipe Scaler",     "Scale ingredients and auto-convert units"),
        ("pomodoro-pro",   "🍅", "Pomodoro Pro",      "Modes, ring timer, session log, focus total"),
        ("kanban",         "📋", "Kanban Board",      "Drag cards across To Do / In Progress / Done"),
    ]

    def cards(apps):
        return "\n".join(
            f'<a class="card" href="/apps/{slug}">'
            f'<div class="card-emoji">{emoji}</div>'
            f'<div class="card-name">{name}</div>'
            f'<div class="card-desc">{desc}</div>'
            f'</a>'
            for slug, emoji, name, desc in apps
        )

    orig_html = cards(originals)
    batch3_html = cards(batch3)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Mini-Apps</title>
  <style>{BASE_STYLES}</style>
</head>
<body>
  <main class="menu-container">
    <div class="menu-hero">
      <h1>Mini-Apps</h1>
      <p>Twenty tiny tools, all in your browser.</p>
    </div>
    <section>
      <h2 style="font-size:1rem;color:var(--text-muted);margin-bottom:1rem">Originals</h2>
      <div class="card-grid">
{orig_html}
      </div>
    </section>
    <section style="margin-top:2rem">
      <h2 style="font-size:1rem;color:var(--text-muted);margin-bottom:1rem">Batch 3</h2>
      <div class="card-grid">
{batch3_html}
      </div>
    </section>
    <div class="menu-footer">20 apps &middot; no tracking &middot; runs entirely in your browser</div>
  </main>
</body>
</html>"""
