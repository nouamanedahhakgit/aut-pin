"""Minimal updater: check for new images, run docker compose pull + up -d."""
import os
import subprocess
import requests
from flask import Flask, jsonify

app = Flask(__name__)
COMPOSE_FILE = os.getenv("COMPOSE_FILE", "/work/docker-compose.hub.yml")
PROJECT_DIR = os.getenv("PROJECT_DIR", "/work")
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


@app.route("/check")
def check():
    updates = []
    for img in IMAGES:
        try:
            hub_ts = hub_updated(img)
            local_ts = local_created(img)
            if not local_ts:
                updates.append(img)
            elif hub_ts and local_ts and hub_ts > local_ts:
                updates.append(img)
        except Exception:
            updates.append(img)
    return jsonify(updates_available=len(updates) > 0, images=updates)


@app.route("/update", methods=["POST"])
def update():
    try:
        r = subprocess.run(
            ["docker", "compose", "-f", COMPOSE_FILE, "pull", "--ignore-pull-failures"],
            cwd=PROJECT_DIR,
            timeout=300,
            capture_output=True,
            text=True,
        )
        r2 = subprocess.run(
            ["docker", "compose", "-f", COMPOSE_FILE, "up", "-d"],
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
