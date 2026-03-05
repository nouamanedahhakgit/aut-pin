#!/usr/bin/env python3
"""
Test script for article-website-generator.

Usage:
  1. With API running (python run_all.py start):
     python test_generate.py

  2. Direct generator (no API):
     python test_generate.py --direct
"""
import json
import sys
import importlib.util
from pathlib import Path

TEST_CONFIG = {
    "title": "Chocolate Chip Cookies",
    "categories_list": [{"id": 1, "categorie": "dessert"}],
}


def test_via_api(base_url="http://localhost:8000"):
    """Call the API to generate an article."""
    import urllib.request
    import urllib.error

    url = f"{base_url.rstrip('/')}/generate-article/generator-1"
    body = json.dumps(TEST_CONFIG).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            out = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"API error {e.code}: {e.read().decode()[:500]}")
        return 1
    except urllib.error.URLError as e:
        print(f"Connection error: {e}. Is the API running? (python run_all.py start)")
        return 1

    print("API returned successfully")
    print("Keys:", list(out.keys()))
    print("article_html length:", len(out.get("article_html", "") or ""))
    print("article_css length:", len(out.get("article_css", "") or ""))
    if out.get("article_html"):
        print("article_html preview:", (out["article_html"][:150] or "") + "...")
    return 0


def test_direct():
    """Run generator-1 directly (no API)."""
    gen_path = Path(__file__).parent / "generators" / "generator-1.py"
    spec = importlib.util.spec_from_file_location("gen_1", gen_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    generator = mod.RecipeArticleGenerator(TEST_CONFIG)
    content = generator.run(return_content_only=True)
    print("Direct run successful")
    print("Keys:", list(content.keys()))
    print("article_html length:", len(content.get("article_html", "") or ""))
    print("article_css length:", len(content.get("article_css", "") or ""))
    return 0


if __name__ == "__main__":
    direct = "--direct" in sys.argv
    if direct:
        sys.exit(test_direct())
    sys.exit(test_via_api())
