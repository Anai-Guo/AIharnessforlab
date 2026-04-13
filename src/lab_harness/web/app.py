"""Web GUI for AI Harness for Lab.

Adaptive interface that dynamically generates measurement forms
from YAML templates — supports 40+ measurement types without
hardcoded pages.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Harness for Lab",
    description="Adaptive measurement interface",
    version="0.1.0",
)

STATIC_DIR = Path(__file__).parent / "static"


@app.get("/api/templates")
async def list_templates():
    """List all available measurement templates grouped by discipline."""
    from lab_harness.planning.plan_builder import TEMPLATES_DIR
    import yaml

    templates = {}
    for path in sorted(TEMPLATES_DIR.glob("*.yaml")):
        with open(path) as f:
            data = yaml.safe_load(f)
        templates[path.stem] = {
            "name": data.get("name", path.stem),
            "description": data.get("description", ""),
            "x_axis": data.get("x_axis", {}),
            "y_channels": data.get("y_channels", []),
            "has_outer_sweep": "outer_sweep" in data,
        }
    return {"count": len(templates), "templates": templates}


@app.get("/api/templates/{measurement_type}")
async def get_template(measurement_type: str):
    """Get full template config for dynamic form generation."""
    from lab_harness.planning.plan_builder import TEMPLATES_DIR
    import yaml

    path = TEMPLATES_DIR / f"{measurement_type.lower()}.yaml"
    if not path.exists():
        return {"error": f"Template '{measurement_type}' not found"}

    with open(path) as f:
        data = yaml.safe_load(f)
    return data


@app.get("/api/instruments")
async def scan_instruments():
    """Scan for connected instruments."""
    from lab_harness.discovery.visa_scanner import scan_visa_instruments
    instruments = scan_visa_instruments()
    return {
        "count": len(instruments),
        "instruments": [i.model_dump() for i in instruments],
    }


@app.post("/api/plan")
async def create_plan(measurement_type: str, overrides: dict | None = None):
    """Generate a measurement plan from template."""
    from lab_harness.planning.plan_builder import build_plan_from_template
    from lab_harness.planning.boundary_checker import check_boundaries

    plan = build_plan_from_template(measurement_type, overrides=overrides)
    validation = check_boundaries(plan)
    return {
        "plan": plan.model_dump(),
        "validation": validation.model_dump(),
    }


@app.get("/api/health")
async def health():
    """System health check."""
    from lab_harness.planning.plan_builder import TEMPLATES_DIR

    visa_ok = False
    instrument_count = 0
    try:
        import pyvisa
        rm = pyvisa.ResourceManager()
        instrument_count = len(rm.list_resources())
        visa_ok = True
    except Exception:
        pass

    templates = [p.stem for p in TEMPLATES_DIR.glob("*.yaml")]

    return {
        "status": "ok",
        "visa_available": visa_ok,
        "instruments_found": instrument_count,
        "templates_available": len(templates),
        "template_list": templates,
    }


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the adaptive measurement dashboard."""
    html_path = STATIC_DIR / "index.html"
    if html_path.exists():
        return html_path.read_text()
    return _embedded_dashboard()


@app.get("/monitor", response_class=HTMLResponse)
async def monitor_page():
    """Serve the multi-panel monitor with user-selectable axes."""
    return _embedded_monitor()


def _embedded_dashboard() -> str:
    """Embedded HTML dashboard — no external files needed."""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Harness for Lab</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
