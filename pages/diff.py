"""Text Diff Viewer mini-app page."""
from pages._shell import page


def render_diff() -> str:
    """Return full HTML for /apps/diff."""
    body = """
<h1 style="margin-bottom:1.5rem">Text Diff Viewer</h1>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem">
  <div>
    <label style="font-size:0.85rem;color:var(--text-muted);display:block;margin-bottom:0.35rem">Original</label>
    <textarea id="diff-original" style="height:220px;font-family:'Courier New',monospace;font-size:0.85rem" placeholder="Paste original text here…"></textarea>
  </div>
  <div>
    <label style="font-size:0.85rem;color:var(--text-muted);display:block;margin-bottom:0.35rem">Modified</label>
    <textarea id="diff-modified" style="height:220px;font-family:'Courier New',monospace;font-size:0.85rem" placeholder="Paste modified text here…"></textarea>
  </div>
</div>
<div style="display:flex;gap:0.75rem;margin-bottom:1rem">
  <button class="btn btn-primary" id="compare-btn">Compare</button>
  <button class="btn btn-ghost" id="clear-btn">Clear</button>
</div>
<div id="diff-stats" style="font-size:0.85rem;color:var(--text-muted);margin-bottom:0.75rem"></div>
<div id="diff-output" style="font-family:'Courier New',monospace;font-size:0.85rem;background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:0.75rem;overflow:auto;min-height:80px"></div>
"""
    css = """
.diff-line { padding:0.1rem 0.5rem; border-radius:3px; white-space:pre-wrap; word-break:break-all; }
.diff-add { background:rgba(38,166,154,0.18); color:var(--success); }
.diff-del { background:rgba(239,83,80,0.18); color:var(--danger); }
.diff-eq  { color:var(--text-muted); }
"""
    js = r"""
  function diffLines(a, b) {
    const m = a.length, n = b.length;
    const dp = Array.from({length:m+1}, () => new Array(n+1).fill(0));
    for (let i=m-1; i>=0; i--)
      for (let j=n-1; j>=0; j--)
        dp[i][j] = a[i]===b[j] ? dp[i+1][j+1]+1 : Math.max(dp[i+1][j], dp[i][j+1]);
    const ops = [];
    let i=0, j=0;
    while (i<m && j<n) {
      if (a[i]===b[j]) { ops.push({type:'eq',text:a[i]}); i++; j++; }
      else if (dp[i+1][j] >= dp[i][j+1]) { ops.push({type:'del',text:a[i]}); i++; }
      else { ops.push({type:'add',text:b[j]}); j++; }
    }
    while (i<m) { ops.push({type:'del',text:a[i++]}); }
    while (j<n) { ops.push({type:'add',text:b[j++]}); }
    return ops;
  }

  document.getElementById('compare-btn').onclick = () => {
    const aText = document.getElementById('diff-original').value;
    const bText = document.getElementById('diff-modified').value;
    const aLines = aText === '' ? [] : aText.split('\n');
    const bLines = bText === '' ? [] : bText.split('\n');
    const ops = diffLines(aLines, bLines);

    let added = 0, removed = 0;
    ops.forEach(op => { if (op.type==='add') added++; else if (op.type==='del') removed++; });
    document.getElementById('diff-stats').textContent =
      '+' + added + ' added   −' + removed + ' removed   =' + (ops.length-added-removed) + ' unchanged';

    const out = document.getElementById('diff-output');
    out.innerHTML = '';
    if (!ops.length) { out.textContent = '(empty)'; return; }
    ops.forEach(op => {
      const div = document.createElement('div');
      div.className = 'diff-line diff-' + op.type;
      const prefix = op.type==='add' ? '+ ' : op.type==='del' ? '− ' : '  ';
      div.textContent = prefix + op.text;
      out.appendChild(div);
    });
  };

  document.getElementById('clear-btn').onclick = () => {
    document.getElementById('diff-original').value = '';
    document.getElementById('diff-modified').value = '';
    document.getElementById('diff-output').innerHTML = '';
    document.getElementById('diff-stats').textContent = '';
  };
"""
    return page("Text Diff Viewer", body, extra_css=css, extra_js=js)
