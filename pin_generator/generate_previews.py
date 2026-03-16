import os
import sys
import json
import base64
import time
from playwright.sync_api import sync_playwright

# Add current dir and subdirs to path to import generators
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "generators"))

from generators import list_generators, load_generator
from generators._base import build_html, build_css, template_from_data, apply_overrides

DEFAULT_PLACEHOLDER = "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png"

def generate_previews():
    available = list_generators()
    # Path where generator.py serves them: generators/templates/*.png
    output_base = os.path.join("generators", "templates")
    os.makedirs(output_base, exist_ok=True)
    
    print(f"Generating previews for {len(available)} templates...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a mobile-like viewport for Pinterest pins
        page = browser.new_page(viewport={"width": 600, "height": 1067})
        
        for name in available:
            print(f"Processing {name}...")
            try:
                mod = load_generator(name)
                if not mod or not hasattr(mod, "TEMPLATE_DATA"):
                    print(f"  Warning: No TEMPLATE_DATA in {name}")
                    continue
                
                tpl_data = mod.TEMPLATE_DATA
                tpl = template_from_data(tpl_data)
                
                # Apply defaults for preview
                preview_overrides = {
                    "title": "PREVIEW DELIGHT",
                    "subtitle": "SNEAK PEEK",
                    "domain": "YOURSITE.COM"
                }
                apply_overrides(tpl, preview_overrides)
                
                # Use EXACT logic from _base.py render_pin to resolve images
                image_urls = {}
                for ik, idata in tpl.get("images", {}).items():
                    resolved_url = None
                    
                    # 1. Check if the image key is at the top level of TEMPLATE_DATA (direct URL)
                    if ik in tpl_data and isinstance(tpl_data[ik], str):
                        resolved_url = tpl_data[ik]
                    
                    # 2. Check for 'src' or 'url' in the images mapping
                    if not resolved_url:
                        resolved_url = idata.get("src") or idata.get("url")
                    
                    # 3. Handle template variables like {{main_image}}
                    if resolved_url and resolved_url.startswith("{{") and resolved_url.endswith("}}"):
                        var_name = resolved_url[2:-2].strip()
                        # Try to resolve from tpl_data (top level) or fall back to default
                        resolved_url = tpl_data.get(var_name) or idata.get("src") or idata.get("url")
                    
                    # 4. Final Fallback to placeholder if still missing
                    if not resolved_url or resolved_url.startswith("{{"):
                        resolved_url = DEFAULT_PLACEHOLDER
                        
                    image_urls[ik] = resolved_url
                    print(f"    - Image [{ik}]: {resolved_url[:60]}...")
                
                css = build_css(tpl)
                html = build_html(tpl, image_urls, css)
                
                # Set viewport to match template canvas size so screenshot isn't cropped
                canvas = tpl.get("canvas", {})
                w = canvas.get("width", 600)
                h = canvas.get("height", 1067)
                page.set_viewport_size({"width": w, "height": h})

                # Small hack: if we're on Windows, file:// paths might be tricky. 
                # Better set content directly.
                page.set_content(html, wait_until="load")
                
                # Wait for images to load if possible
                time.sleep(2)
                
                screenshot_path = os.path.join(output_base, f"{name}.png")
                # Use clip to ensure we capture exactly the canvas area
                page.screenshot(path=screenshot_path, clip={"x": 0, "y": 0, "width": w, "height": h})
                print(f"  [OK] Saved to {screenshot_path}")
                
            except Exception as e:
                import traceback
                print(f"  [FAIL] {name}: {e}")
                traceback.print_exc()
                
        browser.close()

if __name__ == "__main__":
    generate_previews()
