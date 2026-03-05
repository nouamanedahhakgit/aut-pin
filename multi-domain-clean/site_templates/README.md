# Site Templates (Header, Footer, Side, Category)

Each domain can have:
- **header_template** – Header (logo, nav)
- **footer_template** – Footer
- **side_article_template** – Sidebar block (related/popular)
- **category_page_template** – Category listing page

## Structure

Templates are JSON files in:
- `headers/` – e.g. `header-minimal.json`, `header-dark.json`
- `footers/` – e.g. `footer-minimal.json`
- `categories/` – e.g. `category-grid.json`
- `side_articles/` – e.g. `side-related.json`

## JSON format (reskin-friendly)

```json
{
  "name": "header-minimal",
  "label": "Minimal",
  "config": {
    "colors": { "bg": "#fff", "text": "#1a1a1a", "link": "#E60023" },
    "logo_font": "Playfair Display"
  },
  "html": "<header>...{{site_name}}...</header>"
}
```

- **name** – ID used in domain assignment
- **label** – Display name in admin
- **config** – Reskin values (colors, fonts); can be edited
- **html** – Template with `{{placeholders}}` for site_name, year, etc.

## Random distribute

Admin → Site templates (H/F/S/C) → "Random distribute (all domains)" assigns random templates so 100+ domains get variety.
