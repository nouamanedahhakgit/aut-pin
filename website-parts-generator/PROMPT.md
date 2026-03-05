
# Website Parts Generator — AI Prompt for Templates

Use this prompt when generating header, footer, category, side article, index, writer, or article card templates for the multi-domain recipe sites.

**When editing any template file, also update the corresponding section in this PROMPT.md** so the docs stay in sync with the code.

**Quality principle:** Every generated template must be **production-ready** — no KeyError, no broken layout, no missing escapes. Use `.get()` for all dict access. Test mentally: empty config, empty articles, empty categories.

**Index principle:** Index pages must be **magazine-quality** — rich sections, not minimal. **CRITICAL: Each new index = NEW STRUCTURE, not just new CSS.** Structure = HTML layout, section arrangement, hero type, category presentation. See "Index — Structural Variety (MUST Differ)" below.

## Design Reference — Quality Benchmark (MomdishMagic-style)

**Aim for this level of polish.** Reference: header_100, index_2, footer_100. For **index** templates: see "Index — Structural Variety" — each new index MUST use a different structure (hero type, category layout, section order). Not just different CSS.

### Shared Design Tokens

| Element | Pattern | Example |
|---------|---------|---------|
| **Badge** | Pill label, uppercase, small font | `padding: 0.4rem 1rem; background: var(--primary); color: white; border-radius: 9999px; font-size: 0.75rem; font-weight: 600;` |
| **btn-primary** | Solid primary color, rounded-full | `padding: 0.75rem 1.5rem; background: var(--primary); color: white; border-radius: 9999px; font-weight: 500;` |
| **btn-outline** | White bg, border, hover → primary | `border: 2px solid var(--border); background: white; border-radius: 9999px;` |
| **Section title** | Centered, underline accent | `::after { content: ''; position: absolute; bottom: -8px; left: 50%; transform: translateX(-50%); width: 60px; height: 3px; background: var(--primary); }` |
| **Script font** | Accent text (e.g. "Today's Special") | `font-family: Caveat, cursive; font-size: 1.5rem; color: var(--primary);` |
| **Card** | White bg, rounded corners, subtle shadow, hover lift | `border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid var(--border); transition: transform 0.2s;` |

### Header Benchmark

- **Sticky** with `backdrop-filter: blur()` — semi-transparent, frosted glass effect
- **Logo:** Icon (Font Awesome) + site name in serif (Playfair Display)
- **Nav:** Home, Recipes, then categories listing from `config.get("categories", [])` (not a single "Categories" link), then About — use `base_url` and `c.get("url")` for links
- **Do not include:** "Submit Recipe" or any submission/CTA button in the header. Headers are nav + logo only; do not generate submit-recipe or similar CTAs.
- **Icons:** Add `@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');` if using icons

### Index — Structural Patterns (Pick ONE layout type, vary per template)

Different index templates must use **different structure**, not just different colors/fonts. Structure = how sections are arranged in HTML and how content is laid out.

| Structure Type | Hero Layout | Category Layout | Section Order |
|----------------|-------------|-----------------|---------------|
| **A — Split** | Image left, content right (2-column grid) | Circular icons (80px) in a row | Hero → Featured → Categories → Search → Latest |
| **B — Stacked** | Full-width image, then card below (image stacked above title+excerpt) | Pill buttons (rounded, with icon or first letter) | Hero → Categories → Latest |
| **C — Minimal** | Centered card: small image + title + excerpt | Horizontal pill links | Hero → Latest only |
| **D — Magazine** | 1 large featured + sidebar info card | Circular icons + subtitle | Featured block → Categories → Search → Latest |
| **E — Card-first** | Full-width image with overlay badge | Two-row grid of category cards | Hero → Categories → Featured grid → Latest |

**Do NOT repeat the same structure.** If index_1 uses Split, index_2 must use Stacked or Magazine. Vary section order, hero type, and category presentation.

### Footer Benchmark

- **Dark background** (`background: var(--text-primary)`)
- **4+ columns:** (1) Logo + tagline, (2) Quick Links (Home, Recipes, About — no single "Categories" menu), (3) **Categories column:** list actual category names (Dessert, Breakfast, etc.) from `config["categories"]` or from `config["categories_list"]` (items with `categorie` or `name`); build URLs as `base_url/category/{slug}`. Never show a single "Categories" or "Recipes" link as the list. When there are no categories, show "No categories yet". (4) Legal/Pages (links from `config["domain_pages"]`: About Us, Terms of Use, Privacy Policy, Cookie Policy, Disclaimer, Contact Us, etc.), (5) Connect (social icons)
- **Domain pages:** Use `config.get("domain_pages", [])` — each item has `name`, `url`, `slug`. Loop and link: `for p in domain_pages: <a href="{p['url']}">{p['name']}</a>`. Include all 8 domain pages.
- **Social icons:** Circular buttons, hover → primary color
- **Bottom:** Copyright with year

### Fonts

- **Headings:** Playfair Display, Georgia, Cormorant, or similar serif
- **Body:** Inter, Lato, or similar sans
- **Accent/script:** Caveat for "Today's Special", "What are you craving?" style labels

## Project Overview

### Architecture

- **website-parts-generator** — FastAPI service (port 8010) that generates HTML+CSS for each part. Run: `uvicorn route:app --host 0.0.0.0 --port 8010`
- **multi-domain-clean** — Main app that hosts domain previews, assigns templates per domain, and fetches parts via `POST {WEBSITE_PARTS_API_URL}/generate/{part}/{name}`

### Shared Modules (website-parts-generator root)

- `shared_style.py` — `extract_style(config)`, `css_vars(s)`, `part_font(part, config)` for domain colors, layout, fonts
- `shared_article_card.py` — `render_cards(articles, config, show_excerpt, scope_prefix)` loads domain's article_card_template

### Template Parts & Folder Structure

