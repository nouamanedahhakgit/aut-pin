# Article Generator Convention

Add new generators as `generator-N.py` (e.g. `generator-5.py`). The system auto-discovers them.

## Required for full integration

1. **File name**: `generator-*.py` in this folder
2. **CONFIG** (module-level dict): At minimum `title`, `categories_list`. For preview, include:
   - `colors`: primary, secondary, background, text_primary, text_secondary, button_print, button_pin, border
   - `fonts`: heading.family, heading.sizes (h1, h2, h3), body.family, body.size, body.line_height
   - `layout`: max_width, section_spacing, paragraph_spacing, list_spacing, container_padding, border_radius, box_shadow
   - `components`: pro_tips_box, recipe_card, numbered_list, bullet_list (see generator-1)
   - `writer`: (optional) name, title, bio, avatar — **handled automatically by writer template, no need to include in your generator**. System rotates through domain's writers list automatically.

## Font handling (unified params)

Use `font_utils` so fonts from the Article Template Editor load correctly:

```python
from .font_utils import font_family_css, build_font_import_url

# In generate_css():
import_url = build_font_import_url(fonts_config)
body_font = font_family_css(f["body"]["family"], "sans-serif")
heading_font = font_family_css(f["heading"]["family"], "serif")

# In CSS: @import url('{import_url}');
# body { font-family: {body_font}; }
# h1,h2,h3 { font-family: {heading_font}; }
```

Each generator keeps its **own structure** (HTML layout, sections, components); only the param handling (colors, fonts, layout) is shared. See generator-1, 2, 3, 4 for examples.
3. **ArticleGenerator** class with:
   - `run(return_content_only=False)` → full generation (AI), returns content dict with `article_html`, `article_css`, etc.

## Optional for custom preview

- **run_preview()** method: Returns `{article_html, article_css, title, slug}` with placeholder content (no AI).
- If omitted, the system uses a generic preview from your CONFIG (colors, fonts, layout).
- Implement `run_preview()` when your article structure differs from the generic template.

## Writer Info (Author Byline) — AUTOMATIC INJECTION

**IMPORTANT:** Writer HTML/CSS is now handled by a **separate writer template system** and automatically injected at the top of articles. **You do NOT need to include writer HTML in your article generator.**

### How Writer Injection Works:

1. **Domain Setup:**
   - Each domain has a `writer_template` (e.g., "writer_1") set in Site Templates admin
   - Domain has a list of 4 writers with names, titles, bios, and avatar URLs
   - System tracks `last_writer_index` for rotation

2. **During Article Generation:**
   - System picks next writer from domain's list (rotation)
   - Sends writer data in `config.get("writer")`: `{name, title, bio, avatar}`
   - Your generator receives writer data but **ignores it** (focus on article content only)
   - Your generator returns `article_html` and `article_css`

3. **After Article Generation (Automatic):**
   - System fetches writer HTML/CSS from writer template (e.g., writer_1.py)
   - Injects writer HTML at **top of sidebar** (before side articles)
   - Appends writer CSS to your article CSS
   - Saves complete article with writer section in sidebar
   - Saves writer JSON and avatar URL to `article_content.writer` and `article_content.writer_avatar` columns

### What Article Generators Should Do:

✅ **DO:** Generate main article content (intro, recipe, sections, etc.)
✅ **DO:** Start your HTML with standard structure (`<!DOCTYPE html>`, `<html>`, `<body>`)
❌ **DON'T:** Include writer/author HTML in your generator
❌ **DON'T:** Worry about writer styling or layout

### Writer Template Features (Handled by writer_1.py, writer_2.py, etc.):

- 70-80px circular avatar with `object-position: center` (faces are centered in Midjourney images)
- Name in primary color, bold, 1.1-1.3rem
- Title in muted color, smaller, uppercase
- Bio text, 2-3 sentences
- Responsive layout (horizontal on desktop, stacked/centered on mobile)
- Fallback to initials in colored circle if no avatar
- Uses domain colors (primary, text_primary, text_secondary, border)

### Example Flow:

```
1. Domain has writer_template = "writer_1"
2. Domain has 4 writers: [Emma, Marcus, Aisha, Chen]
3. Generate article #1 → Emma's card injected at top of sidebar
4. Generate article #2 → Marcus's card injected at top of sidebar
5. Generate article #3 → Aisha's card injected at top of sidebar
6. Generate article #4 → Chen's card injected at top of sidebar
7. Generate article #5 → Emma again (rotation)
```

The system automatically rotates through the domain's 4 writers for each new article.

### Writer Card Design (Sidebar):

- **Vertical card** with centered content
- **Warm gradient background** (peach/orange tones)
- **Large circular avatar** (100px) at top with white border and shadow
- **Name** in large bold text below avatar
- **Title/Role** in small uppercase text
- **Bio** in readable paragraph
- **2 action buttons** at bottom:
  - Pinterest follow button (red, with icon)
  - View all recipes button (outlined, primary color)
- **Rounded corners** (16px) for modern look
- **Placed at top of sidebar**, before "More Recipes" or other sidebar content

## API usage

- `GET /generators` – list all generator-N names
- `GET /generators/{name}/config` – get default CONFIG
- `POST /generate-article/{name}` – full generation (requires title, categories_list in body; writer auto-added)
- `POST /generate-article-preview/{name}` – preview only (no AI); works for any generator with CONFIG
