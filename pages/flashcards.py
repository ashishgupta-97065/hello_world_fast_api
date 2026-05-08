"""Flashcard Study Deck mini-app page."""
from pages._shell import page


def render_flashcards() -> str:
    """Return full HTML for /apps/flashcards."""
    body = """
<h1 style="margin-bottom:1.5rem">Flashcard Study Deck</h1>
<div style="display:flex;gap:0.75rem;margin-bottom:1.5rem">
  <button class="btn btn-primary" id="tab-list" onclick="switchTab('list')">Card List</button>
  <button class="btn btn-secondary" id="tab-study" onclick="switchTab('study')">Study Mode</button>
</div>

<div id="view-list">
  <div style="display:grid;grid-template-columns:1fr 1fr auto;gap:0.75rem;align-items:end;margin-bottom:1rem">
    <div>
      <label style="font-size:0.85rem;color:var(--text-muted)">Front</label>
      <input type="text" id="card-front" placeholder="Question / term…">
    </div>
    <div>
      <label style="font-size:0.85rem;color:var(--text-muted)">Back</label>
      <input type="text" id="card-back" placeholder="Answer / definition…">
    </div>
    <button class="btn btn-primary" id="card-add-btn">Add Card</button>
  </div>
  <p id="card-error" style="color:var(--danger);font-size:0.85rem;margin-bottom:0.75rem;display:none"></p>
  <div id="card-list"><p class="muted">No cards yet — add some above!</p></div>
</div>

<div id="view-study" style="display:none;text-align:center">
  <div style="margin-bottom:1rem">
    <span>Correct: <strong id="stat-correct">0</strong></span> &nbsp;|&nbsp;
    <span>Wrong: <strong id="stat-wrong">0</strong></span> &nbsp;|&nbsp;
    <span>Remaining: <strong id="stat-remaining">0</strong></span>
  </div>
  <div id="flashcard-display" style="min-height:180px;background:var(--surface);border:1px solid var(--border);border-radius:16px;display:flex;align-items:center;justify-content:center;padding:2rem;margin-bottom:1rem;cursor:pointer" onclick="flipCard()">
    <div>
      <p id="card-side-label" style="font-size:0.78rem;color:var(--text-muted);margin-bottom:0.5rem">FRONT</p>
      <p id="card-content" style="font-size:1.3rem;font-weight:600">No cards to study.</p>
    </div>
  </div>
  <div style="display:flex;gap:0.75rem;justify-content:center;margin-bottom:1rem">
    <button class="btn btn-primary" id="flip-btn" onclick="flipCard()">Flip</button>
    <button class="btn btn-secondary" id="correct-btn" onclick="markCorrect()">✓ Correct</button>
    <button class="btn btn-ghost" id="wrong-btn" onclick="markWrong()">✗ Wrong</button>
  </div>
  <p id="study-done" style="display:none;color:var(--success)">Session complete!</p>
</div>
"""
    css = """
.card-item {
  display:flex; align-items:center; gap:0.75rem;
  padding:0.65rem 0.85rem;
  background:var(--surface); border:1px solid var(--border); border-radius:8px; margin-bottom:0.5rem;
}
.card-face { font-size:0.85rem; flex:1; }
.card-sep { color:var(--text-muted); }
"""
    js = r"""
  const KEY = 'flashcards.v1';
  let state = { cards: [] };
  let session = { queue: [], idx: 0, correct: 0, wrong: 0, flipped: false };

  function load() {
    try { const d = JSON.parse(localStorage.getItem(KEY)); if (d && Array.isArray(d.cards)) state = d; }
    catch(e) {}
  }
  function save() { localStorage.setItem(KEY, JSON.stringify(state)); }

  function switchTab(tab) {
    document.getElementById('view-list').style.display = tab==='list' ? '' : 'none';
    document.getElementById('view-study').style.display = tab==='study' ? '' : 'none';
    document.getElementById('tab-list').className = 'btn ' + (tab==='list' ? 'btn-primary' : 'btn-secondary');
    document.getElementById('tab-study').className = 'btn ' + (tab==='study' ? 'btn-primary' : 'btn-secondary');
    if (tab === 'study') startSession();
  }
  window.switchTab = switchTab;

  function nextCard(sess) {
    if (sess.idx >= sess.queue.length) return null;
    return sess.queue[sess.idx];
  }

  function startSession() {
    session = { queue: [...state.cards], idx: 0, correct: 0, wrong: 0, flipped: false };
    renderStudy();
  }

  function renderStudy() {
    const card = nextCard(session);
    const remaining = session.queue.length - session.idx;
    document.getElementById('stat-correct').textContent = session.correct;
    document.getElementById('stat-wrong').textContent = session.wrong;
    document.getElementById('stat-remaining').textContent = remaining;
    const done = document.getElementById('study-done');
    if (!card) {
      document.getElementById('card-content').textContent = 'No cards to study.';
      document.getElementById('card-side-label').textContent = '';
      done.style.display = remaining === 0 && session.queue.length > 0 ? '' : 'none';
      return;
    }
    done.style.display = 'none';
    document.getElementById('card-side-label').textContent = session.flipped ? 'BACK' : 'FRONT';
    const el = document.getElementById('card-content');
    el.textContent = session.flipped ? card.back : card.front;
  }

  function flipCard() {
    session.flipped = !session.flipped;
    renderStudy();
  }
  window.flipCard = flipCard;

  function markCorrect() {
    if (nextCard(session) === null) return;
    session.correct++; session.idx++; session.flipped = false; renderStudy();
  }
  window.markCorrect = markCorrect;

  function markWrong() {
    if (nextCard(session) === null) return;
    session.wrong++; session.idx++; session.flipped = false; renderStudy();
  }
  window.markWrong = markWrong;

  function renderList() {
    const list = document.getElementById('card-list');
    if (!state.cards.length) { list.innerHTML = '<p class="muted">No cards yet — add some above!</p>'; return; }
    list.innerHTML = '';
    state.cards.forEach((c, i) => {
      const div = document.createElement('div');
      div.className = 'card-item';
      const front = document.createElement('span');
      front.className = 'card-face';
      front.textContent = c.front;
      const sep = document.createElement('span');
      sep.className = 'card-sep';
      sep.textContent = '→';
      const back = document.createElement('span');
      back.className = 'card-face';
      back.textContent = c.back;
      const del = document.createElement('button');
      del.className = 'btn btn-ghost';
      del.style.fontSize = '0.8rem';
      del.style.padding = '0.2rem 0.5rem';
      del.textContent = 'Delete';
      del.onclick = () => { state.cards.splice(i, 1); save(); renderList(); };
      div.append(front, sep, back, del);
      list.appendChild(div);
    });
  }

  document.getElementById('card-add-btn').onclick = () => {
    const err = document.getElementById('card-error');
    const front = document.getElementById('card-front').value.trim();
    const back = document.getElementById('card-back').value.trim();
    if (!front) { err.textContent = 'Front cannot be empty.'; err.style.display=''; return; }
    if (!back) { err.textContent = 'Back cannot be empty.'; err.style.display=''; return; }
    err.style.display = 'none';
    state.cards.push({ id: Date.now()+Math.random(), front, back });
    document.getElementById('card-front').value = '';
    document.getElementById('card-back').value = '';
    save(); renderList();
  };

  load(); renderList(); renderStudy();
"""
    return page("Flashcard Study Deck", body, extra_css=css, extra_js=js)
