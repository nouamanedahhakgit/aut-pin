import os
import re

DIR = r"c:\Users\leno\Documents\GitHub\aut-pin\pin_generator\generators\templates"

SCALE_X = 736 / 600.0
SCALE_Y = 1308 / 1067.0

def scale_val(key, val):
    val = float(val)
    if val == 0:
        return 0
    if key in ["width", "left", "right"]:
        return int(round(val * SCALE_X))
    elif key in ["height", "top", "bottom", "font_size", "star_size"]:
        return int(round(val * SCALE_Y))
    elif key in ["border_radius"]:
        return int(round(val * SCALE_X))
    return int(round(val))

def scale_string_px(match):
    val = int(match.group(1))
    return str(int(round(val * SCALE_X))) + "px"

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    keys = ["width", "height", "top", "left", "bottom", "right", "font_size", "star_size", "border_radius"]
    pattern = r'("?\b(?:' + '|'.join(keys) + r')\b"?\s*:\s*)(\d+)'
    
    def rep(match):
        k_full = match.group(1)
        val = match.group(2)
        k_name = re.search(r'[a-zA-Z_]+', k_full).group(0)
        new_val = scale_val(k_name, val)
        return k_full + str(new_val)
        
    content = re.sub(pattern, rep, content)
    
    def rep_str_val(match):
        k_full = match.group(1)
        str_val = match.group(2)
        new_str_val = re.sub(r'(\d+)px', scale_string_px, str_val)
        return k_full + new_str_val
        
    content = re.sub(r'("?(?:padding|margin|border|box_shadow|text_shadow)"?\s*:\s*)("[^"]+")', rep_str_val, content)
    
    # Enforce exact new canvas metrics
    content = re.sub(r'("canvas"\s*:\s*\{[^}]*?"width"\s*:\s*)\d+', r'\g<1>736', content)
    content = re.sub(r'("canvas"\s*:\s*\{[^}]*?"height"\s*:\s*)\d+', r'\g<1>1308', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

count = 0
for fname in os.listdir(DIR):
    if fname.startswith("template_") and fname.endswith(".py"):
        process_file(os.path.join(DIR, fname))
        count += 1
print(f"Done scaling {count} templates.")
