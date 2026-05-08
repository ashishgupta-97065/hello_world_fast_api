"""Word Counter mini-app page."""
from pages._shell import page

_EXTRA_CSS = """
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
  margin-top: 1.25rem;
}
.stat-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem;
  text-align: center;
}
.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--accent);
  display: block;
}
.stat-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
"""


def render_word_counter() -> str:
    """Return full HTML for /apps/word-counter."""
    body = """
<h1 style="margin-bottom:1.5rem">Word Counter</h1>
<textarea id="wc-input" placeholder="Type or paste your text here…" style="height:200px"></textarea>
<div class="stat-grid">
  <div class="stat-card">
    <span class="stat-value" id="stat-words">0</span>
    <span class="stat-label">Words</span>
  </div>
  <div class="stat-card">
    <span class="stat-value" id="stat-chars">0</span>
    <span class="stat-label">Characters</span>
  </div>
  <div class="stat-card">
    <span class="stat-value" id="stat-sentences">0</span>
    <span class="stat-label">Sentences</span>
  </div>
  <div class="stat-card">
    <span class="stat-value" id="stat-paragraphs">0</span>
    <span class="stat-label">Paragraphs</span>
  </div>
  <div class="stat-card">
    <span class="stat-value" id="stat-reading-time">0 min</span>
    <span class="stat-label">Reading Time</span>
  </div>
</div>
"""
    js = r"""
  const input = document.getElementById('wc-input');

  function update() {
    const text = input.value;

    const words = text.trim() ? text.trim().split(/\s+/).filter(Boolean).length : 0;
    const characters = text.length;
    const sentenceMatches = text.match(/[.!?]+/g);
    const sentences = sentenceMatches ? sentenceMatches.length : 0;
    const paragraphs = text.trim() ? text.trim().split(/\n{2,}/).filter(Boolean).length : 0;
    const readingTime = words === 0 ? '0 min' : Math.ceil(words / 200) + ' min';

    document.getElementById('stat-words').textContent      = words;
    document.getElementById('stat-chars').textContent      = characters;
    document.getElementById('stat-sentences').textContent  = sentences;
    document.getElementById('stat-paragraphs').textContent = paragraphs;
    document.getElementById('stat-reading-time').textContent = readingTime;
  }

  input.oninput = update;
  update();
"""
    return page("Word Counter", body, extra_css=_EXTRA_CSS, extra_js=js)
