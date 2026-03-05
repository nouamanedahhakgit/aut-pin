# Change Domain Group Feature

## Overview
You can now change the group assignment for any domain directly from the `/admin/domains` page.

## How to Use

### 1. Open Domains Page
Navigate to `http://localhost:5001/admin/domains`

### 2. Find the Domain
Locate the domain you want to move to a different group.

### 3. Click the Change Group Button
- Look for the **📁** button next to each domain URL
- It's located between the edit button (📝) and the domain name

### 4. Select New Group
- A modal will open showing all available groups
- Groups are displayed with their full hierarchy (e.g., "Parent → Child → Grandchild")
- Select the desired group from the dropdown
- Or select "-- No Group (Standalone) --" to remove from all groups

### 5. Save Changes
- Click the "Save" button
- The page will reload automatically
- The domain will now appear under the new group

## Features

✅ **Hierarchical Group Display**: Groups shown with full parent → child path
✅ **User Access Control**: Only see groups you have access to
✅ **Automatic Indexing**: Domain automatically gets the next available index in the new group
✅ **Standalone Option**: Can remove domain from all groups
✅ **Real-time Update**: Page reloads to show new group assignment

## Technical Details

### UI Components

**Button Location**: Next to domain URL in the domains table
```html
<button class="change-group-btn" data-domain-id="123" data-current-group="5">📁</button>
```

**Modal**: `#changeGroupModal`
- Shows dropdown of all accessible groups
- Pre-selects current group
- Displays full hierarchy for each group

### API Endpoint

**URL**: `/api/domains/<domain_id>/change-group`
**Method**: `PUT`
**Auth**: Requires login (`@login_required`)

**Request Body**:
```json
{
  "group_id": 5  // or null for standalone
}
```

**Response**:
```json
{
  "success": true
}
```

### Access Control

1. **Domain Access**: User must have access to the domain being moved
2. **Group Access**: User must have access to the target group
3. **Admin Override**: Admins can move any domain to any group

### Database Updates

When changing group:
1. Updates `domains.group_id` to new group (or NULL)
2. Calculates and sets `domains.domain_index` (next available in group)
3. Maintains referential integrity

## Example Use Cases

### Move Domain to Different Group
1. Domain is in "Food → Recipes"
2. Click 📁 button
3. Select "Food → Desserts"
4. Domain moves to Desserts group

### Remove Domain from Group
1. Domain is in "Travel → Europe"
2. Click 📁 button
3. Select "-- No Group (Standalone) --"
4. Domain becomes standalone (no group)

### Organize New Domains
1. Bulk add 10 domains (no group)
2. For each domain, click 📁
3. Assign to appropriate groups
4. All domains now organized

## Benefits

✅ **Flexibility**: Easy to reorganize domains
✅ **No Page Navigation**: Change groups without leaving domains page
✅ **Visual Feedback**: See full group hierarchy before moving
✅ **Error Prevention**: Only shows groups you have access to
✅ **Batch Friendly**: Can quickly organize multiple domains

## Notes

- Page reloads after successful change to show updated layout
- Domain index is automatically calculated (no manual input needed)
- Moving to a full group (4 domains) is allowed - group can exceed 4
- Standalone domains can be assigned to groups at any time
- Group assignment doesn't affect domain's other settings (colors, fonts, etc.)
