"""
Run generator-10 with a custom title without modifying the generator.
Usage: python run.py
       python run.py "Your Title Here"
"""
import sys
import importlib.util
from pathlib import Path

title = sys.argv[1] if len(sys.argv) > 1 else "couscous"

spec = importlib.util.spec_from_file_location("gen10", Path(__file__).parent / "generator-10.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

mod.CONFIG["title"] = title
gen = mod.ArticleGenerator()
gen.run()
