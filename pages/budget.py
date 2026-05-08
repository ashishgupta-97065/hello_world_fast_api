"""Budget Planner mini-app page."""
from pages._shell import page


def render_budget() -> str:
    """Return full HTML for /apps/budget."""
    body = """
<h1 style="margin-bottom:1.5rem">Budget Planner</h1>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem">
  <div>
    <h2 style="font-size:1rem;margin-bottom:0.75rem">Monthly Budgets</h2>
    <div id="budget-inputs" style="display:grid;gap:0.5rem;margin-bottom:1rem"></div>
    <h2 style="font-size:1rem;margin-bottom:0.75rem">Log Spending</h2>
    <div style="display:grid;gap:0.5rem">
      <select id="spend-cat">
        <option value="Housing">Housing</option>
        <option value="Food">Food</option>
        <option value="Transport">Transport</option>
        <option value="Fun">Fun</option>
        <option value="Savings">Savings</option>
        <option value="Other">Other</option>
      </select>
      <input type="number" id="spend-amount" placeholder="Amount" min="0.01" step="0.01">
      <input type="text" id="spend-note" placeholder="Note (optional)">
      <p id="spend-error" class="form-error" style="color:var(--danger);font-size:0.85rem;display:none"></p>
      <button class="btn btn-primary" id="spend-add-btn">Add Spending Entry</button>
    </div>
  </div>
  <div>
    <h2 style="font-size:1rem;margin-bottom:0.75rem">Progress</h2>
    <div id="progress-panel" style="margin-bottom:1.5rem"></div>
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:1rem;font-size:0.9rem">
      <div style="display:flex;justify-content:space-between;margin-bottom:0.4rem">
        <span>Total Budgeted</span><strong id="sum-budget">$0</strong>
      </div>
      <div style="display:flex;justify-content:space-between;margin-bottom:0.4rem">
        <span>Total Spent</span><strong id="sum-spent">$0</strong>
      </div>
      <div style="display:flex;justify-content:space-between">
        <span>Remaining</span><strong id="sum-remaining">$0</strong>
      </div>
    </div>
  </div>
</div>
"""
    css = """
.budget-cat-row { margin-bottom:0.85rem; }
.budget-cat-label { display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:0.25rem; }
.progress-track { background:var(--border); border-radius:999px; height:8px; overflow:hidden; }
.progress-fill { height:100%; border-radius:999px; transition:width 0.2s; }
.bar-ok { background:var(--success); }
.bar-over { background:var(--danger); }
"""
    js = r"""
  const KEY = 'budget.v1';
  const CATS = ['Housing','Food','Transport','Fun','Savings','Other'];
  const DEFAULT = { budgets: {Housing:0,Food:0,Transport:0,Fun:0,Savings:0,Other:0}, spending: [] };
  let state = JSON.parse(JSON.stringify(DEFAULT));

  function load() {
    try {
      const d = JSON.parse(localStorage.getItem(KEY));
      if (d && d.budgets && d.spending) state = d;
    } catch(e) {}
  }
  function save() { localStorage.setItem(KEY, JSON.stringify(state)); }

  function progressFor(cat, budgets, totals) {
    const budget = budgets[cat] || 0;
    const spent = totals[cat] || 0;
    const pct = budget > 0 ? Math.min(spent / budget * 100, 100) : (spent > 0 ? 100 : 0);
    return { pct, over: spent > budget };
  }

  function buildBudgetInputs() {
    const container = document.getElementById('budget-inputs');
    container.innerHTML = '';
    CATS.forEach(cat => {
      const row = document.createElement('div');
      row.style.display = 'flex'; row.style.gap = '0.5rem'; row.style.alignItems = 'center';
      const lbl = document.createElement('label');
      lbl.style.width = '90px'; lbl.style.fontSize = '0.85rem';
      lbl.textContent = cat;
      const inp = document.createElement('input');
      inp.type = 'number'; inp.min = '0'; inp.step = '1';
      inp.style.width = 'auto'; inp.style.flex = '1';
      inp.value = state.budgets[cat] || 0;
      inp.onchange = () => {
        const v = parseFloat(inp.value);
        state.budgets[cat] = (isFinite(v) && v >= 0) ? v : 0;
        save(); renderProgress();
      };
      row.append(lbl, inp);
      container.appendChild(row);
    });
  }

  function renderProgress() {
    const totals = {};
    CATS.forEach(c => totals[c] = 0);
    state.spending.forEach(s => { totals[s.category] = (totals[s.category] || 0) + s.amount; });

    const panel = document.getElementById('progress-panel');
    panel.innerHTML = '';
    CATS.forEach(cat => {
      const { pct, over } = progressFor(cat, state.budgets, totals);
      const row = document.createElement('div');
      row.className = 'budget-cat-row';
      const lbl = document.createElement('div');
      lbl.className = 'budget-cat-label';
      lbl.innerHTML = '<span></span><span></span>';
      lbl.children[0].textContent = cat;
      lbl.children[1].textContent = '$' + (totals[cat]||0).toFixed(0) + ' / $' + (state.budgets[cat]||0).toFixed(0);
      const track = document.createElement('div');
      track.className = 'progress-track';
      const fill = document.createElement('div');
      fill.className = 'progress-fill ' + (over ? 'bar-over' : 'bar-ok');
      fill.style.width = pct + '%';
      track.appendChild(fill);
      row.append(lbl, track);
      panel.appendChild(row);
    });

    const sumBudget = CATS.reduce((s, c) => s + (state.budgets[c]||0), 0);
    const sumSpent = CATS.reduce((s, c) => s + (totals[c]||0), 0);
    document.getElementById('sum-budget').textContent = '$' + sumBudget.toFixed(0);
    document.getElementById('sum-spent').textContent = '$' + sumSpent.toFixed(0);
    document.getElementById('sum-remaining').textContent = '$' + (sumBudget - sumSpent).toFixed(0);
  }

  document.getElementById('spend-add-btn').onclick = () => {
    const err = document.getElementById('spend-error');
    const amt = parseFloat(document.getElementById('spend-amount').value);
    if (!isFinite(amt) || amt <= 0) { err.textContent = 'Enter a valid amount > 0.'; err.style.display=''; return; }
    err.style.display = 'none';
    state.spending.push({
      id: Date.now()+Math.random(),
      category: document.getElementById('spend-cat').value,
      amount: amt,
      note: document.getElementById('spend-note').value.trim(),
      ts: Date.now()
    });
    document.getElementById('spend-amount').value = '';
    document.getElementById('spend-note').value = '';
    save(); renderProgress();
  };

  load(); buildBudgetInputs(); renderProgress();
"""
    return page("Budget Planner", body, extra_css=css, extra_js=js)
