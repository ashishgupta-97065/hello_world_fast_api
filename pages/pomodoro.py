"""Pomodoro Timer mini-app page."""
from pages._shell import page


def render_pomodoro() -> str:
    """Return full HTML for /apps/pomodoro."""
    body = """
<div style="text-align:center;padding:2rem 0">
  <h1 style="margin-bottom:1.5rem">Pomodoro Timer</h1>
  <div id="mode-badge" class="badge badge-info" style="margin-bottom:1.5rem;font-size:1rem">Work Session</div>
  <div id="timer-display" class="mono"
       style="font-size:96px;font-weight:700;letter-spacing:0.05em;color:var(--text);margin-bottom:2rem">
    25:00
  </div>
  <div style="display:flex;justify-content:center;gap:1rem">
    <button class="btn btn-primary" id="start-btn">Start</button>
    <button class="btn btn-secondary" id="pause-btn" disabled>Pause</button>
    <button class="btn btn-secondary" id="reset-btn">Reset</button>
  </div>
</div>
"""
    js = r"""
  const WORK_SECS  = 25 * 60;  // 1500
  const BREAK_SECS = 5  * 60;  // 300  (5:00)
  let secondsRemaining = WORK_SECS;
  let isWork  = true;
  let running = false;
  let timerId = null;

  const display    = document.getElementById('timer-display');
  const badge      = document.getElementById('mode-badge');
  const startBtn   = document.getElementById('start-btn');
  const pauseBtn   = document.getElementById('pause-btn');
  const resetBtn   = document.getElementById('reset-btn');

  function fmt(s) {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return String(m).padStart(2,'0') + ':' + String(sec).padStart(2,'0');
  }

  function updateDisplay() {
    display.textContent = fmt(secondsRemaining);
  }

  function tick() {
    if (secondsRemaining > 0) {
      secondsRemaining--;
      updateDisplay();
    } else {
      clearInterval(timerId);
      timerId = null;
      running = false;
      isWork = !isWork;
      secondsRemaining = isWork ? WORK_SECS : BREAK_SECS;
      badge.textContent  = isWork ? 'Work Session' : 'Break';
      badge.className    = 'badge ' + (isWork ? 'badge-info' : 'badge-success');
      updateDisplay();
      startBtn.disabled = false;
      pauseBtn.disabled = true;
    }
  }

  startBtn.onclick = () => {
    if (running) return;
    running = true;
    timerId = setInterval(tick, 1000);
    startBtn.disabled = true;
    pauseBtn.disabled = false;
  };

  pauseBtn.onclick = () => {
    if (!running) return;
    clearInterval(timerId);
    timerId = null;
    running = false;
    startBtn.disabled = false;
    pauseBtn.disabled = true;
  };

  resetBtn.onclick = () => {
    clearInterval(timerId);
    timerId = null;
    running = false;
    isWork  = true;
    secondsRemaining = WORK_SECS;
    badge.textContent = 'Work Session';
    badge.className   = 'badge badge-info';
    updateDisplay();
    startBtn.disabled = false;
    pauseBtn.disabled = true;
  };

  updateDisplay();
"""
    return page("Pomodoro Timer", body, extra_js=js)
