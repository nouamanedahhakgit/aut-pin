# Website Parts Generator

Generates **headers**, **footers**, **category pages**, and **sidebar** templates for multi-domain recipe sites.
Each domain can have its own named template for each part. Templates are **reskinnable** via colors, fonts, layout.

## Structure

- `templates/headers/` — header templates (header-1, header-2, header-3, …)
- `templates/footers/` — footer templates
- `templates/categories/` — category/article-listing page templates
- `templates/sidebars/` — sidebar / side-article templates

## Per-domain assignment

Each domain in the database has:

- `header_template` — e.g. `header-1`, `header-2`
- `footer_template` — e.g. `footer-1`, `footer-2`
- `category_page_template` — e.g. `category-1`, `category-2`
- `side_article_template` — e.g. `sidebar-1`, `sidebar-2`

## API (port 5003)

```
GET  /templates                    — list all available template names
POST /generate/header/{name}       — generate header HTML+CSS (body: {config})
POST /generate/footer/{name}
POST /generate/category/{name}
POST /generate/sidebar/{name}
```

## Reskin config

Same structure as article templates: `colors`, `fonts`, `layout`. Pass as JSON body.
Domain `article_template_config` can be reused for consistency across header, footer, category, sidebar.

## Run

```bash
cd website-parts-generator
pip install -r requirements.txt
python run.py
# or: uvicorn route:app --host 0.0.0.0 --port 5003
```

## Multi-domain integration

Set in multi-domain `.env`:
```
WEBSITE_PARTS_API_URL=http://localhost:5003
```

- **Add domain** (single or bulk): each new domain gets random header, footer, category, sidebar templates.
- **Random distribute** (Admin → Site Templates): assign random templates to selected domains.
- **Generate part**: POST `/api/generate-site-part` with `{ part: "header", name: "header_1", config: {...} }` to get HTML+CSS.
