"""Recipe Scaler mini-app page."""
from pages._shell import page


def render_recipe() -> str:
    """Return full HTML for /apps/recipe."""
    body = """
<h1 style="margin-bottom:1.5rem">Recipe Scaler</h1>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem">
  <div>
    <div style="margin-bottom:0.75rem">
      <label style="font-size:0.85rem;color:var(--text-muted)">Recipe Title</label>
      <input type="text" id="recipe-title" placeholder="e.g. Chocolate Chip Cookies">
    </div>
    <div style="margin-bottom:0.75rem">
      <label style="font-size:0.85rem;color:var(--text-muted)">Base Servings</label>
      <input type="number" id="base-servings" value="4" min="1" step="1" style="max-width:100px">
    </div>
    <h2 style="font-size:1rem;margin-bottom:0.5rem">Add Ingredient</h2>
    <div style="display:grid;grid-template-columns:80px 1fr 1fr auto;gap:0.5rem;align-items:end;margin-bottom:0.5rem">
      <div>
        <label style="font-size:0.78rem;color:var(--text-muted)">Amount</label>
        <input type="number" id="ing-amount" placeholder="1" min="0.001" step="any">
      </div>
      <div>
        <label style="font-size:0.78rem;color:var(--text-muted)">Unit</label>
        <select id="ing-unit">
          <option value="tsp">tsp</option>
          <option value="tbsp">tbsp</option>
          <option value="cup">cup</option>
          <option value="ml">ml</option>
          <option value="l">l</option>
          <option value="g">g</option>
          <option value="kg">kg</option>
          <option value="oz">oz</option>
          <option value="lb">lb</option>
          <option value="count">count</option>
        </select>
      </div>
      <div>
        <label style="font-size:0.78rem;color:var(--text-muted)">Name</label>
        <input type="text" id="ing-name" placeholder="flour">
      </div>
      <button class="btn btn-primary" id="ing-add-btn" style="align-self:end">+</button>
    </div>
    <p id="ing-error" style="color:var(--danger);font-size:0.85rem;margin-bottom:0.5rem;display:none"></p>
    <div id="ingredient-list" style="margin-bottom:1rem"></div>
    <button class="btn btn-primary" id="save-btn">Save Recipe</button>
    <p id="save-status" style="font-size:0.85rem;color:var(--success);margin-top:0.4rem;display:none">Recipe saved!</p>
  </div>
  <div>
    <h2 style="font-size:1rem;margin-bottom:0.75rem">Scale Recipe</h2>
    <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.75rem">
      <button class="btn btn-secondary scale-preset" data-s="0.5">0.5×</button>
      <button class="btn btn-secondary scale-preset" data-s="1">1×</button>
      <button class="btn btn-secondary scale-preset" data-s="2">2×</button>
      <button class="btn btn-secondary scale-preset" data-s="3">3×</button>
      <button class="btn btn-secondary scale-preset" data-s="4">4×</button>
    </div>
    <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:1rem">
      <label style="font-size:0.85rem;white-space:nowrap">Custom:</label>
      <input type="number" id="custom-scale" placeholder="e.g. 1.5" min="0.1" step="0.1" style="max-width:100px">
    </div>
    <div id="scaled-output" style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:1rem;min-height:100px">
      <p class="muted">Add ingredients to see scaled result.</p>
    </div>
  </div>
</div>
"""
    css = """
.ing-row {
  display:flex; align-items:center; gap:0.5rem;
  padding:0.45rem 0.65rem;
  background:var(--surface); border:1px solid var(--border); border-radius:6px; margin-bottom:0.35rem;
  font-size:0.85rem;
}
.scaled-row { font-size:0.9rem; margin-bottom:0.4rem; }
"""
    js = r"""
  const KEY = 'recipe.v1';
  let state = { title:'', baseServings:4, ingredients:[] };
  let scaleFactor = 1;

  function load() {
    try {
      const d = JSON.parse(localStorage.getItem(KEY));
      if (d && d.ingredients) {
        state = d;
        document.getElementById('recipe-title').value = state.title || '';
        document.getElementById('base-servings').value = state.baseServings || 4;
      }
    } catch(e) {}
  }
  function save() {
    state.title = document.getElementById('recipe-title').value.trim();
    state.baseServings = parseInt(document.getElementById('base-servings').value) || 1;
    localStorage.setItem(KEY, JSON.stringify(state));
  }

  function convertVolume(amount, unit) {
    if (unit === 'tsp' && amount >= 3)  return convertVolume(amount / 3, 'tbsp');
    if (unit === 'tbsp' && amount >= 16) return convertVolume(amount / 16, 'cup');
    if (unit === 'ml' && amount >= 1000) return { amount: amount/1000, unit: 'l' };
    return { amount, unit };
  }

  function fmtAmt(n) {
    const r = Math.round(n * 1000) / 1000;
    return r % 1 === 0 ? r.toString() : r.toFixed(3).replace(/0+$/, '');
  }

  function renderIngredients() {
    const list = document.getElementById('ingredient-list');
    list.innerHTML = '';
    state.ingredients.forEach((ing, i) => {
      const div = document.createElement('div');
      div.className = 'ing-row';
      const txt = document.createElement('span');
      txt.style.flex = '1';
      txt.textContent = fmtAmt(ing.amount) + ' ' + ing.unit + ' ' + ing.name;
      const del = document.createElement('button');
      del.className = 'btn btn-ghost';
      del.style.fontSize = '0.75rem';
      del.style.padding = '0.15rem 0.4rem';
      del.textContent = '✕';
      del.onclick = () => { state.ingredients.splice(i, 1); renderIngredients(); renderScaled(); };
      div.append(txt, del);
      list.appendChild(div);
    });
  }

  function renderScaled() {
    const out = document.getElementById('scaled-output');
    if (!state.ingredients.length) { out.innerHTML = '<p class="muted">Add ingredients to see scaled result.</p>'; return; }
    const servings = (parseInt(document.getElementById('base-servings').value) || 1) * scaleFactor;
    out.innerHTML = '<div style="font-weight:600;margin-bottom:0.5rem">Servings: ' + fmtAmt(servings) + '</div>';
    state.ingredients.forEach(ing => {
      const scaled = ing.amount * scaleFactor;
      const conv = convertVolume(scaled, ing.unit);
      const div = document.createElement('div');
      div.className = 'scaled-row';
      div.textContent = fmtAmt(conv.amount) + ' ' + conv.unit + ' ' + ing.name;
      out.appendChild(div);
    });
  }

  document.getElementById('ing-add-btn').onclick = () => {
    const err = document.getElementById('ing-error');
    const amt = parseFloat(document.getElementById('ing-amount').value);
    const name = document.getElementById('ing-name').value.trim();
    if (!isFinite(amt) || amt <= 0) { err.textContent = 'Amount must be > 0.'; err.style.display=''; return; }
    if (!name) { err.textContent = 'Enter an ingredient name.'; err.style.display=''; return; }
    err.style.display = 'none';
    state.ingredients.push({ amount: amt, unit: document.getElementById('ing-unit').value, name });
    document.getElementById('ing-amount').value = '';
    document.getElementById('ing-name').value = '';
    renderIngredients(); renderScaled();
  };

  document.querySelectorAll('.scale-preset').forEach(btn => {
    btn.onclick = () => { scaleFactor = parseFloat(btn.dataset.s); renderScaled(); };
  });

  document.getElementById('custom-scale').oninput = () => {
    const v = parseFloat(document.getElementById('custom-scale').value);
    if (isFinite(v) && v > 0) { scaleFactor = v; renderScaled(); }
  };

  document.getElementById('save-btn').onclick = () => {
    save();
    const s = document.getElementById('save-status');
    s.style.display = '';
    setTimeout(() => s.style.display='none', 2000);
  };

  load(); renderIngredients(); renderScaled();
"""
    return page("Recipe Scaler", body, extra_css=css, extra_js=js)
