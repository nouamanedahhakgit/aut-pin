"""Unified log aggregation for all microservices. Used by /admin/logs dashboard."""
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta

LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".logs")
LOG_APPS = [
    "multi-domain-clean",
    "articles-website-generator",
    "pin_generator",
    "website-parts-generator",
]

# ANSI color codes to strip for dedupe/key
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

# Level detection from line content
LEVEL_PATTERNS = [
    (re.compile(r"^(INFO|DEBUG|WARNING|ERROR|CRITICAL)[:\s]", re.I), lambda m: m.group(1).upper()),
    (re.compile(r"\[31m|ERROR|Exception|Traceback|Error:"), "ERROR"),
    (re.compile(r"\[33m|WARNING|WARN[:\s]"), "WARNING"),
    (re.compile(r"\[32m|INFO[:\s]"), "INFO"),
]


def _normalize_line(raw):
    """Strip ANSI and return normalized string for dedupe."""
    return ANSI_RE.sub("", raw).strip()


def _detect_level(line):
    for pat, level in LEVEL_PATTERNS:
        if isinstance(level, str):
            if pat.search(line):
                return level
        else:
            m = pat.match(line)
            if m:
                return level(m)
    return "INFO"


def _read_log_tail(app, tail=2000, max_bytes=2 * 1024 * 1024):
    """Read last tail lines from one log file. Returns list of (raw_line, normalized)."""
    path = os.path.join(LOGS_DIR, f"{app}.log")
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            f.seek(max(0, os.path.getsize(path) - max_bytes))
            if f.tell() > 0:
                f.readline()  # skip partial line
            lines = f.readlines()
    except Exception:
        return []
    # keep last tail
    lines = lines[-tail:] if len(lines) > tail else lines
    return [(ln, _normalize_line(ln)) for ln in lines]


def _dedupe_lines(lines_with_norm, keep_first_last=True):
    """Collapse consecutive identical normalized lines. Returns list of dicts with raw, repeated."""
    if not lines_with_norm:
        return []
    out = []
    i = 0
    while i < len(lines_with_norm):
        raw, norm = lines_with_norm[i]
        j = i + 1
        while j < len(lines_with_norm) and lines_with_norm[j][1] == norm:
            j += 1
        repeated = j - i
        if repeated > 1 and keep_first_last:
            out.append({"raw": raw, "normalized": norm, "repeated": repeated, "first": True})
            out.append({"raw": raw, "normalized": norm, "repeated": repeated, "last": True})
        else:
            out.append({"raw": raw, "normalized": norm, "repeated": 1})
        i = j
    return out


def get_log_apps():
    """Return list of app names that have log files."""
    return [a for a in LOG_APPS if os.path.isfile(os.path.join(LOGS_DIR, f"{a}.log"))]


def fetch_logs(
    apps=None,
    tail=1500,
    search=None,
    level_filter=None,
    dedupe=True,
):
    """
    Fetch and merge logs from selected apps.
    apps: list of app names or None for all
    tail: max lines per app
    search: substring to filter (case-insensitive)
    level_filter: INFO | WARNING | ERROR or None
    dedupe: collapse consecutive identical lines to first+last
    Returns: { "lines": [...], "stats": { "by_app": {}, "by_level": {} }, "apps": [...] }
    """
    apps = apps or LOG_APPS
    apps = [a for a in apps if a in LOG_APPS]
    if not apps:
        apps = get_log_apps()

    all_entries = []
    by_app = defaultdict(int)
    by_level = defaultdict(int)
    by_hour = defaultdict(int)

    for app in apps:
        lines_with_norm = _read_log_tail(app, tail=tail)
        if dedupe:
            merged = _dedupe_lines(lines_with_norm, keep_first_last=True)
        else:
            merged = [{"raw": r, "normalized": n, "repeated": 1} for r, n in lines_with_norm]

        for item in merged:
            raw = item["raw"]
            norm = item.get("normalized") or _normalize_line(raw)
            if search and search.lower() not in norm.lower():
                continue
            lvl = _detect_level(raw)
            if level_filter and lvl != level_filter:
                continue
            by_app[app] += 1
            by_level[lvl] += 1
            # try parse time for chart (first part of line often has date)
            try:
                if raw.strip():
                    # common: "INFO:werkzeug:127.0.0.1 - - [05/Mar/2026 22:35:21]"
                    dt_match = re.search(r"\[?(\d{2}/\w{3}/\d{4}\s+\d{2}:\d{2}:\d{2})\]?", raw)
                    if dt_match:
                        dt = datetime.strptime(dt_match.group(1), "%d/%b/%Y %H:%M:%S")
                        by_hour[dt.strftime("%Y-%m-%d %H:00")] += 1
            except Exception:
                pass
            all_entries.append({
                "app": app,
                "raw": raw,
                "level": lvl,
                "repeated": item.get("repeated", 1),
                "first": item.get("first"),
                "last": item.get("last"),
            })

    # sort by app then by order (we lost order across apps; per-app order preserved in all_entries)
    # actually we merged per-app so order is app1 lines, app2 lines... Reverse so newest at bottom or keep chronological per file
    # For merged view we could timestamp-sort but lines may not have timestamps. Keep per-app order, newest last per file.
    return {
        "lines": all_entries,
        "stats": {
            "by_app": dict(by_app),
            "by_level": dict(by_level),
            "by_hour": dict(sorted(by_hour.items())),
        },
        "apps": get_log_apps(),
    }
