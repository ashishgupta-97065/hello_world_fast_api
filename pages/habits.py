"""Habit Tracker mini-app page."""
from pages._shell import page


def render_habits() -> str:
    """Return full HTML for /apps/habits."""
    body = """
<h1 style="margin-bottom:1.5rem">Habit Tracker</h1>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;margin-bottom:1.25rem;align-items:end">
  <input type="text" id="habit-name" placeholder="Habit name (max 40 chars)…" maxlength="40">
  <input type="text" id="habit-emoji" placeholder="Emoji (default ⭐)" maxlength="4">
  <button class="btn btn-primary" id="habit-add-btn" style="grid-column:span 2">Add Habit</button>
</div>
<p id="habit-error" style="color:var(--danger);font-size:0.85rem;margin-bottom:0.75rem;display:none"></p>
<div style="margin-bottom:1rem;font-size:0.9rem">
  Today's completion: <strong id="today-pct">0%</strong>
</div>
<div id="habits-grid"></div>
"""
    css = """
.habit-row { margin-bottom:1.25rem; }
.habit-header { display:flex; align-items:center; gap:0.5rem; margin-bottom:0.4rem; }
.habit-name-label { font-weight:600; flex:1; }
.streak-badge { font-size:0.78rem; background:rgba(92,107,192,0.2); color:var(--accent); padding:0.15rem 0.55rem; border-radius:999px; }
.day-grid { display:grid; grid-template-columns:60px repeat(7,1fr); gap:4px; align-items:center; }
.day-hdr { font-size:0.75rem; color:var(--text-muted); text-align:center; }
.day-cell {
  aspect-ratio:1; border-radius:6px; border:1px solid var(--border);
  background:var(--surface); cursor:pointer; font-size:1.1rem;
  display:flex; align-items:center; justify-content:center;
}
.day-cell.done { background:var(--accent); border-color:var(--accent); }
.del-habit { background:none; border:none; color:var(--danger); cursor:pointer; font-size:0.85rem; }
"""
    js = r"""
  const KEY = 'habits.v1';
  const DAY_ABBREVS = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
  let state = { habits: [] };

  function load() {
    try { const d = JSON.parse(localStorage.getItem(KEY)); if (d && Array.isArray(d.habits)) state = d; }
    catch(e) {}
  }
  function save() { localStorage.setItem(KEY, JSON.stringify(state)); }

  function todayStr() { return new Date().toISOString().slice(0,10); }

  function last7Dates() {
    const dates = [];
    for (let i=6; i>=0; i--) {
      const d = new Date(); d.setDate(d.getDate() - i);
      dates.push(d.toISOString().slice(0,10));
    }
    return dates;
  }

  function streak(habit, today) {
    let count = 0;
    const d = new Date(today);
    while (habit.days[d.toISOString().slice(0,10)] === true) {
      count++;
      d.setDate(d.getDate() - 1);
    }
    return count;
  }

  function render() {
    const dates = last7Dates();
    const today = todayStr();
    const grid = document.getElementById('habits-grid');
    grid.innerHTML = '';

    // header row
    if (state.habits.length) {
      const hdr = document.createElement('div');
      hdr.className = 'day-grid';
      hdr.style.marginBottom = '0.25rem';
      const lbl = document.createElement('div');
      grid.appendChild(hdr);
      hdr.appendChild(lbl);
      DAY_ABBREVS.forEach(d => {
        const h = document.createElement('div');
        h.className = 'day-hdr';
        h.textContent = d;
        hdr.appendChild(h);
      });
    }

    state.habits.forEach((habit, hi) => {
      const row = document.createElement('div');
      row.className = 'habit-row';

      const header = document.createElement('div');
      header.className = 'habit-header';
      const nameEl = document.createElement('span');
      nameEl.className = 'habit-name-label';
      nameEl.textContent = (habit.emoji || '⭐') + ' ' + habit.name;
      const s = streak(habit, today);
      const badge = document.createElement('span');
      badge.className = 'streak-badge';
      badge.textContent = '🔥 ' + s + ' day streak';
      const delBtn = document.createElement('button');
      delBtn.className = 'del-habit';
      delBtn.textContent = '✕';
      delBtn.onclick = () => { state.habits.splice(hi, 1); save(); render(); };
      header.append(nameEl, badge, delBtn);

      const cellRow = document.createElement('div');
      cellRow.className = 'day-grid';
      const spacer = document.createElement('div');
      cellRow.appendChild(spacer);

      dates.forEach(date => {
        const cell = document.createElement('button');
        cell.className = 'day-cell' + (habit.days[date] ? ' done' : '');
        cell.setAttribute('aria-pressed', habit.days[date] ? 'true' : 'false');
        cell.textContent = habit.days[date] ? (habit.emoji || '⭐') : '';
        cell.onclick = () => {
          if (habit.days[date]) { delete habit.days[date]; }
          else { habit.days[date] = true; }
          save(); render();
        };
        cellRow.appendChild(cell);
      });

      row.append(header, cellRow);
      grid.appendChild(row);
    });

    // today completion
    const total = state.habits.length;
    const done = state.habits.filter(h => h.days[today] === true).length;
    const pct = total ? Math.round(done / total * 100) : 0;
    document.getElementById('today-pct').textContent = pct + '%';
  }

  load();
  render();

  document.getElementById('habit-add-btn').onclick = () => {
    const err = document.getElementById('habit-error');
    const name = document.getElementById('habit-name').value.trim();
    const emoji = document.getElementById('habit-emoji').value.trim() || '⭐';
    if (!name) { err.textContent = 'Enter a habit name.'; err.style.display=''; return; }
    if (state.habits.length >= 10) { err.textContent = 'Maximum 10 habits reached.'; err.style.display=''; return; }
    err.style.display = 'none';
    state.habits.push({ id: Date.now() + '' + Math.random(), name, emoji, days: {} });
    document.getElementById('habit-name').value = '';
    document.getElementById('habit-emoji').value = '';
    save(); render();
  };
"""
    return page("Habit Tracker", body, extra_css=css, extra_js=js)
