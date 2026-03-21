"""Minimal updater: check for new images, run docker compose pull + up -d."""
import os
import subprocess
import requests
from flask import Flask, jsonify

app = Flask(__name__)
COMPOSE_FILE = os.getenv("COMPOSE_FILE", "/work/docker-compose.hub.yml")
PROJECT_DIR = os.getenv("PROJECT_DIR", "/work")
PROJECT_NAME = os.getenv("PROJECT_NAME", "aut-pin")
NAMESPACE = os.getenv("DOCKERHUB_USERNAME", "boarddash31")
IMAGES = [
    f"{NAMESPACE}/aut-pin-orchestrator:latest",
    f"{NAMESPACE}/aut-pin-multi-domain-clean:latest",
    f"{NAMESPACE}/aut-pin-pin_generator:latest",
    f"{NAMESPACE}/aut-pin-articles-website-generator:latest",
    f"{NAMESPACE}/aut-pin-website-parts-generator:latest",
    f"{NAMESPACE}/aut-pin-llamacpp_manager:latest",
]


def _run(cmd, timeout=15):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=PROJECT_DIR)
    return r.returncode == 0, (r.stdout or "").strip(), (r.stderr or "").strip()


def hub_updated(repo_tag):
    try:
        name, _ = repo_tag.rsplit(":", 1)
        owner, repo = name.split("/", 1)
        r = requests.get(
            f"https://hub.docker.com/v2/repositories/{owner}/{repo}/tags?name=latest&page_size=1",
            timeout=10,
        )
        if r.ok:
            results = (r.json().get("results") or [])
            if results:
                return results[0].get("last_updated")
        return None
    except Exception:
        return None


def local_created(repo_tag):
    ok, out, _ = _run(["docker", "image", "inspect", repo_tag, "--format", "{{.Created}}"])
    return out if ok and out else None


def _parse_iso(ts):
    """Parse ISO-ish timestamp to sortable format. Docker uses 2024-01-15T10:30:00.123Z."""
    if not ts:
        return None
    try:
        return ts[:19].replace("T", " ") if len(ts) >= 19 else ts
    except Exception:
        return ts


@app.route("/check")
def check():
    updates = []
    installed = []
    newest_local = None
    for img in IMAGES:
        try:
            hub_ts = hub_updated(img)
            local_ts = local_created(img)
            local_display = _parse_iso(local_ts) if local_ts else None
            hub_display = _parse_iso(hub_ts) if hub_ts else None
            installed.append({
                "image": img,
                "local_created": local_display,
                "hub_updated": hub_display,
                "has_update": False,
            })
            if not local_ts:
                updates.append(img)
                installed[-1]["has_update"] = True
            elif hub_ts and local_ts and hub_ts > local_ts:
                updates.append(img)
                installed[-1]["has_update"] = True
            if local_ts and (newest_local is None or local_ts > newest_local):
                newest_local = local_ts
        except Exception:
            updates.append(img)
            installed.append({"image": img, "local_created": None, "hub_updated": None, "has_update": True})
    return jsonify(
        updates_available=len(updates) > 0,
        images=updates,
        installed=installed,
        newest_local=_parse_iso(newest_local),
    )


@app.route("/update", methods=["POST"])
def update():
    try:
        os.environ["COMPOSE_PROJECT_NAME"] = PROJECT_NAME
        compose_cmd = ["docker", "compose", "-p", PROJECT_NAME, "-f", COMPOSE_FILE]
        # Stop orphaned "work" project if it exists (from old cwd-based naming)
        subprocess.run(
            ["docker", "compose", "-p", "work", "-f", COMPOSE_FILE, "down"],
            cwd=PROJECT_DIR,
            timeout=60,
            capture_output=True,
        )
        r = subprocess.run(
            compose_cmd + ["pull", "--ignore-pull-failures"],
            cwd=PROJECT_DIR,
            timeout=300,
            capture_output=True,
            text=True,
        )
        # Exclude updater - it cannot replace itself while running
        r2 = subprocess.run(
            compose_cmd + ["up", "-d",
             "orchestrator", "multi-domain-clean", "pin_generator",
             "articles-website-generator", "website-parts-generator", "llamacpp_manager"],
            cwd=PROJECT_DIR,
            timeout=120,
            capture_output=True,
            text=True,
        )
        if r2.returncode != 0:
            err = (r2.stderr or r2.stdout or str(r2.returncode)).strip()[:500]
            return jsonify(success=False, error=f"compose up failed: {err}"), 500
        return jsonify(success=True)
    except subprocess.TimeoutExpired as e:
        return jsonify(success=False, error=f"Timeout: {e}"), 500
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6006)
