#!/usr/bin/env node
/**
 * Load a pin theme JavaScript file (exports THEMES or THEME) and print themes as JSON array to stdout.
 * Usage: node scripts/theme_js_to_json.js path/to/theme.js
 * Used with: node scripts/theme_js_to_json.js theme.js | python scripts/insert_pin_templates.py --from-stdin
 * Or: python scripts/insert_pin_templates.py --from-js path/to/theme.js
 */
const path = require("path");
const fs = require("fs");

const jsPath = process.argv[2];
if (!jsPath) {
  process.stderr.write("Usage: node theme_js_to_json.js <path/to/theme.js>\n");
  process.exit(1);
}

const absPath = path.isAbsolute(jsPath) ? jsPath : path.resolve(process.cwd(), jsPath);
if (!fs.existsSync(absPath)) {
  process.stderr.write("File not found: " + absPath + "\n");
  process.exit(1);
}

const mod = require(absPath);
const themes = mod.THEMES || (mod.THEME ? [mod.THEME] : []);
process.stdout.write(JSON.stringify(themes));