.header { background: linear-gradient(135deg, #1e1b4b, #312e81); padding: 24px 32px; border-bottom: 2px solid #4f46e5; }
.header h1 { font-size: 28px; font-weight: 700; }
.header h1 span { color: #a78bfa; }
.header p { color: #94a3b8; margin-top: 4px; }
.container { max-width: 1200px; margin: 0 auto; padding: 24px; }
.grid { display: grid; grid-template-columns: 300px 1fr; gap: 24px; }
.sidebar { background: #1e293b; border-radius: 12px; padding: 16px; max-height: calc(100vh - 160px); overflow-y: auto; }
.sidebar h3 { color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin: 16px 0 8px; }
.sidebar h3:first-child { margin-top: 0; }
.template-btn { display: block; width: 100%; text-align: left; background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 10px 12px; margin-bottom: 6px; color: #e2e8f0; cursor: pointer; transition: all 0.2s; font-size: 13px; }
.template-btn:hover { border-color: #6366f1; background: #1e1b4b; }
.template-btn.active { border-color: #6366f1; background: #312e81; }
.template-btn .desc { color: #64748b; font-size: 11px; margin-top: 2px; }
.main { background: #1e293b; border-radius: 12px; padding: 24px; }
.main h2 { margin-bottom: 16px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.field { display: flex; flex-direction: column; gap: 4px; }
.field label { font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
.field input, .field select { background: #0f172a; border: 1px solid #334155; border-radius: 6px; padding: 8px 12px; color: #e2e8f0; font-size: 14px; }
.field input:focus { outline: none; border-color: #6366f1; }
.safety-box { background: #1c1917; border: 1px solid #854d0e; border-radius: 8px; padding: 12px; margin-top: 16px; }
.safety-box h4 { color: #fbbf24; font-size: 13px; margin-bottom: 8px; }
.safety-box .limit { color: #a3a3a3; font-size: 12px; }
.channels { margin-top: 16px; }
.channel-tag { display: inline-block; background: #312e81; border-radius: 12px; padding: 4px 12px; font-size: 12px; margin: 4px 4px 4px 0; color: #c4b5fd; }
.btn-row { margin-top: 20px; display: flex; gap: 12px; }
.btn { padding: 10px 24px; border-radius: 8px; border: none; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.btn-primary { background: #6366f1; color: white; }
.btn-primary:hover { background: #4f46e5; }
.btn-secondary { background: #334155; color: #e2e8f0; }
.btn-secondary:hover { background: #475569; }
.status-bar { background: #1e293b; border-radius: 8px; padding: 12px 16px; margin-top: 16px; font-size: 13px; color: #94a3b8; }
.status-bar .dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.dot-green { background: #22c55e; }
.dot-red { background: #ef4444; }
.empty-state { text-align: center; padding: 60px; color: #64748b; }
.empty-state h3 { font-size: 18px; margin-bottom: 8px; color: #94a3b8; }
#result { margin-top: 16px; background: #0f172a; border-radius: 8px; padding: 16px; font-family: monospace; font-size: 12px; max-height: 300px; overflow-y: auto; display: none; white-space: pre-wrap; }
</style>
</head>
<body>
<div class="header">
  <h1><span>AI</span> Harness for Lab</h1>
  <p>Fully Automated Lab Assistant &mdash; Select a measurement template to begin</p>
</div>
<div class="container">
  <div class="grid">
    <div class="sidebar" id="sidebar">
      <p style="color:#64748b;font-size:13px;">Loading templates...</p>
    </div>
    <div class="main" id="main">
      <div class="empty-state">
        <h3>Select a measurement template</h3>
        <p>Choose from the sidebar to configure your measurement</p>
      </div>
    </div>
  </div>
  <div class="status-bar" id="statusBar">
    <span class="dot dot-green"></span> System ready
  </div>
</div>

<script>
let templates = {};
let currentTemplate = null;

async function loadTemplates() {
  const res = await fetch("/api/templates");
  const data = await res.json();
  templates = data.templates;
  renderSidebar();
}

function renderSidebar() {
  const sidebar = document.getElementById("sidebar");
  const groups = {};

  // Group templates by category
  for (const [key, t] of Object.entries(templates)) {
    let cat = "General";
    if (key.startsWith("ppms_") || key.startsWith("mpms_")) cat = "Quantum Design";
    else if (["ahe","mr","sot","hall","fmr","hysteresis","magnetostriction","nernst"].includes(key)) cat = "Magnetic";
    else if (["iv","rt","delta","high_r","transfer","output","breakdown","tunneling"].includes(key)) cat = "Electrical";
    else if (["tc","jc"].includes(key)) cat = "Superconductivity";
    else if (["cv","pe_loop","pyroelectric","capacitance_frequency","dlts","eis"].includes(key)) cat = "Dielectric / Electrochem";
    else if (["seebeck","thermal_conductivity"].includes(key)) cat = "Thermoelectric";
    else if (["photocurrent","photoresponse","photo_iv"].includes(key)) cat = "Optical / Solar";
    else if (["cyclic_voltammetry","chronoamperometry","potentiometry"].includes(key)) cat = "Chemistry";
    else if (["gas_sensor","ph_calibration","humidity_response","impedance_biosensor","cell_counting"].includes(key)) cat = "Sensors / Bio";
    else if (["strain_gauge","fatigue"].includes(key)) cat = "Materials";
    if (!groups[cat]) groups[cat] = [];
    groups[cat].push({key, ...t});
  }

  let html = "";
  for (const [cat, items] of Object.entries(groups).sort()) {
    html += `<h3>${cat} (${items.length})</h3>`;
    for (const item of items) {
      html += `<button class="template-btn" onclick="selectTemplate('${item.key}')" id="btn-${item.key}">
        ${item.name}
        <div class="desc">${item.description.substring(0,60)}</div>
      </button>`;
    }
  }
  sidebar.innerHTML = html;
}

async function selectTemplate(key) {
  document.querySelectorAll(".template-btn").forEach(b => b.classList.remove("active"));
  document.getElementById("btn-"+key)?.classList.add("active");

  const res = await fetch(`/api/templates/${key}`);
  currentTemplate = await res.json();
  currentTemplate._key = key;
  renderForm(currentTemplate);
}

function renderForm(t) {
  const main = document.getElementById("main");
  const x = t.x_axis || {};
  const channels = (t.y_channels || []).map(c =>
    `<span class="channel-tag">${c.label} (${c.unit})</span>`
  ).join("");

  let outerHtml = "";
  if (t.outer_sweep) {
    const o = t.outer_sweep;
    outerHtml = `
      <div class="field"><label>Outer: ${o.label} Start (${o.unit})</label><input type="number" value="${o.start}" id="outer_start"></div>
      <div class="field"><label>Outer: ${o.label} Stop (${o.unit})</label><input type="number" value="${o.stop}" id="outer_stop"></div>
      <div class="field"><label>Outer Step (${o.unit})</label><input type="number" value="${o.step}" id="outer_step"></div>
    `;
  }

  main.innerHTML = `
    <h2>${t.name || t._key}</h2>
    <p style="color:#94a3b8;margin-bottom:16px;">${t.description || ""}</p>

    <div class="form-grid">
      <div class="field"><label>X: ${x.label} Start (${x.unit})</label><input type="number" value="${x.start}" id="x_start"></div>
      <div class="field"><label>X: ${x.label} Stop (${x.unit})</label><input type="number" value="${x.stop}" id="x_stop"></div>
      <div class="field"><label>Step (${x.unit})</label><input type="number" value="${x.step}" id="x_step"></div>
      <div class="field"><label>Settling Time (s)</label><input type="number" value="${t.settling_time_s || 0.5}" id="settling"></div>
      <div class="field"><label>Averages</label><input type="number" value="${t.num_averages || 1}" id="averages"></div>
      ${outerHtml}
    </div>

    <div class="channels">
      <label style="font-size:12px;color:#94a3b8;text-transform:uppercase;">Data Channels</label><br>
      ${channels || '<span style="color:#64748b">No channels defined</span>'}
    </div>

    <div class="safety-box">
      <h4>Safety Limits</h4>
      <div class="limit">Max Current: ${t.max_current_a ? (t.max_current_a*1000).toFixed(1)+" mA" : "N/A"}</div>
      <div class="limit">Max Voltage: ${t.max_voltage_v || "N/A"} V</div>
      <div class="limit">Max Field: ${t.max_field_oe ? (t.max_field_oe/1000).toFixed(0)+" kOe" : "N/A"}</div>
      <div class="limit">Max Temperature: ${t.max_temperature_k || "N/A"} K</div>
    </div>

    <div class="btn-row">
      <button class="btn btn-primary" onclick="validatePlan()">Validate Plan</button>
      <button class="btn btn-secondary" onclick="generatePlan()">Generate Plan JSON</button>
    </div>

    <div id="result"></div>
  `;
}

async function validatePlan() {
  if (!currentTemplate) return;
  const overrides = {
    x_axis: {
      start: parseFloat(document.getElementById("x_start").value),
      stop: parseFloat(document.getElementById("x_stop").value),
      step: parseFloat(document.getElementById("x_step").value),
    },
    settling_time_s: parseFloat(document.getElementById("settling").value),
    num_averages: parseInt(document.getElementById("averages").value),
  };
  const res = await fetch("/api/plan?measurement_type=" + currentTemplate._key, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(overrides),
  });
  const data = await res.json();
  const el = document.getElementById("result");
  el.style.display = "block";
  const v = data.validation;
  let color = v.decision === "allow" ? "#22c55e" : v.decision === "require_confirm" ? "#fbbf24" : "#ef4444";
  el.innerHTML = `<span style="color:${color};font-weight:bold;">${v.decision.toUpperCase()}</span>\\n`;
  if (v.warnings?.length) el.innerHTML += "Warnings:\\n" + v.warnings.map(w=>"  - "+w).join("\\n") + "\\n";
  if (v.violations?.length) el.innerHTML += "Violations:\\n" + v.violations.map(v=>"  - "+v.message).join("\\n") + "\\n";
  el.innerHTML += "\\nTotal points: " + data.plan.x_axis.num_points;
  if (v.ai_advice) el.innerHTML += "\\n\\nAI Advice: " + v.ai_advice;
}

async function generatePlan() {
  if (!currentTemplate) return;
  const el = document.getElementById("result");
  el.style.display = "block";
  const res = await fetch(`/api/templates/${currentTemplate._key}`);
  el.textContent = JSON.stringify(await res.json(), null, 2);
}

// Init
loadTemplates();
fetch("/api/health").then(r=>r.json()).then(d=>{
  const bar = document.getElementById("statusBar");
  bar.innerHTML = `<span class="dot ${d.visa_available?'dot-green':'dot-red'}"></span>` +
    `VISA: ${d.visa_available?'Connected':'Not available'} | ` +
    `Instruments: ${d.instruments_found} | ` +
    `Templates: ${d.templates_available}`;
});
</script>
</body>
</html>'''


def _embedded_monitor() -> str:
    """Embedded multi-panel real-time monitor with selectable axes."""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Harness for Lab — Monitor</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0f172a; color: #e2e8f0; }
.header { background: linear-gradient(135deg, #1e1b4b, #312e81); padding: 16px 24px; border-bottom: 2px solid #4f46e5; display: flex; justify-content: space-between; align-items: center; }
.header h1 { font-size: 20px; } .header h1 span { color: #a78bfa; }
.header a { color: #94a3b8; text-decoration: none; font-size: 13px; }
.header a:hover { color: #e2e8f0; }
.toolbar { background: #1e293b; padding: 10px 24px; display: flex; gap: 12px; align-items: center; border-bottom: 1px solid #334155; }
.toolbar label { font-size: 12px; color: #94a3b8; }
.toolbar select, .toolbar input { background: #0f172a; border: 1px solid #334155; border-radius: 6px; padding: 5px 10px; color: #e2e8f0; font-size: 13px; }
.toolbar button { background: #6366f1; border: none; border-radius: 6px; padding: 6px 16px; color: white; font-size: 13px; cursor: pointer; font-weight: 600; }
.toolbar button:hover { background: #4f46e5; }
.toolbar .btn-add { background: #059669; } .toolbar .btn-add:hover { background: #047857; }
.panels { display: grid; gap: 12px; padding: 16px; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); }
.panel { background: #1e293b; border-radius: 12px; border: 1px solid #334155; overflow: hidden; }
.panel-header { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: #0f172a; border-bottom: 1px solid #334155; }
.panel-header h3 { font-size: 13px; font-weight: 600; }
.panel-controls { display: flex; gap: 8px; align-items: center; }
.panel-controls select { background: #1e293b; border: 1px solid #475569; border-radius: 4px; padding: 3px 8px; color: #e2e8f0; font-size: 11px; }
.panel-controls .btn-close { background: none; border: none; color: #64748b; cursor: pointer; font-size: 16px; }
.panel-controls .btn-close:hover { color: #ef4444; }
.canvas-wrap { padding: 12px; height: 280px; position: relative; }
canvas { width: 100%; height: 100%; background: #0f172a; border-radius: 6px; }
.panel-footer { padding: 6px 14px; background: #0f172a; border-top: 1px solid #334155; font-size: 11px; color: #64748b; display: flex; justify-content: space-between; }
.value-display { font-family: 'Courier New', monospace; font-size: 13px; color: #22c55e; }
</style>
</head>
<body>
<div class="header">
  <h1><span>AI</span> Harness — Monitor</h1>
  <a href="/">← Back to Dashboard</a>
</div>
<div class="toolbar">
  <label>Panels:</label>
  <button class="btn-add" onclick="addPanel()">+ Add Panel</button>
  <label style="margin-left:16px;">Refresh:</label>
  <select id="refreshRate">
    <option value="1000">1 Hz</option>
    <option value="500">2 Hz</option>
    <option value="2000">0.5 Hz</option>
    <option value="5000">0.2 Hz</option>
  </select>
  <label style="margin-left:16px;">Data Points:</label>
  <input type="number" id="maxPoints" value="200" min="50" max="2000" style="width:70px;">
  <button onclick="clearAllData()" style="background:#dc2626;margin-left:auto;">Clear All</button>
</div>
<div class="panels" id="panels"></div>

<script>
const CHANNELS = [
  {id:"time", label:"Time", unit:"s"},
  {id:"voltage", label:"Voltage", unit:"V"},
  {id:"current", label:"Current", unit:"A"},
  {id:"resistance", label:"Resistance", unit:"Ω"},
  {id:"temperature", label:"Temperature", unit:"K"},
  {id:"field", label:"Magnetic Field", unit:"Oe"},
  {id:"capacitance", label:"Capacitance", unit:"pF"},
  {id:"frequency", label:"Frequency", unit:"Hz"},
  {id:"magnetization", label:"Magnetization", unit:"emu"},
  {id:"power", label:"Power", unit:"W"},
  {id:"strain", label:"Strain", unit:"με"},
  {id:"pressure", label:"Pressure", unit:"Torr"},
  {id:"ph", label:"pH", unit:""},
  {id:"impedance_real", label:"Z Real", unit:"Ω"},
  {id:"impedance_imag", label:"Z Imaginary", unit:"Ω"},
  {id:"hall_voltage", label:"Hall Voltage", unit:"V"},
  {id:"seebeck_voltage", label:"Seebeck Voltage", unit:"μV"},
];

let panelCount = 0;
let panels = {};

function channelOptions(selected="") {
  return CHANNELS.map(c =>
    `<option value="${c.id}" ${c.id===selected?"selected":""}>${c.label} (${c.unit})</option>`
  ).join("");
}

function addPanel(xDefault="time", yDefault="voltage") {
  panelCount++;
  const id = "p" + panelCount;
  const container = document.getElementById("panels");
  const div = document.createElement("div");
  div.className = "panel";
  div.id = id;
  div.innerHTML = `
    <div class="panel-header">
      <h3>Panel ${panelCount}</h3>
      <div class="panel-controls">
        <label style="font-size:11px;color:#94a3b8;">X:</label>
        <select onchange="updateAxis('${id}')" id="${id}_x">${channelOptions(xDefault)}</select>
        <label style="font-size:11px;color:#94a3b8;">Y:</label>
        <select onchange="updateAxis('${id}')" id="${id}_y">${channelOptions(yDefault)}</select>
        <button class="btn-close" onclick="removePanel('${id}')">&times;</button>
      </div>
    </div>
    <div class="canvas-wrap"><canvas id="${id}_canvas"></canvas></div>
    <div class="panel-footer">
      <span id="${id}_info">No data</span>
      <span class="value-display" id="${id}_value">--</span>
    </div>
  `;
  container.appendChild(div);
  panels[id] = { data: [], xCh: xDefault, yCh: yDefault };
  initCanvas(id);
}

function removePanel(id) {
  document.getElementById(id)?.remove();
  delete panels[id];
}

function updateAxis(id) {
  const xSel = document.getElementById(id+"_x");
  const ySel = document.getElementById(id+"_y");
  if (panels[id]) {
    panels[id].xCh = xSel.value;
    panels[id].yCh = ySel.value;
    panels[id].data = [];
    drawPanel(id);
  }
}

function clearAllData() {
  for (const id in panels) { panels[id].data = []; drawPanel(id); }
}

function initCanvas(id) {
  const canvas = document.getElementById(id+"_canvas");
  const rect = canvas.parentElement.getBoundingClientRect();
  canvas.width = rect.width - 24;
  canvas.height = rect.height - 24;
  drawPanel(id);
}

function drawPanel(id) {
  const panel = panels[id];
  if (!panel) return;
  const canvas = document.getElementById(id+"_canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const w = canvas.width, h = canvas.height;
  const pad = {t:20, r:20, b:35, l:55};

  ctx.fillStyle = "#0f172a";
  ctx.fillRect(0, 0, w, h);

  const data = panel.data;
  const xLabel = CHANNELS.find(c=>c.id===panel.xCh)?.label || panel.xCh;
  const yLabel = CHANNELS.find(c=>c.id===panel.yCh)?.label || panel.yCh;
  const xUnit = CHANNELS.find(c=>c.id===panel.xCh)?.unit || "";
  const yUnit = CHANNELS.find(c=>c.id===panel.yCh)?.unit || "";

  // Axis labels
  ctx.fillStyle = "#64748b"; ctx.font = "11px Segoe UI";
  ctx.textAlign = "center";
  ctx.fillText(`${xLabel} (${xUnit})`, pad.l + (w-pad.l-pad.r)/2, h - 5);
  ctx.save(); ctx.translate(12, pad.t + (h-pad.t-pad.b)/2);
  ctx.rotate(-Math.PI/2); ctx.fillText(`${yLabel} (${yUnit})`, 0, 0);
  ctx.restore();

  if (data.length < 2) {
    ctx.fillStyle = "#475569"; ctx.font = "14px Segoe UI"; ctx.textAlign = "center";
    ctx.fillText("Waiting for data...", w/2, h/2);
    // Draw grid anyway
    ctx.strokeStyle = "#1e293b"; ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
      const y = pad.t + i * (h-pad.t-pad.b)/4;
      ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w-pad.r, y); ctx.stroke();
      const x = pad.l + i * (w-pad.l-pad.r)/4;
      ctx.beginPath(); ctx.moveTo(x, pad.t); ctx.lineTo(x, h-pad.b); ctx.stroke();
    }
    return;
  }

  const xs = data.map(d=>d.x), ys = data.map(d=>d.y);
  let xMin = Math.min(...xs), xMax = Math.max(...xs);
  let yMin = Math.min(...ys), yMax = Math.max(...ys);
  if (xMin === xMax) { xMin -= 1; xMax += 1; }
  if (yMin === yMax) { yMin -= 1; yMax += 1; }
  const xRange = xMax - xMin, yRange = yMax - yMin;

  // Grid
  ctx.strokeStyle = "#1e293b"; ctx.lineWidth = 1;
  ctx.fillStyle = "#475569"; ctx.font = "10px Courier New"; ctx.textAlign = "right";
  for (let i = 0; i <= 4; i++) {
    const y = pad.t + i * (h-pad.t-pad.b)/4;
    ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w-pad.r, y); ctx.stroke();
    const val = yMax - i * yRange / 4;
    ctx.fillText(val.toPrecision(3), pad.l - 5, y + 4);
  }
  ctx.textAlign = "center";
  for (let i = 0; i <= 4; i++) {
    const x = pad.l + i * (w-pad.l-pad.r)/4;
    ctx.beginPath(); ctx.moveTo(x, pad.t); ctx.lineTo(x, h-pad.b); ctx.stroke();
    const val = xMin + i * xRange / 4;
    ctx.fillText(val.toPrecision(3), x, h - pad.b + 14);
  }

  // Plot line
  ctx.strokeStyle = "#6366f1"; ctx.lineWidth = 2; ctx.beginPath();
  for (let i = 0; i < data.length; i++) {
    const px = pad.l + (data[i].x - xMin) / xRange * (w - pad.l - pad.r);
    const py = pad.t + (1 - (data[i].y - yMin) / yRange) * (h - pad.t - pad.b);
    if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
  }
  ctx.stroke();

  // Latest point dot
  const last = data[data.length - 1];
  const lpx = pad.l + (last.x - xMin) / xRange * (w - pad.l - pad.r);
  const lpy = pad.t + (1 - (last.y - yMin) / yRange) * (h - pad.t - pad.b);
  ctx.fillStyle = "#22c55e"; ctx.beginPath(); ctx.arc(lpx, lpy, 4, 0, Math.PI*2); ctx.fill();

  // Update footer
  const info = document.getElementById(id+"_info");
  const value = document.getElementById(id+"_value");
  if (info) info.textContent = `${data.length} points | X: [${xMin.toPrecision(3)}, ${xMax.toPrecision(3)}]`;
  if (value) value.textContent = `${yLabel}: ${last.y.toPrecision(5)} ${yUnit}`;
}

// Simulate data for demo
function simulateData() {
  const maxPts = parseInt(document.getElementById("maxPoints").value) || 200;
  const t = Date.now() / 1000;
  for (const id in panels) {
    const p = panels[id];
    const x = p.xCh === "time" ? t % 100 : (Math.random()-0.5)*200;
    const y = Math.sin(t * 0.5) * (1 + Math.random()*0.1) + Math.random()*0.05;
    p.data.push({x, y});
    if (p.data.length > maxPts) p.data.shift();
    drawPanel(id);
  }
}

// Start with 2 default panels
addPanel("time", "voltage");
addPanel("field", "resistance");

// Refresh loop
let simInterval = setInterval(simulateData, 1000);
document.getElementById("refreshRate").addEventListener("change", function() {
  clearInterval(simInterval);
  simInterval = setInterval(simulateData, parseInt(this.value));
});

// Resize handling
window.addEventListener("resize", () => {
  for (const id in panels) initCanvas(id);
});
</script>
</body>
</html>'''


# CLI integration
def run_web(host: str = "127.0.0.1", port: int = 8080):
    """Start the web GUI server."""
    import uvicorn
    print(f"Starting AI Harness for Lab at http://{host}:{port}")
    print(f"  Dashboard: http://{host}:{port}/")
    print(f"  Monitor:   http://{host}:{port}/monitor")
    uvicorn.run(app, host=host, port=port)
