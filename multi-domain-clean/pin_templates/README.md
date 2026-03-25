# Pin Templates

## HTML templates (`html_templates.json`)

- **Source file:** `html_templates.json` — keep this in the repo as the canonical source.
- **On deploy:** The app auto-seeds templates from this file into `pin_template_pool` when it starts. No manual insert script needed.
- **Flow:** Edit `html_templates.json` → commit → deploy → app starts and seeds any new templates into the DB.
- **Manual insert (optional):** To load without restarting the app:
  ```powershell
  cd multi-domain-clean
  python scripts/insert_pin_templates.py --from-json pin_templates/html_templates.json
  ```

### Editing and domain colors

- **Pin Editor:** Open `/pin-editor` (or from a domain). Select an HTML template (e.g. cottage_cheese_bread). Edit the HTML in the textarea and click **Domain Colors** to replace hardcoded hex colors with the domain’s colors.
- **Update pool template:** When editing a pool template, click **Update pool template** to save changes back to the pool. Use **Save to domain** (when opened from a domain) to create a domain-specific copy.
- **style_slots.html_colors:** Maps hex values to domain color keys (primary, secondary, etc.). Example: `[{"find": "#5D4037", "use": "primary"}]`.
