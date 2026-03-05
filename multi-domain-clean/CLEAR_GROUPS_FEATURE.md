# Clear Groups Feature

## Overview
You can now remove domains from groups (make them standalone) in three ways:
1. **Clear single domain** - Remove one domain from its group
2. **Clear current group** - Remove all domains from the group you're viewing
3. **Clear all groups** - Remove ALL domains from ALL groups

## Features Added

### 1. Clear Single Domain Button (✖️)
- **Location**: Next to each domain in the domains table
- **Action**: Removes that specific domain from its group
- **Visibility**: Only shows if domain is in a group

### 2. Clear This Group Button (🗑️)
- **Location**: Top of `/admin/domains` page (when viewing a specific group)
- **Action**: Removes all domains from the currently viewed group
- **Visibility**: Only shows when filtering by `group_id`

### 3. Clear All Groups Button (🗑️)
- **Location**: Top of `/admin/domains` page
- **Action**: Removes ALL domains from ALL groups (makes all standalone)
- **Visibility**: Always visible

## How to Use

### Clear Single Domain
1. Go to `http://localhost:5001/admin/domains`
2. Find a domain that's in a group
3. Click the **✖️** button next to it
4. Confirm the action
5. Domain becomes standalone (no group)

### Clear Current Group
1. Go to a specific group: `http://localhost:5001/admin/domains?group_id=X`
2. Click **🗑️ Clear This Group** button at the top
3. Confirm the action
4. All domains in that group become standalone

### Clear All Groups
1. Go to `http://localhost:5001/admin/domains`
2. Click **🗑️ Clear All Groups** button at the top
3. Confirm the action (⚠️ This affects ALL domains!)
4. All domains become standalone

## Technical Details

### UI Components

**Single Domain Clear Button**:
```html
<button class="clear-group-btn" data-domain-id="123">✖️</button>
```
- Only rendered if `domain.group_id` is not NULL
- Red outline (danger style)

**Bulk Clear Buttons**:
```html
<button onclick="clearAllGroups()">🗑️ Clear All Groups</button>
<button onclick="clearCurrentGroup()">🗑️ Clear This Group</button>
```

### API Endpoints

#### 1. Clear Single Domain
**Endpoint**: `/api/domains/<domain_id>/change-group`
**Method**: `PUT`
**Body**: `{"group_id": null}`
**Response**: `{"success": true}`

#### 2. Clear All Groups
**Endpoint**: `/api/domains/clear-all-groups`
**Method**: `POST`
**Response**: `{"success": true, "count": 42}`

#### 3. Clear Specific Group
**Endpoint**: `/api/domains/clear-group/<group_id>`
**Method**: `POST`
**Response**: `{"success": true, "count": 4}`

### Access Control

**Admin Users**:
- Can clear any domain from any group
- Can clear all domains from all groups
- No restrictions

**Regular Users**:
- Can only clear their own domains
- Can only clear groups they have access to
- Filtered by `user_domain_ids` and `user_group_ids`

### Database Updates

When clearing:
```sql
UPDATE domains 
SET group_id = NULL, domain_index = NULL 
WHERE [conditions]
```

## Use Cases

### Reorganize Domains
1. Clear all groups
2. Reassign domains to new group structure
3. Clean slate for reorganization

### Remove Domain from Group
1. Domain was incorrectly assigned
2. Click ✖️ to make it standalone
3. Reassign to correct group

### Empty a Group
1. Group structure changed
2. Clear all domains from that group
3. Delete the empty group if needed

### Bulk Cleanup
1. Too many misassigned domains
2. Clear all groups at once
3. Start fresh with proper assignments

## Safety Features

✅ **Confirmation Dialogs**: All actions require confirmation
✅ **Access Control**: Users can only clear their own domains
✅ **Non-Destructive**: Domains are not deleted, just unassigned
✅ **Reversible**: Can reassign domains to groups anytime
✅ **Count Feedback**: Shows how many domains were affected

## Button Styles

- **✖️ Clear Single**: Red outline, small, next to domain
- **🗑️ Clear This Group**: Orange/warning style
- **🗑️ Clear All Groups**: Orange/warning style

## Notes

- Clearing doesn't delete domains, just removes group assignment
- `group_id` and `domain_index` are set to NULL
- Domains remain in database and keep all other settings
- Can reassign to groups at any time using the 📁 button
- Page reloads after successful clear to show updated state
- Shows count of affected domains in success message

## Example Workflow

**Before**:
```
Group "Recipes" (id=5):
├── Domain A: recipe1.com
├── Domain B: recipe2.com
├── Domain C: recipe3.com
└── Domain D: recipe4.com
```

**After clearing group**:
```
Standalone Domains:
- recipe1.com (no group)
- recipe2.com (no group)
- recipe3.com (no group)
- recipe4.com (no group)
```

All domains are now independent and can be reassigned to any group!
