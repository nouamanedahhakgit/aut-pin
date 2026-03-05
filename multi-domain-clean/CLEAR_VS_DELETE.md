# Clear vs Delete - Understanding the Difference

## Two Different Actions

### 🔓 Ungroup (Clear) - NON-DESTRUCTIVE
**What it does**: Removes domains from groups but keeps the domains

**Buttons**:
- **🔓 Ungroup All** - Remove all domains from all groups
- **🔓 Ungroup This Group** - Remove domains from current group
- **✖️** (per domain) - Remove single domain from its group

**Result**: Domains become standalone (no group assignment)

**Example**:
```
BEFORE:
Group "Recipes":
├── A: recipe1.com
├── B: recipe2.com
├── C: recipe3.com
└── D: recipe4.com

AFTER clicking "Ungroup All":
Standalone domains:
- recipe1.com (no group)
- recipe2.com (no group)
- recipe3.com (no group)
- recipe4.com (no group)

✅ Domains still exist
✅ All content preserved
✅ Can reassign to groups later
```

### 🗑️ Delete - DESTRUCTIVE & PERMANENT
**What it does**: Permanently deletes domains and ALL their content

**Buttons**:
- **🗑️ Delete All Domains** - Delete ALL domains permanently
- **🗑️ Clear All Groups & Domains** (on `/admin/groups`) - Delete everything

**Result**: Domains are completely removed from database

**Example**:
```
BEFORE:
Group "Recipes":
├── A: recipe1.com (with 50 articles)
├── B: recipe2.com (with 30 articles)
├── C: recipe3.com (with 40 articles)
└── D: recipe4.com (with 25 articles)

AFTER clicking "Delete All Domains":
❌ All domains deleted
❌ All 145 articles deleted
❌ All titles deleted
❌ All content gone forever
```

## Button Locations

### On `/admin/domains` Page

| Button | Action | Destructive? |
|--------|--------|--------------|
| 🔓 Ungroup All | Remove all domains from groups | ❌ No |
| 🗑️ Delete All Domains | Delete all domains permanently | ✅ YES |
| 🔓 Ungroup This Group | Remove domains from current group | ❌ No |
| ✖️ (per domain) | Remove single domain from group | ❌ No |

### On `/admin/groups` Page

| Button | Action | Destructive? |
|--------|--------|--------------|
| 🗑️ Clear All Groups & Domains | Delete everything | ✅ YES |
| Delete (per group) | Delete group + subgroups + domains | ✅ YES |

## When to Use Each

### Use 🔓 Ungroup When:
- ✅ You want to reorganize domains
- ✅ You want to move domains to different groups
- ✅ You want to keep domains but remove group structure
- ✅ You're testing group assignments
- ✅ You want to start fresh with grouping

### Use 🗑️ Delete When:
- ✅ You want to completely remove domains
- ✅ You're cleaning up test data
- ✅ You want to start completely fresh
- ✅ Domains are no longer needed
- ⚠️ You're absolutely sure (cannot be undone!)

## Safety Features

### Ungroup Operations
- ✅ Single confirmation
- ✅ Shows count of affected domains
- ✅ Reversible (can regroup anytime)
- ✅ Available to all users (for their domains)

### Delete Operations
- ✅ **Double confirmation** (two dialogs)
- ✅ Clear warning messages
- ✅ Shows count of deleted items
- ✅ **Admin only** (for safety)
- ⚠️ **PERMANENT** - cannot be undone

## API Endpoints

### Ungroup Endpoints
```
POST /api/domains/clear-all-groups
POST /api/domains/clear-group/<group_id>
PUT  /api/domains/<domain_id>/change-group (with group_id: null)
```

### Delete Endpoints
```
POST /api/domains/delete-all (Admin only)
POST /api/groups/delete-all (Admin only)
GET  /admin/groups/delete/<group_id> (Cascade delete)
```

## Quick Reference

**Want to reorganize?** → Use 🔓 Ungroup
**Want to delete?** → Use 🗑️ Delete

**Domains remain?** → Ungroup ✅
**Domains gone forever?** → Delete ✅

**Can undo?** → Ungroup ✅ / Delete ❌

## Current Button Labels

On `/admin/domains`:
- **🔓 Ungroup All** - Makes all domains standalone
- **🗑️ Delete All Domains** - Deletes all domains permanently
- **🔓 Ungroup This Group** - Makes group's domains standalone

The buttons are now clearly labeled to avoid confusion! 🎯
