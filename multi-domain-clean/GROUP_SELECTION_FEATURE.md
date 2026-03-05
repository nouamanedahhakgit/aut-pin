# Group Selection for Domain Adding

## Overview
You can now select a group when adding domains, both for single and bulk additions.

## Features

### 1. Single Domain Add with Group Selection
**Location**: `/admin/domains` - "➕ Add New Domain" section

**Features**:
- **3 Assignment Modes**:
  - **Standalone** - Domain without group
  - **Specific Group** ✅ (Selected by default)
  - **Random Group** - Auto-assign to group with <4 domains

- **Parent/Subgroup Selection**:
  - Choose a parent group
  - Optionally select a subgroup
  - Or add directly to parent

### 2. Bulk Add with Group Selection ✅ NEW!
**Location**: `/admin/domains` - "Bulk add" button

**Features**:
- Add multiple domains at once
- Select a group for ALL domains
- All domains get sequential indexes (A, B, C, D, E, F...)
- Or leave as standalone

## How to Use

### Single Domain with Group

1. **Go to** `http://localhost:5001/admin/domains`
2. **Expand** "➕ Add New Domain" section
3. **Enter** domain URL (e.g., `example.com`)
4. **"Specific Group" is selected by default**
5. **Select** a parent group from dropdown
6. **Optionally** select a subgroup
7. **Click** "Add Domain"

**Result**: Domain added to selected group with next available index

### Bulk Add with Group

1. **Go to** `http://localhost:5001/admin/domains`
2. **Click** "Bulk add" button to expand form
3. **Enter** domains (one per line):
   ```
   domain1.com
   domain2.com
   domain3.com
   domain4.com
   ```
4. **Select** group from dropdown (or leave as "Standalone")
5. **Click** "Bulk Add"

**Result**: All domains added to selected group with sequential indexes

## Examples

### Example 1: Add 4 Domains to "Recipes" Group

**Input**:
```
recipe-blog-1.com
recipe-blog-2.com
recipe-blog-3.com
recipe-blog-4.com
```

**Group Selected**: "Food → Recipes"

**Result**:
```
Group: "Food → Recipes" (id=5)
├── Domain A (index 0): recipe-blog-1.com
├── Domain B (index 1): recipe-blog-2.com
├── Domain C (index 2): recipe-blog-3.com
└── Domain D (index 3): recipe-blog-4.com
```

### Example 2: Add More Domains to Existing Group

If "Recipes" group already has 2 domains (A, B):

**Bulk Add**:
```
recipe-blog-3.com
recipe-blog-4.com
recipe-blog-5.com
```

**Result**: New domains get indexes 2, 3, 4 (C, D, E)

## Technical Details

### Backend Changes

**Single Domain Add** (`/admin/domains/add`):
- Already supported group selection
- Made "Specific Group" mode default
- Shows group selector automatically

**Bulk Domain Add** (`/admin/domains/bulk-add`):
- Added `target_group_id` parameter
- Calculates starting index for group
- Assigns sequential indexes to all domains
- Each domain gets random templates, colors, fonts

### Database Updates

When adding with group:
```sql
INSERT INTO domains 
(domain_url, domain_name, group_id, domain_index) 
VALUES (?, ?, ?, ?)
```

- `group_id`: Selected group ID (or NULL for standalone)
- `domain_index`: Sequential index starting from current max + 1

### Auto-Assignment Features

All added domains automatically get:
- ✅ Random website theme (1-9)
- ✅ Random article generator (2, 4, 6, 7, 8, 9)
- ✅ Random font combination (professional pairings)
- ✅ Default colors (clean black/white/green)
- ✅ 2 Random pin templates
- ✅ User's default categories (from profile)
- ✅ Assigned to current user (`user_domains` table)

## UI Improvements

### Single Add Form
- "Specific Group" selected by default
- Group selector visible immediately
- No need to click radio button first
- Cleaner, faster workflow

### Bulk Add Form
- Group dropdown added
- Clear label: "Assign to Group (Optional)"
- Help text: "All domains will be added to this group"
- Matches single add UX

## Benefits

✅ **Faster Workflow**: Group selector shown by default
✅ **Bulk Efficiency**: Add many domains to one group at once
✅ **Organized**: Domains immediately grouped
✅ **Flexible**: Can still add standalone domains
✅ **Sequential Indexing**: Automatic A, B, C, D... assignment
✅ **User Isolation**: Only see your own groups

## Notes

- Groups are filtered by user access (non-admin users only see their groups)
- Duplicate domains are skipped (shows error message)
- Domain index auto-increments within each group
- Can add more than 4 domains to a group (no limit)
- Standalone domains can be assigned to groups later using the 📁 button

## Related Features

- **Change Group** (📁 button): Move domain to different group
- **Clear Group** (✖️ button): Remove domain from group
- **Clear All Groups**: Remove all domains from all groups
- **Group Management**: `/admin/groups` for creating/editing groups
