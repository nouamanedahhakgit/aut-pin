"""llamacpp_manager: manage models, resolve paths, launch llama-server."""
import logging
import os
import re
import subprocess
import threading
from typing import Any, Optional

import requests

from . import config
from .db import get_connection

log = logging.getLogger(__name__)

DEFAULT_PARAMS = {
    "ctx": 4096, "threads": 0, "gpu_layers": -1, "temperature": 0.7, "top_p": 0.9,
    "top_k": 40, "repeat_penalty": 1.1, "max_tokens": 1024, "stop_words": None,
    "seed": -1, "mirostat": 0, "mirostat_eta": 0.1, "mirostat_tau": 5.0,
}

_HF_REPO_PREFIXES: list[tuple[str, str]] = [
    ("qwen2.5-7b-instruct", "Qwen/Qwen2.5-7B-Instruct-GGUF"),
    ("qwen2.5-7b", "Qwen/Qwen2.5-7B-Instruct-GGUF"),
    ("mistral-7b-instruct", "TheBloke/Mistral-7B-Instruct-v0.2-GGUF"),
    ("Phi-3-mini-4k-instruct", "microsoft/Phi-3-mini-4k-instruct-gguf"),
    ("llama-2-7b-chat", "TheBloke/Llama-2-7B-Chat-GGUF"),
    ("mixtral-8x7b-instruct", "TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF"),
    ("falcon-7b-instruct", "TheBloke/Falcon-7B-Instruct-GGUF"),
    ("SmolLM2-7B-Instruct", "HuggingFaceTB/SmolLM2-7B-Instruct-GGUF"),
    ("Meta-Llama-3-8B-Instruct", "TheBloke/Meta-Llama-3-8B-Instruct-GGUF"),
]

_processes: dict[int, subprocess.Popen] = {}
_lock = threading.Lock()
_SPLIT_PATTERN = re.compile(r"(\d{5})-of-(\d{5})\.gguf$", re.IGNORECASE)


def _detect_cpu_cores() -> int:
    try:
        return os.cpu_count() or 4
    except Exception:
        return 4


def _find_llama_server() -> Optional[str]:
    bin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
    for p in [os.path.join(bin_dir, "llama-server.exe"), os.path.join(bin_dir, "llama-server"), "llama-server"]:
        if os.path.isfile(p):
            return os.path.abspath(p)
        if p == "llama-server":
            try:
                subprocess.run([p, "--help"], capture_output=True, timeout=2)
                return p
            except Exception:
                pass
    return None


def _to_abs_path(path: str) -> str:
    p = (path or "").strip()
    if not p:
        return ""
    if not os.path.isabs(p):
        p = os.path.join(config.MODELS_DIR, p)
    return os.path.normpath(p)


def _resolve_split_gguf_path(model_path: str) -> tuple[Optional[str], Optional[str]]:
    """Resolve path for split GGUF. Returns (path, None) or (None, error)."""
    abs_path = _to_abs_path(model_path)
    if not abs_path or not abs_path.lower().endswith(".gguf"):
        return (abs_path, None)
    m = _SPLIT_PATTERN.search(os.path.basename(abs_path))
    if not m:
        return (abs_path, None) if os.path.isfile(abs_path) else (None, f"Model file not found: {abs_path}")
    idx = int(m.group(1))
    total = int(m.group(2))
    if idx <= 1:
        return (abs_path, None) if os.path.isfile(abs_path) else (None, f"Model file not found: {abs_path}")
    first_filename = _SPLIT_PATTERN.sub(lambda mo: f"00001-of-{mo.group(2)}.gguf", os.path.basename(abs_path))
    first_path = os.path.join(os.path.dirname(abs_path), first_filename)
    if os.path.isfile(first_path):
        return (first_path, None)
    return (None, f"Split model requires first part: {first_filename} (not found). Download it.")


def _infer_hf_url_for_first_split(model_path: str, first_filename: str) -> Optional[str]:
    base = re.sub(r"-\d{5}-of-\d{5}$", "", os.path.splitext(first_filename)[0])
    base_lower = base.lower()
    for prefix, repo in _HF_REPO_PREFIXES:
        if base_lower.startswith(prefix.lower()) or prefix.lower() in base_lower:
            return f"https://huggingface.co/{repo}/resolve/main/{first_filename}"
    return None


