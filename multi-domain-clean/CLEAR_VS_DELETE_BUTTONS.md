# Clear vs Delete Buttons - Important Differences

## Overview
There are two types of operations available on the `/admin/domains` page:

1. **🔓 Ungroup (Clear)** - Removes domains from groups but keeps the domains
2. **🗑️ Delete** - Permanently deletes domains and all their content

## Button Differences

### 1. 🔓 Ungroup All (Clear All Groups)
**What it does:**
- Removes ALL domains from ALL groups
- Makes all domains "standalone" (no group)
- **Domains are NOT deleted** - they remain in the database
- You can reassign them to groups later

**Result:**
```
Before:
Group "Food" → domain1.com, domain2.com
Group "Travel" → domain3.com, domain4.com

After:
Standalone domains:
- domain1.com (no group)
- domain2.com (no group)
- domain3.com (no group)
- domain4.com (no group)
```

### 2. 🗑️ Delete All Domains
**What it does:**
- **PERMANENTLY DELETES** all domains
- Deletes all titles associated with domains
- Deletes all article content
- Deletes all domain-user associations
- **Cannot be undone!**

**Result:**
```
Before:
- domain1.com
- domain2.com
- domain3.com
- domain4.com

After:
(empty - everything deleted)
```

### 3. 🔓 Ungroup This Group
**What it does:**
- Removes domains from the currently viewed group only
- Domains become standalone
- **Domains are NOT deleted**

**Result:**
```
Before (viewing Group "Food"):
- domain1.com (in Food group)
- domain2.com (in Food group)

After:
- domain1.com (standalone)
- domain2.com (standalone)
```

### 4. ✖️ Clear Single Domain
**What it does:**
- Removes one specific domain from its group
- Domain becomes standalone
- **Domain is NOT deleted**

## When to Use Each

### Use 🔓 Ungroup When:
- ✅ You want to reorganize domains into different groups
- ✅ You want to keep domains but remove group structure
- ✅ You made a mistake assigning domains to groups
- ✅ You want to start fresh with group assignments

### Use 🗑️ Delete When:
- ⚠️ You want to completely remove domains from the system
- ⚠️ You want to delete all content (titles, articles)
- ⚠️ You're sure you don't need the domains anymore
- ⚠️ You understand this cannot be undone

## Safety Features

### Ungroup Operations (🔓)
- ✅ Single confirmation
- ✅ Non-destructive
- ✅ Reversible (can reassign to groups)
- ✅ Fast operation

### Delete Operations (🗑️)
- ⚠️ **Double confirmation** required
- ⚠️ **Destructive** - cannot be undone
- ⚠️ **Admin only** for delete all
- ⚠️ Deletes all related content

## Button Locations

**On `/admin/domains` page:**
```
Top Right:
[🔓 Ungroup All] [🗑️ Delete All Domains] [🔓 Ungroup This Group]
```

**Next to each domain:**
```
Domain URL [📝 Edit] [📁 Change Group] [✖️ Ungroup]
```

## Technical Details

### Ungroup Operations
**API Endpoints:**
- `POST /api/domains/clear-all-groups` - Ungroup all
- `POST /api/domains/clear-group/<id>` - Ungroup specific group
- `PUT /api/domains/<id>/change-group` (with `group_id: null`) - Ungroup single

**Database:**
```sql
UPDATE domains 
SET group_id = NULL, domain_index = NULL 
WHERE [conditions]
```

### Delete Operations
**API Endpoints:**
- `POST /api/domains/delete-all` - Delete all domains
- `POST /api/groups/delete-all` - Delete all groups and domains

**Database:**
```sql
DELETE FROM titles WHERE domain_id IN (...)
DELETE FROM article_content WHERE title_id IN (...)
DELETE FROM user_domains WHERE domain_id IN (...)
DELETE FROM domains WHERE [conditions]
```

## Quick Reference

| Button | Icon | Action | Destructive? | Reversible? |
|--------|------|--------|--------------|-------------|
| Ungroup All | 🔓 | Remove from groups | No | Yes |
| Delete All | 🗑️ | Delete everything | **Yes** | **No** |
| Ungroup This Group | 🔓 | Remove from current group | No | Yes |
| Ungroup Single | ✖️ | Remove one from group | No | Yes |

## Important Notes

- **"Clear" = Ungroup** - Domains remain, just no group assignment
- **"Delete" = Permanent** - Domains and all content removed forever
- **Always use Ungroup first** if you're unsure
- **Delete requires admin** for safety
- **Ungroup is safe** - you can always reassign domains to groups later

## Example Workflow

**Reorganizing Domains:**
1. Click "🔓 Ungroup All" to remove all group assignments
2. Domains become standalone
3. Use "📁 Change Group" button to reassign to new groups
4. Or use bulk add to create new group structure

**Starting Fresh:**
1. Click "🗑️ Delete All Domains" (admin only)
2. Confirm twice
3. Everything deleted
4. Add new domains and groups from scratch
