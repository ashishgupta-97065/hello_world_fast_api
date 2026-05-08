"""Todo List mini-app page."""
from pages._shell import page


def render_todo() -> str:
    """Return full HTML for /apps/todo."""
    body = """
<h1 style="margin-bottom:1.5rem">Todo List</h1>
<div style="display:flex;gap:0.75rem;margin-bottom:1.25rem">
  <input type="text" id="task-input" placeholder="Enter a new task…" style="flex:1">
  <button class="btn btn-primary" id="add-btn">Add</button>
</div>
<p class="validation" id="empty-msg">Please enter a task first.</p>
<ul id="task-list" style="list-style:none;padding:0"></ul>
<p class="muted" id="empty-state" style="margin-top:1rem">No tasks yet — add one above!</p>
"""
    js = r"""
  const input   = document.getElementById('task-input');
  const addBtn  = document.getElementById('add-btn');
  const list    = document.getElementById('task-list');
  const emptyMsg= document.getElementById('empty-msg');
  const emptyState = document.getElementById('empty-state');
  let tasks = [];

  function render() {
    list.innerHTML = '';
    tasks.forEach((t, i) => {
      const li = document.createElement('li');
      li.style.cssText = 'display:flex;align-items:center;gap:0.75rem;padding:0.65rem 0.85rem;' +
        'background:var(--surface);border:1px solid var(--border);border-radius:8px;margin-bottom:0.5rem';
      const cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.checked = t.done;
      cb.style.cursor = 'pointer';
      cb.onchange = () => { tasks[i].done = cb.checked; render(); };
      const span = document.createElement('span');
      span.textContent = t.text;
      span.style.flex = '1';
      if (t.done) {
        span.style.textDecoration = 'line-through';
        span.style.color = 'var(--text-muted)';
      }
      const del = document.createElement('button');
      del.textContent = 'Delete';
      del.className = 'btn btn-ghost';
      del.style.padding = '0.25rem 0.6rem';
      del.style.fontSize = '0.8rem';
      del.onclick = () => { tasks.splice(i, 1); render(); };
      li.append(cb, span, del);
      list.appendChild(li);
    });
    emptyState.style.display = tasks.length ? 'none' : 'block';
  }

  function addTask() {
    const text = input.value.trim();
    if (!text) { emptyMsg.classList.add('visible'); return; }
    emptyMsg.classList.remove('visible');
    tasks.push({ text, done: false });
    input.value = '';
    render();
  }

  addBtn.onclick = addTask;
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') addTask();
  });

  render();
"""
    return page("Todo List", body, extra_js=js)
