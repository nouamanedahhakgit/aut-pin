# AI-generated pin themes (JavaScript)

Drop here **JavaScript theme files** that export `THEMES` or `THEME` (from the prompt `prompt-image-to-pin-theme-js.txt`), then insert into the DB:

```bash
# From multi-domain-clean folder
python scripts/insert_pin_templates.py --from-js pin_templates/themes_from_ai/listicle_50.js
```

- **listicle_50.js** – example theme (same as in themes.py). Use it to test the `--from-js` flow.
- **theme_xyz.js** was only an example name in the docs; use your real file name when you add AI-generated themes.