| Part | Folder | Example | Scope prefix |
|------|--------|---------|--------------|
| header | `templates/headers/` | header_53.py, header_100.py | .site-header / .header-XX |
| footer | `templates/footers/` | footer_39.py, footer_100.py | .site-footer / .footer-XX |
| category | `templates/categories/` | category_55.py | .category-page |
| sidebar | `templates/sidebars/` | sidebar_56.py | .side-article |
| index | `templates/indexes/` | index_1.py, index_2.py | .index-page |
| writer | `templates/writers/` | writer_1.py | .article-writer |
| article_card | `templates/article_cards/` | article_card_1.py | passed via scope_prefix |

### Domain Template Assignment (multi-domain-clean)

Each domain has: `header_template`, `footer_template`, `index_template`, `category_page_template`, `side_article_template`, `writer_template`, `article_card_template`. These are stored in the domains table. The app passes the domain's chosen template name when calling the generator.

### Domain Page Generation (About, Legal, Contact)

Domain pages (About Us, Terms of Use, Privacy Policy, GDPR Policy, Cookie Policy, Copyright Policy, Disclaimer, Contact Us) are generated by **multi-domain-clean** via `POST /api/domains/<id>/generate-page/<slug>`. When `OPENROUTER_API_KEY` is set, **all** domain pages use **OpenRouter**; the model is **configurable** via `DOMAIN_PAGE_MODEL` in `.env` (default: `anthropic/claude-3-haiku` for good quality at low cost; alternatives: `openai/gpt-3.5-turbo`, `google/palm-2-chat-bison`, `meta-llama/llama-2-70b-chat`). Generation uses temperature 0.3 and strict output format (---HTML--- / ---CSS--- / ---END---) for reliable parsing.

