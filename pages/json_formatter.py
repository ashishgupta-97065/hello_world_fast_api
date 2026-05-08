"""JSON Formatter mini-app page."""
from pages._shell import page


def render_json_formatter() -> str:
    """Return full HTML for /apps/json-formatter."""
    body = """
<h1 style="margin-bottom:1.5rem">JSON Formatter</h1>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem">
  <div>
    <label style="font-size:0.85rem;color:var(--text-muted);display:block;margin-bottom:0.35rem">Input JSON</label>
    <textarea id="json-input" style="height:300px;font-family:'Courier New',monospace;font-size:0.85rem" placeholder='{"key": "value"}'></textarea>
    <div id="json-stats" style="font-size:0.8rem;color:var(--text-muted);margin-top:0.3rem">
      <span id="char-count">0 chars</span> &nbsp;·&nbsp; <span id="line-count">0 lines</span>
    </div>
  </div>
  <div>
    <label style="font-size:0.85rem;color:var(--text-muted);display:block;margin-bottom:0.35rem">Output</label>
    <div id="json-output" style="height:300px;background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:0.55rem 0.85rem;overflow:auto;font-family:'Courier New',monospace;font-size:0.85rem;white-space:pre-wrap;word-break:break-all"></div>
  </div>
</div>
<div style="display:flex;gap:0.75rem;flex-wrap:wrap;margin-bottom:0.75rem">
  <button class="btn btn-primary" id="format-btn">Format</button>
  <button class="btn btn-secondary" id="minify-btn">Minify</button>
  <button class="btn btn-secondary" id="validate-btn">Validate</button>
  <button class="btn btn-ghost" id="copy-btn">Copy</button>
  <button class="btn btn-ghost" id="clear-btn">Clear</button>
</div>
<div id="json-status" style="font-size:0.85rem;min-height:1.4rem"></div>
"""
    css = """
.json-valid { color: var(--success); }
.json-error { color: var(--danger); }
"""
    js = r"""
  const input = document.getElementById('json-input');
  const output = document.getElementById('json-output');
  const status = document.getElementById('json-status');

  function lineFromError(str, err) {
    const msg = err.message || '';
    const posMatch = msg.match(/position (\d+)/i);
    if (posMatch) {
      const pos = parseInt(posMatch[1], 10);
      const before = str.slice(0, pos);
      return (before.match(/\n/g) || []).length + 1;
    }
    const lineMatch = msg.match(/line (\d+)/i);
    if (lineMatch) return parseInt(lineMatch[1], 10);
    return null;
  }

  function updateStats() {
    const val = input.value;
    document.getElementById('char-count').textContent = val.length + ' chars';
    const lines = val === '' ? 0 : val.split('\n').length;
    document.getElementById('line-count').textContent = lines + ' lines';
  }

  input.addEventListener('input', updateStats);

  document.getElementById('format-btn').onclick = () => {
    try {
      const parsed = JSON.parse(input.value);
      const formatted = JSON.stringify(parsed, null, 2);
      output.textContent = formatted;
      status.textContent = '✓ Valid JSON — formatted.';
      status.className = 'json-valid';
    } catch(e) {
      const line = lineFromError(input.value, e);
      status.textContent = '✗ Parse error' + (line ? ' on line ' + line : '') + ': ' + e.message;
      status.className = 'json-error';
    }
  };

  document.getElementById('minify-btn').onclick = () => {
    try {
      const parsed = JSON.parse(input.value);
      output.textContent = JSON.stringify(parsed);
      status.textContent = '✓ Valid JSON — minified.';
      status.className = 'json-valid';
    } catch(e) {
      const line = lineFromError(input.value, e);
      status.textContent = '✗ Parse error' + (line ? ' on line ' + line : '') + ': ' + e.message;
      status.className = 'json-error';
    }
  };

  document.getElementById('validate-btn').onclick = () => {
    try {
      JSON.parse(input.value);
      status.textContent = '✓ Valid JSON.';
      status.className = 'json-valid';
    } catch(e) {
      const line = lineFromError(input.value, e);
      status.textContent = '✗ Invalid JSON' + (line ? ' (line ' + line + ')' : '') + ': ' + e.message;
      status.className = 'json-error';
    }
  };

  document.getElementById('copy-btn').onclick = () => {
    const text = output.textContent;
    if (!text) return;
    navigator.clipboard.writeText(text).then(() => {
      status.textContent = '✓ Copied to clipboard.';
      status.className = 'json-valid';
    }).catch(() => {
      status.textContent = '✗ Copy failed.';
      status.className = 'json-error';
    });
  };

  document.getElementById('clear-btn').onclick = () => {
    input.value = '';
    output.textContent = '';
    status.textContent = '';
    status.className = '';
    updateStats();
  };

  updateStats();
"""
    return page("JSON Formatter", body, extra_css=css, extra_js=js)
