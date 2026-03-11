# Per-template generators. Each template_*.py has TEMPLATE_ID, TEMPLATE_DATA, and run(output_dir).
# Add a new template by creating generators/template_N.py with the same pattern.

import os
import sys
import logging
import importlib.util

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

_log = logging.getLogger("generators")

# Pre-import _base and register it in sys.modules so dynamically loaded
# templates can do `from _base import ...` without sys.path issues.
_base_path = os.path.join(_HERE, "_base.py")
try:
    if os.path.isfile(_base_path) and "_base" not in sys.modules:
        _spec = importlib.util.spec_from_file_location("_base", _base_path)
        _base_mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_base_mod)
        sys.modules["_base"] = _base_mod
        print(f"[generators] _base pre-imported OK from {_base_path}")
    elif "_base" in sys.modules:
        print("[generators] _base already in sys.modules")
except Exception as e:
    print(f"[generators] ERROR pre-importing _base: {e}")
    import traceback; traceback.print_exc()


_TEMPLATES_ROOT = os.path.join(_HERE, "templates")
if not os.path.isdir(_TEMPLATES_ROOT):
    os.makedirs(_TEMPLATES_ROOT, exist_ok=True)


def list_generators():
    """Return list of generator paths (e.g. template_1, group_1/template_1)."""
    names = []
    # Walk the templates directory to find all template_*.py files
    for root, dirs, files in os.walk(_TEMPLATES_ROOT):
        for f in files:
            if f.startswith("template_") and f.endswith(".py"):
                # Calculate relative path from _TEMPLATES_ROOT
                rel_dir = os.path.relpath(root, _TEMPLATES_ROOT)
                if rel_dir == ".":
                    names.append(f[:-3])  # e.g. "template_1"
                else:
                    # e.g. "group_1/template_1"
                    name = os.path.join(rel_dir, f[:-3]).replace(os.sep, "/")
                    names.append(name)
    return sorted(names)


def load_generator(name):
    """Load generator module by name (e.g. template_1 or group_1/template_1). Returns module or None."""
    # name might contain slashes if in a subdirectory
    path = os.path.join(_TEMPLATES_ROOT, f"{name}.py")
    if not os.path.isfile(path):
        # Fallback for old templates that might still be in the root (legacy)
        legacy_path = os.path.join(_HERE, f"{name}.py")
        if os.path.isfile(legacy_path):
            path = legacy_path
        else:
            print(f"[generators] load_generator: file not found: {path}")
            return None
    try:
        # Unique module name to avoid conflicts; handle spaces/slashes for safe import naming
        safe_name = name.replace("/", ".").replace(" ", "_")
        mod_name = f"generators.templates.{safe_name}"
        spec = importlib.util.spec_from_file_location(mod_name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        print(f"[generators] load_generator: {name} OK")
        return mod
    except Exception as e:
        print(f"[generators] load_generator: FAILED to load {name}: {e}")
        import traceback; traceback.print_exc()
        return None