- **About Us:** Prompt reference `website-parts-generator/prompts/about_page_1.txt`. Structure: Hero (greeting, h1, intro) → Meet the Chef (featured writer) → Story sections (About [founder], What You'll Find, Recipe Philosophy, Journey, For Every Kind of Cook, Connect with Me) → optional Contributors → CTA. Input: domain_name, design_seed, writers (list of {name, title, bio, avatar?}).
- **Legal pages (Terms, Privacy, GDPR, Cookie, Copyright, Disclaimer):** Shared layout: Hero "Legal Information" + h1 (page title); content with h2, "Last Updated", then h3 (and h4 where noted) sections. Full section lists per page: `website-parts-generator/prompts/domain_pages_momdishmagic.txt`.
- **Contact Us:** Hero "We'd love to hear from you!" / "Get in Touch"; two-column: contact form (name, email, subject, message, submit) + Quick Contact sidebar (General, Recipes, Business); optional "All Contact Options" cards.

### One Article Card Template Everywhere (CRITICAL)

Each domain selects ONE `article_card_template` (e.g. `article_card_1` or `article_card_2`). Index, category, and sidebar **must all use** `render_cards()` from `shared_article_card` — never custom card HTML. This ensures the same card design appears on:

- **Index (home):** `render_cards(articles, config, show_excerpt=True, scope_prefix=".index-page")`
- **Category:** `render_cards(articles, config, show_excerpt=True, scope_prefix=".category-page")`
- **Sidebar:** `render_cards(articles[:6], config, show_excerpt=False, scope_prefix=".side-article")`

## Technical Format

- Output **Python** with a `generate(config: dict) -> dict` function.
- Use **f-strings** for HTML and CSS, not Jinja2. No `{% for %}`, `{{ var }}` — use Python loops and `{var}`.
- Return: `return {"html": html_content, "css": css}` — **single braces only**. Never `return {{"html":...}}` (causes `TypeError: unhashable type: 'dict'`).
- In CSS f-strings, escape literal braces as `{{` and `}}` for `{`, `}`. **Every** `{` and `}` in CSS must be doubled — a single `}` causes `SyntaxError: f-string: single '}' is not allowed`. **Never use** `{{{` or `}}}` — exactly two braces; triple braces cause parser errors.

## Config Keys

- **Domain colors** (CRITICAL — use these exact keys):
  - Each domain has its own palette in `config["colors"]`: `primary`, `secondary`, `background`, `text_primary`, `text_secondary`, `border` (hex e.g. #6C8AE4)
  - Access via `extract_style(config)` which returns a dict with these keys:
    - `s["primary"]` — main brand color (e.g. #6C8AE4)
    - `s["secondary"]` — secondary brand color (e.g. #9C6ADE)
    - `s["background"]` — page background (e.g. #FFFFFF)
    - `s["text_primary"]` — main text color (e.g. #2D2D2D)
    - `s["text_secondary"]` — secondary/muted text (e.g. #5A5A5A)
    - `s["border"]` — border color (e.g. #E2E8FF)
  - **NEVER use** `primary_color`, `background_color`, `text_color`, `footer_background_color`, etc. — these are WRONG
  - **ALWAYS use** `primary`, `background`, `text_primary`, `text_secondary` — these are CORRECT
- `domain_name`, `domain_url` — from `extract_style(config)` or `s.get("domain_name", "Recipe Blog")`.
- `categories` — list of dicts: `{"name": "...", "url": "...", "slug": "...", "count": N}`. For header/footer, if missing the app may pass `categories_list` (e.g. `[{ "id": 1, "categorie": "dessert" }]`); normalize to name + url using `base_url/category/{slug}` (slug from lowercased, hyphenated name). Footers must list these category names in the Categories column, not a single "Categories" or "Recipes" link; empty state: "No categories yet".
- `domain_pages` — list of dicts for footer links: `{"name": "About Us", "url": "{base_url}/about-us", "slug": "about-us"}`, etc. Pages: About Us, Terms of Use, Privacy Policy, GDPR Policy, Cookie Policy, Copyright Policy, Disclaimer, Contact Us. Footers MUST include these links (e.g. in a "Legal" or "Pages" column).
- **Part-specific fonts** — `config["fonts"]["header"]` (or `footer`, `side_article`, `category`) may have:
  - `cdn`: Google Fonts or other font CDN URL, e.g. `https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600&display=swap`
  - `family`: CSS font-family value, e.g. `"Cormorant Garamond", serif`
- Use `from shared_style import part_font` then `pf = part_font("header", config)` to get `pf["cdn"]` and `pf["family"]` for the current part.
- Use `s.get("key", default)` — `extract_style(config)` returns a dict, not object attributes.

## Part-Specific Fonts (Critical — do NOT affect other parts)

When config provides `fonts.<part>.cdn` and `fonts.<part>.family` for your part:
1. **Use them** — Add `@import url('...')` at the very start of your CSS if `cdn` is present. Use `family` for all text in your part. If not provided, use `s.get("heading_family")` / `s.get("body_family")` or your own choice.
2. **Scope strictly** — All your CSS selectors MUST be prefixed with your part's root class. Never use bare selectors like `.nav-link` or `body` or `*`.
   - **Header:** prefix with `.site-header` or `.header-XX` — e.g. `.site-header .nav-link { font-family: ... }`
   - **Footer:** prefix with `.site-footer` or `.footer-XX`
   - **Side Article:** prefix with `.side-article` or `.side-article-XX`
   - **Category:** prefix with `.category-page` or `.category-XX`
3. **No leakage** — Your font and styles must apply ONLY inside your part's wrapper. Other parts (header, footer, side article, main content) must not be affected.

Example for header with correct color keys:

```python
from shared_style import extract_style, part_font

s = extract_style(config)
pf = part_font("header", config)

font_import = f"@import url('{pf['cdn']}');" if pf.get("cdn") else ""
font_family = pf.get("family") or "Inter, sans-serif"

# CSS: all selectors prefixed with .site-header
# CORRECT color keys: primary, background, text_primary, border
css = f"""
{font_import}
.site-header {{
    --primary: {s.get("primary", "#6C8AE4")};
    --background: {s.get("background", "#FFFFFF")};
    --text: {s.get("text_primary", "#2D2D2D")};
    --border: {s.get("border", "#E2E8FF")};
    
    background-color: var(--background);
    color: var(--text);
    border-bottom: 1px solid var(--border);
    font-family: {font_family};
}}
.site-header .logo {{ 
    font-size: 1.5rem; 
    color: var(--primary);
}}
.site-header .nav-link {{ 
    font-size: 1rem;
    color: var(--text);
}}
.site-header .nav-link:hover {{
    color: var(--primary);
}}
"""
```

**WRONG keys (never use these):**
- ❌ `s.get("primary_color")` 
- ❌ `s.get("background_color")`
- ❌ `s.get("text_color")`
- ❌ `s.get("footer_background_color")`

**CORRECT keys (always use these):**
- ✅ `s.get("primary")`
- ✅ `s.get("background")`
- ✅ `s.get("text_primary")`
- ✅ `s.get("text_secondary")`
- ✅ `s.get("border")`

## Article Card Templates (selectable per domain)

Article cards are **part templates** (like header, footer). Each domain has an `article_card_template` (e.g. `article_card_1`, `article_card_2`). Index, category, and sidebar use `render_cards()` which loads the domain's template.

### Using article cards in your templates

```python
from shared_article_card import render_cards

# Index / Category (with excerpt)
cards_html, card_css = render_cards(articles, config, show_excerpt=True, scope_prefix=".index-page")
# Include card_css in your part's CSS output

# Sidebar (no excerpt)
article_cards, card_css = render_cards(articles[:6], config, show_excerpt=False, scope_prefix=".side-article")
```

Config must include `article_card_template` (set by the app from the domain). **Do not** define custom card HTML/CSS — use `render_cards()`.

### Creating new article card templates

Create `templates/article_cards/article_card_N.py`:

```python
def generate(config: dict) -> dict:
    from shared_style import extract_style
    import html as html_module

    article = config.get("article", {})
    show_excerpt = config.get("show_excerpt", True)
    scope_prefix = config.get("scope_prefix", "")
    s = extract_style(config) if not config.get("style") else config["style"]

    title = html_module.escape((article.get("title") or "Recipe")[:200])
    url = article.get("url") or "#"
    img = (article.get("main_image") or article.get("image") or "").strip()
    # ... build HTML and CSS, return {"html": ..., "css": ...}
    return {"html": html, "css": css}
```

Config keys: `article` (dict with title, url, main_image, image, excerpt), `show_excerpt`, `scope_prefix`. Use CSS vars: `var(--primary)`, `var(--border)`, etc. Add fallbacks for vars, e.g. `var(--border, #e2e8f0)`. Image wrap: use `aspect-ratio: 16/10` or `4/3` with `max-height: 180px` to avoid stretching on single-column layouts.

## Header Navigation

- **Nav structure:** Home | Recipes | Categories | About — or list actual category names from `config.get("categories", [])` with links to `c.get("url")` and label `c.get("name")`.
- **Links:** Use `base_url` from config (e.g. `base_url/categories`, `base_url/about`). Never hardcode paths.
- **About in header:** If `config.get("domain_pages", [])` contains an About-type page (slug `about-us`/`about` or name starting with "About"), use that page's `url` and `name` for the About nav link; otherwise use `base_url/about` with label "About".
- **Do not generate:** "Submit Recipe" or any submission/CTA button. Headers are logo + nav links only.

## Side Article (Sidebar) Layout

Side article templates render the **right sidebar** on **article pages only** (not on category pages). They display "Latest Recipes" (or "Popular Recipes") and "Categories".

### Config Keys (CRITICAL — use these exact names)

- `articles` — List of article dicts (up to 6). **NOT** `latest_articles`, `popular_recipes`, or `sidebar_articles`.
- Each article has: `title`, `url`, `main_image`, `image`. **Use `main_image` first** (fallback to `image`).
- `categories` — List of dicts: `{name, url, slug, count}`. Link to `c.get("url")`, label `c.get("name")`, show `c.get("count")`.

```python
articles = config.get("articles", [])   # CORRECT
categories = config.get("categories", [])
```

### Required Structure

1. **Wrapper:** `<aside class="side-article">` (or `.site-sidebar`) for semantic HTML.
2. **Section 1 — Recipes:** Heading "Latest Recipes" or "Popular Recipes", then article cards.
3. **Section 2 — Categories:** Heading "Categories", then list of category links with counts.
4. **Article cards:** Use **shared_article_card** — `render_cards(articles[:6], config, show_excerpt=False, scope_prefix=".side-article")` for sidebar.

### Complete Python Example

```python
def generate(config: dict) -> dict:
    import html as html_module
    from shared_style import extract_style, part_font
    from shared_article_card import render_cards

    s = extract_style(config)
    pf = part_font("side_article", config)
    font_import = f"@import url('{pf['cdn']}');" if pf.get("cdn") else ""
    font_family = pf.get("family") or "Inter, sans-serif"

    articles = config.get("articles", []) or config.get("latest_articles", [])
    categories = config.get("categories", [])

    article_cards, card_css = render_cards(articles[:6], config, show_excerpt=False, scope_prefix=".side-article")

    cat_links = ""
    for c in categories:
        name = html_module.escape(c.get("name", ""))
        cat_url = c.get("url") or "#"
        count = c.get("count", 0)
        cat_links += f'<li><a href="{html_module.escape(cat_url)}" class="side-category-link"><span>{name}</span><span class="side-category-count">{count}</span></a></li>'

    html_content = f'''<aside class="side-article">
    <div class="side-section"><h2 class="side-section-title">Latest Recipes</h2><div class="side-article-list">{article_cards}</div></div>
    <div class="side-section"><h2 class="side-section-title">Categories</h2><ul class="side-category-list">{cat_links}</ul></div>
</aside>'''

    css = f"""
{font_import}
.side-article {{ --primary: {s.get("primary", "#6C8AE4")}; --secondary: {s.get("secondary", "#9C6ADE")}; --background: {s.get("background", "#FFFFFF")}; --text-primary: {s.get("text_primary", "#2D2D2D")}; --text-secondary: {s.get("text_secondary", "#5A5A5A")}; --border: {s.get("border", "#E2E8FF")}; font-family: {font_family}; }}
.side-article .side-section {{ margin-bottom: 2rem; }}
.side-article .side-section-title {{ font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; color: var(--text-primary); }}
.side-article .side-article-list {{ display: flex; flex-direction: column; gap: 1.25rem; }}
{card_css}
.side-article .side-category-list {{ list-style: none; padding: 0; margin: 0; }}
.side-article .side-category-link {{ display: flex; justify-content: space-between; padding: 0.5rem 0; color: var(--text-primary); text-decoration: none; }}
.side-article .side-category-link:hover {{ color: var(--primary); }}
"""
    return {"html": html_content, "css": css}
```

### CSS Scope

- **Prefix ALL selectors** with `.side-article` (or `.site-sidebar`) — e.g. `.side-article .side-article-card`
- Never use bare `.side-article-card` — it will leak into other parts.

### What NOT to do

- ❌ `config.get("latest_articles")` — use `articles`
- ❌ `config.get("popular_recipes")` — use `articles`
- ❌ Horizontal layout (image left, text right) — too cramped for sidebar
- ❌ Small images (under 150px height) — hard to see
- ❌ Including excerpts — takes too much space
- ❌ Variable image heights — use fixed 180px for consistency
- ❌ Forgetting `html.escape()` on user content (title, url)

## Category Page

Category templates display a **paginated list of articles** for a given category (e.g. Desserts, Mains, All Recipes).

### Config Keys

- `category_name` — Display name of the category (e.g. "Desserts", "All Recipes")
- `articles` — List of article dicts (already paginated by the system). Each article has:
  - `title` — Article title
  - `url` — Link to the article
  - `main_image` — **Primary image URL** (from article_content.main_image) — **ALWAYS use this for card images**
  - `image` — Fallback (same as main_image)
  - `excerpt` — Short description (from meta_description)
- `total` — Total number of articles in the category (across all pages)
- `total_pages` — Number of pagination pages
- `current_page` — Current page number (1-based)
- `per_page` — Articles per page (typically 12)

### Required Structure

1. **Header:** Category name + total count (e.g. "Desserts — 24 recipes"). Use `config.get("total", len(articles))` for the count.
2. **Articles grid:** Use **shared_article_card** — `render_cards(articles, config, show_excerpt=True, scope_prefix=".category-page")` for consistent design with index and sidebar.
3. **Empty state:** When `articles_html` is empty, show a message: `'<p class="category-no-articles">No recipes in this category yet. Add articles with this category/course.</p>'` and add `.category-no-articles { grid-column: 1 / -1; color: var(--text-secondary); padding: 2rem; text-align: center; }` to CSS.
4. **Pagination:** The system injects pagination HTML before `</main>`. Your template MUST end with `</main>` to receive Prev/Next and page numbers.

### Example (use shared_article_card)

```python
from shared_article_card import render_cards

articles = config.get("articles", [])
articles_html, card_css = render_cards(articles, config, show_excerpt=True, scope_prefix=".category-page")
if not articles_html:
    articles_html = '<p class="category-no-articles">No recipes in this category yet. Add articles with this category/course.</p>'
css += card_css
# ... plus .category-no-articles { grid-column: 1 / -1; color: var(--text-secondary); padding: 2rem; text-align: center; }
```

### CSS Scope

- Prefix all selectors with `.category-page` or `.category-XX` to avoid leaking styles.
- Use `width: 100%` on `.category-container` and `.articles-grid` so the grid sizes correctly.

## Index (Home) Page

Index templates display the **home page** with hero, categories, and latest recipes.

**GOAL: Each new index template must have a DIFFERENT STRUCTURE — different HTML layout, section arrangement, hero type, category presentation. Not just different CSS colors or fonts.**

### Before generating — pick your structure

1. **Check existing index templates** — index_1, index_2, etc. What structure do they use?
2. **Pick a DIFFERENT structure** — different hero layout (split vs stacked vs centered), different category layout (circular vs pill vs links), different section order.
3. **Write the HTML structure first** — then add CSS. Structure = semantics and layout order.

### Index — Structural Variety (MUST Differ)

**Structure** = how the page is built in HTML: hero layout, section order, category presentation. **CSS** = colors, fonts, spacing. You must vary **structure**.

| What to vary | Examples |
|--------------|----------|
| **Hero layout** | (A) Split: image left, content right in 2 columns. (B) Stacked: full-width image above, white card below with title+excerpt. (C) Centered: small image + text in one card. (D) Overlay: image with text overlay. |
| **Category layout** | (A) Circular icons (80px) in a row. (B) Pill buttons with first letter or icon. (C) Horizontal text links. (D) Grid of small cards. |
| **Section order** | Hero → Categories → Latest. Or Hero → Featured → Categories → Search → Latest. Or Hero → Latest → Categories (minimal). |
| **Featured block** | Include or skip. If included: info card + grid, or 1 large + 6 small. Use `render_cards(articles[1:7])`. |
| **Search / About** | Include or skip. Optional. |

**Example — Stacked hero (different from split):**
```html
<!-- Structure: full-width image above, white card below with title+excerpt+CTAs -->
<section class="hero">
  <div class="hero-image-wrap"><img ... or placeholder /></div>
  <div class="hero-card">
    <h1>{title}</h1>
    <p>{excerpt}</p>
    <a href="...">Get Recipe</a>
    <a href="{base_url}/categories">Browse All</a>
  </div>
</section>
```

**Example — Pill categories (different from circular icons):**
```html
<!-- Structure: rounded pill buttons with icon/letter, horizontal row. Loop: for c in categories, url = c.get("url") -->
<section class="categories">
  <h2>What are you craving?</h2>
  <div class="category-pills">
    <a href="{url}" class="pill"><span class="letter">D</span> dessert</a>
    <a href="{url}" class="pill"><span class="letter">B</span> baking</a>
  </div>
</section>
```

**Example — Latest section (same for all):**
```html
<section class="latest">
  <h2>Latest Recipes</h2>
  <div class="latest-grid">{cards_html}</div>
  <div class="index-pagination-slot"></div>
  <a href="{base_url}/categories" class="btn">View All Recipes</a>
</section>
```

### Config Keys

- `domain_name`, `base_url`, `articles`, `categories`, `total`, `total_pages`, `current_page`, `per_page`, `article_card_template`
- Articles: `title`, `url`, `main_image`, `image`, `excerpt` — **only these**. No prep_time, servings.

### Index — Rules (MUST follow)

1. **render_cards() only** — Every article grid: `cards_html, card_css = render_cards(articles, config, show_excerpt=True, scope_prefix=".index-page")`. Use `scope_prefix=".index-page"` exactly (not `.index-page-15` or similar). Never custom card HTML. Append `{card_css}` to CSS.
2. **Pagination slot** — `<div class="index-pagination-slot"></div>` in Latest section. Required.
3. **View All / Browse All** — `href="{base_url_esc}/categories"` with `base_url_esc = html_module.escape(base_url)`. Never raw `base_url` in HTML.
4. **Category links** — `c.get("url")` from config, or fallback `f"{base_url}/categories"`. Never hardcode `/category/slug` or build from slug.
5. **Image fallback** — No image → `<div class="placeholder">🍽️</div>`. Never Unsplash or external URL.
6. **No hardcoded content** — Use `domain_name`, `article.get("title")`, `article.get("excerpt")`. Never "Emma", "MomdishMagic", "Chicken Alfredo".

### Index — Anti-patterns (common AI mistakes)

| Wrong | Right |
|-------|-------|
| Raw `{` or `}` in CSS f-string | Escape as `{{` and `}}` — single `}` causes SyntaxError |
| `cat_items.append(f'` with newline before closing `'` | One f-string per line in parens, or single-line |
| `pf['cdn']` or `pf["cdn"]` | `pf.get("cdn")` — avoid KeyError |
| Custom `render_small_card()` / `render_latest_card()` | `render_cards()` for ALL grids |
| Manual `<article class="recipe-card">` | `{cards_html}` from render_cards |
| Missing pagination slot | `<div class="index-pagination-slot"></div>` |
| `href="{base_url}"` for Browse All | `href="{base_url}/categories"` |
| `href="/category/desserts"` | `c.get("url")` |
| `feat_img = "https://unsplash.com/..."` | Placeholder div if no image |
| `article.get("prep_time")` | Articles don't have this — omit or use excerpt only |

### Hero — Dynamic content

```python
featured = articles[0] if articles else None
base_url = (config.get("base_url") or config.get("domain_url") or "/").rstrip("/")
base_url_esc = html_module.escape(base_url)  # use in href for Browse All, View All
if featured:
    feat_img = (featured.get("main_image") or featured.get("image") or "").strip()
    feat_title = html_module.escape((featured.get("title") or "Recipe")[:120])
    feat_url = html_module.escape(featured.get("url") or "#")
    feat_excerpt = html_module.escape((featured.get("excerpt") or "")[:200])
    if feat_img and feat_img.startswith("http"):
        hero_img = f'<img src="{html_module.escape(feat_img)}" alt="{feat_title}" ...>'
    else:
        hero_img = '<div class="hero-placeholder">🍽️</div>'
else:
    hero_img = '<div class="hero-placeholder">🍽️</div>'
    feat_title = html_module.escape(config.get("domain_name", "Recipe Blog"))
```

### Category loop (avoid SyntaxError)

**NEVER** put a newline inside a single- or double-quoted f-string — causes `SyntaxError: EOL while scanning string literal`. **NEVER** use raw `{` or `}` in CSS inside an f-string — causes `SyntaxError: f-string: single '}' is not allowed`. Use one of these patterns:

```python
# Category URL: use c.get("url") or base_url/categories. Escaped for HTML.
url = html_module.escape(cat.get("url") or f"{base_url}/categories")
# OK: One f-string per line, parentheses for implicit concatenation
cat_items.append(
    f'<a href="{url}" class="category-item">'
    f'<span class="cat-icon">{first_letter}</span>'
    f'<span class="cat-name">{name}</span></a>'
)

# OK: Single line
cat_items.append(f'<a href="{url}" class="category-item"><span class="cat-name">{name}</span></a>')

# WRONG — newline inside f-string causes SyntaxError:
# cat_items.append(f'
#     <a href="{url}">...
# ')
```

### CSS braces in f-strings (avoid triple braces)

```python
# OK: exactly {{ and }} for literal braces
css = f"""
.selector {{
    property: value;
}}
.other {{
    font-family: {font_family};  /* {var} for interpolation */
}}
"""

# WRONG — triple braces cause SyntaxError:
# .selector {{{     ← use {{ not {{{
#     ...
# }}}               ← use }} not }}}
```

### Quality checklist

- Use `.get()` for all dict access. `pf.get("cdn") or ""`
- `html.escape()` on title, excerpt, url, domain_name
- Max-width container, responsive breakpoints (768px, 600px)
- Empty states: "No recipes yet", "No categories yet"
- Scope CSS: prefix with `.index-page`

### CSS Scope

- Prefix all selectors with `.index-page` or `.index-N` to avoid leaking styles.

## Footer Design (aim for benchmark quality)
ter100.py`, `index_2.py`, `footer_100.py`)
3. **Implement:** `def generate(config: dict) -> dict:` returning `{"html": str, "css": str}`
4. **Scope CSS:** Prefix all selectors with the part's root class (see table in Project Overview)
5. **Article cards:** Index, category, sidebar — always use `render_cards()`, never custom card markup
6. **Design benchmark:** Follow "Design Reference — Quality Benchmark"
7. **Index:** Choose a DIFFERENT structure than existing templates (split vs stacked hero, circular vs pill categories, vary section order). Use `render_cards()`, pagination slot, `base_url/categories` for View All

## Tailwind CSS

- You may use Tailwind classes. The page head includes `<script src="https://cdn.tailwindcss.com"></script>`.

## Common Mistakes to Avoid

1. `return {{"html":...}}` → use `return {"html":...}`
2. `s.font_family` → use `s.get("heading_family", "serif")`
3. Static "Recipes" link → use dynamic category names from `config["categories"]`
4. Splitting HTML in the middle of tags (e.g. `nav_html[:len//2]`)
5. Jinja2-style loops → convert to Python `"".join(...)` or `for` loops
6. **Index:** `pf["cdn"]` or `config["base_url"]` → use `pf.get("cdn")`, `config.get("base_url", "/")`
7. **Index:** Forgetting to append `{card_css}` to the final CSS string
8. **Index:** No max-width container → content stretches full-width on large screens
9. **Index:** Custom `render_small_card()` or manual card HTML → MUST use `render_cards()` only
10. **Index:** Hardcoded `/category/desserts` → use `c.get("url")` from `config["categories"]`
11. **Index:** Missing `<div class="index-pagination-slot"></div>` → required for pagination injection
12. **Index:** Fallback image as `https://images.unsplash.com/...` → use placeholder div instead
13. **f-strings:** Never put newline inside `f'...'` or `f"..."` — causes `SyntaxError: EOL while scanning string literal`. Use one f-string per line in parentheses, or single-line, or triple-quoted `f'''...'''` for multi-line HTML.
14. **CSS in f-strings:** Every literal `{` and `}` in CSS must be escaped as `{{` and `}}`. A single `}` causes `SyntaxError: f-string: single '}' is not allowed`. Never use `{{{` or `}}}` — use exactly `{{` and `}}` for literal braces. Check every rule block.

## UI/UX Requirements (Critical — follow strictly)

- **Readability:** Min 16px body text, 1.5–1.7 line-height. Contrast ratio ≥ 4.5:1 for text.
- **Touch targets:** Links/buttons min 44×44px for mobile. Add padding, not tiny clickable areas.
- **Spacing:** Consistent whitespace. Min 1rem between nav items; 1.5–2rem between sections. Avoid cramped layouts.
- **Hierarchy:** Clear heading levels (h1 > h2 > h3). Logo/nav visually distinct from content. One clear primary CTA.
- **Cards/Grids:** Article cards with clear borders or shadows, hover feedback (opacity/underline). Image aspect ratio 16:10 or 4:3. Consistent gap between cards (1–1.5rem).
- **Navigation:** Simple, scannable nav. Max 8–10 links. Mobile: collapsible hamburger or stacked links; never horizontal scroll.
- **Colors:** Always use `config["colors"]` (domain palette): `primary`, `secondary`, `background`, `text_primary`, `text_secondary`, `border`. Use `extract_style(config)` and `css_vars(s)` so `:root { --primary: ...; }` is set. Never hardcode hex values; use CSS variables. Avoid pure black (#000); use dark gray.
- **Accessibility:** Use semantic HTML (header, nav, main, aside for side articles, article). Alt text on images. Focus states for links.
- **Images:** Always handle empty/missing images: show placeholder (gradient or icon), never broken img.
- **Performance:** No heavy animations. Subtle transitions (0.2s) only. Avoid layout shift (reserve space for images).

## Header Design Variety (Essential — each header MUST be unique)

**Every new header must have a different design.** Never repeat layouts, fonts, or sizes.

**Benchmark pattern (header_100):** Sticky nav, backdrop-blur, logo with icon (Font Awesome) + site name, nav links (Home, Recipes, then **categories listing** from `config.get("categories", [])` with `c.get("url")` and `c.get("name")` — not a single "Categories" menu — then About). Use `base_url` for all links. **About link:** if `config.get("domain_pages")` has an About-type page (slug `about-us`/`about` or name starting with "About"), use its `url` and `name` for the About nav link; else use `base_url/about` and label "About". **Do not add "Submit Recipe" or any submission CTA button** — headers are navigation only.

- **Fonts:** Pick a new combo. Playfair + Inter, Cormorant + Lato, Merriweather + Source Sans, DM Serif + DM Sans, etc.
- **Logo:** Icon + text, or text only. Vary size (1.2rem–3rem).
- **Layout:** Logo left + nav right + CTA right. Or logo center + nav below. Or stacked on mobile.
- **Style:** Sticky with backdrop-blur (benchmark), or minimal flat, pill buttons, gradient bar.

## Domain Colors (used by all parts and articles)

Each domain has its own color palette stored in the domain table. The config passed to every part (header, footer, side article, category) and to article generation includes `config["colors"]` with: `primary`, `secondary`, `background`, `text_primary`, `text_secondary`, `border`. 

**Use them consistently** — same domain = same colors across header, footer, side article, category, and article content.

### How to use domain colors correctly:

1. **Import and extract:**
   ```python
   from shared_style import extract_style
   s = extract_style(config)
   ```

2. **Use in CSS with CSS variables:**
   ```python
   css = f"""
   .your-part {{
       --primary: {s.get("primary", "#6C8AE4")};
       --secondary: {s.get("secondary", "#9C6ADE")};
       --background: {s.get("background", "#FFFFFF")};
       --text-primary: {s.get("text_primary", "#2D2D2D")};
       --text-secondary: {s.get("text_secondary", "#5A5A5A")};
       --border: {s.get("border", "#E2E8FF")};
       
       background: var(--background);
       color: var(--text-primary);
   }}
   ```

3. **Apply to elements:**
   - Backgrounds: use `var(--background)`
   - Primary actions/links: use `var(--primary)`
   - Headings: use `var(--text-primary)`
   - Body text: use `var(--text-primary)`
   - Muted text: use `var(--text-secondary)`
   - Borders: use `var(--border)`
   - Hover states: use `var(--primary)` or `var(--secondary)`

This ensures that when domain colors are changed in the admin panel, ALL parts (header, footer, side article, category, writer, articles) automatically update to match the new color scheme.

## Writer (Author Byline) Section

Writer templates display article author information in the **sidebar at the top** (before side articles/recipes). These are standalone components that get injected into the sidebar during article generation.

### Purpose & Placement

- **Location:** Top of sidebar (right column), before "More Recipes" or other sidebar content
- **Design:** Vertical card with centered content, warm inviting style
- **Function:** Introduce the article author, build trust, provide social follow buttons
- **Rotation:** System automatically rotates through domain's 4 writers for each new article

### Writer Data Structure

The writer object comes from `config.get("writer", {})` with:
- `name`: Writer's full name (e.g., "Emma")
- `title`: Professional title/role (e.g., "Owner & Founder of MomdishMagic")
- `bio`: Short 2-3 sentence bio describing their expertise and personality
- `avatar`: Avatar image URL (generated via Midjourney with **face perfectly centered in frame**)

### Template Structure (Python with f-strings):

```python
def generate(config: dict) -> dict:
    """Generate writer/author byline card for sidebar."""
    import html
    from shared_style import extract_style, part_font

    s = extract_style(config)
    pf = part_font("writer", config)

    font_import = f"@import url('{pf['cdn']}');" if pf.get("cdn") else ""
    font_family = pf.get("family") or "Inter, sans-serif"

    writer = config.get("writer", {})
    name = writer.get("name", "")
    title = writer.get("title", "")
    bio = writer.get("bio", "")
    avatar = writer.get("avatar", "")

    if not name:
        return {"html": "", "css": ""}  # No writer, return empty

    # Avatar with fallback to initials
    if avatar:
        avatar_html = f'<img src="{html.escape(avatar)}" alt="{html.escape(name)}" class="writer-avatar">'
    else:
        initials = "".join([word[0].upper() for word in name.split()[:2]])
        avatar_html = f'<div class="writer-avatar-placeholder">{html.escape(initials)}</div>'

    html_content = f"""
<div class="article-writer">
    <div class="writer-avatar-wrapper">
        {avatar_html}
    </div>
    <h4 class="writer-name">{html.escape(name)}</h4>
    <p class="writer-title">{html.escape(title)}</p>
    <p class="writer-bio">{html.escape(bio)}</p>
    <div class="writer-actions">
        <a href="#" class="writer-btn writer-btn-primary">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm0 22c-3.123 0-5.914-1.441-7.749-3.69.259-.588.783-.995 1.867-1.246 2.244-.518 4.459-.981 3.393-2.945-3.155-5.82-.899-9.119 2.489-9.119 3.322 0 5.634 3.177 2.489 9.119-1.035 1.952 1.1 2.416 3.393 2.945 1.082.25 1.61.655 1.871 1.241-1.836 2.253-4.628 3.695-7.753 3.695z"/>
            </svg>
            Follow on Pinterest
        </a>
        <a href="#" class="writer-btn writer-btn-secondary">View All Recipes</a>
    </div>
</div>
"""
    
    # CSS with warm gradient background, centered layout, action buttons
    css = f"""
{font_import}

.article-writer {{
    --primary: {s.get("primary", "#E07C5E")};
    --background: {s.get("background", "#ffffff")};
    --text-primary: {s.get("text_primary", "#2D2D2D")};
    --text-secondary: {s.get("text_secondary", "#666666")};
    --border: {s.get("border", "#e5e7eb")};

    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 2rem 1.5rem;
    margin: 0 0 1.5rem 0;
    background: linear-gradient(135deg, #FFF5F0 0%, #FFE8DC 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    font-family: {font_family};
}}

.article-writer .writer-avatar {{
    width: 100px;
    height: 100px;
    border-radius: 50%;
    object-fit: cover;
    object-position: center;
    border: 3px solid rgba(255, 255, 255, 0.8);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    margin-bottom: 1rem;
}}

.article-writer .writer-name {{
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 0.5rem 0;
}}

.article-writer .writer-title {{
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 0 0 1rem 0;
}}

.article-writer .writer-bio {{
    font-size: 0.9rem;
    color: var(--text-primary);
    line-height: 1.6;
    margin: 0 0 1.5rem 0;
}}

.article-writer .writer-actions {{
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    width: 100%;
}}

.article-writer .writer-btn {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.2s;
}}

.article-writer .writer-btn-primary {{
    background: #E60023;
    color: white;
    border: none;
}}

.article-writer .writer-btn-primary:hover {{
    background: #AD081B;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(230, 0, 35, 0.3);
}}

.article-writer .writer-btn-secondary {{
    background: white;
    color: var(--primary);
    border: 2px solid var(--primary);
}}

.article-writer .writer-btn-secondary:hover {{
    background: var(--primary);
    color: white;
}}

@media (max-width: 640px) {{
    .article-writer {{
        padding: 1.5rem 1rem;
    }}
    
    .article-writer .writer-avatar {{
        width: 80px;
        height: 80px;
    }}
}}
"""

    return {"html": html_content, "css": css}
```

### Design Requirements (Sidebar Card):

**CRITICAL:** Writer templates are **sidebar cards**, not inline article sections. They must be self-contained, visually distinct cards that sit at the top of the sidebar.

#### Container & Background:
- **Layout:** Vertical card (`flex-direction: column`), all content centered (`align-items: center`, `text-align: center`)
- **Background:** Warm gradient (e.g., `linear-gradient(135deg, #FFF5F0 0%, #FFE8DC 100%)`) or solid light color with warmth
- **Padding:** Generous (2rem vertical, 1.5rem horizontal) for breathing room
- **Border:** Rounded corners (16px) for modern, friendly look
- **Margin:** Bottom margin (1.5rem) to separate from "More Recipes" section below
- **Width:** 100% of sidebar width (typically 280-320px)

#### Avatar:
- **Size:** 90-110px circle (larger than typical avatars for prominence)
- **Position:** Top of card, centered horizontally
- **Cropping:** `object-fit: cover` + `object-position: center` (faces are centered in Midjourney images)
- **Border:** 3px white border (`rgba(255, 255, 255, 0.8)`) for depth
- **Shadow:** Subtle shadow (`0 4px 12px rgba(0, 0, 0, 0.1)`) for elevation
- **Margin:** 1rem bottom spacing before name
- **Placeholder:** If no avatar, show 2-letter initials in colored circle with gradient background

#### Text Content:
- **Name:** 
  - Font size: 1.4-1.6rem
  - Weight: 700 (bold)
  - Color: `var(--text-primary)` (dark, readable)
  - Margin: 0 0 0.5rem 0
- **Title/Role:**
  - Font size: 0.7-0.8rem
  - Weight: 600 (semi-bold)
  - Color: `var(--text-secondary)` (muted)
  - Transform: uppercase
  - Letter spacing: 0.1em (spaced out)
  - Margin: 0 0 1rem 0
- **Bio:**
  - Font size: 0.85-0.95rem
  - Line height: 1.6 (readable)
  - Color: `var(--text-primary)`
  - Margin: 0 0 1.5rem 0
  - Keep to 2-3 lines max

#### Action Buttons:
- **Container:** Vertical stack (`flex-direction: column`), 0.75rem gap, full width
- **Button 1 (Pinterest Follow):**
  - Background: Pinterest red (`#E60023`)
  - Color: white
  - Include Pinterest icon (SVG) to the left of text
  - Text: "Follow on Pinterest"
  - Hover: Darker red (`#AD081B`), slight lift (`translateY(-1px)`), shadow
- **Button 2 (View Recipes):**
  - Background: white
  - Color: `var(--primary)`
  - Border: 2px solid `var(--primary)`
  - Text: "View All Recipes"
  - Hover: Filled with `var(--primary)`, white text
- **Button styling:**
  - Padding: 0.75rem 1.5rem
  - Border radius: 8px
  - Font size: 0.9rem
  - Font weight: 600
  - Display: flex, centered content
  - Transition: all 0.2s
  - No text decoration

#### Responsive (Mobile <640px):
- Slightly smaller avatar (80px)
- Slightly smaller text
- Maintain centered layout
- Buttons remain full width

### Important Notes:

1. **Sidebar placement:** Writer card is injected at the **top of the sidebar**, before side articles
2. **Face centered:** All avatar images are generated with the face centered in the frame, so `object-position: center` will work correctly
3. **Prefix selectors:** Use `.article-writer` as root class, prefix all child selectors (e.g., `.article-writer .writer-name`)
4. **Color variables:** Use CSS variables for colors (e.g., `--primary`, `--text-primary`)
5. **Fallback:** Always handle missing avatar with initials placeholder
6. **Empty state:** If no writer name, return empty HTML/CSS
7. **Self-contained:** Card should be fully styled and not depend on sidebar styles
8. **Warm aesthetic:** Use warm, inviting colors (peach, orange tones) for background gradient
9. **Visual hierarchy:** Avatar → Name → Title → Bio → Buttons (top to bottom)
10. **Database tracking:** Writer JSON and avatar URL are saved to `article_content.writer` and `article_content.writer_avatar` columns

### Design Variations for Different Templates:

When creating writer_2.py, writer_3.py, etc., you can vary:
- **Background:** Different gradients (blue, green, purple tones) or solid colors
- **Avatar size:** 80-120px range
- **Avatar shape:** Circle (50%), rounded square (20%), or other
- **Layout:** Horizontal (avatar left, info right) vs vertical (current)
- **Buttons:** Different colors, icons, text, or number of buttons
- **Typography:** Different font sizes, weights, spacing
- **Border style:** Solid, dashed, shadow, or none

But always maintain:
- ✅ Centered face in avatar (`object-position: center`)
- ✅ Clear visual hierarchy (avatar → name → title → bio → actions)
- ✅ Responsive design (mobile-friendly)
- ✅ Domain color integration (CSS variables)
- ✅ Fallback for missing avatar (initials)
- ✅ Empty state handling (return empty if no name)

### Example CSS Structure (Sidebar Card):

```css
.article-writer {
    --primary: {s.get("primary", "#E07C5E")};
    --text-primary: {s.get("text_primary", "#2D2D2D")};
    --text-secondary: {s.get("text_secondary", "#666666")};
    --border: {s.get("border", "#e5e7eb")};
    
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 2rem 1.5rem;
    margin: 0 0 1.5rem 0;
    background: linear-gradient(135deg, #FFF5F0 0%, #FFE8DC 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
}

.article-writer .writer-avatar {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    object-fit: cover;
    object-position: center;  /* Face is centered in source image */
    border: 3px solid rgba(255, 255, 255, 0.8);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    margin-bottom: 1rem;
}

.article-writer .writer-name {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 0.5rem 0;
}

.article-writer .writer-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 0 0 1rem 0;
}

.article-writer .writer-bio {
    font-size: 0.9rem;
    color: var(--text-primary);
    line-height: 1.6;
    margin: 0 0 1.5rem 0;
}

.article-writer .writer-actions {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    width: 100%;
}

.article-writer .writer-btn {
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.2s;
}

.article-writer .writer-btn-primary {
    background: #E60023;
    color: white;
}

.article-writer .writer-btn-primary:hover {
    background: #AD081B;
    transform: translateY(-1px);
}

.article-writer .writer-btn-secondary {
    background: white;
    color: var(--primary);
    border: 2px solid var(--primary);
}

.article-writer .writer-btn-secondary:hover {
    background: var(--primary);
    color: white;
}
```
