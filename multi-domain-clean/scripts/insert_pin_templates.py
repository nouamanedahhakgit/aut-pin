"""
Insert pin template themes into pin_template_pool.
Run from repo root or from multi-domain-clean:
  python multi-domain-clean/scripts/insert_pin_templates.py
  cd multi-domain-clean && python scripts/insert_pin_templates.py

Sources (first wins):
  --from-js FILE   Load themes from a JavaScript file (exports THEMES or THEME). Runs node theme_js_to_json.js.
  --from-json FILE Load themes from a JSON file (array of theme objects).
  --from-stdin     Read JSON array of themes from stdin (e.g. pipe from node theme_js_to_json.js).
  (default)        Load from pin_templates/themes.py THEMES list.
"""
import json
import os
import subprocess
import sys

_script_dir = os.path.dirname(os.path.abspath(__file__))
_app_dir = os.path.dirname(_script_dir)
sys.path.insert(0, _app_dir)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(_app_dir, ".env"))
except ImportError:
    pass

from db import get_connection, execute


def insert_or_update_template(conn, name, template_json_str, preview_image_url=""):
    """Insert or update one row in pin_template_pool. name is unique."""
    cur = execute(conn, "SELECT id FROM pin_template_pool WHERE name = ?", (name,))
    row = cur.fetchone()
    if row:
        execute(conn, "UPDATE pin_template_pool SET template_json = ?, preview_image_url = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?",
               (template_json_str, preview_image_url or "", name))
        return "updated"
    execute(conn, "INSERT INTO pin_template_pool (name, template_json, preview_image_url) VALUES (?, ?, ?)",
           (name, template_json_str, preview_image_url or ""))
    return "inserted"


def load_themes_from_args():
    """Return list of theme dicts from argv: --from-js, --from-json, --from-stdin, or default Python THEMES."""
    argv = sys.argv[1:]
    if "--from-js" in argv:
        i = argv.index("--from-js")
        if i + 1 >= len(argv):
            print("--from-js requires a file path", file=sys.stderr)
            sys.exit(1)
        js_path = argv[i + 1]
        node_script = os.path.join(_script_dir, "theme_js_to_json.js")
        if not os.path.isfile(node_script):
            print("theme_js_to_json.js not found", file=sys.stderr)
            sys.exit(1)
        js_path_clean = js_path.replace("multi-domain-clean/", "").replace("multi-domain-clean\\", "").lstrip("/\\")
        abs_js = os.path.normpath(os.path.join(_app_dir, js_path_clean)) if not os.path.isabs(js_path) else js_path
        result = subprocess.run(
            ["node", node_script, abs_js],
            capture_output=True,
            text=True,
            cwd=_app_dir,
        )
        if result.returncode != 0:
            print(result.stderr or result.stdout, file=sys.stderr)
            sys.exit(1)
        return json.loads(result.stdout or "[]")
    if "--from-json" in argv:
        i = argv.index("--from-json")
        if i + 1 >= len(argv):
            print("--from-json requires a file path", file=sys.stderr)
            sys.exit(1)
        json_path = argv[i + 1]
        abs_json = json_path if os.path.isabs(json_path) else os.path.join(os.getcwd(), json_path)
        with open(abs_json, "r", encoding="utf-8") as f:
            return json.load(f)
    if "--from-stdin" in argv:
        return json.load(sys.stdin)
    if _app_dir not in sys.path:
        sys.path.insert(0, _app_dir)
    from pin_templates.themes import THEMES
    return THEMES


def main():
    themes = load_themes_from_args()
    if not themes:
        print("No themes to insert.")
        sys.exit(0)

    with get_connection() as conn:
        for theme in themes:
            name = (theme.get("template_id") or theme.get("template_name") or "").strip().lower().replace("-", "_")
            if not name:
                print("Skip theme missing template_id/template_name:", theme.get("name", "?"))
                continue
            payload = {
                "template_id": theme.get("template_id") or name,
                "template_name": theme.get("template_name") or name,
                "style_slots": theme.get("style_slots") or {},
                "font_slots": theme.get("font_slots") or {},
                "template_data": theme.get("template_data") or {},
            }
            template_json_str = json.dumps(payload)
            action = insert_or_update_template(conn, name, template_json_str, "")
            print(f"  {action}: {name}")
    print("Done.")


if __name__ == "__main__":
    main()