def _download_file_sync(url: str, dest_path: str) -> tuple[bool, str]:
    try:
        os.makedirs(os.path.dirname(dest_path) or ".", exist_ok=True)
        resp = requests.get(url, stream=True, timeout=(30, 3600))
        resp.raise_for_status()
        total = int(resp.headers.get("content-length") or 0)
        done = 0
        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
                    done += len(chunk)
        if total and done < total:
            return (False, f"Incomplete: {done}/{total} bytes")
        return (True, "")
    except Exception as e:
        return (False, str(e))


def list_models() -> list[dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, model_path, port, status, created_at FROM models ORDER BY id")
        out = []
        for m in cur.fetchall():
            m = dict(m)
            m["parameters"] = get_parameters(m["id"])
            out.append(m)
        return out


def get_model(model_id: int) -> Optional[dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, model_path, port, status, created_at FROM models WHERE id = ?", (model_id,))
        row = cur.fetchone()
        if not row:
            return None
        m = dict(row)
        m["parameters"] = get_parameters(model_id)
        return m


def get_model_by_name(name: str) -> Optional[dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, model_path, port, status, created_at FROM models WHERE name = ?", (name.strip(),))
        row = cur.fetchone()
        if not row:
            return None
        m = dict(row)
        m["parameters"] = get_parameters(m["id"])
        return m


def get_parameters(model_id: int) -> dict[str, Any]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT ctx, threads, gpu_layers, temperature, top_p, top_k, repeat_penalty, max_tokens, "
                    "stop_words, seed, mirostat, mirostat_eta, mirostat_tau FROM model_parameters WHERE model_id = ?", (model_id,))
        row = cur.fetchone()
        return {k: row[k] for k in row} if row else dict(DEFAULT_PARAMS)


def update_parameters(model_id: int, params: dict[str, Any]) -> bool:
    cols = ["ctx", "threads", "gpu_layers", "temperature", "top_p", "top_k", "repeat_penalty", "max_tokens",
            "stop_words", "seed", "mirostat", "mirostat_eta", "mirostat_tau"]
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM model_parameters WHERE model_id = ?", (model_id,))
        all_p = {**DEFAULT_PARAMS, **{k: params[k] for k in cols if k in params}}
        if cur.fetchone():
            cur.execute("UPDATE model_parameters SET ctx=?, threads=?, gpu_layers=?, temperature=?, top_p=?, "
                        "top_k=?, repeat_penalty=?, max_tokens=?, stop_words=?, seed=?, mirostat=?, "
                        "mirostat_eta=?, mirostat_tau=? WHERE model_id = ?",
                        (all_p.get("ctx",4096), all_p.get("threads",0), all_p.get("gpu_layers",-1),
                         all_p.get("temperature",0.7), all_p.get("top_p",0.9), all_p.get("top_k",40),
                         all_p.get("repeat_penalty",1.1), all_p.get("max_tokens",1024), all_p.get("stop_words"),
                         all_p.get("seed",-1), all_p.get("mirostat",0), all_p.get("mirostat_eta",0.1),
                         all_p.get("mirostat_tau",5.0), model_id))
        else:
            cur.execute("INSERT INTO model_parameters (model_id, ctx, threads, gpu_layers, temperature, top_p, "
                        "top_k, repeat_penalty, max_tokens, stop_words, seed, mirostat, mirostat_eta, mirostat_tau) "
                        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (model_id, all_p.get("ctx",4096), all_p.get("threads",0), all_p.get("gpu_layers",-1),
                         all_p.get("temperature",0.7), all_p.get("top_p",0.9), all_p.get("top_k",40),
                         all_p.get("repeat_penalty",1.1), all_p.get("max_tokens",1024), all_p.get("stop_words"),
                         all_p.get("seed",-1), all_p.get("mirostat",0), all_p.get("mirostat_eta",0.1),
                         all_p.get("mirostat_tau",5.0)))
    return True


def update_model_name(model_id: int, name: str) -> tuple[bool, Optional[str]]:
    name = (name or "").strip()
    if not name:
        return (False, "name required")
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE models SET name = ? WHERE id = ?", (name, model_id))
        return (cur.rowcount > 0, None) if cur.rowcount else (False, "Model not found")


def update_model_port(model_id: int, port: int) -> tuple[bool, Optional[str]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT status FROM models WHERE id = ?", (model_id,))
        row = cur.fetchone()
        if not row:
            return (False, "Model not found")
        if row["status"] != "stopped":
            return (False, "Model must be stopped")
        cur.execute("UPDATE models SET port = ? WHERE id = ?", (port, model_id))
    return (True, None)


def update_model_path(model_id: int, path: str) -> tuple[bool, Optional[str]]:
    path = (path or "").strip()
    if not path:
        return (False, "path required")
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT status FROM models WHERE id = ?", (model_id,))
        row = cur.fetchone()
        if not row:
            return (False, "Model not found")
        if row["status"] != "stopped":
            return (False, "Model must be stopped")
        cur.execute("UPDATE models SET model_path = ? WHERE id = ?", (path, model_id))
    return (True, None)


def register_model(name: str, model_path: str, port: int) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO models (name, model_path, port, status) VALUES (?, ?, ?, 'stopped')", (name, model_path, port))
        model_id = cur.lastrowid
        cur.execute("INSERT INTO model_parameters (model_id) VALUES (?)", (model_id,))
    return model_id


def get_next_port() -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COALESCE(MAX(port), 5019) + 1 AS next FROM models")
        return cur.fetchone()["next"]


def resolve_threads_preset(spec: Any) -> Optional[int]:
    if spec is None or spec == "":
        return None
    s = str(spec).strip().lower()
    cores = _detect_cpu_cores()
    max_t = int(get_system_config().get("max_threads") or 8)
    if s == "max":
        return min(cores, max_t)
    if s == "min":
        return max(1, min(2, cores))
    if s == "medium":
        return min(cores, max(4, cores // 2))
    try:
        return max(1, min(int(spec), cores, max_t))
    except (ValueError, TypeError):
        return None


def resolve_ram_preset(spec: Any, default_ctx: int) -> int:
    if spec is None or spec == "":
        return default_ctx
    s = str(spec).strip().lower()
    if s == "max":
        return 8192
    if s == "medium":
        return 4096
    if s == "min":
        return 2048
    return default_ctx


def resolve_threads(model_id: int, overrides: Optional[dict] = None) -> int:
    overrides = overrides or {}
    if "threads" in overrides and overrides["threads"] is not None:
        t = overrides["threads"]
        if isinstance(t, int) and t > 0:
            return t
    params = get_parameters(model_id)
    t = params.get("threads") or 0
    if t > 0:
        return t
    sys_cfg = get_system_config()
    if not sys_cfg.get("auto_threads"):
        return int(sys_cfg.get("max_threads") or 8)
    cores = _detect_cpu_cores()
    max_t = int(sys_cfg.get("max_threads") or 8)
    with _lock:
        running = sum(1 for p in _processes.values() if p.poll() is None)
    return min(cores, max_t) if running <= 0 else max(1, min(cores // (running + 1), max_t))


def get_system_config() -> dict[str, Any]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT max_threads, auto_threads, max_ram_usage FROM system_config WHERE id = 1")
        row = cur.fetchone()
        return dict(row) if row else {"max_threads": 8, "auto_threads": 1, "max_ram_usage": "4G"}


def update_system_config(cfg: dict[str, Any]) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        for k in ("max_threads", "auto_threads", "max_ram_usage"):
            if k in cfg:
                cur.execute(f"UPDATE system_config SET {k} = ? WHERE id = 1", (cfg[k],))


def start_model(model_id: int, overrides: Optional[dict] = None, _retried: bool = False) -> tuple[bool, Any]:
    overrides = overrides or {}
    model = get_model(model_id)
    if not model:
        return (False, "Model not found")
    if model["status"] == "running":
        with _lock:
            p = _processes.get(model_id)
        if p and p.poll() is None:
            return (True, model["port"])
        with _lock:
            _processes.pop(model_id, None)
        with get_connection() as conn:
            conn.cursor().execute("UPDATE models SET status = 'stopped' WHERE id = ?", (model_id,))

    model_path = model["model_path"]
    resolved, err = _resolve_split_gguf_path(model_path)
    if err and not _retried:
        m = _SPLIT_PATTERN.search(os.path.basename(_to_abs_path(model_path)))
        if m and int(m.group(1)) > 1:
            first_filename = _SPLIT_PATTERN.sub(lambda mo: f"00001-of-{mo.group(2)}.gguf", os.path.basename(_to_abs_path(model_path)))
            url = _infer_hf_url_for_first_split(model_path, first_filename)
            if url:
                dest_path = os.path.join(config.MODELS_DIR, first_filename)
                log.info("[model_manager] Auto-downloading missing first split: %s", first_filename)
                ok, dl_err = _download_file_sync(url, dest_path)
                if ok:
                    ok_up, _ = update_model_path(model_id, first_filename)
                    if ok_up:
                        log.info("[model_manager] Updated path to first split, retrying")
                        return start_model(model_id, overrides=overrides, _retried=True)
                    err = "Failed to update model path"
                else:
                    err = f"Download failed: {dl_err}"
    if err:
        return (False, err)

    exe = _find_llama_server()
    if not exe:
        return (False, "llama-server not found")
    params = get_parameters(model_id)
    ctx = overrides.get("ctx") or params.get("ctx") or 4096
    threads = resolve_threads(model_id, overrides)
    port = model["port"]
    with _lock:
        running = sum(1 for p in _processes.values() if p.poll() is None)
    log.info("[model_manager] auto threads: cores=%s max=%s running=%s -> %s threads",
             _detect_cpu_cores(), get_system_config().get("max_threads", 8), running, threads)
    cmd = [exe, "-m", resolved, "--port", str(port), "-c", str(ctx), "-t", str(threads)]
    if params.get("gpu_layers", -1) not in (None, 0):
        cmd.extend(["-ngl", str(params["gpu_layers"])])
    log.info("[model_manager] Starting model id=%s port=%s cmd=%s", model_id, port, " ".join(cmd))
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.path.dirname(exe) or None)
        with _lock:
            _processes[model_id] = proc
        with get_connection() as conn:
            conn.cursor().execute("UPDATE models SET status = 'running' WHERE id = ?", (model_id,))
        log.info("[model_manager] Started model id=%s port=%s (PID %s)", model_id, port, proc.pid)

        def _log():
            try:
                for line in proc.stdout:
                    log.info("[llama-server id=%s] %s", model_id, (line or b"").decode(errors="replace").strip())
            except Exception:
                pass
            finally:
                if proc.poll() is not None and proc.poll() != 0:
                    log.warning("[model_manager] Model id=%s exited code=%s", model_id, proc.poll())
                with _lock:
                    _processes.pop(model_id, None)
                with get_connection() as conn:
                    conn.cursor().execute("UPDATE models SET status = 'stopped' WHERE id = ?", (model_id,))
        threading.Thread(target=_log, daemon=True).start()
        return (True, port)
    except Exception as e:
        with _lock:
            _processes.pop(model_id, None)
        return (False, str(e))


def stop_model(model_id: int) -> None:
    with _lock:
        p = _processes.pop(model_id, None)
    if p and p.poll() is None:
        try:
            p.terminate()
            p.wait(timeout=10)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    with get_connection() as conn:
        conn.cursor().execute("UPDATE models SET status = 'stopped' WHERE id = ?", (model_id,))


def delete_model(model_id: int, delete_file: bool = False) -> tuple[bool, Optional[str]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, model_path, status FROM models WHERE id = ?", (model_id,))
        row = cur.fetchone()
        if not row:
            return (False, "Model not found")
        if row["status"] != "stopped":
            return (False, "Model must be stopped")
        model_path = (row.get("model_path") or "").strip()
        cur.execute("DELETE FROM model_parameters WHERE model_id = ?", (model_id,))
        cur.execute("DELETE FROM models WHERE id = ?", (model_id,))
    with _lock:
        _processes.pop(model_id, None)
    if delete_file and model_path and ":" not in model_path:
        try:
            path = _to_abs_path(model_path)
            if path and os.path.isfile(path):
                os.unlink(path)
        except OSError:
            pass
    return (True, None)


def reset_running_status() -> None:
    with get_connection() as conn:
        conn.cursor().execute("UPDATE models SET status = 'stopped'")
    with _lock:
        _processes.clear()


def mark_stopped_if_dead(model_id: int) -> None:
    with _lock:
        p = _processes.get(model_id)
    if p and p.poll() is not None:
        with _lock:
            _processes.pop(model_id, None)
        with get_connection() as conn:
            conn.cursor().execute("UPDATE models SET status = 'stopped' WHERE id = ?", (model_id,))
