"""Password Generator mini-app page."""
from pages._shell import page


def render_password() -> str:
    """Return full HTML for /apps/password."""
    body = """
<h1 style="margin-bottom:1.5rem">Password Generator</h1>
<div style="max-width:480px">
  <div style="margin-bottom:1.25rem">
    <label style="display:flex;justify-content:space-between;margin-bottom:0.5rem;font-size:0.9rem">
      <span>Length</span>
      <span id="length-label" class="mono">16</span>
    </label>
    <input type="range" id="length-slider" min="8" max="64" value="16">
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem 1.5rem;margin-bottom:1.25rem">
    <label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer;font-size:0.9rem">
      <input type="checkbox" id="cb-uppercase" checked> Uppercase (A–Z)
    </label>
    <label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer;font-size:0.9rem">
      <input type="checkbox" id="cb-lowercase" checked> Lowercase (a–z)
    </label>
    <label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer;font-size:0.9rem">
      <input type="checkbox" id="cb-numbers" checked> Numbers (0–9)
    </label>
    <label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer;font-size:0.9rem">
      <input type="checkbox" id="cb-symbols" checked> Symbols
    </label>
  </div>
  <div style="font-size:0.8rem;color:var(--text-muted);margin-bottom:1rem">
    Symbol set: <span class="mono">!@#$%^&amp;*()-_=+[]{};:,.?/</span>
  </div>
  <button class="btn btn-primary" id="gen-btn" style="margin-bottom:0.75rem">Generate</button>
  <p class="validation" id="pw-error">Please select at least one character class.</p>
  <div style="display:flex;gap:0.75rem;margin-top:0.75rem">
    <input type="text" id="pw-output" readonly placeholder="Your password will appear here…" style="flex:1">
    <button class="btn btn-secondary" id="copy-btn">Copy</button>
  </div>
</div>
"""
    js = r"""
  const UPPER   = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const LOWER   = 'abcdefghijklmnopqrstuvwxyz';
  const DIGITS  = '0123456789';
  const SYMBOLS = '!@#$%^&*()-_=+[]{};:,.?/';

  const slider    = document.getElementById('length-slider');
  const lenLabel  = document.getElementById('length-label');
  const cbUpper   = document.getElementById('cb-uppercase');
  const cbLower   = document.getElementById('cb-lowercase');
  const cbNumbers = document.getElementById('cb-numbers');
  const cbSymbols = document.getElementById('cb-symbols');
  const genBtn    = document.getElementById('gen-btn');
  const copyBtn   = document.getElementById('copy-btn');
  const output    = document.getElementById('pw-output');
  const errorEl   = document.getElementById('pw-error');

  slider.oninput = () => { lenLabel.textContent = slider.value; };

  function randomInt(max) {
    if (window.crypto && window.crypto.getRandomValues) {
      const arr = new Uint32Array(1);
      window.crypto.getRandomValues(arr);
      return arr[0] % max;
    }
    return Math.floor(Math.random() * max);
  }

  genBtn.onclick = function() {
    let pool = '';
    if (cbUpper.checked)   pool += UPPER;
    if (cbLower.checked)   pool += LOWER;
    if (cbNumbers.checked) pool += DIGITS;
    if (cbSymbols.checked) pool += SYMBOLS;

    if (!pool) {
      errorEl.classList.add('visible');
      output.value = '';
      return;
    }
    errorEl.classList.remove('visible');

    const len = parseInt(slider.value, 10);
    let pw = '';
    for (let i = 0; i < len; i++) {
      pw += pool[randomInt(pool.length)];
    }
    output.value = pw;
  };

  copyBtn.onclick = function() {
    if (!output.value) return;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(output.value).catch(() => fallback());
    } else {
      fallback();
    }
    copyBtn.textContent = 'Copied!';
    setTimeout(() => { copyBtn.textContent = 'Copy'; }, 1500);

    function fallback() {
      try {
        const ta = document.createElement('textarea');
        ta.value = output.value;
        ta.style.cssText = 'position:fixed;opacity:0';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
      } catch(e) {}
    }
  };

  genBtn.click();
"""
    return page("Password Generator", body, extra_js=js)
