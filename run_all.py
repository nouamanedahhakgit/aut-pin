#!/usr/bin/env python3
"""
Start or stop all automation microservices at once.

  python run_all.py start         -- start all services in background
  python run_all.py start -f      -- start in foreground (see output, Ctrl+C to stop)
  python run_all.py stop          -- stop all services
  python run_all.py restart       -- stop then start

If services fail to start, run one manually to see errors:
  cd multi-domain-clean && python app.py
"""
import os
import sys
import signal
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PID_FILE = ROOT / ".services.pid"
LOGS_DIR = ROOT / ".logs"

SERVICES = [
    {
        "name": "multi-domain-clean",
        "cwd": ROOT / "multi-domain-clean",
        "cmd": [sys.executable, "app.py"],
        "port": 5001,
    },
    {
        "name": "llamacpp_manager",
        "cwd": ROOT / "_archive",
        "cmd": [sys.executable, "-m", "llamacpp_manager.app"],
        "port": 8080,
    },
    {
        "name": "pin_generator",
        "cwd": ROOT / "pin_generator",
        "cmd": [sys.executable, "generator.py", "--serve", "--port", "5000"],
        "port": 5000,
    },
    {
        "name": "articles-website-generator",
        "cwd": ROOT / "articles-website-generator",
        "cmd": [sys.executable, "-m", "uvicorn", "route:app", "--host", "0.0.0.0", "--port", "8000"],
        "port": 8000,
    },
    {
        "name": "website-parts-generator",
        "cwd": ROOT / "website-parts-generator",
        "cmd": [sys.executable, "-m", "uvicorn", "route:app", "--host", "0.0.0.0", "--port", "8010"],
        "port": 8010,
    },
]


def _read_pids():
    """Return list of (name, pid) from PID file."""
    if not PID_FILE.exists():
        return []
    out = []
    for line in PID_FILE.read_text(encoding="utf-8").strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(",", 1)
        if len(parts) == 2:
            try:
                out.append((parts[0].strip(), int(parts[1].strip())))
            except ValueError:
                pass
    return out


def _write_pids(entries):
    """Write (name, pid) list to PID file."""
    PID_FILE.write_text(
        "\n".join(f"{name},{pid}" for name, pid in entries),
        encoding="utf-8",
    )


def _kill_pid(pid):
    """Kill process and on Windows try to kill child process tree."""
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                capture_output=True,
                timeout=10,
            )
        else:
            os.kill(pid, signal.SIGTERM)
    except (ProcessLookupError, OSError):
        pass


def start():
    """Start all services in the background and save PIDs."""
    existing = _read_pids()
    if existing:
        print("Some PIDs already in .services.pid. Run 'python run_all.py stop' first.")
        return 1

    foreground = "-f" in sys.argv or "--foreground" in sys.argv
    procs = []
    for svc in SERVICES:
        cwd = svc["cwd"]
        if not cwd.is_dir():
            print(f"Skip {svc['name']}: directory not found {cwd}")
            continue
        try:
            flags = 0
            if os.name == "nt" and not foreground:
                flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) | subprocess.CREATE_NEW_PROCESS_GROUP
            if foreground:
                stdout_dst = sys.stdout
                stderr_dst = sys.stderr
            else:
                LOGS_DIR.mkdir(exist_ok=True)
                log_file = open(LOGS_DIR / f"{svc['name']}.log", "a", encoding="utf-8")
                log_file.write(f"\n--- Started ---\n")
                log_file.flush()
                stdout_dst = log_file
                stderr_dst = subprocess.STDOUT
            p = subprocess.Popen(
                svc["cmd"],
                cwd=os.fspath(cwd),
                stdout=stdout_dst,
                stderr=stderr_dst,
                stdin=subprocess.DEVNULL,
                creationflags=flags,
            )
            procs.append((svc["name"], p.pid, p))
            print(f"Started {svc['name']} (port {svc['port']}) PID {p.pid}" + (f" -> .logs/{svc['name']}.log" if not foreground else ""))
        except Exception as e:
            print(f"Failed to start {svc['name']}: {e}")
    if foreground:
        print("\nRunning in foreground. Ctrl+C to stop all.")
        try:
            import time
            while any(p.poll() is None for _, _, p in procs):
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        for name, pid, proc in procs:
            if proc.poll() is None:
                _kill_pid(pid)
                print(f"Stopped {name}")
        return 0
    if procs:
        _write_pids([(n, p) for n, p, _ in procs])
        print("\nAll services started. Stop with: python run_all.py stop")
        print("If a service fails, check .logs/<service>.log for errors.")
    return 0


def stop():
    """Stop all services whose PIDs are in .services.pid."""
    entries = _read_pids()
    if not entries:
        print("No services tracked in .services.pid (or already stopped).")
        return 0
    for name, pid in entries:
        _kill_pid(pid)
        print(f"Stopped {name} (PID {pid})")
    _write_pids([])
    PID_FILE.unlink(missing_ok=True)
    print("All services stopped.")
    return 0


def restart():
    """Stop all services, then start them again."""
    stop()
    return start()


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 1
    cmd = sys.argv[1].lower()
    if cmd not in ("start", "stop", "restart"):
        print(__doc__.strip())
        return 1
    if cmd == "start":
        return start()
    if cmd == "restart":
        return restart()
    return stop()


if __name__ == "__main__":
    sys.exit(main())
