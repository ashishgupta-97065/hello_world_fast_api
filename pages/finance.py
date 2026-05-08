"""Personal Finance Tracker mini-app page."""
from pages._shell import page


def render_finance() -> str:
    """Return full HTML for /apps/finance."""
    body = """
<h1 style="margin-bottom:1.5rem">Personal Finance Tracker</h1>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin-bottom:1.5rem">
  <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1.25rem">
    <h2 style="font-size:1rem;margin-bottom:1rem">Add Transaction</h2>
    <div style="display:grid;gap:0.75rem">
      <div>
        <label style="font-size:0.85rem;color:var(--text-muted)">Type</label>
        <select id="tx-type">
          <option value="income">Income</option>
          <option value="expense">Expense</option>
        </select>
      </div>
      <div>
        <label style="font-size:0.85rem;color:var(--text-muted)">Amount</label>
        <input type="number" id="tx-amount" placeholder="0.00" min="0.01" step="0.01">
      </div>
      <div>
        <label style="font-size:0.85rem;color:var(--text-muted)">Category</label>
        <select id="tx-category">
          <option value="Housing">Housing</option>
          <option value="Food">Food</option>
          <option value="Transport">Transport</option>
          <option value="Entertainment">Entertainment</option>
          <option value="Other">Other</option>
        </select>
      </div>
      <div>
        <label style="font-size:0.85rem;color:var(--text-muted)">Description</label>
        <input type="text" id="tx-description" placeholder="Short description…">
      </div>
      <div>
        <label style="font-size:0.85rem;color:var(--text-muted)">Date</label>
        <input type="date" id="tx-date">
      </div>
      <p class="form-error" id="tx-error" style="color:var(--danger);font-size:0.85rem;display:none"></p>
      <button class="btn btn-primary" id="tx-add-btn">Add Transaction</button>
    </div>
  </div>
  <div>
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1.25rem;margin-bottom:1rem;text-align:center">
      <div style="font-size:0.85rem;color:var(--text-muted);margin-bottom:0.25rem">Current Balance</div>
      <div id="balance-display" style="font-size:2rem;font-weight:700">$0.00</div>
    </div>
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1.25rem">
      <h3 style="font-size:0.9rem;margin-bottom:0.75rem">Category Breakdown</h3>
      <div id="breakdown-panel"></div>
    </div>
  </div>
</div>
<div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1.25rem">
  <h2 style="font-size:1rem;margin-bottom:1rem">Transactions</h2>
  <div id="tx-list"><p class="muted">No transactions yet.</p></div>
</div>
"""
    css = """
.balance-positive { color: var(--success) !important; }
.balance-negative { color: var(--danger) !important; }
.tx-item {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.6rem 0.85rem;
  border: 1px solid var(--border); border-radius: 8px; margin-bottom: 0.5rem;
}
.tx-income { border-left: 3px solid var(--success); }
.tx-expense { border-left: 3px solid var(--danger); }
.cat-row { display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:0.3rem; }
"""
    js = r"""
  const CATS = ['Housing','Food','Transport','Entertainment','Other'];
  let transactions = [];

  function categoryBreakdown(txs) {
    const result = {};
    CATS.forEach(c => result[c] = { amount: 0, pct: 0 });
    const expenses = txs.filter(t => t.type === 'expense');
    const total = expenses.reduce((s, t) => s + t.amount, 0);
    expenses.forEach(t => {
      if (result[t.category]) result[t.category].amount += t.amount;
    });
    if (total > 0) CATS.forEach(c => result[c].pct = Math.round(result[c].amount / total * 100));
    return result;
  }

  function fmt(n) { return '$' + n.toFixed(2); }

  function render() {
    const income = transactions.filter(t => t.type === 'income').reduce((s, t) => s + t.amount, 0);
    const expenses = transactions.filter(t => t.type === 'expense').reduce((s, t) => s + t.amount, 0);
    const balance = income - expenses;

    const balEl = document.getElementById('balance-display');
    balEl.textContent = fmt(Math.abs(balance));
    balEl.className = '';
    balEl.classList.add(balance >= 0 ? 'balance-positive' : 'balance-negative');

    const bd = categoryBreakdown(transactions);
    const bp = document.getElementById('breakdown-panel');
    bp.innerHTML = '';
    CATS.forEach(c => {
      const row = document.createElement('div');
      row.className = 'cat-row';
      row.innerHTML = '<span></span><span></span>';
      row.children[0].textContent = c;
      row.children[1].textContent = fmt(bd[c].amount) + ' (' + bd[c].pct + '%)';
      bp.appendChild(row);
    });

    const list = document.getElementById('tx-list');
    if (!transactions.length) { list.innerHTML = '<p class="muted">No transactions yet.</p>'; return; }
    list.innerHTML = '';
    [...transactions].reverse().forEach((t, i) => {
      const realIdx = transactions.length - 1 - i;
      const div = document.createElement('div');
      div.className = 'tx-item tx-' + t.type;
      const info = document.createElement('span');
      info.style.flex = '1';
      info.textContent = t.description + ' — ' + t.category + ' (' + t.date + ')';
      const amt = document.createElement('span');
      amt.style.fontWeight = '600';
      amt.style.color = t.type === 'income' ? 'var(--success)' : 'var(--danger)';
      amt.textContent = (t.type === 'income' ? '+' : '-') + fmt(t.amount);
      const del = document.createElement('button');
      del.className = 'btn btn-ghost';
      del.style.fontSize = '0.8rem';
      del.style.padding = '0.2rem 0.5rem';
      del.textContent = 'Delete';
      del.onclick = () => { transactions.splice(realIdx, 1); render(); };
      div.append(info, amt, del);
      list.appendChild(div);
    });
  }

  document.getElementById('tx-date').valueAsDate = new Date();

  document.getElementById('tx-add-btn').onclick = () => {
    const err = document.getElementById('tx-error');
    const amt = parseFloat(document.getElementById('tx-amount').value);
    const desc = document.getElementById('tx-description').value.trim();
    if (!isFinite(amt) || amt <= 0) { err.textContent = 'Enter a valid amount > 0.'; err.style.display = ''; return; }
    if (!desc) { err.textContent = 'Enter a description.'; err.style.display = ''; return; }
    err.style.display = 'none';
    transactions.push({
      type: document.getElementById('tx-type').value,
      amount: amt,
      category: document.getElementById('tx-category').value,
      description: desc,
      date: document.getElementById('tx-date').value || new Date().toISOString().slice(0,10),
      id: Date.now() + Math.random()
    });
    document.getElementById('tx-amount').value = '';
    document.getElementById('tx-description').value = '';
    render();
  };

  render();
"""
    return page("Personal Finance Tracker", body, extra_css=css, extra_js=js)
