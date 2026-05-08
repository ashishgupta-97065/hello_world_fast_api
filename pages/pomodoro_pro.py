"""Pomodoro Pro mini-app page."""
from pages._shell import page


def render_pomodoro_pro() -> str:
    """Return full HTML for /apps/pomodoro-pro."""
    body = """
<h1 style="margin-bottom:1.25rem">Pomodoro Pro</h1>
<div style="display:grid;grid-template-columns:1fr 340px;gap:1.5rem;align-items:start">
  <div>
    <div style="display:flex;gap:0.5rem;margin-bottom:1.25rem">
      <button class="btn btn-primary mode-btn" id="mode-work" data-mode="work">Work</button>
      <button class="btn btn-secondary mode-btn" id="mode-short" data-mode="short">Short Break</button>
      <button class="btn btn-secondary mode-btn" id="mode-long" data-mode="long">Long Break</button>
    </div>

    <div style="display:flex;justify-content:center;margin-bottom:1.25rem">
      <svg width="200" height="200" viewBox="0 0 200 200">
        <circle cx="100" cy="100" r="88" fill="none" stroke="var(--border)" stroke-width="12"/>
        <circle id="ring-progress" cx="100" cy="100" r="88"
          fill="none" stroke="var(--accent)" stroke-width="12"
          stroke-linecap="round"
          stroke-dasharray="553"
          stroke-dashoffset="0"
          transform="rotate(-90 100 100)"/>
        <text x="100" y="108" text-anchor="middle" font-size="36" font-weight="700" fill="var(--text)" id="ring-label">25:00</text>
      </svg>
    </div>

    <div style="display:flex;gap:0.75rem;justify-content:center;margin-bottom:1.5rem">
      <button class="btn btn-primary" id="start-btn">Start</button>
      <button class="btn btn-secondary" id="pause-btn" disabled>Pause</button>
      <button class="btn btn-ghost" id="reset-btn">Reset</button>
    </div>

    <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:1rem;margin-bottom:1rem">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem">
        <span style="font-size:0.9rem;font-weight:600">Today's Focus</span>
        <span id="focus-total" style="font-size:0.9rem;color:var(--accent)">0 min</span>
      </div>
      <div style="display:flex;gap:1.5rem;font-size:0.85rem">
        <label style="display:flex;align-items:center;gap:0.4rem">
          <input type="checkbox" id="auto-advance"> Auto-advance
        </label>
        <label style="display:flex;align-items:center;gap:0.4rem">
          <input type="checkbox" id="sound-cue"> Sound cue
        </label>
      </div>
    </div>
  </div>

  <div>
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:1rem;margin-bottom:1rem">
      <h3 style="font-size:0.9rem;margin-bottom:0.75rem">Settings</h3>
      <div style="display:grid;gap:0.5rem;font-size:0.85rem">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <label>Work (min)</label>
          <input type="number" id="work-min" value="25" min="1" max="120" step="1" style="width:60px">
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <label>Short Break (min)</label>
          <input type="number" id="short-min" value="5" min="1" max="60" step="1" style="width:60px">
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <label>Long Break (min)</label>
          <input type="number" id="long-min" value="15" min="1" max="120" step="1" style="width:60px">
        </div>
      </div>
    </div>

    <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:1rem">
      <h3 style="font-size:0.9rem;margin-bottom:0.75rem">Session Log</h3>
      <div class="session-log" id="session-log" style="max-height:200px;overflow-y:auto;font-size:0.82rem">
        <p class="muted">Completed sessions appear here.</p>
      </div>
    </div>
  </div>
</div>
"""
    css = """
.mode-btn.active { background:var(--accent); color:#fff; border-color:var(--accent); }
"""
    js = r"""
  const CIRCUMFERENCE = 553;
  const SETTINGS_KEY = 'pomodoro_pro.settings.v1';

  let settings = { workMin:25, shortMin:5, longMin:15, autoAdvance:false, soundCue:false };
  let mode = 'work';
  let totalSecs = 25 * 60;
  let remainSecs = totalSecs;
  let running = false;
  let intervalId = null;
  let audioCtx = null;

  function loadSettings() {
    try {
      const d = JSON.parse(localStorage.getItem(SETTINGS_KEY));
      if (d) settings = { ...settings, ...d };
    } catch(e) {}
    document.getElementById('work-min').value = settings.workMin;
    document.getElementById('short-min').value = settings.shortMin;
    document.getElementById('long-min').value = settings.longMin;
    document.getElementById('auto-advance').checked = settings.autoAdvance;
    document.getElementById('sound-cue').checked = settings.soundCue;
  }
  function saveSettings() {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
  }

  function todayKey() {
    return 'pomodoro_pro.focus.' + new Date().toISOString().slice(0,10);
  }
  function getFocusTotal() {
    try { return parseFloat(localStorage.getItem(todayKey())) || 0; }
    catch(e) { return 0; }
  }
  function addFocusMinutes(mins) {
    const v = getFocusTotal() + mins;
    localStorage.setItem(todayKey(), v.toString());
    document.getElementById('focus-total').textContent = Math.round(v) + ' min';
  }

  function ringOffset(elapsed, total, circ) {
    if (total === 0) return 0;
    return circ * (elapsed / total);
  }

  function updateRing() {
    const elapsed = totalSecs - remainSecs;
    const offset = ringOffset(elapsed, totalSecs, CIRCUMFERENCE);
    document.getElementById('ring-progress').setAttribute('stroke-dashoffset', CIRCUMFERENCE - offset);
    const m = Math.floor(remainSecs / 60);
    const s = remainSecs % 60;
    document.getElementById('ring-label').textContent = String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
  }

  function setMode(m) {
    mode = m;
    document.querySelectorAll('.mode-btn').forEach(b => {
      b.className = 'btn mode-btn ' + (b.dataset.mode === m ? 'btn-primary active' : 'btn-secondary');
    });
    const mins = m === 'work' ? settings.workMin : m === 'short' ? settings.shortMin : settings.longMin;
    totalSecs = mins * 60;
    remainSecs = totalSecs;
    stopTimer();
    updateRing();
  }

  function stopTimer() {
    running = false;
    clearInterval(intervalId);
    document.getElementById('start-btn').disabled = false;
    document.getElementById('pause-btn').disabled = true;
    document.getElementById('start-btn').textContent = 'Start';
  }

  function beep() {
    if (!settings.soundCue) return;
    try {
      if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.connect(gain); gain.connect(audioCtx.destination);
      osc.frequency.value = 880;
      osc.type = 'sine';
      gain.gain.setValueAtTime(0.5, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.2);
      osc.start(audioCtx.currentTime);
      osc.stop(audioCtx.currentTime + 0.2);
    } catch(e) {}
  }

  function sessionComplete() {
    beep();
    if (mode === 'work') {
      const mins = settings.workMin;
      addFocusMinutes(mins);
      const log = document.getElementById('session-log');
      if (log.querySelector('.muted')) log.innerHTML = '';
      const entry = document.createElement('div');
      entry.style.padding = '0.25rem 0';
      entry.style.borderBottom = '1px solid var(--border)';
      const now = new Date();
      entry.textContent = now.toLocaleTimeString() + ' — Work ' + mins + 'min ✓';
      log.insertBefore(entry, log.firstChild);
    }
    stopTimer();
    if (settings.autoAdvance) {
      const next = mode === 'work' ? 'short' : 'work';
      setMode(next);
      document.getElementById('start-btn').click();
    }
  }

  document.getElementById('start-btn').onclick = () => {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    running = true;
    document.getElementById('start-btn').disabled = true;
    document.getElementById('pause-btn').disabled = false;
    intervalId = setInterval(() => {
      if (remainSecs <= 0) { clearInterval(intervalId); sessionComplete(); return; }
      remainSecs--;
      updateRing();
    }, 1000);
  };

  document.getElementById('pause-btn').onclick = () => {
    running = false;
    clearInterval(intervalId);
    document.getElementById('start-btn').disabled = false;
    document.getElementById('start-btn').textContent = 'Resume';
    document.getElementById('pause-btn').disabled = true;
  };

  document.getElementById('reset-btn').onclick = () => {
    remainSecs = totalSecs;
    stopTimer();
    updateRing();
  };

  document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.onclick = () => setMode(btn.dataset.mode);
  });

  ['work-min','short-min','long-min'].forEach(id => {
    document.getElementById(id).onchange = () => {
      settings.workMin = parseInt(document.getElementById('work-min').value) || 25;
      settings.shortMin = parseInt(document.getElementById('short-min').value) || 5;
      settings.longMin = parseInt(document.getElementById('long-min').value) || 15;
      saveSettings(); setMode(mode);
    };
  });

  document.getElementById('auto-advance').onchange = e => {
    settings.autoAdvance = e.target.checked; saveSettings();
  };
  document.getElementById('sound-cue').onchange = e => {
    settings.soundCue = e.target.checked; saveSettings();
  };

  document.getElementById('focus-total').textContent = Math.round(getFocusTotal()) + ' min';
  loadSettings();
  setMode('work');
"""
    return page("Pomodoro Pro", body, extra_css=css, extra_js=js)
