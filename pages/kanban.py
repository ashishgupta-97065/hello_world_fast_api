"""Kanban Board mini-app page."""
from pages._shell import page


def render_kanban() -> str:
    """Return full HTML for /apps/kanban."""
    body = """
<h1 style="margin-bottom:1.5rem">Kanban Board</h1>
<div style="margin-bottom:1rem;display:flex;gap:0.75rem;align-items:center">
  <input type="text" id="new-card-title" placeholder="New card title…" style="max-width:300px">
  <textarea id="new-card-notes" placeholder="Notes (optional)" style="max-width:300px;min-height:unset;height:36px;resize:none"></textarea>
  <button class="btn btn-primary" id="add-card-btn">Add Card</button>
</div>
<p id="card-add-error" style="color:var(--danger);font-size:0.85rem;margin-bottom:0.75rem;display:none"></p>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem">
  <div class="kb-col" id="col-todo" data-col="todo">
    <div class="kb-col-header">
      <span>To Do</span><span class="col-count" id="count-todo">0</span>
    </div>
    <div class="kb-col-body" id="body-todo" ondragover="onDragOver(event)" ondrop="onDrop(event,'todo')"></div>
  </div>
  <div class="kb-col" id="col-in_progress" data-col="in_progress">
    <div class="kb-col-header">
      <span>In Progress</span><span class="col-count" id="count-in_progress">0</span>
    </div>
    <div class="kb-col-body" id="body-in_progress" ondragover="onDragOver(event)" ondrop="onDrop(event,'in_progress')"></div>
  </div>
  <div class="kb-col" id="col-done" data-col="done">
    <div class="kb-col-header">
      <span>Done</span><span class="col-count" id="count-done">0</span>
    </div>
    <div class="kb-col-body" id="body-done" ondragover="onDragOver(event)" ondrop="onDrop(event,'done')"></div>
  </div>
</div>
"""
    css = """
.kb-col {
  background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:0.75rem;
  min-height:300px;
}
.kb-col-header {
  display:flex; justify-content:space-between; align-items:center;
  font-weight:600; margin-bottom:0.75rem; padding-bottom:0.5rem;
  border-bottom:1px solid var(--border);
}
.col-count {
  background:var(--border); border-radius:999px;
  padding:0.1rem 0.55rem; font-size:0.78rem; font-weight:700;
}
.kb-card {
  background:var(--bg); border:1px solid var(--border); border-radius:8px;
  padding:0.65rem 0.85rem; margin-bottom:0.5rem; cursor:grab;
}
.kb-card:active { cursor:grabbing; opacity:0.8; }
.kb-card-title { font-weight:600; font-size:0.9rem; margin-bottom:0.25rem; }
.kb-card-notes { font-size:0.8rem; color:var(--text-muted); }
.kb-card-del { float:right; background:none; border:none; color:var(--danger); cursor:pointer; font-size:0.85rem; }
.kb-col-body.drag-over { background:rgba(92,107,192,0.1); border-radius:8px; }
"""
    js = r"""
  const KEY = 'kanban.v1';
  const COLS = ['todo','in_progress','done'];
  let state = { todo:[], in_progress:[], done:[] };
  let draggingId = null;
  let draggingFrom = null;

  function load() {
    try {
      const d = JSON.parse(localStorage.getItem(KEY));
      if (d) { COLS.forEach(c => { if (Array.isArray(d[c])) state[c] = d[c]; }); }
    } catch(e) {}
  }
  function save() { localStorage.setItem(KEY, JSON.stringify(state)); }

  function moveCard(st, cardId, fromCol, toCol) {
    const idx = st[fromCol].findIndex(c => c.id === cardId);
    if (idx === -1) return st;
    const [card] = st[fromCol].splice(idx, 1);
    st[toCol].push(card);
    return st;
  }

  function render() {
    COLS.forEach(col => {
      const body = document.getElementById('body-' + col);
      body.innerHTML = '';
      state[col].forEach(card => {
        const div = document.createElement('div');
        div.className = 'kb-card';
        div.draggable = true;
        div.dataset.id = card.id;
        div.dataset.col = col;

        const del = document.createElement('button');
        del.className = 'kb-card-del';
        del.textContent = '✕';
        del.onclick = (e) => {
          e.stopPropagation();
          const i = state[col].findIndex(c => c.id === card.id);
          if (i !== -1) { state[col].splice(i,1); save(); render(); }
        };

        const title = document.createElement('div');
        title.className = 'kb-card-title';
        title.textContent = card.title;

        div.append(del, title);

        if (card.notes) {
          const notes = document.createElement('div');
          notes.className = 'kb-card-notes';
          notes.textContent = card.notes;
          div.appendChild(notes);
        }

        div.addEventListener('dragstart', (e) => {
          draggingId = card.id;
          draggingFrom = col;
          e.dataTransfer.effectAllowed = 'move';
        });
        div.addEventListener('dragend', () => {
          draggingId = null; draggingFrom = null;
          document.querySelectorAll('.kb-col-body').forEach(b => b.classList.remove('drag-over'));
        });

        body.appendChild(div);
      });
      document.getElementById('count-' + col).textContent = state[col].length;
    });
  }

  window.onDragOver = function(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    const body = e.currentTarget;
    body.classList.add('drag-over');
  };

  window.onDrop = function(e, toCol) {
    e.preventDefault();
    document.querySelectorAll('.kb-col-body').forEach(b => b.classList.remove('drag-over'));
    if (!draggingId || !draggingFrom || draggingFrom === toCol) return;
    state = moveCard(state, draggingId, draggingFrom, toCol);
    save(); render();
  };

  document.getElementById('add-card-btn').onclick = () => {
    const err = document.getElementById('card-add-error');
    const title = document.getElementById('new-card-title').value.trim();
    const notes = document.getElementById('new-card-notes').value.trim();
    if (!title) { err.textContent = 'Card title cannot be empty.'; err.style.display=''; return; }
    err.style.display = 'none';
    state.todo.push({ id: Date.now()+Math.random()+'', title, notes });
    document.getElementById('new-card-title').value = '';
    document.getElementById('new-card-notes').value = '';
    save(); render();
  };

  load(); render();
"""
    return page("Kanban Board", body, extra_css=css, extra_js=js)
