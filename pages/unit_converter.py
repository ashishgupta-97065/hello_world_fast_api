"""Unit Converter mini-app page."""
from pages._shell import page


def render_unit_converter() -> str:
    """Return full HTML for /apps/unit-converter."""
    body = """
<h1 style="margin-bottom:1.5rem">Unit Converter</h1>
<div class="tab-strip">
  <button class="tab active" id="tab-length" onclick="showTab('length')">Length</button>
  <button class="tab" id="tab-weight" onclick="showTab('weight')">Weight</button>
  <button class="tab" id="tab-temperature" onclick="showTab('temperature')">Temperature</button>
</div>

<!-- Length form -->
<div id="form-length" style="display:block">
  <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
    <input type="number" id="len-val" placeholder="Value" style="max-width:160px" oninput="convertLength()">
    <select id="len-from" onchange="convertLength()" style="max-width:160px">
      <option value="m">Meters</option>
      <option value="km">Kilometers</option>
      <option value="mi">Miles</option>
      <option value="ft">Feet</option>
    </select>
    <span class="muted">→</span>
    <select id="len-to" onchange="convertLength()" style="max-width:160px">
      <option value="km">Kilometers</option>
      <option value="m">Meters</option>
      <option value="mi">Miles</option>
      <option value="ft">Feet</option>
    </select>
    <span id="len-result" style="font-size:1.25rem;font-weight:600;min-width:100px">—</span>
  </div>
</div>

<!-- Weight form -->
<div id="form-weight" style="display:none">
  <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
    <input type="number" id="wt-val" placeholder="Value" style="max-width:160px" oninput="convertWeight()">
    <select id="wt-from" onchange="convertWeight()" style="max-width:160px">
      <option value="kg">Kilograms</option>
      <option value="lb">Pounds</option>
      <option value="g">Grams</option>
      <option value="oz">Ounces</option>
    </select>
    <span class="muted">→</span>
    <select id="wt-to" onchange="convertWeight()" style="max-width:160px">
      <option value="lb">Pounds</option>
      <option value="kg">Kilograms</option>
      <option value="g">Grams</option>
      <option value="oz">Ounces</option>
    </select>
    <span id="wt-result" style="font-size:1.25rem;font-weight:600;min-width:100px">—</span>
  </div>
</div>

<!-- Temperature form -->
<div id="form-temperature" style="display:none">
  <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
    <input type="number" id="tmp-val" placeholder="Value" style="max-width:160px" oninput="convertTemp()">
    <select id="tmp-from" onchange="convertTemp()" style="max-width:160px">
      <option value="C">Celsius</option>
      <option value="F">Fahrenheit</option>
      <option value="K">Kelvin</option>
    </select>
    <span class="muted">→</span>
    <select id="tmp-to" onchange="convertTemp()" style="max-width:160px">
      <option value="F">Fahrenheit</option>
      <option value="C">Celsius</option>
      <option value="K">Kelvin</option>
    </select>
    <span id="tmp-result" style="font-size:1.25rem;font-weight:600;min-width:100px">—</span>
  </div>
</div>
"""
    js = r"""
  // Length factors to meters
  const LEN_TO_M = { m: 1, km: 1000, mi: 1609.344, ft: 0.3048 };
  // Weight factors to grams
  const WT_TO_G  = { kg: 1000, lb: 453.592, g: 1, oz: 28.3495 };

  function fmt(val) {
    if (isNaN(val)) return '—';
    return Number(val.toFixed(4)).toString();
  }

  function showTab(name) {
    ['length', 'weight', 'temperature'].forEach(t => {
      document.getElementById('form-' + t).style.display = t === name ? 'block' : 'none';
      const tab = document.getElementById('tab-' + t);
      tab.className = 'tab' + (t === name ? ' active' : '');
    });
  }

  function convertLength() {
    const v = parseFloat(document.getElementById('len-val').value);
    const from = document.getElementById('len-from').value;
    const to   = document.getElementById('len-to').value;
    const el   = document.getElementById('len-result');
    if (isNaN(v)) { el.textContent = '—'; return; }
    el.textContent = fmt(v * LEN_TO_M[from] / LEN_TO_M[to]);
  }

  function convertWeight() {
    const v = parseFloat(document.getElementById('wt-val').value);
    const from = document.getElementById('wt-from').value;
    const to   = document.getElementById('wt-to').value;
    const el   = document.getElementById('wt-result');
    if (isNaN(v)) { el.textContent = '—'; return; }
    el.textContent = fmt(v * WT_TO_G[from] / WT_TO_G[to]);
  }

  function convertTemp() {
    const v = parseFloat(document.getElementById('tmp-val').value);
    const from = document.getElementById('tmp-from').value;
    const to   = document.getElementById('tmp-to').value;
    const el   = document.getElementById('tmp-result');
    if (isNaN(v)) { el.textContent = '—'; return; }
    let result;
    if (from === to) {
      result = v;
    } else if (from === 'C' && to === 'F') {
      result = v * 9/5 + 32;
    } else if (from === 'F' && to === 'C') {
      result = (v - 32) * 5/9;
    } else if (from === 'C' && to === 'K') {
      result = v + 273.15;
    } else if (from === 'K' && to === 'C') {
      result = v - 273.15;
    } else if (from === 'F' && to === 'K') {
      result = (v - 32) * 5/9 + 273.15;
    } else if (from === 'K' && to === 'F') {
      result = (v - 273.15) * 9/5 + 32;
    }
    el.textContent = fmt(result);
  }

  // Expose tab switcher to onclick handlers in HTML (outside IIFE)
  window.showTab = showTab;
  window.convertLength = convertLength;
  window.convertWeight = convertWeight;
  window.convertTemp = convertTemp;
"""
    return page("Unit Converter", body, extra_js=js)
