"""Stopwatch + Lap Timer mini-app page."""
from pages._shell import page


def render_stopwatch() -> str:
    """Return full HTML for /apps/stopwatch."""
    body = """
<h1 style="margin-bottom:1.5rem">Stopwatch</h1>
<div style="text-align:center;margin-bottom:2rem">
  <div id="timer-display" style="font-size:4rem;font-weight:700;font-family:'Courier New',monospace;letter-spacing:0.05em">00:00.00</div>
  <div style="display:flex;gap:0.75rem;justify-content:center;margin-top:1.25rem">
    <button class="btn btn-primary" id="start-btn">Start</button>
    <button class="btn btn-secondary" id="pause-btn" disabled>Pause</button>
    <button class="btn btn-secondary" id="reset-btn">Reset</button>
    <button class="btn btn-ghost" id="lap-btn" disabled>Lap</button>
  </div>
</div>
<div>
  <h2 style="font-size:1rem;margin-bottom:0.75rem">Lap Times</h2>
  <div id="lap-list"><p class="muted">No laps yet.</p></div>
</div>
"""
    css = """
.lap-item {
  display:flex; align-items:center; gap:0.75rem;
  padding:0.5rem 0.85rem;
  background:var(--surface); border:1px solid var(--border); border-radius:8px; margin-bottom:0.4rem;
  font-family:'Courier New',monospace;
}
.lap-best { border-left:3px solid var(--success); }
.lap-worst { border-left:3px solid var(--danger); }
.lap-num { color:var(--text-muted); width:40px; }
"""
    js = r"""
  let startTime = null;
  let elapsed = 0;
  let running = false;
  let intervalId = null;
  let laps = [];

  function fmt(ms) {
    const total = Math.floor(ms / 10);
    const cs = total % 100;
    const secs = Math.floor(total / 100) % 60;
    const mins = Math.floor(total / 6000);
    return String(mins).padStart(2,'0') + ':' + String(secs).padStart(2,'0') + '.' + String(cs).padStart(2,'0');
  }

  function markBestWorst(lapList) {
    if (lapList.length < 2) return lapList.map(l => ({...l, tag: ''}));
    const times = lapList.map(l => l.split);
    const best = Math.min(...times);
    const worst = Math.max(...times);
    return lapList.map(l => ({
      ...l, tag: l.split === best ? 'best' : (l.split === worst ? 'worst' : '')
    }));
  }

  function renderLaps() {
    const el = document.getElementById('lap-list');
    if (!laps.length) { el.innerHTML = '<p class="muted">No laps yet.</p>'; return; }
    const tagged = markBestWorst(laps);
    el.innerHTML = '';
    [...tagged].reverse().forEach(l => {
      const div = document.createElement('div');
      div.className = 'lap-item' + (l.tag === 'best' ? ' lap-best' : l.tag === 'worst' ? ' lap-worst' : '');
      const num = document.createElement('span');
      num.className = 'lap-num';
      num.textContent = '#' + l.num;
      const time = document.createElement('span');
      time.textContent = fmt(l.split);
      const total = document.createElement('span');
      total.style.marginLeft = 'auto';
      total.style.color = 'var(--text-muted)';
      total.style.fontSize = '0.85rem';
      total.textContent = 'Total: ' + fmt(l.total);
      if (l.tag) {
        const badge = document.createElement('span');
        badge.style.fontSize = '0.75rem';
        badge.style.color = l.tag === 'best' ? 'var(--success)' : 'var(--danger)';
        badge.textContent = l.tag === 'best' ? '★ Best' : '▼ Worst';
        div.append(num, time, badge, total);
      } else {
        div.append(num, time, total);
      }
      el.appendChild(div);
    });
  }

  function tick() {
    const now = performance.now();
    const ms = elapsed + (now - startTime);
    document.getElementById('timer-display').textContent = fmt(ms);
  }

  document.getElementById('start-btn').onclick = () => {
    if (running) return;
    running = true;
    startTime = performance.now();
    intervalId = setInterval(tick, 50);
    document.getElementById('start-btn').disabled = true;
    document.getElementById('pause-btn').disabled = false;
    document.getElementById('lap-btn').disabled = false;
  };

  document.getElementById('pause-btn').onclick = () => {
    if (!running) return;
    running = false;
    elapsed += performance.now() - startTime;
    clearInterval(intervalId);
    document.getElementById('start-btn').disabled = false;
    document.getElementById('start-btn').textContent = 'Resume';
    document.getElementById('pause-btn').disabled = true;
  };

  document.getElementById('reset-btn').onclick = () => {
    running = false;
    clearInterval(intervalId);
    elapsed = 0; startTime = null; laps = [];
    document.getElementById('timer-display').textContent = '00:00.00';
    document.getElementById('start-btn').disabled = false;
    document.getElementById('start-btn').textContent = 'Start';
    document.getElementById('pause-btn').disabled = true;
    document.getElementById('lap-btn').disabled = true;
    renderLaps();
  };

  document.getElementById('lap-btn').onclick = () => {
    if (!running) return;
    const now = performance.now();
    const total = elapsed + (now - startTime);
    const prev = laps.length ? laps[laps.length-1].total : 0;
    laps.push({ num: laps.length + 1, split: total - prev, total });
    renderLaps();
  };

  renderLaps();
"""
    return page("Stopwatch", body, extra_css=css, extra_js=js)
