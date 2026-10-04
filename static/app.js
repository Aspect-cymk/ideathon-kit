const $ = (id) => document.getElementById(id);
let engines = [];

const COLORS = {
  well: "#121314",
  free: "#24272a",
  wall: "#5d6267",
  path: "#d4891c",
  start: "#7aa65a",
  goal: "#d4634a",
  axis: "#565b60",
  gridline: "#2e3236",
  text: "#d9d6cf",
  muted: "#8d9195",
  bar: "#c8841d",
};

async function api(path, opts) {
  const r = await fetch(path, opts);
  let body = {};
  try { body = await r.json(); } catch (e) { /* non-JSON response */ }
  if (!r.ok) throw new Error(body.detail || r.statusText);
  return body;
}

function setError(msg) { $("error").textContent = msg || ""; }

function setStatus(text, kind, meta) {
  const s = $("status");
  s.textContent = text;
  s.className = kind || "";
  $("meta").textContent = meta || "";
}

function setServer(online) {
  $("dot").className = "dot " + (online ? "on" : "off");
  $("server-text").textContent = online ? "SERVER ONLINE" : "SERVER OFFLINE";
}

async function loadEngines() {
  engines = await api("/api/engines");
  const sel = $("engine");
  sel.innerHTML = "";
  engines.forEach((e) => {
    const o = document.createElement("option");
    o.value = e.name;
    o.textContent = e.name;
    sel.appendChild(o);
  });
  await loadSample();
}

async function loadSample() {
  const name = $("engine").value;
  const eng = engines.find((e) => e.name === name);
  $("engine-desc").textContent = eng ? eng.description : "";
  const sample = await api(`/api/engines/${name}/sample`);
  $("input").value = JSON.stringify(sample, null, 2);
}

