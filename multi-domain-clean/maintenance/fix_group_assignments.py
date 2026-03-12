#!/usr/bin/env python3
"""
Fix group assignments - assign all existing groups to their respective users.
This script assigns:
1. All groups to admin users (is_admin=1)
2. Groups containing user's domains to those users
"""
from db import get_connection, execute as db_execute, dict_row

def fix_group_assignments():
    """Assign groups to users based on their domains."""
    
    with get_connection() as conn:
        # Get all users
        cur = db_execute(conn, "SELECT id, username, is_admin FROM users")
        users = [dict_row(r) for r in cur.fetchall()]
        
        if not users:
            print("❌ No users found! Create users first.")
            return False
        
        print(f"Found {len(users)} user(s)")
        
        for user in users:
            user_id = user["id"]
            username = user["username"]
            is_admin = user.get("is_admin", 0)
            
            if is_admin:
                # Assign ALL groups to admin users
                cur = db_execute(conn, "SELECT id FROM `groups`")
                all_groups = [dict_row(r)["id"] for r in cur.fetchall()]
                
                assigned = 0
                for group_id in all_groups:
                    try:
                        db_execute(conn, "INSERT INTO user_groups (user_id, group_id) VALUES (?, ?)", (user_id, group_id))
                        assigned += 1
                    except:
                        pass  # Already assigned
                
                print(f"✅ Admin '{username}': Assigned {assigned} group(s)")
            
            else:
                # Assign groups that contain user's domains
                cur = db_execute(conn, """
                    SELECT DISTINCT d.group_id
                    FROM user_domains ud
                    JOIN domains d ON d.id = ud.domain_id
                    WHERE ud.user_id = ? AND d.group_id IS NOT NULL
                """, (user_id,))
                group_ids = [dict_row(r)["group_id"] for r in cur.fetchall()]
                
                assigned = 0
                for group_id in group_ids:
                    try:
                        db_execute(conn, "INSERT INTO user_groups (user_id, group_id) VALUES (?, ?)", (user_id, group_id))
                        assigned += 1
                    except:
                        pass  # Already assigned
                
                print(f"✅ User '{username}': Assigned {assigned} group(s)")
        
        return True

if __name__ == "__main__":
    print("=" * 60)
    print("Fix Group Assignments")
    print("=" * 60)
    
    try:
        if fix_group_assignments():
            print("\n" + "=" * 60)
            print("✅ Group assignments fixed!")
            print("=" * 60)
            print("\nUsers can now see their groups at:")
            print("http://localhost:5001/admin/groups")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
