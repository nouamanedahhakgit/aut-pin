#!/usr/bin/env python3
"""
Stitch Processor: Converts Stitch HTML outputs (group folders) into Python generator templates.
Uses OpenAI to transcode HTML/CSS into the project's dictionary-based template structure.

Usage:
    python stitch_processor.py --source "../_archive/stitch-pins/group 1" --template-id group_1
"""

import os
import re
import sys
import json
import argparse
import logging
from openai import OpenAI

# Project Root
ROOT = os.path.dirname(os.path.abspath(__file__))
_TEMPLATES_ROOT = os.path.join(ROOT, "generators", "templates")

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("stitch_processor")

def load_env():
    """Load API key from .env."""
    dotenv_path = os.path.join(ROOT, ".env")
    if os.path.isfile(dotenv_path):
        with open(dotenv_path, "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#") and "=" in line:
                    k, v = line.strip().split("=", 1)
                    os.environ[k] = v.strip('"').strip("'")

def get_transcoder_prompt():
    """Extract the transcoder prompt from stitch_prompt_template.txt."""
    path = os.path.join(ROOT, "..", "_archive", "prompts", "stitch_prompt_template.txt")
    if not os.path.isfile(path):
        # Fallback if specific file missing, but we should find it.
        log.error("Stitch prompt template not found at %s", path)
        return None
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract between the markers
    start_marker = "TRANSCODER PROMPT (Use this with the HTML result)"
    end_marker = "END TRANSCODER PROMPT"
    
    parts = content.split(start_marker)
    if len(parts) < 2:
        return None
    
    sub_parts = parts[1].split(end_marker)
    if not sub_parts:
        return None
        
    return sub_parts[0].strip("- \n\r")

def get_next_template_id():
    """Find the highest template_N number in the templates folder and return N+1."""
    max_id = 0
    pattern = re.compile(r"template_(\d+)\.py")
    
    # Check main templates root
    if os.path.isdir(_TEMPLATES_ROOT):
        for f in os.listdir(_TEMPLATES_ROOT):
            match = pattern.match(f)
            if match:
                max_id = max(max_id, int(match.group(1)))
    
    return max_id + 1

def transcode_html(html, template_id, prompt_text):
    """Call OpenAI to transcode HTML into Python code."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        log.error("Missing OPENAI_API_KEY in environment.")
        return None
    
    client = OpenAI(api_key=api_key)
    model = os.environ.get("OPENAI_MODEL", "gpt-4o")
    
    # Replace {N} with the specific template number we just calculated
    p = prompt_text.replace("{N}", str(template_id))
    
    user_content = f"{p}\n\nSTITCH HTML DESIGN:\n{html}"
    
    log.info("Processing template_%s...", template_id)
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a senior python developer. You only output valid Python code. No markdown, no explanations."},
                {"role": "user", "content": user_content},
            ],
            temperature=0.1
        )
        code = (resp.choices[0].message.content or "").strip()
        # Clean markdown code fences if any
        if code.startswith("```"):
            code = re.sub(r"^```(?:python)?\s*", "", code)
            code = re.sub(r"\s*```$", "", code)
        return code
    except Exception as e:
        log.exception("OpenAI failed: %s", e)
        return None

def process_group(source_dir):
    """Walk through group folders and process each code.html into incremental templates."""
    transcoder_prompt = get_transcoder_prompt()
    if not transcoder_prompt:
        log.error("Could not load transcoder prompt.")
        return
    
    # We save everything directly to the templates root as requested
    next_id = get_next_template_id()
    
    # Gather all potential html files
    screens = []
    for item in sorted(os.listdir(source_dir)):
        item_path = os.path.join(source_dir, item)
        if os.path.isdir(item_path) and "generated_screen_" in item:
            html_path = os.path.join(item_path, "code.html")
            if os.path.isfile(html_path):
                screens.append(html_path)
    
    for html_path in screens:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Pass the next incremental ID to OpenAI
        code = transcode_html(html_content, next_id, transcoder_prompt)
        if code:
            # Target filename template_N.py
            filename = f"template_{next_id}.py"
            dest_path = os.path.join(_TEMPLATES_ROOT, filename)
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(code)
            log.info("Saved template_%d -> %s", next_id, dest_path)
            
            # Copy preview image if exists
            screen_png = os.path.join(os.path.dirname(html_path), "screen.png")
            if os.path.isfile(screen_png):
                import shutil
                image_dest = os.path.join(_TEMPLATES_ROOT, f"template_{next_id}.png")
                shutil.copy2(screen_png, image_dest)
                log.info("Saved preview -> %s", image_dest)
                
            next_id += 1 # Increment for the next screen in the group
        else:
            log.warning("Failed to transcode screen at %s", html_path)

def main():
    parser = argparse.ArgumentParser(description="Process Stitch group folders into templates.")
    parser.add_argument("--source", required=True, help="Source group folder path")
    parser.add_argument("--group-name", help="Optional name of the group (defaults to folder name)")
    args = parser.parse_args()
    
    load_env()
    
    source_path = os.path.abspath(args.source)
    if not os.path.isdir(source_path):
        print(f"Error: Source directory not found: {source_path}")
        return 1
        
    process_group(source_path)
    print(f"\nDone processing.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
