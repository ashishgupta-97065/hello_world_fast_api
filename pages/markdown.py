"""Markdown Previewer mini-app page."""
from pages._shell import page

_EXTRA_CSS = """
.md-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  height: calc(100vh - 120px);
  min-height: 400px;
}
.md-pane { display: flex; flex-direction: column; gap: 0.5rem; }
.md-label { font-size: 0.8rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
#md-input  { flex: 1; resize: none; font-family: monospace; }
#md-preview {
  flex: 1;
  overflow-y: auto;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.85rem;
  line-height: 1.7;
}
#md-preview h1 { font-size:1.6rem; margin-bottom:0.5rem; border-bottom:1px solid var(--border); padding-bottom:0.3rem; }
#md-preview h2 { font-size:1.3rem; margin-bottom:0.4rem; }
#md-preview h3 { font-size:1.1rem; margin-bottom:0.35rem; }
#md-preview p  { margin-bottom:0.75rem; }
#md-preview ul { padding-left:1.5rem; margin-bottom:0.75rem; }
#md-preview li { margin-bottom:0.25rem; }
#md-preview code { background:rgba(255,255,255,0.08); padding:0.15rem 0.35rem; border-radius:4px; font-size:0.85em; }
#md-preview strong { font-weight:700; }
#md-preview em { font-style:italic; }
#md-preview a  { color:var(--accent); }
"""

_SAMPLE = "# Hello, Markdown!\\n\\nType **bold**, *italic*, `inline code`, or a [link](https://example.com).\\n\\n## Lists\\n\\n- Item one\\n- Item two\\n- Item three"


def render_markdown() -> str:
    """Return full HTML for /apps/markdown."""
    body = f"""
<div class="md-grid">
  <div class="md-pane">
    <div class="md-label">Markdown Input</div>
    <textarea id="md-input" placeholder="Type Markdown here…">{_SAMPLE}</textarea>
  </div>
  <div class="md-pane">
    <div class="md-label">Preview</div>
    <div id="md-preview" aria-label="preview output"></div>
  </div>
</div>
"""
    js = r"""
  const input   = document.getElementById('md-input');
  const preview = document.getElementById('md-preview');

  function parseMarkdown(raw) {
    // 1. HTML-escape
    let s = raw
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    const lines = s.split('\n');
    const out = [];
    let i = 0;
    while (i < lines.length) {
      const line = lines[i];
      // Headings (must come before other replacements)
      if (/^### /.test(line)) { out.push('<h3>' + inlineReplace(line.slice(4)) + '</h3>'); i++; continue; }
      if (/^## /.test(line))  { out.push('<h2>' + inlineReplace(line.slice(3)) + '</h2>'); i++; continue; }
      if (/^# /.test(line))   { out.push('<h1>' + inlineReplace(line.slice(2)) + '</h1>'); i++; continue; }
      // Unordered list
      if (/^- /.test(line)) {
        const items = [];
        while (i < lines.length && /^- /.test(lines[i])) {
          items.push('<li>' + inlineReplace(lines[i].slice(2)) + '</li>');
          i++;
        }
        out.push('<ul>' + items.join('') + '</ul>');
        continue;
      }
      // Blank lines
      if (line.trim() === '') { out.push(''); i++; continue; }
      // Paragraph
      const parts = [];
      while (i < lines.length && lines[i].trim() !== '' && !/^[#-]/.test(lines[i])) {
        parts.push(inlineReplace(lines[i]));
        i++;
      }
      if (parts.length) out.push('<p>' + parts.join(' ') + '</p>');
    }
    return out.join('\n');
  }

  function inlineReplace(s) {
    // bold: **text**
    s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    // italic: *text*
    s = s.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    // inline code: `text`
    s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
    // links: [label](url)
    s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
    return s;
  }

  function update() {
    preview.innerHTML = parseMarkdown(input.value);
  }

  input.oninput = update;
  update();
"""
    return page("Markdown Previewer", body, extra_css=_EXTRA_CSS, extra_js=js)
