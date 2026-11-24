"""Render the milestone graph as one self-contained interactive HTML page.

No external assets: all CSS/JS is inline and the graph data is embedded.
Open the file in any browser.

Features (DESIGN.md §9):
  - Trace view: layered DAG layout by depth (root at top, predecessors
    below), SVG edges, expand/collapse of predecessor branches.
  - Timeline view: nodes laid out by year on a horizontal axis.
  - Click a node: detail panel with bottleneck sentence, definition,
    status, sources, and the full 12-question verdict table (with
    evidence and falsification notes) for every edge it enables.
  - Search box: jump to a node by name or alias.
"""

import json

QUESTIONS = {
    "Q1": "Impossibility flip", "Q2": "Generativity", "Q3": "Necessity",
    "Q4": "Cost collapse", "Q5": "Measurability", "Q6": "Understanding",
    "Q7": "Composability", "Q8": "Cross-domain reach", "Q9": "Iteration speed",
    "Q10": "Displacement", "Q11": "Lineage centrality", "Q12": "Irreversibility",
}

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Behind 01 — Tracing the Milestones</title>
<style>
  :root{ --ink:#1c1a17; --muted:#6b655c; --paper:#faf8f4; --card:#fff;
         --line:#e3ded4; --accent:#8a5a2b; --soft:#f3e9dc; }
  *{box-sizing:border-box}
  body{margin:0;background:var(--paper);color:var(--ink);
       font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif}
  header{padding:18px 20px 10px;border-bottom:2px solid var(--ink)}
  header h1{margin:0 0 4px;font-size:24px}
  header p{margin:0;color:var(--muted);font-size:14px}
  .bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:12px 20px}
  .bar button,.bar input{font-size:14px;padding:7px 12px;border:1px solid var(--line);
    border-radius:8px;background:var(--card)}
  .bar button{cursor:pointer}
  .bar button.active{background:var(--ink);color:#fff;border-color:var(--ink)}
  .bar input{min-width:220px;flex:0 1 320px}
  #stats{color:var(--muted);font-size:13px;margin-left:auto}
  #stage{overflow:auto;border-top:1px solid var(--line);background:
    radial-gradient(circle,#e7e0d2 1px,transparent 1px);background-size:22px 22px}
  svg{display:block}
  .node{cursor:pointer}
  .node rect{fill:var(--card);stroke:var(--ink);stroke-width:1.2}
  .node.verified rect{stroke:var(--accent);stroke-width:2.2}
  .node.selected rect{fill:var(--soft);stroke:var(--accent);stroke-width:2.6}
  .node text{font-size:12.5px;fill:var(--ink);pointer-events:none}
  .node .yr{font-size:11px;fill:var(--muted)}
  .node.dim{opacity:.25}
  .edge{stroke:#b9ac93;stroke-width:1.4;fill:none;opacity:.75}
  .edge.hl{stroke:var(--accent);stroke-width:2.6;opacity:1}
  .toggle{cursor:pointer}
  .toggle circle{fill:var(--ink)}
  .toggle text{fill:#fff;font-size:12px;font-weight:700;pointer-events:none}
  #panel{border-top:2px solid var(--ink);background:var(--card);padding:18px 20px 30px}
  #panel h2{margin:0 0 2px;font-size:21px}
  #panel .meta{color:var(--muted);font-size:13.5px;margin-bottom:8px}
  .badge{display:inline-block;padding:1px 8px;border-radius:99px;font-size:12px;
    border:1px solid var(--accent);color:var(--accent);margin-left:6px}
  .badge.prov{border-color:var(--muted);color:var(--muted)}
  blockquote{margin:10px 0;padding:10px 14px;background:var(--soft);
    border-left:3px solid var(--accent);border-radius:0 8px 8px 0}
  table{border-collapse:collapse;width:100%;font-size:13.5px;margin:8px 0 16px}
  th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
  th{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.05em}
  .vpass{color:#1e7a1e;font-weight:700}.vpartial{color:#b07d10;font-weight:700}.vfail{color:#b03030;font-weight:700}
  .src{font-size:13px;color:var(--muted)}
  #searchResults{padding:0 20px}
  #searchResults button{display:block;margin:4px 0;padding:6px 10px;background:var(--card);
    border:1px solid var(--line);border-radius:8px;cursor:pointer;font-size:14px}
  .hint{color:var(--muted);font-size:13px;padding:0 20px 8px}
</style>
</head>
<body>
<header>
  <h1>Tracing the Milestones</h1>
  <p>The Behind · 01 — the breakthroughs that made the modern AI agent possible, traced backwards. Click any node for its evidence.</p>
</header>
<div class="bar">
  <button id="btnTrace" class="active">Trace view</button>
  <button id="btnTime">Timeline view</button>
  <input id="search" type="search" placeholder="Search a node or alias…">
  <span id="stats"></span>
</div>
<div id="searchResults"></div>
<div id="stage"></div>
<p class="hint">In Trace view, use the +/− button on a node to collapse or expand the branch behind it. Gold outline = verified by the adversarial pass; grey badge = provisional.</p>
<div id="panel"><p style="color:var(--muted)">Select a node to see its bottleneck sentence, verdicts, and sources.</p></div>

<script>
const GRAPH = __GRAPH_JSON__;
const QNAMES = __Q_JSON__;
const nodes = {}; GRAPH.nodes.forEach(n => nodes[n.id] = n);
const preds = {};   // successor_id -> [predecessor nodes]
const succs = {};   // predecessor_id -> [successor nodes]
GRAPH.nodes.forEach(n => { preds[n.id] = []; succs[n.id] = []; });
GRAPH.edges.forEach(e => {
  if (nodes[e.predecessor_id] && nodes[e.successor_id]) {
    preds[e.successor_id].push(nodes[e.predecessor_id]);
    succs[e.predecessor_id].push(nodes[e.successor_id]);
  }
});
const root = GRAPH.nodes.reduce((a,b) => (a.depth <= b.depth ? a : b), GRAPH.nodes[0]);
let mode = 'trace';
let collapsed = new Set();
let selected = null;

function visibleNodes() {
  if (mode === 'time') return GRAPH.nodes;
  const hidden = new Set();
  collapsed.forEach(cid => {
    // hide predecessor-branch nodes reachable only through cid
    const stack = [...preds[cid]];
    while (stack.length) {
      const n = stack.pop();
      if (hidden.has(n.id)) continue;
      const otherVisibleSucc = succs[n.id].some(s => s.id !== cid && !hidden.has(s.id) && !collapsed.has(s.id));
      if (otherVisibleSucc) continue;
      hidden.add(n.id);
      stack.push(...preds[n.id]);
    }
  });
  return GRAPH.nodes.filter(n => !hidden.has(n.id));
}

function layoutTrace(vis) {
  const byDepth = {};
  vis.forEach(n => { (byDepth[n.depth] = byDepth[n.depth] || []).push(n); });
  const depths = Object.keys(byDepth).map(Number).sort((a,b) => a-b);
  const pos = {}; const NW = 208, NH = 54, GX = 26, GY = 92;
  let maxRow = 0;
  depths.forEach(d => {
    const row = byDepth[d].slice().sort((a,b) => (a.year||9999) - (b.year||9999) || a.name.localeCompare(b.name));
    maxRow = Math.max(maxRow, row.length);
    row.forEach((n, i) => { pos[n.id] = { x: 30 + i * (NW + GX), y: 26 + (d - depths[0]) * GY, n }; });
  });
  return { pos, w: 60 + maxRow * (NW + GX), h: 40 + depths.length * GY };
}

function layoutTime(vis) {
  const years = vis.map(n => n.year).filter(y => y !== null && y !== undefined);
  const minY = Math.min(...years), maxY = Math.max(...years);
  const W = Math.max(1100, vis.length * 30), pad = 90;
  const span = Math.max(1, maxY - minY);
  const lanes = {};
  const pos = {};
  vis.slice().sort((a,b) => (a.year||0) - (b.year||0)).forEach(n => {
    const x = pad + ((n.year ?? maxY) - minY) / span * (W - 2 * pad);
    let lane = 0;
    while (true) {
      const used = lanes[lane] || [];
      if (used.every(u => Math.abs(u - x) > 200)) { used.push(x); lanes[lane] = used; break; }
      lane++;
    }
    pos[n.id] = { x: x - 100, y: 40 + lane * 78, n };
  });
  const laneCount = Object.keys(lanes).length || 1;
  return { pos, w: W, h: 60 + laneCount * 78, axis: { minY, maxY, W, pad, span } };
}

function esc(s){ return String(s ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;'); }

function draw() {
  const vis = visibleNodes();
  const L = mode === 'trace' ? layoutTrace(vis) : layoutTime(vis);
  const visIds = new Set(vis.map(n => n.id));
  let s = `<svg width="${L.w}" height="${L.h}" viewBox="0 0 ${L.w} ${L.h}">`;
  if (mode === 'time' && L.axis) {
    const a = L.axis;
    s += `<line x1="${a.pad}" y1="${L.h - 24}" x2="${a.W - a.pad}" y2="${L.h - 24}" stroke="#1c1a17"/>`;
    for (let i = 0; i <= 6; i++) {
      const yr = Math.round(a.minY + a.span * i / 6), x = a.pad + (a.W - 2 * a.pad) * i / 6;
      s += `<text x="${x}" y="${L.h - 6}" font-size="11" fill="#6b655c" text-anchor="middle">${yr}</text>`;
    }
  }
  GRAPH.edges.forEach(e => {
    if (!visIds.has(e.predecessor_id) || !visIds.has(e.successor_id)) return;
    const a = L.pos[e.successor_id], b = L.pos[e.predecessor_id];
    if (!a || !b) return;
    const x1 = a.x + 104, y1 = a.y + 54, x2 = b.x + 104, y2 = b.y;
    const hl = selected && (e.predecessor_id === selected || e.successor_id === selected) ? 'edge hl' : 'edge';
    s += `<path class="${hl}" d="M${x1},${y1} C${x1},${y1 + 34} ${x2},${y2 - 34} ${x2},${y2}"/>`;
  });
  vis.forEach(n => {
    const p = L.pos[n.id]; if (!p) return;
    const cls = ['node', n.status === 'verified' ? 'verified' : '', selected === n.id ? 'selected' : ''].join(' ');
    const name = n.name.length > 26 ? n.name.slice(0, 25) + '…' : n.name;
    s += `<g class="${cls}" data-id="${n.id}" transform="translate(${p.x},${p.y})">
      <rect width="208" height="54" rx="9"></rect>
      <text x="10" y="23">${esc(name)}</text>
      <text class="yr" x="10" y="41">${n.year ?? ''} · depth ${n.depth} · in-degree ${GRAPH.edges.filter(e => e.predecessor_id === n.id).length}</text>
    </g>`;
    if (mode === 'trace' && preds[n.id].length) {
      const isC = collapsed.has(n.id);
      s += `<g class="toggle" data-toggle="${n.id}" transform="translate(${p.x + 196},${p.y + 54})">
        <circle r="10"></circle><text text-anchor="middle" dy="4">${isC ? '+' : '−'}</text></g>`;
    }
  });
  s += '</svg>';
  document.getElementById('stage').innerHTML = s;
  document.querySelectorAll('.node').forEach(g => g.addEventListener('click', () => selectNode(g.dataset.id)));
  document.querySelectorAll('.toggle').forEach(g => g.addEventListener('click', ev => {
    ev.stopPropagation();
    const id = g.dataset.toggle;
    collapsed.has(id) ? collapsed.delete(id) : collapsed.add(id);
    draw();
  }));
}

function verdictTable(edge) {
  let rows = '';
  for (let i = 1; i <= 12; i++) {
    const q = 'Q' + i, v = (edge.verdicts || {})[q];
    if (!v) continue;
    rows += `<tr><td><b>${q}</b> ${QNAMES[q]}</td><td class="v${v.verdict}">${v.verdict}</td>
      <td>${esc(v.evidence)}</td><td>${esc(v.falsification)}</td></tr>`;
  }
  return `<table><tr><th>Question</th><th>Verdict</th><th>Evidence</th><th>Falsification note</th></tr>${rows}</table>`;
}

function selectNode(id) {
  selected = id;
  const n = nodes[id]; if (!n) return;
  const badge = n.status === 'verified' ? '<span class="badge">verified</span>' : '<span class="badge prov">provisional</span>';
  let h = `<h2>${esc(n.name)}${badge}</h2>
    <div class="meta">${n.year ?? 'year unknown'} · ${esc(n.domain)} · ${esc(n.type)} · depth ${n.depth} · aliases: ${esc((n.aliases || []).join(', ') || '—')}</div>
    <p>${esc(n.definition)}</p>
    <blockquote><b>Bottleneck it removed:</b> ${esc(n.bottleneck)}</blockquote>`;
  const outEdges = GRAPH.edges.filter(e => e.predecessor_id === id);
  if (outEdges.length) {
    h += '<h3>How it scored, per node it enables</h3>';
    outEdges.forEach(e => {
      h += `<p><b>Enables:</b> ${esc(nodes[e.successor_id].name)} · score ${e.score} · gate ${e.gate && e.gate.passed ? 'passed' : '—'}</p>` + verdictTable(e);
    });
  }
  const inEdges = GRAPH.edges.filter(e => e.successor_id === id);
  if (inEdges.length) h += `<p><b>Enabled by:</b> ${inEdges.map(e => esc(nodes[e.predecessor_id].name)).join(' · ')}</p>`;
  if (n.verification) h += `<p><b>Verifier:</b> ${esc(n.verification.outcome)} — ${esc(n.verification.notes)}</p>`;
  if ((n.sources || []).length) {
    h += '<h3>Sources</h3>' + n.sources.map(s2 => `<div class="src">• ${esc(s2.title)} — <a href="${esc(s2.url)}" target="_blank" rel="noopener">${esc(s2.url)}</a></div>`).join('');
  }
  document.getElementById('panel').innerHTML = h;
  draw();
}

document.getElementById('btnTrace').addEventListener('click', () => { mode = 'trace'; document.getElementById('btnTrace').classList.add('active'); document.getElementById('btnTime').classList.remove('active'); draw(); });
document.getElementById('btnTime').addEventListener('click', () => { mode = 'time'; document.getElementById('btnTime').classList.add('active'); document.getElementById('btnTrace').classList.remove('active'); draw(); });
document.getElementById('search').addEventListener('input', ev => {
  const q = ev.target.value.trim().toLowerCase();
  const box = document.getElementById('searchResults');
  if (!q) { box.innerHTML = ''; return; }
  const hits = GRAPH.nodes.filter(n => n.name.toLowerCase().includes(q) || (n.aliases || []).some(a => a.toLowerCase().includes(q))).slice(0, 8);
  box.innerHTML = '';
  hits.forEach(n => {
    const b = document.createElement('button');
    b.textContent = `${n.name} (${n.year ?? ''})`;
    b.addEventListener('click', () => { collapsed.clear(); selectNode(n.id); });
    box.appendChild(b);
  });
});

const ver = GRAPH.nodes.filter(n => n.status === 'verified').length;
document.getElementById('stats').textContent = `${GRAPH.nodes.length} nodes · ${GRAPH.edges.length} edges · ${ver} verified · profile: ${GRAPH.profile}`;
draw();
if (root) selectNode(root.id);
</script>
</body>
</html>
"""


def render(graph_data, profile=""):
    public = {
        "nodes": [
            {k: n.get(k) for k in ("id", "name", "aliases", "year", "domain", "type",
                                    "definition", "bottleneck", "status", "depth",
                                    "sources", "verification")}
            for n in graph_data["nodes"].values() if n.get("merged_into") is None
        ],
        "edges": graph_data["edges"],
        "profile": profile or graph_data.get("config", {}).get("profile", ""),
    }
    payload = json.dumps(public, ensure_ascii=False).replace("</script>", "<\\/script>")
    html = TEMPLATE.replace("__GRAPH_JSON__", payload)
    html = html.replace("__Q_JSON__", json.dumps(QUESTIONS))
    return html
