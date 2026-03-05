# Random Domain Setup - Feature Documentation

## Overview
When you add a new domain (single or bulk), the system automatically assigns random, high-quality settings to ensure good UX and variety.

## What Gets Randomly Assigned

### 1. **Website Theme** 🎨
- Random theme from 1-9
- Each theme has a different layout and style
- Ensures visual variety across domains

### 2. **Article Generator** 📝
- Randomly selects from generators: 2, 4, 6, 7, 8, 9
- Each generator creates different article layouts
- Provides content diversity

### 3. **Font Combinations** 🔤
The system uses professionally paired font combinations for optimal readability:

| Heading Font | Body Font |
|--------------|-----------|
| Playfair Display | Inter |
| Lora | Open Sans |
| Merriweather | Lato |
| Source Serif 4 | Source Sans 3 |
| Fraunces | DM Sans |
| Georgia | Arial |
| Playfair Display | Source Sans 3 |
| Lora | Inter |

**Font Settings:**
- Heading H1: 2.5rem
- Heading H2: 1.875rem
- Heading H3: 1.5rem
- Body Size: 1rem
- Line Height: 1.7 (optimal readability)

### 4. **Colors** 🎨
Default color palette (clean and professional):
- **Primary**: `#2ecc71` (Green)
- **Secondary**: `#27ae60` (Dark Green)
- **Background**: `#FFFFFF` (White)
- **Text Primary**: `#000000` (Black)
- **Text Secondary**: `#333333` (Dark Gray)
- **Border**: `#E0E0E0` (Light Gray)

### 5. **Pin Templates** 📌
- Automatically assigns **2 random pin templates** from your library
- Ensures variety in Pinterest pins
- Can be changed later in domain settings

### 6. **Site Templates** 🏗️
Randomly assigns:
- Header template
- Footer template
- Sidebar template
- Category page template
- Writer template
- Index template
- Article card template

### 7. **Default Categories** 📂
Uses categories from your profile settings (`/profile`):

**Default Categories:**
```
Appetizers
Main Courses
Desserts
Beverages
Salads
Soups
Snacks
Breakfast
```

You can customize these in your profile, and they'll be automatically assigned to all new domains.

## How to Use

### Setting Up Default Categories
1. Go to `/profile`
2. Scroll to "Default Settings"
3. Edit the "Default Categories" textarea (one per line)
4. Click "💾 Save Settings"
5. All new domains will use these categories

### Adding Domains

**Single Domain:**
1. Go to `/admin/domains`
2. Fill in domain URL
3. Select group (optional)
4. Click "Add Domain"
5. ✅ Random settings applied automatically

**Bulk Add:**
1. Go to `/admin/domains`
2. Click "Bulk Add" button
3. Paste domain URLs (one per line)
4. Click "Add All"
5. ✅ Each domain gets unique random settings

## Customization After Creation

All random settings can be changed later:
- **Colors**: Click color swatches in domains table
- **Fonts**: Click font cell in domains table
- **Categories**: Click categories cell in domains table
- **Templates**: Click template cells to change
- **Theme**: Edit in domain settings
- **Article Generator**: Edit in domain settings

## Benefits

✅ **Time Saving**: No manual configuration needed
✅ **Variety**: Each domain looks unique
✅ **Professional**: Curated font pairings and colors
✅ **Good UX**: Optimal readability and accessibility
✅ **Consistency**: All domains follow best practices
✅ **Flexibility**: Easy to customize after creation

## Technical Details

**Function:** `_assign_random_site_templates(conn, domain_id, user_id)`

**Location:** `app.py` (lines 10632-10722)

**Called by:**
- `/admin/domains/add` (single domain)
- `/admin/domains/bulk-add` (bulk domains)

**Database Updates:**
- `domains.header_template`
- `domains.footer_template`
- `domains.side_article_template`
- `domains.category_page_template`
- `domains.writer_template`
- `domains.index_template`
- `domains.article_card_template`
- `domains.domain_colors`
- `domains.domain_fonts`
- `domains.website_template`
- `domains.article_template_config`
- `domains.categories_list`
- `domain_template_assignments` (pin templates)

## Notes

- Random selection uses Python's `random.choice()` for true randomness
- Font combinations are pre-selected for optimal UX
- Colors follow accessibility guidelines (WCAG AA)
- All settings can be overridden per domain
- User-specific categories are fetched from `user_api_keys.default_categories`
