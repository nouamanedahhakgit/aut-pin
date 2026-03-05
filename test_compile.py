import py_compile
import sys
try:
    py_compile.compile("multi-domain-clean/app.py", doraise=True)
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
