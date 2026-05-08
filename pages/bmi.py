"""BMI Calculator mini-app page."""
from pages._shell import page


def render_bmi() -> str:
    """Return full HTML for /apps/bmi."""
    body = """
<h1 style="margin-bottom:1.5rem">BMI Calculator</h1>
<div style="max-width:400px">
  <div style="margin-bottom:1rem">
    <label for="height-input" style="display:block;margin-bottom:0.35rem;font-size:0.9rem">Height (cm)</label>
    <input type="number" id="height-input" placeholder="e.g. 175" min="1" step="0.1">
  </div>
  <div style="margin-bottom:1rem">
    <label for="weight-input" style="display:block;margin-bottom:0.35rem;font-size:0.9rem">Weight (kg)</label>
    <input type="number" id="weight-input" placeholder="e.g. 70" min="1" step="0.1">
  </div>
  <button class="btn btn-primary" id="calc-btn" style="margin-bottom:0.5rem">Calculate</button>
  <p class="validation" id="bmi-error">Please enter valid positive values for height and weight.</p>
  <div id="bmi-result" style="display:none;margin-top:1.25rem;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1.25rem">
    <div style="font-size:2.5rem;font-weight:700;margin-bottom:0.5rem" id="bmi-value"></div>
    <div id="bmi-badge" class="badge" style="font-size:0.9rem;margin-bottom:0.75rem"></div>
    <div class="muted" style="font-size:0.85rem">
      Underweight: &lt;18.5 &nbsp;|&nbsp; Normal: 18.5–24.9 &nbsp;|&nbsp; Overweight: 25–29.9 &nbsp;|&nbsp; Obese: ≥30
    </div>
  </div>
</div>
"""
    js = r"""
  document.getElementById('calc-btn').onclick = function() {
    const heightEl = document.getElementById('height-input');
    const weightEl = document.getElementById('weight-input');
    const errorEl  = document.getElementById('bmi-error');
    const resultEl = document.getElementById('bmi-result');
    const valueEl  = document.getElementById('bmi-value');
    const badgeEl  = document.getElementById('bmi-badge');

    const h = parseFloat(heightEl.value);
    const w = parseFloat(weightEl.value);

    if (!h || !w || h <= 0 || w <= 0 || isNaN(h) || isNaN(w)) {
      errorEl.classList.add('visible');
      resultEl.style.display = 'none';
      return;
    }
    errorEl.classList.remove('visible');

    const heightM = h / 100;
    const bmi = w / (heightM * heightM);
    valueEl.textContent = bmi.toFixed(1);

    let category, badgeClass;
    if (bmi < 18.5) {
      category  = 'Underweight'; badgeClass = 'badge-info';
    } else if (bmi < 25) {
      category  = 'Normal';      badgeClass = 'badge-success';
    } else if (bmi < 30) {
      category  = 'Overweight';  badgeClass = 'badge-warning';
    } else {
      category  = 'Obese';       badgeClass = 'badge-danger';
    }
    badgeEl.textContent = category;
    badgeEl.className   = 'badge ' + badgeClass;
    resultEl.style.display = 'block';
  };
"""
    return page("BMI Calculator", body, extra_js=js)
