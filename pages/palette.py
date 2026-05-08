"""Color Palette Generator mini-app page."""
from pages._shell import page

_EXTRA_CSS = """
.swatch-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1rem;
  margin-top: 1.5rem;
}
.swatch {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border);
}
.swatch-color {
  height: 120px;
  width: 100%;
}
.swatch-footer {
  background: var(--surface);
  padding: 0.5rem;
  text-align: center;
}
.swatch-hex {
  font-family: monospace;
  font-size: 0.85rem;
  color: var(--text);
  display: block;
  margin-bottom: 0.35rem;
}
.copy-btn {
  width: 100%;
  font-size: 0.78rem;
  padding: 0.3rem 0.5rem;
}
"""


def render_palette() -> str:
    """Return full HTML for /apps/palette."""
    body = """
<h1 style="margin-bottom:1.5rem">Color Palette Generator</h1>
<button class="btn btn-primary" id="generate-btn">Generate</button>
<div class="swatch-grid" id="swatch-grid"></div>
"""
    js = r"""
  const grid = document.getElementById('swatch-grid');

  function randomHex() {
    const r = Math.floor(Math.random() * 256);
    const g = Math.floor(Math.random() * 256);
    const b = Math.floor(Math.random() * 256);
    return '#' + [r, g, b].map(v => v.toString(16).padStart(2, '0')).join('').toUpperCase();
  }

  function copyToClipboard(text, btn) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).catch(() => fallbackCopy(text, btn));
    } else {
      fallbackCopy(text, btn);
    }
    btn.textContent = 'Copied!';
    setTimeout(() => { btn.textContent = 'Copy'; }, 1500);
  }

  function fallbackCopy(text, btn) {
    try {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.cssText = 'position:fixed;opacity:0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    } catch (e) {
      console.warn('Copy failed', e);
    }
  }

  function generate() {
    grid.innerHTML = '';
    for (let i = 0; i < 5; i++) {
      const hex = randomHex();
      const swatch = document.createElement('div');
      swatch.className = 'swatch';
      const colorDiv = document.createElement('div');
      colorDiv.className = 'swatch-color';
      colorDiv.style.backgroundColor = hex;
      const footer = document.createElement('div');
      footer.className = 'swatch-footer';
      const hexSpan = document.createElement('span');
      hexSpan.className = 'swatch-hex';
      hexSpan.textContent = hex;
      const copyBtn = document.createElement('button');
      copyBtn.className = 'btn btn-secondary copy-btn';
      copyBtn.textContent = 'Copy';
      copyBtn.onclick = () => copyToClipboard(hex, copyBtn);
      footer.appendChild(hexSpan);
      footer.appendChild(copyBtn);
      swatch.appendChild(colorDiv);
      swatch.appendChild(footer);
      grid.appendChild(swatch);
    }
  }

  document.getElementById('generate-btn').onclick = generate;
  generate();
"""
    return page("Color Palette Generator", body, extra_css=_EXTRA_CSS, extra_js=js)
