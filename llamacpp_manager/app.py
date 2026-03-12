"""llamacpp_manager Flask app: API routes for models and generation."""
import html as html_mod
from typing import Optional
import json
import logging
import os
import time
import requests
import threading
import uuid
from flask import Flask, request, jsonify, Response

from . import config
from .db import init_db, get_connection
from .model_manager import (
    list_models,
    get_model,
    get_model_by_name,
    get_parameters,
    update_parameters,
    update_model_name,
    update_model_port,
    update_model_path,
    register_model,
    start_model,
    stop_model,
    delete_model,
    resolve_threads_preset,
    resolve_ram_preset,
    get_next_port,
    reset_running_status,
    mark_stopped_if_dead,
    get_system_config,
    update_system_config,
    resolve_threads,
    _detect_cpu_cores,
    _find_llama_server,
    DEFAULT_PARAMS,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("llamacpp_manager")

app = Flask(__name__)

with app.app_context():
    try:
        init_db()
        reset_running_status()
    except Exception as e:
        log.warning("init_db failed (run once manually if needed): %s", e)

_download_progress = {}  # job_id -> {status, pct, bytes_done, bytes_total, name, error, model_id}

DEFAULT_PRESETS = [
    {"id": "qwen25-7b", "name": "Qwen2.5-7B-Instruct-GGUF", "path": "Qwen/Qwen2.5-7B-Instruct-GGUF:qwen2.5-7b-instruct-q4_k_m.gguf", "desc": "Great balance of quality + speed (recommended)"},
    {"id": "mistral-7b", "name": "Mistral-7B-Instruct-GGUF", "path": "TheBloke/Mistral-7B-Instruct-v0.2-GGUF:mistral-7b-instruct-v0.2.Q4_K_M.gguf", "desc": "Excellent long text + structured content"},
    {"id": "phi3-mini", "name": "Phi-3-mini-4k-instruct", "path": "microsoft/Phi-3-mini-4k-instruct-gguf:Phi-3-mini-4k-instruct-q4.gguf", "desc": "Fastest small model (good for drafts)"},
    {"id": "llama2-7b", "name": "LLaMA-2-7B-Chat-Q4_K_M-GGUF", "path": "TheBloke/Llama-2-7B-Chat-GGUF:llama-2-7b-chat.Q4_K_M.gguf", "desc": "Solid classic LLaMA-2 writing quality"},
    {"id": "mixtral-8x7b", "name": "Mixtral-8x7B-Q4_K_M-GGUF", "path": "TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF:mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf", "desc": "Variant mix for reasoning/text generation"},
    {"id": "falcon-7b", "name": "Falcon-7B-Instruct-Q4_K_M-GGUF", "path": "TheBloke/Falcon-7B-Instruct-GGUF:falcon-7b-instruct.Q4_K_M.gguf", "desc": "Good quality, decent CPU speed"},
    {"id": "smol-7b", "name": "SmolLM2-7B-Instruct-Q4_K_M-GGUF", "path": "HuggingFaceTB/SmolLM2-7B-Instruct-GGUF:SmolLM2-7B-Instruct-Q4_K_M.gguf", "desc": "Efficient 7B instruct model"},
    {"id": "llama3-8b", "name": "Llama-3-8B-Instruct-Q4_K_M-GGUF", "path": "TheBloke/Meta-Llama-3-8B-Instruct-GGUF:Meta-Llama-3-8B-Instruct.Q4_K_M.gguf", "desc": "Newer LLaMA 3 quality"},
]


def _model_url(port: int, host: str = "127.0.0.1"):
    return f"http://{host}:{port}"


# ---------------------------------------------------------------------------
# Web Dashboard
# ---------------------------------------------------------------------------

@app.route("/")
def dashboard():
    """Management dashboard: download, manage, test models."""
    llama_exe = _find_llama_server()
    sys_cfg = get_system_config()
    cores = _detect_cpu_cores()
    models_dir = config.MODELS_DIR

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>llama.cpp Manager</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
<style>
body {{ background:#0d1117; color:#c9d1d9; }}
.card {{ background:#161b22; border-color:#30363d; }}
.card-header {{ background:#21262d; border-color:#30363d; }}
.table {{ color:#c9d1d9; --bs-table-bg: transparent; --bs-table-striped-bg: rgba(33,38,45,.5); --bs-table-hover-bg: rgba(33,38,45,.8); }}
.table thead th {{ background:#21262d; border-color:#30363d; color:#8b949e; font-size:.85rem; font-weight:600; text-transform:uppercase; }}
.table td {{ border-color:#30363d; vertical-align:middle; }}
.table tbody tr {{ border-color:#30363d; }}
.badge-running {{ background:#238636; }}
.badge-loading {{ background:#9e6a03; }}
.badge-stopped {{ background:#6e7681; }}
.badge-error {{ background:#da3633; }}
.form-label {{ color:#e6edf3 !important; }}
.form-control,.form-select {{ background:#21262d !important; color:#e6edf3 !important; border-color:#30363d; }}
.form-control::placeholder {{ color:#8b949e !important; opacity:1; }}
input.form-control, select.form-select, textarea.form-control {{ color:#e6edf3 !important; }}
.form-control:focus,.form-select:focus {{ background:#21262d !important; color:#e6edf3 !important; border-color:#58a6ff; box-shadow:0 0 0 .2rem rgba(88,166,255,.25); }}
.text-danger {{ color:#f85149 !important; }}
.text-success {{ color:#3fb950 !important; }}
.btn-outline-success {{ color:#3fb950; border-color:#238636; }}
.btn-outline-success:hover {{ background:#238636; color:#fff; }}
.btn-outline-danger {{ color:#f85149; border-color:#da3633; }}
.btn-outline-danger:hover {{ background:#da3633; color:#fff; }}
.toast-container {{ z-index:9999; }}
pre.gen-output {{ background:#0d1117; border:1px solid #30363d; border-radius:6px; padding:12px; max-height:400px; overflow:auto; white-space:pre-wrap; font-size:.85rem; color:#c9d1d9; }}
.progress {{ height:6px; background:#21262d; }}
.progress-bar {{ background:#58a6ff; }}
#downloadLog {{ font-size:.8rem; max-height:120px; overflow-y:auto; }}
.sys-info {{ font-size:.8rem; color:#8b949e; }}
.form-text, .text-muted {{ color:#8b949e !important; }}
.card, .card-body {{ color:#c9d1d9; }}
input, select, textarea {{ color:#e6edf3 !important; }}
</style>
</head>
<body>
<div class="container-fluid py-4" style="max-width:1200px">

  <!-- Header -->
  <div class="d-flex align-items-center justify-content-between mb-4">
    <div>
      <h3 class="mb-0"><i class="bi bi-cpu"></i> llama.cpp Manager</h3>
      <div class="sys-info mt-1">
        CPU cores: <strong>{cores}</strong> &middot;
        Max threads: <strong>{sys_cfg.get('max_threads',8)}</strong> &middot;
        Auto threads: <strong>{'On' if sys_cfg.get('auto_threads') else 'Off'}</strong> &middot;
        Models dir: <code>{html_mod.escape(str(models_dir))}</code> &middot;
        llama-server: <span class="{'text-success' if llama_exe else 'text-danger'}">{'Found' if llama_exe else 'Not found'}</span>
      </div>
    </div>
    <div>
      <a class="btn btn-sm btn-outline-secondary" href="/api-docs" target="_blank" title="API documentation"><i class="bi bi-book"></i> API Docs</a>
      <button class="btn btn-sm btn-outline-secondary" data-bs-toggle="collapse" data-bs-target="#installHelp" title="How to install llama-server"><i class="bi bi-question-circle"></i> Install</button>
      <button class="btn btn-sm btn-outline-secondary" onclick="loadModels()"><i class="bi bi-arrow-clockwise"></i> Refresh</button>
      <button class="btn btn-sm btn-outline-info" data-bs-toggle="modal" data-bs-target="#settingsModal"><i class="bi bi-gear"></i> Settings</button>
    </div>
  </div>

  <div class="collapse mb-3" id="installHelp">
    <div class="alert alert-info small py-2">llama-server auto-downloads if missing. <code>owner/repo:file</code> for HuggingFace. <a href="https://github.com/ggerganov/llama.cpp" target="_blank" rel="noopener">docs</a></div>
  </div>

  <!-- Recommended Models -->
  <div class="card mb-4">
    <div class="card-header d-flex justify-content-between align-items-center">
      <span><i class="bi bi-stars"></i> Recommended Models</span>
      <div>
        <button class="btn btn-sm btn-outline-secondary me-1" onclick="restoreHiddenPresets()" title="Restore removed presets">Restore</button>
        <button class="btn btn-sm btn-outline-success" onclick="showAddPresetModal()"><i class="bi bi-plus-lg"></i> Add preset</button>
      </div>
    </div>
    <div class="card-body">
      <div id="presetsList" class="d-flex flex-wrap gap-2"></div>
    </div>
  </div>

  <!-- Download / Add Model -->
  <div class="card mb-4">
    <div class="card-header"><i class="bi bi-cloud-download"></i> Download or Register Model</div>
    <div class="card-body">
      <div class="row g-2 align-items-end">
        <div class="col-md-5">
          <label class="form-label small">URL or HuggingFace path</label>
          <input type="text" id="dlUrl" class="form-control form-control-sm" placeholder="owner/repo:file.gguf or https://.../model.gguf">
        </div>
        <div class="col-md-2">
          <button class="btn btn-sm btn-primary" onclick="downloadModel()"><i class="bi bi-download"></i> Download</button>
        </div>
        <div class="col-md-1 text-muted small align-self-end pb-1">or</div>
        <div class="col-md-2">
          <label class="form-label small">Name</label>
          <input type="text" id="regName" class="form-control form-control-sm" placeholder="my-model">
        </div>
        <div class="col-md-2">
          <label class="form-label small">Path</label>
          <input type="text" id="regPath" class="form-control form-control-sm" placeholder="owner/repo:file">
        </div>
        <div class="col-md-1">
          <button class="btn btn-sm btn-outline-success" onclick="registerModel()"><i class="bi bi-plus"></i></button>
        </div>
      </div>
      <div id="dlProgress" class="mt-2 d-none">
        <div class="progress mb-1"><div id="dlBar" class="progress-bar" style="width:0%"></div></div>
        <div id="downloadLog" class="text-muted"></div>
      </div>
    </div>
  </div>

  <!-- Models Table -->
  <div class="card mb-4">
    <div class="card-header"><i class="bi bi-collection"></i> Models</div>
    <div class="table-responsive">
      <table class="table table-hover mb-0">
        <thead><tr>
          <th>ID</th><th>Name</th><th>Status</th><th>Port</th><th>API</th><th>Ctx</th><th>Threads</th><th>GPU</th><th>Actions</th>
        </tr></thead>
        <tbody id="modelsBody"><tr><td colspan="9" class="text-center text-muted">Loading...</td></tr></tbody>
      </table>
    </div>
  </div>

  <!-- Test / Playground Card -->
  <div class="card mb-4">
    <div class="card-header"><i class="bi bi-chat-dots"></i> Test / Playground</div>
    <div class="card-body">
      <div class="row g-2 mb-2">
        <div class="col-md-4">
          <label class="form-label small">Model</label>
          <select id="testModel" class="form-select form-select-sm" onchange="applyModelParamsToTest()"></select>
        </div>
        <div class="col-md-2">
          <label class="form-label small">Max tokens</label>
          <input type="text" id="testMaxTokens" class="form-control form-control-sm" value="auto" placeholder="auto or number">
          <div class="form-text small">auto=4096</div>
        </div>
        <div class="col-md-2">
          <label class="form-label small">Temperature</label>
          <input type="number" id="testTemp" class="form-control form-control-sm" value="0.7" step="0.01" min="0" max="2">
        </div>
        <div class="col-md-2">
          <label class="form-label small">Top P / Top K</label>
          <div class="input-group input-group-sm">
            <input type="number" id="testTopP" class="form-control form-control-sm" value="0.9" step="0.01" min="0" max="1" placeholder="Top P">
            <input type="number" id="testTopK" class="form-control form-control-sm" value="40" min="0" placeholder="K">
          </div>
        </div>
        <div class="col-md-1">
          <label class="form-label small">Repeat penalty</label>
          <input type="number" id="testRepeatPenalty" class="form-control form-control-sm" value="1.1" step="0.01" min="1">
        </div>
        <div class="col-md-1">
          <label class="form-label small">Seed</label>
          <input type="number" id="testSeed" class="form-control form-control-sm" value="-1" title="-1=random">
        </div>
        <div class="col-md-1">
          <label class="form-label small">Threads</label>
          <select id="testThreads" class="form-select form-select-sm">
            <option value="max" selected>max</option>
            <option value="medium">medium</option>
            <option value="min">min</option>
          </select>
        </div>
        <div class="col-md-1">
          <label class="form-label small">RAM</label>
          <select id="testRam" class="form-select form-select-sm">
            <option value="max" selected>max</option>
            <option value="medium">medium</option>
            <option value="min">min</option>
          </select>
        </div>
        <div class="col-md-auto d-flex align-items-end pb-1">
          <button class="btn btn-sm btn-outline-secondary" onclick="applyModelParamsToTest()" title="Apply model defaults"><i class="bi bi-arrow-repeat"></i></button>
        </div>
      </div>
      <div class="mb-2">
        <label class="form-label small">System prompt <span class="text-muted">(optional)</span></label>
        <input type="text" id="testSystem" class="form-control form-control-sm" placeholder="You are a helpful assistant.">
      </div>
      <div class="mb-2">
        <label class="form-label small">Prompt</label>
        <textarea id="testPrompt" class="form-control form-control-sm" rows="3" placeholder="Write a couscous recipe"></textarea>
      </div>
      <button class="btn btn-sm btn-primary" id="testBtn" onclick="testGenerate()"><i class="bi bi-play-fill"></i> Generate</button>
      <div id="testResult" class="mt-3 d-none">
        <label class="form-label small text-muted">Output</label>
        <pre class="gen-output" id="testOutput"></pre>
        <div id="testUsage" class="text-muted small mt-1"></div>
      </div>
    </div>
  </div>

  <!-- API Tester -->
  <div class="card mb-4">
    <div class="card-header"><i class="bi bi-send"></i> API Tester (POST, GET, PUT, DELETE)</div>
    <div class="card-body">
      <div class="d-flex flex-wrap gap-2 mb-2 align-items-center">
        <select id="apiMethod" class="form-select form-select-sm" style="width:100px">
          <option value="GET">GET</option>
          <option value="POST">POST</option>
          <option value="PUT">PUT</option>
          <option value="DELETE">DELETE</option>
        </select>
        <input type="text" id="apiUrl" class="form-control form-control-sm flex-grow-1" style="min-width:200px" placeholder="/ai/models">
        <button class="btn btn-sm btn-primary" onclick="apiTesterSend()"><i class="bi bi-play-fill"></i> Send</button>
      </div>
      <div class="mb-2">
        <label class="form-label small">Headers</label>
        <div id="apiHeaders">
          <div class="input-group input-group-sm mb-1">
            <input type="text" class="form-control" placeholder="Content-Type" value="Content-Type">
            <input type="text" class="form-control" placeholder="application/json" value="application/json">
          </div>
        </div>
        <button class="btn btn-sm btn-outline-secondary py-0 mt-1" onclick="apiTesterAddHeader()">+ Add header</button>
      </div>
      <div class="mb-2">
        <label class="form-label small">Body (JSON for POST/PUT)</label>
        <textarea id="apiBody" class="form-control form-control-sm font-monospace" rows="4" placeholder='{{"model_id": 1, "prompt": "hello"}}'>{{"model_id": 1, "prompt": "hello"}}</textarea>
      </div>
      <div class="mb-2">
        <span class="text-muted small me-2">Quick:</span>
        <button class="btn btn-sm btn-outline-secondary py-0" onclick="apiTesterLoad('/ai/models','GET')">GET /ai/models</button>
        <button class="btn btn-sm btn-outline-secondary py-0" onclick="apiTesterLoad('/ai/generate','POST')">POST /ai/generate</button>
        <button class="btn btn-sm btn-outline-secondary py-0" onclick="apiTesterLoad('/ai/models/download','POST')">POST download</button>
      </div>
      <div id="apiResponse" class="d-none">
        <label class="form-label small">Response <span id="apiStatus" class="badge ms-1"></span></label>
        <pre class="gen-output font-monospace small p-2" id="apiResponseBody" style="max-height:250px; overflow:auto"></pre>
      </div>
    </div>
  </div>

</div>

<!-- Settings Modal -->
<div class="modal fade" id="settingsModal" tabindex="-1">
  <div class="modal-dialog"><div class="modal-content" style="background:#161b22;border-color:#30363d">
    <div class="modal-header" style="border-color:#30363d">
      <h5 class="modal-title"><i class="bi bi-gear"></i> System Settings</h5>
      <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
    </div>
    <div class="modal-body">
      <div class="mb-3">
        <label class="form-label">Max threads</label>
        <input type="number" id="cfgMaxThreads" class="form-control form-control-sm" value="{sys_cfg.get('max_threads',8)}">
        <div class="form-text">Upper limit for threads per model. CPU has {cores} cores.</div>
      </div>
      <div class="mb-3">
        <div class="form-check form-switch">
          <input class="form-check-input" type="checkbox" id="cfgAutoThreads" {'checked' if sys_cfg.get('auto_threads') else ''}>
          <label class="form-check-label">Auto-distribute threads across running models</label>
        </div>
      </div>
      <div class="mb-3">
        <label class="form-label">Max RAM usage</label>
        <input type="text" id="cfgMaxRam" class="form-control form-control-sm" value="{html_mod.escape(str(sys_cfg.get('max_ram_usage','4G')))}">
      </div>
    </div>
    <div class="modal-footer" style="border-color:#30363d">
      <button class="btn btn-primary btn-sm" onclick="saveSettings()">Save</button>
    </div>
  </div></div>
</div>

<!-- Add Preset Modal -->
<div class="modal fade" id="addPresetModal" tabindex="-1">
  <div class="modal-dialog"><div class="modal-content" style="background:#161b22;border-color:#30363d">
    <div class="modal-header" style="border-color:#30363d">
      <h5 class="modal-title"><i class="bi bi-plus-circle"></i> Add preset</h5>
      <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
    </div>
    <div class="modal-body">
      <div class="mb-2">
        <label class="form-label small">Name</label>
        <input type="text" id="newPresetName" class="form-control form-control-sm" placeholder="My Model">
      </div>
      <div class="mb-2">
        <label class="form-label small">HuggingFace path</label>
        <input type="text" id="newPresetPath" class="form-control form-control-sm" placeholder="owner/repo:file.gguf">
      </div>
      <div class="mb-2">
        <label class="form-label small">Description (optional)</label>
        <input type="text" id="newPresetDesc" class="form-control form-control-sm" placeholder="Short description">
      </div>
    </div>
    <div class="modal-footer" style="border-color:#30363d">
      <button class="btn btn-primary btn-sm" onclick="saveNewPreset()">Add</button>
    </div>
  </div></div>
</div>

<!-- Parameters Modal -->
<div class="modal fade" id="paramsModal" tabindex="-1">
  <div class="modal-dialog"><div class="modal-content" style="background:#161b22;border-color:#30363d">
    <div class="modal-header" style="border-color:#30363d">
      <h5 class="modal-title"><i class="bi bi-sliders"></i> Model Parameters — <span id="pmName"></span></h5>
      <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
    </div>
    <div class="modal-body" id="paramsBody"></div>
    <div class="modal-footer" style="border-color:#30363d">
      <button class="btn btn-primary btn-sm" onclick="saveParams()">Save Parameters</button>
    </div>
  </div></div>
</div>

<!-- Toast container -->
<div class="toast-container position-fixed bottom-0 end-0 p-3" id="toastBox"></div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
var _models = [];
var _presets = [];

function loadPresets() {{
  fetch('/ai/presets').then(function(r){{ return r.json(); }}).then(function(d){{
    _presets = d.presets || [];
    var hidden = JSON.parse(localStorage.getItem('llamacpp_hidden_presets') || '[]');
    var custom = JSON.parse(localStorage.getItem('llamacpp_custom_presets') || '[]');
    renderPresets(_presets.filter(function(p){{ return hidden.indexOf(p.id)===-1; }}).concat(custom));
  }});
}}
function renderPresets(list) {{
  var el = document.getElementById('presetsList');
  el.innerHTML = list.map(function(p, i){{
    var pathSafe = esc(p.path).replace(/"/g, '&quot;');
    return '<div class="card d-inline-block" style="background:#21262d;border-color:#30363d;max-width:280px">'
      +'<div class="card-body p-2">'
      +'<div class="d-flex justify-content-between align-items-start"><strong class="small">'+esc(p.name)+'</strong>'
      +'<button class="btn btn-sm btn-outline-secondary py-0 px-1" onclick="removePreset(\\''+esc(p.id)+'\\')" title="Remove from list"><i class="bi bi-x"></i></button></div>'
      +'<p class="small text-muted mb-1" style="font-size:.75rem">'+esc(p.desc||'')+'</p>'
      +'<button class="btn btn-sm btn-primary w-100" data-path="'+pathSafe+'" onclick="downloadPreset(this.dataset.path)"><i class="bi bi-download"></i> Download</button>'
      +'</div></div>';
  }}).join('');
}}
function downloadPreset(path) {{
  document.getElementById('dlUrl').value = path || '';
  if (path) downloadModel();
}}
function removePreset(id) {{
  var hidden = JSON.parse(localStorage.getItem('llamacpp_hidden_presets') || '[]');
  if (hidden.indexOf(id)===-1) {{ hidden.push(id); localStorage.setItem('llamacpp_hidden_presets', JSON.stringify(hidden)); }}
  var custom = JSON.parse(localStorage.getItem('llamacpp_custom_presets') || '[]');
  custom = custom.filter(function(p){{ return p.id!==id; }});
  localStorage.setItem('llamacpp_custom_presets', JSON.stringify(custom));
  loadPresets();
}}
function showAddPresetModal() {{
  document.getElementById('newPresetName').value = '';
  document.getElementById('newPresetPath').value = '';
  document.getElementById('newPresetDesc').value = '';
  new bootstrap.Modal(document.getElementById('addPresetModal')).show();
}}
function saveNewPreset() {{
  var name = document.getElementById('newPresetName').value.trim();
  var path = document.getElementById('newPresetPath').value.trim();
  var desc = document.getElementById('newPresetDesc').value.trim();
  if (!name || !path) {{ toast('Name and path required','error'); return; }}
  var custom = JSON.parse(localStorage.getItem('llamacpp_custom_presets') || '[]');
  var id = 'custom_' + Date.now();
  custom.push({{id:id, name:name, path:path, desc:desc}});
  localStorage.setItem('llamacpp_custom_presets', JSON.stringify(custom));
  bootstrap.Modal.getInstance(document.getElementById('addPresetModal')).hide();
  loadPresets();
  toast('Preset added');
}}
function restoreHiddenPresets() {{
  localStorage.removeItem('llamacpp_hidden_presets');
  loadPresets();
  toast('Presets restored');
}}

function toast(msg, type) {{
  var id = 't'+Date.now();
  var bg = type==='error'?'bg-danger':type==='warn'?'bg-warning text-dark':'bg-success';
  document.getElementById('toastBox').insertAdjacentHTML('beforeend',
    '<div id="'+id+'" class="toast align-items-center '+bg+' border-0" role="alert"><div class="d-flex"><div class="toast-body">'+msg+'</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div></div>');
  var el = document.getElementById(id);
  new bootstrap.Toast(el, {{delay:4000}}).show();
  el.addEventListener('hidden.bs.toast', function(){{ el.remove(); }});
}}

function api(method, url, body) {{
  var opts = {{method:method, headers:{{'Content-Type':'application/json'}}}};
  if (body) opts.body = JSON.stringify(body);
  return fetch(url, opts).then(function(r){{ return r.json().then(function(d){{ d._status=r.status; return d; }}); }});
}}

var _loadModelsInterval = null;
function loadModels(autoRefresh) {{
  api('GET','/ai/models').then(function(d){{
    _models = d.models || [];
    renderModels();
    renderTestSelect();
    if (autoRefresh !== false) {{
      clearInterval(_loadModelsInterval);
      var hasLoading = _models.some(function(m){{ return m.status==='running' && m.ready!==true; }});
      if (hasLoading) {{
        _loadModelsInterval = setInterval(loadModels, 3000);
      }}
    }}
  }}).catch(function(){{ toast('Failed to load models','error'); }});
}}

function editName(id) {{
  var m = _models.find(function(x){{ return x.id===id; }});
  var currentName = m ? m.name : '';
  var n = prompt('Model name:', currentName);
  if (n === null) return;
  n = n.trim();
  if (!n) {{ toast('Name cannot be empty','error'); return; }}
  api('PUT','/ai/models/'+id+'/name', {{name:n}}).then(function(d){{
    if (d.error) toast(d.error,'error'); else {{ toast('Name updated'); loadModels(); }}
  }});
}}

function editPath(id) {{
  var m = _models.find(function(x){{ return x.id===id; }});
  if (!m) return;
  if (m.status==='running') {{ toast('Stop the model first to change path','error'); return; }}
  var p = prompt('Model path (for split files use first part: -00001-of-00002.gguf):', m.model_path || '');
  if (p === null) return;
  p = p.trim();
  if (!p) {{ toast('Path cannot be empty','error'); return; }}
  api('PUT','/ai/models/'+id+'/path', {{model_path:p}}).then(function(d){{
    if (d.error) toast(d.error,'error'); else {{ toast('Path updated'); loadModels(); }}
  }});
}}
function editPort(id, currentPort, isRunning) {{
  if (isRunning) {{ toast('Stop the model first to change port','error'); return; }}
  var p = prompt('New port (1-65535):', currentPort);
  if (p === null) return;
  var port = parseInt(p, 10);
  if (isNaN(port) || port < 1 || port > 65535) {{ toast('Invalid port','error'); return; }}
  api('PUT','/ai/models/'+id+'/port', {{port:port}}).then(function(d){{
    if (d.error) toast(d.error,'error'); else {{ toast('Port updated to '+port); loadModels(); }}
  }});
}}

function copyApi(id, port) {{
  var base = window.location.origin;
  var gen = base + '/ai/generate';
  var host = window.location.hostname || 'localhost';
  var proto = window.location.protocol || 'http:';
  var direct = proto + '//' + host + ':' + port + '/v1/chat/completions';
  var opt = 'Optional: temperature, top_p, top_k, repeat_penalty, max_tokens (auto=4096), seed, threads, ram, ctx';
  var getUrl = gen + '?model_id=' + id + '&prompt=Your+prompt&temperature=0.7&threads=max&ram=max';
  var txt = 'Manager API:\\n  POST ' + gen + '\\n  Body: {{"model_id": ' + id + ', "prompt": "Your prompt", "temperature": 0.7, "max_tokens": "auto", "threads": "max", "ram": "max"}}\\n  ' + opt + '\\n\\n  GET: ' + getUrl + '\\n\\nDirect (OpenAI): ' + direct;
  navigator.clipboard.writeText(txt).then(function(){{ toast('API copied to clipboard'); }}).catch(function(){{ toast('Copy failed','error'); }});
}}

function renderModels() {{
  var tb = document.getElementById('modelsBody');
  if (!_models.length) {{ tb.innerHTML='<tr><td colspan="9" class="text-center text-muted">No models registered. Download or register one above.</td></tr>'; return; }}
  tb.innerHTML = _models.map(function(m){{
    var p = m.parameters || {{}};
    var running = m.status==='running';
    var ready = m.ready === true;
    var badge = running ? (ready ? 'badge-running' : 'badge-loading') : (m.status==='error'?'badge-error':'badge-stopped');
    var dp = m.download_progress || {{}};
    var pct = dp.pct != null ? Math.round(dp.pct) : null;
    var mbDone = dp.bytes_done_mb;
    var mbTotal = dp.bytes_total_mb;
    var progStr = '';
    if (!ready && (pct != null || mbDone != null)) {{
      if (mbTotal != null) progStr = ' ' + (mbDone||0) + ' / ' + mbTotal + ' MB';
      else if (mbDone != null) progStr = ' ' + mbDone + ' MB';
      if (pct != null) progStr = (progStr ? ' ' : ' ') + pct + '%' + progStr;
    }}
    var statusText = running ? (ready ? 'ready' : 'downloading...' + progStr) : m.status;
    var startBtn = running
      ? '<button class="btn btn-outline-danger btn-sm me-1" onclick="stopM('+m.id+')"><i class="bi bi-stop-fill"></i></button>'
      : '<button class="btn btn-outline-success btn-sm me-1" onclick="startM('+m.id+')"><i class="bi bi-play-fill"></i></button>';
    var base = window.location.origin;
    var apiUrl = base + '/ai/generate';
    var directUrl = (window.location.hostname || 'localhost') + ':' + m.port;
    return '<tr>'
      +'<td>'+m.id+'</td>'
      +'<td><strong>'+esc(m.name)+'</strong><button class="btn btn-sm btn-outline-secondary py-0 px-1 ms-1" onclick="editName('+m.id+')" title="Edit name"><i class="bi bi-pencil"></i></button><br><small class="text-muted" style="font-size:.75rem">'+esc(m.model_path)+'</small><button class="btn btn-sm btn-outline-secondary py-0 px-1 ms-1" onclick="editPath('+m.id+')" title="Edit path"><i class="bi bi-pencil"></i></button></td>'
      +'<td><span class="badge '+badge+'" title="'+(ready?'Ready for requests':'Downloading/loading model')+'">'+statusText+'</span>'+(dp.pct!=null&&!ready?'<div class="progress mt-1" style="height:4px;width:80px"><div class="progress-bar" style="width:'+Math.min(100,dp.pct||0)+'%"></div></div>':'')+'</td>'
      +'<td><span class="port-val">'+m.port+'</span><button class="btn btn-sm btn-outline-secondary py-0 px-1 ms-1" onclick="editPort('+m.id+','+m.port+','+(m.status==='running'?'true':'false')+')" title="Edit port"><i class="bi bi-pencil"></i></button></td>'
      +'<td><small><code class="text-info" style="font-size:.7rem">POST '+apiUrl+'</code><br>model_id: '+m.id+'</small><button class="btn btn-sm btn-outline-secondary py-0 px-1 ms-1" onclick="copyApi('+m.id+','+m.port+')" title="Copy API"><i class="bi bi-clipboard"></i></button></td>'
      +'<td>'+(p.ctx||4096)+'</td>'
      +'<td>'+(p.threads||'auto')+'</td>'
      +'<td>'+(p.gpu_layers!=null&&p.gpu_layers>=0?p.gpu_layers:'off')+'</td>'
      +'<td class="text-nowrap">'
        +startBtn
        +'<button class="btn btn-outline-info btn-sm me-1" onclick="openParams('+m.id+')"><i class="bi bi-sliders"></i></button>'
        +'<button class="btn btn-outline-danger btn-sm" onclick="deleteM('+m.id+',\\''+esc(m.name)+'\\')"><i class="bi bi-trash"></i></button>'
      +'</td></tr>';
  }}).join('');
}}

function renderTestSelect() {{
  var sel = document.getElementById('testModel');
  sel.innerHTML = _models.map(function(m){{ return '<option value="'+m.id+'">'+esc(m.name)+' (id:'+m.id+')</option>'; }}).join('');
}}

function esc(s) {{ var d=document.createElement('div'); d.textContent=s||''; return d.innerHTML; }}

function startM(id) {{
  toast('Starting model '+id+'...','warn');
  api('POST','/ai/models/'+id+'/start').then(function(d){{
    if (d.error) toast(d.error,'error'); else {{ toast('Model started on port '+d.port); loadModels(); }}
  }});
}}
function stopM(id) {{
  api('POST','/ai/models/'+id+'/stop').then(function(d){{
    if (d.error) toast(d.error,'error'); else {{ toast('Model stopped'); loadModels(); }}
  }});
}}
function deleteM(id, name) {{
  if (!confirm('Delete model "'+name+'" (id:'+id+')? This removes it from the database.')) return;
  var delFile = confirm('Also delete the .gguf file from disk?');
  api('POST','/ai/models/'+id+'/delete', {{delete_file:delFile}}).then(function(d){{
    if (d.error) toast(d.error,'error'); else {{ toast('Model deleted'); loadModels(); }}
  }});
}}

function openParams(id) {{
  var m = _models.find(function(x){{ return x.id===id; }});
  if (!m) return;
  document.getElementById('pmName').textContent = m.name;
  var p = m.parameters || {{}};
  var fields = [
    ['ctx','Context size',p.ctx||4096,'number'],
    ['threads','Threads (0=auto)',p.threads||0,'number'],
    ['gpu_layers','GPU layers (-1=off)',p.gpu_layers!=null?p.gpu_layers:-1,'number'],
    ['temperature','Temperature',p.temperature!=null?p.temperature:0.7,'number'],
    ['top_p','Top P',p.top_p!=null?p.top_p:0.9,'number'],
    ['top_k','Top K',p.top_k||40,'number'],
    ['repeat_penalty','Repeat penalty',p.repeat_penalty||1.1,'number'],
    ['max_tokens','Max tokens',p.max_tokens||1024,'number'],
    ['seed','Seed (-1=random)',p.seed!=null?p.seed:-1,'number'],
  ];
  document.getElementById('paramsBody').innerHTML = '<input type="hidden" id="pmId" value="'+id+'">'
    + fields.map(function(f){{ return '<div class="mb-2"><label class="form-label small">'+f[1]+'</label><input type="'+f[3]+'" step="any" class="form-control form-control-sm pm-field" data-key="'+f[0]+'" value="'+f[2]+'"></div>'; }}).join('');
  new bootstrap.Modal(document.getElementById('paramsModal')).show();
}}
function saveParams() {{
  var id = document.getElementById('pmId').value;
  var params = {{}};
  document.querySelectorAll('.pm-field').forEach(function(el){{ params[el.dataset.key] = parseFloat(el.value); }});
  api('PUT','/ai/models/'+id+'/parameters',params).then(function(d){{
    if (d.error) toast(d.error,'error'); else {{ toast('Parameters saved'); bootstrap.Modal.getInstance(document.getElementById('paramsModal')).hide(); loadModels(); }}
  }});
}}

function registerModel() {{
  var name = document.getElementById('regName').value.trim();
  var path = document.getElementById('regPath').value.trim();
  var port = parseInt(document.getElementById('regPort').value) || 0;
  if (!name || !path) {{ toast('Name and path required','error'); return; }}
  var body = {{name:name, model_path:path}};
  if (port) body.port = port;
  else {{ toast('Getting next port...'); }}
  if (!port) {{
    api('GET','/ai/next-port').then(function(d){{
      body.port = d.port;
      doRegister(body);
    }});
  }} else {{ doRegister(body); }}
}}
function doRegister(body) {{
  api('POST','/ai/models',body).then(function(d){{
    if (d.error) toast(d.error,'error'); else {{ toast('Model registered (id:'+d.id+')'); loadModels(); document.getElementById('regName').value=''; document.getElementById('regPath').value=''; document.getElementById('regPort').value=''; }}
  }});
}}

function downloadModel() {{
  var val = document.getElementById('dlUrl').value.trim();
  if (!val) {{ toast('Enter URL or owner/repo:file','error'); return; }}
  document.getElementById('dlProgress').classList.remove('d-none');
  document.getElementById('dlBar').style.width = '0%';
  document.getElementById('downloadLog').textContent = 'Starting download...';
  var body = val.startsWith('http://') || val.startsWith('https://') ? {{url:val}} : {{model:val}};
  api('POST','/ai/models/download', body).then(function(d){{
    if (d.job_id) {{
      pollDownload(d.job_id);
    }} else if (d.error) {{
      document.getElementById('downloadLog').textContent = 'Error: ' + d.error;
      toast(d.error,'error');
    }} else {{
      document.getElementById('dlBar').style.width = '100%';
      document.getElementById('downloadLog').textContent = 'Done! Registered as "' + d.name + '" (id:'+d.model_id+')';
      toast('Model downloaded and registered!');
      loadModels();
    }}
  }}).catch(function(e){{ document.getElementById('downloadLog').textContent = 'Error: '+e; toast('Download failed','error'); }});
}}
function pollDownload(jobId) {{
  var iv = setInterval(function(){{
    fetch('/ai/models/download/progress?job_id='+encodeURIComponent(jobId)).then(function(r){{return r.json();}}).then(function(d){{
      document.getElementById('dlBar').style.width = (d.pct||0)+'%';
      var msg = (d.pct!=null ? d.pct+'% ' : '') + (d.status || '');
      if (d.bytes_done_mb!=null || d.bytes_done) msg += ' — ' + (d.bytes_done_mb!=null ? d.bytes_done_mb+'MB' : formatBytes(d.bytes_done)) + (d.bytes_total_mb!=null ? ' / '+d.bytes_total_mb+'MB' : (d.bytes_total ? ' / '+formatBytes(d.bytes_total) : ''));
      document.getElementById('downloadLog').textContent = msg;
      if (d.status === 'done') {{
        clearInterval(iv);
        toast('Model downloaded! id:'+d.model_id);
        loadModels();
      }} else if (d.status === 'error') {{
        clearInterval(iv);
        toast(d.error||'Download failed','error');
      }}
    }}).catch(function(){{}});
  }}, 1000);
}}
function formatBytes(b) {{ if (b<1024) return b+'B'; if (b<1048576) return (b/1024).toFixed(1)+'KB'; if (b<1073741824) return (b/1048576).toFixed(1)+'MB'; return (b/1073741824).toFixed(2)+'GB'; }}

function applyModelParamsToTest() {{
  var mid = document.getElementById('testModel').value;
  var m = _models.find(function(x){{ return String(x.id)===String(mid); }});
  if (!m || !m.parameters) return;
  var p = m.parameters;
  var set = function(id, val) {{ var el = document.getElementById(id); if (el && val!=null) el.value = val; }};
  set('testMaxTokens', p.max_tokens);
  set('testTemp', p.temperature);
  set('testTopP', p.top_p);
  set('testTopK', p.top_k);
  set('testRepeatPenalty', p.repeat_penalty);
  set('testSeed', p.seed);
}}
function testGenerate() {{
  var modelId = document.getElementById('testModel').value;
  var prompt = document.getElementById('testPrompt').value.trim();
  if (!prompt) {{ toast('Enter a prompt','error'); return; }}
  var btn = document.getElementById('testBtn');
  btn.disabled = true; btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Generating...';
  document.getElementById('testResult').classList.remove('d-none');
  document.getElementById('testOutput').textContent = 'Waiting for response...';
  document.getElementById('testUsage').textContent = '';
  var body = {{
    model_id: parseInt(modelId),
    prompt: prompt,
    system: document.getElementById('testSystem').value.trim(),
    max_tokens: (function(){{ var v=document.getElementById('testMaxTokens').value.trim().toLowerCase(); return (v===''||v==='auto') ? 'auto' : (parseInt(v)||4096); }})(),
    temperature: parseFloat(document.getElementById('testTemp').value)||0.7,
    top_p: parseFloat(document.getElementById('testTopP').value),
    top_k: parseInt(document.getElementById('testTopK').value),
    repeat_penalty: parseFloat(document.getElementById('testRepeatPenalty').value),
    seed: parseInt(document.getElementById('testSeed').value),
    threads: document.getElementById('testThreads').value,
    ram: document.getElementById('testRam').value
  }};
  if (isNaN(body.top_p)) delete body.top_p;
  if (isNaN(body.top_k)) delete body.top_k;
  if (isNaN(body.repeat_penalty)) delete body.repeat_penalty;
  if (isNaN(body.seed)) delete body.seed;
  api('POST','/ai/generate', body).then(function(d){{
    btn.disabled = false; btn.innerHTML = '<i class="bi bi-play-fill"></i> Generate';
    if (d.error) {{ document.getElementById('testOutput').textContent = 'ERROR: '+d.error; toast(d.error,'error'); }}
    else {{
      document.getElementById('testOutput').textContent = d.text||'(empty response)';
      var u = d.usage||{{}};
      var parts = [];
      if (u.total_tokens) parts.push('Tokens: prompt='+u.prompt_tokens+' completion='+u.completion_tokens+' total='+u.total_tokens);
      if (u.tokens_per_second!=null||u.gen_second!=null) parts.push((u.tokens_per_second||u.gen_second)+' tok/s');
      if (u.prompt_second!=null||u.prompt_tokens_per_second!=null) parts.push('prompt: '+(u.prompt_second||u.prompt_tokens_per_second)+' tok/s');
      if (u.eval_duration!=null) parts.push('eval: '+(u.eval_duration/1e9).toFixed(2)+'s');
      if (u.duration_seconds!=null||d.duration_seconds!=null) parts.push('total: '+(u.duration_seconds||d.duration_seconds)+'s');
      document.getElementById('testUsage').textContent = parts.length ? parts.join(' | ') : '';
    }}
  }}).catch(function(e){{ btn.disabled=false; btn.innerHTML='<i class="bi bi-play-fill"></i> Generate'; toast('Request failed','error'); }});
}}

function saveSettings() {{
  api('PUT','/ai/system-config', {{
    max_threads: parseInt(document.getElementById('cfgMaxThreads').value)||8,
    auto_threads: document.getElementById('cfgAutoThreads').checked ? 1 : 0,
    max_ram_usage: document.getElementById('cfgMaxRam').value.trim()||'4G'
  }}).then(function(d){{
    if (d.error) toast(d.error,'error');
    else {{ toast('Settings saved'); bootstrap.Modal.getInstance(document.getElementById('settingsModal')).hide(); }}
  }});
}}

function apiTesterAddHeader() {{
  var c = document.getElementById('apiHeaders');
  c.insertAdjacentHTML('beforeend', '<div class="input-group input-group-sm mb-1"><input type="text" class="form-control" placeholder="Header"><input type="text" class="form-control" placeholder="Value"></div>');
}}
function apiTesterLoad(url, method) {{
  document.getElementById('apiUrl').value = url.startsWith('http') ? url : (window.location.origin + (url.startsWith('/') ? url : '/' + url));
  document.getElementById('apiMethod').value = method;
  if (method === 'POST' && url.includes('generate')) document.getElementById('apiBody').value = '{{"model_id": 1, "prompt": "hello", "max_tokens": "auto"}}';
  else if (method === 'POST' && url.includes('download')) document.getElementById('apiBody').value = '{{"model": "Qwen/Qwen2.5-7B-Instruct-GGUF:qwen2.5-7b-instruct-q4_k_m.gguf"}}';
  else if (method === 'POST' && url.includes('/ai/models') && !url.includes('download')) document.getElementById('apiBody').value = '{{"name": "my-model", "model_path": "owner/repo:file.gguf"}}';
}}
function apiTesterSend() {{
  var method = document.getElementById('apiMethod').value;
  var urlRaw = document.getElementById('apiUrl').value.trim();
  var url = urlRaw.startsWith('http') ? urlRaw : (window.location.origin + (urlRaw.startsWith('/') ? urlRaw : '/' + urlRaw));
  var headers = {{}};
  document.querySelectorAll('#apiHeaders .input-group').forEach(function(g){{
    var inp = g.querySelectorAll('input');
    if (inp[0] && inp[0].value.trim()) headers[inp[0].value.trim()] = (inp[1] && inp[1].value) || '';
  }});
  if (!headers['Content-Type'] && (method === 'POST' || method === 'PUT')) headers['Content-Type'] = 'application/json';
  var opts = {{ method: method, headers: headers }};
  var bodyStr = document.getElementById('apiBody').value.trim();
  if (bodyStr && (method === 'POST' || method === 'PUT')) {{
    try {{ opts.body = JSON.stringify(JSON.parse(bodyStr)); }} catch(e) {{ opts.body = bodyStr; }}
  }}
  document.getElementById('apiResponse').classList.add('d-none');
  fetch(url, opts).then(function(r){{
    var ct = r.headers.get('content-type') || '';
    return r.text().then(function(t){{
      var j = null;
      try {{ j = ct.includes('json') ? JSON.parse(t) : null; }} catch(e) {{}}
      return {{ status: r.status, ok: r.ok, text: t, json: j }};
    }});
  }}).then(function(d){{
    document.getElementById('apiResponse').classList.remove('d-none');
    var st = document.getElementById('apiStatus');
    st.textContent = d.status;
    st.className = 'badge ms-1 ' + (d.ok ? 'bg-success' : 'bg-danger');
    var out = document.getElementById('apiResponseBody');
    out.textContent = d.json ? JSON.stringify(d.json, null, 2) : d.text;
    out.style.whiteSpace = 'pre-wrap';
  }}).catch(function(e){{
    document.getElementById('apiResponse').classList.remove('d-none');
    document.getElementById('apiStatus').textContent = 'Error';
    document.getElementById('apiStatus').className = 'badge ms-1 bg-danger';
    document.getElementById('apiResponseBody').textContent = String(e);
  }});
}}

loadModels();
loadPresets();
</script>
</body></html>"""


@app.route("/api-docs")
def api_docs():
    """API documentation page."""
    base = request.url_root.rstrip("/")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>llama.cpp Manager — API Docs</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body {{ background:#0d1117; color:#c9d1d9; font-family: system-ui, sans-serif; }}
code {{ background:#21262d; padding:2px 6px; border-radius:4px; font-size:.9em; }}
pre {{ background:#161b22; padding:12px; border-radius:6px; overflow-x:auto; color:#e6edf3; }}
h2 {{ color:#58a6ff; margin-top:1.5rem; border-bottom:1px solid #30363d; padding-bottom:.5rem; }}
h3 {{ color:#8b949e; font-size:1rem; margin-top:1rem; }}
.badge-get {{ background:#238636; }} .badge-post {{ background:#1f6feb; }} .badge-put {{ background:#9e6a03; }}
.endpoint {{ font-family: monospace; color:#58a6ff; }}
a {{ color:#58a6ff; }}
</style>
</head>
<body>
<div class="container py-4" style="max-width:800px">
<h1>llama.cpp Manager — API</h1>
<p class="text-muted">Base URL: <code>{base}</code></p>

<h2>Models (installed &amp; available)</h2>

<h3><span class="badge badge-get">GET</span> <span class="endpoint">/ai/models</span></h3>
<p>List all registered models. Use this to get model IDs for generation.</p>
<pre>curl "{base}/ai/models"</pre>
<p><strong>Response:</strong> <code>{{"models": [{{"id": 1, "name": "...", "port": 5011, "status": "running", "parameters": {{...}}}}]}}</code></p>

<h2>Generate text</h2>

<h3><span class="badge badge-post">POST</span> or <span class="badge badge-get">GET</span> <span class="endpoint">/ai/generate</span></h3>
<p>Generate text using a model. Model auto-starts if stopped.</p>
<pre>curl -X POST "{base}/ai/generate" -H "Content-Type: application/json" -d '{{
  "model_id": 1,
  "prompt": "Hello!",
  "max_tokens": "auto",
  "temperature": 0.7
}}'</pre>
<p><strong>Params:</strong> model_id (required), prompt (required), system, max_tokens, temperature, top_p, top_k, repeat_penalty, seed, threads, ram, ctx</p>
<p><strong>Response:</strong> <code>{{"text": "...", "usage": {{...}}, "duration_seconds": 1.2}}</code></p>

<h2>Download model</h2>

<h3><span class="badge badge-post">POST</span> <span class="endpoint">/ai/models/download</span></h3>
<p>Download a model and register it. Returns job_id to poll progress.</p>
<pre>curl -X POST "{base}/ai/models/download" -H "Content-Type: application/json" -d '{{
  "model": "Qwen/Qwen2.5-7B-Instruct-GGUF:qwen2.5-7b-instruct-q4_k_m.gguf"
}}'</pre>
<p>Or use <code>"url": "https://.../model.gguf"</code> for direct URL.</p>

<h3><span class="badge badge-get">GET</span> <span class="endpoint">/ai/models/download/progress?job_id=xxx</span></h3>
<p>Poll download status.</p>

<h2>Register / manage models</h2>

<h3><span class="badge badge-post">POST</span> <span class="endpoint">/ai/models</span></h3>
<p>Register a model (no download). Port is optional (auto-assigned).</p>
<pre>curl -X POST "{base}/ai/models" -H "Content-Type: application/json" -d '{{
  "name": "my-model",
  "model_path": "owner/repo:file.gguf"
}}'</pre>

<h3><span class="badge badge-post">POST</span> <span class="endpoint">/ai/models/{{id}}/start</span></h3>
<p>Start a model.</p>

<h3><span class="badge badge-post">POST</span> <span class="endpoint">/ai/models/{{id}}/stop</span></h3>
<p>Stop a model.</p>

<h2>Other</h2>

<h3><span class="badge badge-get">GET</span> <span class="endpoint">/ai/presets</span></h3>
<p>List recommended model presets for download.</p>

<h3><span class="badge badge-get">GET</span> <span class="endpoint">/ai/next-port</span></h3>
<p>Get next available port.</p>

<p class="mt-4"><a href="{base}/">← Back to dashboard</a></p>
</div>
</body>
</html>"""


@app.route("/ai/presets", methods=["GET"])
def api_presets():
    """GET /ai/presets - return default model presets for one-click download."""
    return jsonify({"presets": DEFAULT_PRESETS})


@app.route("/ai/next-port", methods=["GET"])
def api_next_port():
    return jsonify({"port": get_next_port()})


@app.route("/ai/system-config", methods=["GET"])
def api_get_system_config():
    try:
        cfg = get_system_config()
        cfg["cpu_cores"] = _detect_cpu_cores()
        cfg["llama_server_found"] = _find_llama_server() is not None
        cfg["models_dir"] = config.MODELS_DIR
        return jsonify(cfg)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/ai/system-config", methods=["PUT"])
def api_update_system_config():
    try:
        data = request.get_json() or {}
        ok = update_system_config(
            max_threads=data.get("max_threads"),
            auto_threads=data.get("auto_threads"),
            max_ram_usage=data.get("max_ram_usage"),
        )
        if not ok:
            return jsonify({"error": "No valid fields provided"}), 400
        return jsonify({"message": "Settings updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/ai/models/<int:model_id>/delete", methods=["POST"])
def api_delete_model(model_id):
    try:
        data = request.get_json() or {}
        delete_file = bool(data.get("delete_file", False))
        ok, err = delete_model(model_id, delete_file=delete_file)
        if not ok:
            return jsonify({"error": err or "Model not found"}), 404
        return jsonify({"message": "Model deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/ai/models", methods=["GET"])
def api_list_models():
    """GET /ai/models - list all models."""
    try:
        models = list_models()
        log.info("[GET /ai/models] returning %d models", len(models))
        return jsonify({"models": models})
    except Exception as e:
        log.error("[GET /ai/models] error: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/ai/models", methods=["POST"])
def api_register_model():
    """POST /ai/models - register a new model."""
    try:
        data = request.get_json() or {}
        name = (data.get("name") or "").strip()
        model_path = (data.get("model_path") or "").strip()
        port = int(data.get("port") or 0)
        if not name or not model_path:
            return jsonify({"error": "name and model_path required"}), 400
        if not port:
            port = get_next_port()
        model_id = register_model(name, model_path, port)
        log.info("[POST /ai/models] registered model id=%s", model_id)
        return jsonify({"id": model_id, "message": "Model registered"})
    except Exception as e:
        log.error("[POST /ai/models] error: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/ai/models/<int:model_id>/start", methods=["POST"])
def api_start_model(model_id):
    """POST /ai/models/{id}/start - start model server."""
    try:
        ok, result = start_model(model_id)
        if not ok:
            log.error("[POST /ai/models/%s/start] failed: %s", model_id, result)
            return jsonify({"error": result}), 400
        log.info("[POST /ai/models/%s/start] started port=%s", model_id, result)
        return jsonify({"port": result, "message": "Model started"})
    except Exception as e:
        log.error("[POST /ai/models/%s/start] error: %s", model_id, e)
        return jsonify({"error": str(e)}), 500


@app.route("/ai/models/<int:model_id>/stop", methods=["POST"])
def api_stop_model(model_id):
    """POST /ai/models/{id}/stop - stop model server."""
    try:
        stop_model(model_id)
        log.info("[POST /ai/models/%s/stop] stopped", model_id)
        return jsonify({"message": "Model stopped"})
    except Exception as e:
        log.error("[POST /ai/models/%s/stop] error: %s", model_id, e)
        return jsonify({"error": str(e)}), 500


@app.route("/ai/models/<int:model_id>/name", methods=["PUT"])
def api_update_model_name(model_id):
    """PUT /ai/models/{id}/name - update model name."""
    try:
        data = request.get_json() or {}
        name = (data.get("name") or "").strip()
        if not name:
            return jsonify({"error": "name required"}), 400
        ok, err = update_model_name(model_id, name)
        if not ok:
            return jsonify({"error": err or "Failed"}), 400
        return jsonify({"message": "Name updated", "name": name})
    except Exception as e:
        log.error("[PUT /ai/models/%s/name] error: %s", model_id, e)
        return jsonify({"error": str(e)}), 500


@app.route("/ai/models/<int:model_id>/port", methods=["PUT"])
def api_update_model_port(model_id):
    """PUT /ai/models/{id}/port - update model port (model must be stopped)."""
    try:
        data = request.get_json() or {}
        port = int(data.get("port", 0))
        if not port:
            return jsonify({"error": "port required"}), 400
        ok, err = update_model_port(model_id, port)
        if not ok:
            return jsonify({"error": err}), 400
        return jsonify({"message": "Port updated", "port": port})
    except Exception as e:
        log.error("[PUT /ai/models/%s/port] error: %s", model_id, e)
        return jsonify({"error": str(e)}), 500


@app.route("/ai/models/<int:model_id>/path", methods=["PUT"])
def api_update_model_path(model_id):
    """PUT /ai/models/{id}/path - update model path (model must be stopped)."""
    try:
        data = request.get_json() or {}
        path = (data.get("model_path") or data.get("path") or "").strip()
        if not path:
            return jsonify({"error": "model_path required"}), 400
        ok, err = update_model_path(model_id, path)
        if not ok:
            return jsonify({"error": err or "Failed"}), 400
        return jsonify({"message": "Path updated", "model_path": path})
    except Exception as e:
        log.error("[PUT /ai/models/%s/path] error: %s", model_id, e)
        return jsonify({"error": str(e)}), 500


@app.route("/ai/models/<int:model_id>/parameters", methods=["PUT"])
def api_update_parameters(model_id):
    """PUT /ai/models/{id}/parameters - update model parameters."""
    try:
        data = request.get_json() or {}
        allowed = ["ctx", "threads", "gpu_layers", "temperature", "top_p", "top_k",
                   "repeat_penalty", "max_tokens", "stop_words", "seed", "mirostat",
                   "mirostat_eta", "mirostat_tau"]
        params = {k: data[k] for k in allowed if k in data}
        if not params:
            return jsonify({"error": "No valid parameters provided"}), 400
        ok = update_parameters(model_id, params)
        if not ok:
            return jsonify({"error": "Model not found"}), 404
        log.info("[PUT /ai/models/%s/parameters] updated", model_id)
        return jsonify({"message": "Parameters updated"})
    except Exception as e:
        log.error("[PUT /ai/models/%s/parameters] error: %s", model_id, e)
        return jsonify({"error": str(e)}), 500


@app.route("/ai/generate", methods=["POST", "GET"])
def api_generate():
    """
    POST /ai/generate - generate text via a model.
    Body: { "model": str, "prompt": str } or { "model_id": int, "prompt": str }
    Accepts "model" by name (e.g. "mistral") or "model_id" by id. Proxies to llama-server.
    GET: ?model_id=3&prompt=hi&temperature=0.7&max_tokens=512&threads=max&ram=max
    POST body: same fields. threads: max|medium|min|N. ram: max|medium|min (default max). ctx: override context size.
    """
    try:
        if request.method == "GET":
            data = dict(request.args)
            # Coerce numeric params from query string
            for k in ("model_id", "max_tokens", "top_k", "seed"):
                if k in data and data[k] != "":
                    try:
                        data[k] = int(data[k])
                    except (ValueError, TypeError):
                        pass
            for k in ("temperature", "top_p", "repeat_penalty"):
                if k in data and data[k] != "":
                    try:
                        data[k] = float(data[k])
                    except (ValueError, TypeError):
                        pass
        else:
            data = request.get_json() or {}
        model_id = data.get("model_id")
        model_name = (data.get("model") or "").strip()
        if model_id is not None:
            model_id = int(model_id)
            model = get_model(model_id)
        elif model_name:
            model = get_model_by_name(model_name)
            if model:
                model_id = model["id"]
        else:
            return jsonify({"error": "model or model_id required"}), 400
        if not model:
            return jsonify({"error": "Model not found"}), 404
        prompt = (data.get("prompt") or "").strip()
        if not prompt:
            return jsonify({"error": "prompt required"}), 400
        # Support params from JSON body or query string
        src = data if request.method == "POST" else request.args
        system = (src.get("system") or data.get("system") or "").strip()
        max_tokens_raw = src.get("max_tokens") or data.get("max_tokens")
        if max_tokens_raw is None or max_tokens_raw == "" or str(max_tokens_raw).strip().lower() == "auto":
            max_tokens = 4096
        else:
            max_tokens = int(max_tokens_raw)
        temperature = float(src.get("temperature") or data.get("temperature") or 0.7)
        top_p = src.get("top_p") or data.get("top_p")
        top_k = src.get("top_k") or data.get("top_k")
        repeat_penalty = src.get("repeat_penalty") or data.get("repeat_penalty")
        seed = src.get("seed") or data.get("seed")
        threads_spec = src.get("threads") or data.get("threads")
        ram_spec = src.get("ram") or data.get("ram") or "max"
        ctx_spec = src.get("ctx") or data.get("ctx")

        def build_start_overrides():
            o = {}
            if threads_spec is not None and threads_spec != "":
                o["threads"] = resolve_threads_preset(threads_spec)
            default_ctx = int((model.get("parameters") or {}).get("ctx", 4096))
            if ctx_spec is not None and ctx_spec != "":
                try:
                    o["ctx"] = max(512, int(ctx_spec))
                except (ValueError, TypeError):
                    pass
            elif ram_spec is not None and ram_spec != "":
                o["ctx"] = resolve_ram_preset(ram_spec, default_ctx)
            return o if o else None

        start_overrides = build_start_overrides()

        if model["status"] != "running":
            ok, res = start_model(model_id, overrides=start_overrides)
            if not ok:
                return jsonify({"error": f"Model not running: {res}"}), 400
            model = get_model(model_id)

        port = model["port"]
        url = f"{_model_url(port)}/v1/chat/completions"
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model["name"],
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if top_p is not None:
            payload["top_p"] = float(top_p)
        if top_k is not None:
            payload["top_k"] = int(top_k)
        if repeat_penalty is not None:
            payload["repeat_penalty"] = float(repeat_penalty)
        if seed is not None:
            payload["seed"] = int(seed)
        log.info("[POST /ai/generate] model_id=%s port=%s url=%s", model_id, port, url)
        auto_started = False
        while True:
            try:
                last_err = None
                t0 = time.perf_counter()
                for attempt in range(15):
                    r = requests.post(url, json=payload, timeout=120)
                    if r.status_code == 503 and attempt < 14:
                        log.info("[POST /ai/generate] 503 (model loading) attempt %s/15, retrying in 3s", attempt + 1)
                        time.sleep(3)
                        continue
                    last_err = r
                    break
                r = last_err
                if r.status_code == 500:
                    mark_stopped_if_dead(model_id)
                    try:
                        err_body = r.json()
                        err_msg = err_body.get("error") or err_body.get("message") or r.text[:200]
                    except Exception:
                        err_msg = r.text[:200] if r.text else str(r.reason)
                    log.error("[POST /ai/generate] 500 model_id=%s: %s", model_id, err_msg)
                    return jsonify({"error": f"Model error: {err_msg}"}), 502
                r.raise_for_status()
                break
            except requests.RequestException as e:
                err_str = str(e)
                is_refused = "refused" in err_str.lower() or "10061" in err_str
                if is_refused and not auto_started:
                    mark_stopped_if_dead(model_id)
                    log.info("[POST /ai/generate] Connection refused, auto-starting model_id=%s", model_id)
                    ok, res = start_model(model_id, overrides=start_overrides)
                    if not ok:
                        return jsonify({"error": f"Model failed to start: {res}"}), 502
                    auto_started = True
                    model = get_model(model_id)
                    port = model["port"]
                    url = f"{_model_url(port)}/v1/chat/completions"
                    log.info("[POST /ai/generate] Model started, waiting 10s for load, then retrying port=%s", port)
                    time.sleep(10)
                    continue
                mark_stopped_if_dead(model_id)
                msg = "Connection refused. Model process may have crashed. Try Stop then Start." if is_refused else str(e)
                log.error("[POST /ai/generate] %s model_id=%s port=%s", msg, model_id, port)
                return jsonify({"error": msg}), 502

        j = r.json()
        content = ""
        if j.get("choices"):
            content = (j["choices"][0].get("message") or {}).get("content") or ""
        usage = dict(j.get("usage") or {})
        # Add tokens/sec and timing stats (llama-server provides gen_second, prompt_second, eval_duration)
        comp = usage.get("completion_tokens") or 0
        eval_ns = usage.get("eval_duration")
        if comp and usage.get("gen_second") is None and eval_ns is not None:
            sec = float(eval_ns) / 1e9 if eval_ns > 1e6 else float(eval_ns) / 1000
            if sec > 0:
                usage["gen_second"] = round(comp / sec, 2)
        if usage.get("gen_second") is None and comp > 0:
            elapsed = time.perf_counter() - t0
            if elapsed > 0.05:
                usage["gen_second"] = round(comp / elapsed, 2)
                usage["eval_duration"] = int(elapsed * 1e9)
        if usage.get("gen_second") is not None and "tokens_per_second" not in usage:
            usage["tokens_per_second"] = usage["gen_second"]
        duration_seconds = round(time.perf_counter() - t0, 2)
        usage["duration_seconds"] = duration_seconds
        log.info("[POST /ai/generate] model_id=%s success duration=%.2fs", model_id, duration_seconds)
        return jsonify({"text": content.strip(), "usage": usage, "duration_seconds": duration_seconds})
    except requests.RequestException as e:
        mark_stopped_if_dead(model_id)
        err_str = str(e)
        is_refused = "refused" in err_str.lower() or "10061" in err_str
        if is_refused:
            msg = "Connection refused to llama-server. Model process may have crashed. Check llamacpp_manager.log for errors. Try Stop then Start."
            log.error("[POST /ai/generate] %s model_id=%s port=%s", msg, model_id, port)
            return jsonify({"error": msg}), 502
        log.error("[POST /ai/generate] request error: %s", e)
        return jsonify({"error": f"Model request failed: {e}"}), 502
    except Exception as e:
        log.error("[POST /ai/generate] error: %s", e)
        return jsonify({"error": str(e)}), 500


def _download_worker(job_id, url, dest_path, name):
    """Background thread that downloads a model and updates _download_progress."""
    try:
        _download_progress[job_id] = {"status": "connecting", "pct": 0, "bytes_done": 0, "bytes_total": 0, "bytes_done_mb": 0, "bytes_total_mb": None, "name": name}
        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()
        total = int(resp.headers.get("content-length") or 0)
        _download_progress[job_id]["bytes_total"] = total
        _download_progress[job_id]["bytes_total_mb"] = round(total / (1024 * 1024), 1) if total else None
        _download_progress[job_id]["status"] = "downloading"
        done = 0
        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
                    done += len(chunk)
                    _download_progress[job_id]["bytes_done"] = done
                    _download_progress[job_id]["pct"] = int(done * 100 / total) if total else 0
                    _download_progress[job_id]["bytes_done_mb"] = round(done / (1024 * 1024), 1)
                    _download_progress[job_id]["bytes_total_mb"] = round(total / (1024 * 1024), 1) if total else None
        port = get_next_port()
        model_id = register_model(name, dest_path, port)
        _download_progress[job_id].update({"status": "done", "pct": 100, "model_id": model_id, "port": port})
        log.info("[download] done job=%s model_id=%s", job_id, model_id)
    except Exception as e:
        log.error("[download] job=%s error: %s", job_id, e)
        _download_progress[job_id].update({"status": "error", "error": str(e)})


def _model_path_to_url(model_path: str) -> Optional[str]:
    """Convert owner/repo:file to HuggingFace direct download URL."""
    s = (model_path or "").strip()
    if ":" in s:
        repo, filename = s.split(":", 1)
        repo = repo.strip()
        filename = filename.strip()
        if repo and filename:
            # owner/repo or org/repo
            parts = repo.split("/")
            if len(parts) >= 2:
                return f"https://huggingface.co/{repo}/resolve/main/{filename}"
    return None


@app.route("/ai/models/download", methods=["POST"])
def api_download_model():
    """
    POST /ai/models/download - download a model and register it.
    Body: { "url": "https://.../model.gguf" } or { "model": "owner/repo:file.gguf" }
    Returns { job_id, name, dest_path } for progress polling. Poll GET /ai/models/download/progress?job_id=xxx
    """
    try:
        data = request.get_json() or {}
        url = (data.get("url") or "").strip()
        model_path = (data.get("model") or data.get("path") or "").strip()
        if not url and not model_path:
            return jsonify({"error": "url or model required. Example: {\"url\":\"https://.../model.gguf\"} or {\"model\":\"owner/repo:file.gguf\"}"}), 400

        if not url:
            url = _model_path_to_url(model_path)
            if not url:
                return jsonify({"error": "model must be owner/repo:filename (e.g. Qwen/Qwen2.5-7B-Instruct-GGUF:qwen2.5-7b-instruct-q4_0.gguf)"}), 400

        if not (url.startswith("http://") or url.startswith("https://")):
            return jsonify({"error": "url must be http or https"}), 400

        models_dir = config.MODELS_DIR
        os.makedirs(models_dir, exist_ok=True)
        filename = url.rstrip("/").split("/")[-1].split("?")[0] or "model.gguf"
        if not filename.lower().endswith(".gguf"):
            filename = filename + ".gguf"
        dest_path = os.path.join(models_dir, filename)
        name = os.path.splitext(filename)[0]

        job_id = uuid.uuid4().hex[:12]
        threading.Thread(target=_download_worker, args=(job_id, url, dest_path, name), daemon=True).start()
        log.info("[POST /ai/models/download] started job=%s url=%s", job_id, url)
        return jsonify({"job_id": job_id, "name": name, "dest_path": dest_path})
    except Exception as e:
        log.error("[POST /ai/models/download] error: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/ai/models/download/progress", methods=["GET"])
def api_download_progress():
    """
    GET /ai/models/download/progress?job_id=xxx - poll download status.
    Returns: status (connecting|downloading|done|error), pct, bytes_done, bytes_total,
             bytes_done_mb, bytes_total_mb, name, model_id (when done), port (when done), error (when error).
    """
    job_id = request.args.get("job_id", "").strip()
    if not job_id or job_id not in _download_progress:
        return jsonify({"error": "Unknown job_id. Use job_id from POST /ai/models/download."}), 404
    return jsonify(_download_progress[job_id])


def main():
    port = int(os.getenv("LLAMACPP_MANAGER_PORT", "5004"))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
