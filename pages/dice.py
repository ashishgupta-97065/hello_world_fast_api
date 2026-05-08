"""Dice Roller mini-app page."""
from pages._shell import page

_EXTRA_CSS = """
.die-seg {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}
.die-btn {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text-muted);
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: background 0.1s, border-color 0.1s, color 0.1s;
}
.die-btn.selected {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}
.die-result {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 12px;
  background: var(--surface);
  border: 2px solid var(--border);
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0.35rem;
  transition: transform 0.05s ease;
}
.die-result.rolling {
  transform: rotate(15deg) scale(1.1);
}
"""


def render_dice() -> str:
    """Return full HTML for /apps/dice."""
    body = """
<h1 style="margin-bottom:1.5rem">Dice Roller</h1>

<div>
  <div style="margin-bottom:0.5rem;font-size:0.85rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em">Die Type</div>
  <div class="die-seg" id="die-seg">
    <button class="die-btn" data-sides="4">D4</button>
    <button class="die-btn selected" data-sides="6">D6</button>
    <button class="die-btn" data-sides="8">D8</button>
    <button class="die-btn" data-sides="10">D10</button>
    <button class="die-btn" data-sides="12">D12</button>
    <button class="die-btn" data-sides="20">D20</button>
  </div>
</div>

<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem">
  <label for="dice-count" style="font-size:0.9rem">Count (1–6)</label>
  <select id="dice-count" style="max-width:100px">
    <option value="1">1</option>
    <option value="2">2</option>
    <option value="3" selected>3</option>
    <option value="4">4</option>
    <option value="5">5</option>
    <option value="6">6</option>
  </select>
</div>

<button class="btn btn-primary" id="roll-btn" style="margin-bottom:1.5rem;font-size:1rem;padding:0.65rem 2rem">Roll</button>

<div id="results-row" style="display:flex;flex-wrap:wrap;align-items:center;gap:0.5rem;min-height:80px"></div>
<div id="total-line" style="margin-top:1rem;font-size:1.1rem;font-weight:600;color:var(--text-muted)"></div>
"""
    js = r"""
  let selectedSides = 6;

  document.getElementById('die-seg').querySelectorAll('.die-btn').forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll('.die-btn').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      selectedSides = parseInt(btn.dataset.sides, 10);
    };
  });

  const rollBtn    = document.getElementById('roll-btn');
  const resultsRow = document.getElementById('results-row');
  const totalLine  = document.getElementById('total-line');

  rollBtn.onclick = function() {
    const count = parseInt(document.getElementById('dice-count').value, 10);
    const sides = selectedSides;

    rollBtn.disabled = true;
    resultsRow.innerHTML = '';
    totalLine.textContent = '';

    const dice = [];
    for (let i = 0; i < count; i++) {
      const el = document.createElement('div');
      el.className = 'die-result';
      resultsRow.appendChild(el);
      dice.push(el);
    }

    let elapsed = 0;
    const animDuration = 400;
    const tickInterval = 50;

    const timerId = setInterval(() => {
      elapsed += tickInterval;
      dice.forEach(el => {
        el.textContent = Math.floor(Math.random() * sides) + 1;
        el.classList.toggle('rolling');
      });

      if (elapsed >= animDuration) {
        clearInterval(timerId);
        const finals = dice.map(() => Math.floor(Math.random() * sides) + 1);
        dice.forEach((el, i) => {
          el.textContent = finals[i];
          el.classList.remove('rolling');
        });
        const total = finals.reduce((a, b) => a + b, 0);
        totalLine.textContent = 'Total: ' + total;
        rollBtn.disabled = false;
      }
    }, tickInterval);
  };
"""
    return page("Dice Roller", body, extra_css=_EXTRA_CSS, extra_js=js)