async function runEngine() {
  setError("");
  let data;
  try { data = JSON.parse($("input").value); }
  catch (e) {
    setError("Invalid JSON: " + e.message);
    return setStatus("INPUT REJECTED", "err", "");
  }
  const name = $("engine").value;
  setStatus("RUNNING", "", name);
  const t0 = performance.now();
  try {
    const res = await api(`/api/run/${name}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    render(res);
    loadHistory();
    setStatus("RUN COMPLETE", "ok", `${name} | run #${res.run_id} | ${Math.round(performance.now() - t0)} ms`);
  } catch (e) {
    setError(e.message);
    setStatus("RUN FAILED", "err", name);
  }
}

function render(res) {
  const cards = $("cards");
  cards.innerHTML = "";
  Object.entries(res.summary || {}).forEach(([k, v]) => {
    const d = document.createElement("div");
    d.className = "card";
    const kk = document.createElement("div"); kk.className = "k"; kk.textContent = k.replace(/_/g, " ");
    const vv = document.createElement("div"); vv.className = "v"; vv.textContent = v;
    d.append(kk, vv);
    cards.appendChild(d);
  });
  drawBars(res.series);
  drawGrid(res.grid);
  drawTable(res.table || []);
  const log = $("log");
  log.innerHTML = "";
  (res.log || []).forEach((l) => { const li = document.createElement("li"); li.textContent = l; log.appendChild(li); });
  const csv = $("csv");
  if (res.run_id && (res.table || []).length) { csv.href = `/api/runs/${res.run_id}/csv`; csv.hidden = false; }
  else csv.hidden = true;
}

function drawTable(rows) {
  const wrap = $("table-wrap");
  wrap.innerHTML = "";
  if (!rows.length) return;
  const t = document.createElement("table");
  const thead = document.createElement("thead");
  const head = document.createElement("tr");
  Object.keys(rows[0]).forEach((k) => { const th = document.createElement("th"); th.textContent = k.replace(/_/g, " "); head.appendChild(th); });
  thead.appendChild(head);
  t.appendChild(thead);
  const tbody = document.createElement("tbody");
  rows.forEach((r) => {
    const tr = document.createElement("tr");
    Object.values(r).forEach((v) => { const td = document.createElement("td"); td.textContent = v; tr.appendChild(td); });
    tbody.appendChild(tr);
  });
  t.appendChild(tbody);
  wrap.appendChild(t);
}

function drawBars(series) {
  const cv = $("bars");
  if (!series || !series.values.length) { cv.hidden = true; return; }
  cv.hidden = false;
  const ctx = cv.getContext("2d");
  const W = cv.width, H = cv.height;
  const left = 46, right = 16, top = 34, bottom = 30;
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = COLORS.muted;
  ctx.font = "12px Consolas, monospace";
  ctx.textBaseline = "alphabetic";
  ctx.fillText((series.title || "").toUpperCase(), left, 20);

  const max = Math.max(...series.values, 1);
  const plotH = H - top - bottom;
  for (let i = 0; i <= 4; i++) {
    const y = top + plotH - (plotH * i) / 4;
    ctx.strokeStyle = i === 0 ? COLORS.axis : COLORS.gridline;
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(left, y + 0.5); ctx.lineTo(W - right, y + 0.5); ctx.stroke();
    ctx.fillStyle = COLORS.muted;
    ctx.textAlign = "right";
    ctx.fillText(String(Math.round((max * i) / 4)), left - 6, y + 4);
  }
  const slot = (W - left - right) / series.values.length;
  series.values.forEach((v, i) => {
    const h = (plotH * v) / max;
    const bw = Math.min(slot * 0.6, 70);
    const x = left + i * slot + (slot - bw) / 2;
    ctx.fillStyle = COLORS.bar;
    ctx.fillRect(x, top + plotH - h, bw, h);
    ctx.fillStyle = COLORS.text;
    ctx.textAlign = "center";
    ctx.fillText(String(v), x + bw / 2, top + plotH - h - 5);
    ctx.fillStyle = COLORS.muted;
    ctx.fillText(String(series.labels[i]).slice(0, 12), x + bw / 2, H - 10);
  });
  ctx.textAlign = "left";
}

function drawGrid(grid) {
  const cv = $("grid");
  if (!grid) { cv.hidden = true; return; }
  cv.hidden = false;
  const rows = grid.rows, R = rows.length, C = rows[0].length;
  const cell = Math.floor(Math.min(cv.width / C, cv.height / R));
  const ox = Math.floor((cv.width - cell * C) / 2);
  const oy = Math.floor((cv.height - cell * R) / 2);
  const ctx = cv.getContext("2d");
  ctx.clearRect(0, 0, cv.width, cv.height);
  const onPath = new Set(grid.path.map((p) => p[0] + "," + p[1]));
  for (let r = 0; r < R; r++) {
    for (let c = 0; c < C; c++) {
      const ch = rows[r][c];
      let fill = COLORS.free;
      if (ch === "#") fill = COLORS.wall;
      else if (ch === "S") fill = COLORS.start;
      else if (ch === "G") fill = COLORS.goal;
      else if (onPath.has(r + "," + c)) fill = COLORS.path;
      ctx.fillStyle = fill;
      ctx.fillRect(ox + c * cell + 1, oy + r * cell + 1, cell - 2, cell - 2);
    }
  }
  ctx.fillStyle = COLORS.well;
  ctx.font = `bold ${Math.max(10, cell * 0.45)}px Consolas, monospace`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  for (let r = 0; r < R; r++) {
    for (let c = 0; c < C; c++) {
      const ch = rows[r][c];
      if (ch === "S" || ch === "G") ctx.fillText(ch, ox + c * cell + cell / 2, oy + r * cell + cell / 2 + 1);
    }
  }
  ctx.textAlign = "left";
  ctx.textBaseline = "alphabetic";
}

async function loadHistory() {
  const list = await api("/api/runs?limit=10");
  const ul = $("history");
  ul.innerHTML = "";
  list.forEach((r) => {
    const li = document.createElement("li");
    const a = document.createElement("span"); a.textContent = `#${r.id}  ${r.engine}`;
    const b = document.createElement("span"); b.className = "t"; b.textContent = r.created_at.slice(11, 19) + " UTC";
    li.append(a, b);
    li.onclick = async () => {
      const d = await api(`/api/runs/${r.id}`);
      $("engine").value = d.engine;
      $("input").value = JSON.stringify(d.input, null, 2);
      d.result.run_id = d.id;
      render(d.result);
      setStatus("HISTORY LOADED", "", `${d.engine} | run #${d.id}`);
    };
    ul.appendChild(li);
  });
}

$("run").onclick = runEngine;
$("reset").onclick = loadSample;
$("engine").onchange = loadSample;
api("/api/health")
  .then((h) => { $("title").textContent = h.title; document.title = h.title; setServer(true); })
  .catch(() => setServer(false));
loadEngines().then(loadHistory).catch((e) => { setError(e.message); setServer(false); });
