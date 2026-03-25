# Theme Generation Guide

When creating new themes (header, footer, index, category, sidebar, domain pages):

## Colors — All Editable

**Never hardcode colors.** Every color visible in the UI must be configurable via Domain Settings (⚙️).

### Required CSS variables (from config)

Define these in your theme's `_shared.py` or equivalent, using `s.get("key", "#default")` from `extract_style(config)`:

| Variable | Domain Settings key | Use for |
|----------|---------------------|---------|
| `--primary` | primary | Backgrounds, buttons, accents |
| `--secondary` | secondary | Complementary accents |
| `--gold` / `--accent` | gold, accent | Ornaments, diamonds, highlights |
| `--text` | text_primary | Main body text on light bg |
| `--muted` | text_secondary | Secondary/muted text |
| `--text-on-primary` | text_on_primary | Text on primary/dark bg (e.g. footer, hero) |
| `--text-on-primary-muted` | text_on_primary_muted | Muted text on primary bg (links, labels) |
| `--bg` | background | Page background |
| `--border` | border | Borders |
| `--border-light` | border_light | Lighter borders |
| `--gold-light` | (from gold) | Subtle gold borders: `rgba(gold_rgb, 0.15)` |
| `--gold-border` | (from gold) | Gold-tinted borders: `rgba(gold_rgb, 0.45)` |

### Apply to ALL page types

- Header
- Footer
- Index
- Category
- Sidebar
- About Us, Contact, Terms, Privacy, etc.

**Do not** use `#F7F1E8`, `rgba(247,241,232,0.5)`, `#C9A96E` or similar inline. Use `var(--text-on-primary)`, `var(--text-on-primary-muted)`, `var(--gold)` etc.

### Example

```python
# In CSS
.dp-t11-footer { background: var(--primary); color: var(--text-on-primary); }
.ft11-link { color: var(--text-on-primary-muted); }
.ft11-heading { color: var(--gold); }
.ft11-cat { border: 1px solid var(--gold-border); }
```

## New theme checklist

- [ ] All colors use CSS variables from config
- [ ] Footer uses var(--primary), var(--text-on-primary), var(--text-on-primary-muted), var(--gold)
- [ ] Header uses same
- [ ] Index, category, sidebar, domain pages use same
- [ ] No `#hex`, `rgb()`, `rgba()` except in fallbacks like `var(--x, #fallback)`
