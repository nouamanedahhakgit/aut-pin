"""
Fix domain assignments - assign existing domains to users
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from db import get_connection, execute as db_execute, dict_row

def main():
    print("=== Fix Domain Assignments ===\n")
    
    with get_connection() as conn:
        # Get all users
        cur = db_execute(conn, "SELECT id, username, is_admin FROM users ORDER BY id")
        users = [dict_row(r) for r in cur.fetchall()]
        
        if not users:
            print("No users found in database.")
            return
        
        print("Available users:")
        for u in users:
            admin_label = " (ADMIN)" if u["is_admin"] else ""
            print(f"  {u['id']}: {u['username']}{admin_label}")
        
        print("\n" + "="*50)
        print("OPTION 1: Assign ALL domains to admin users")
        print("OPTION 2: Assign specific user's group domains to them")
        print("OPTION 3: Assign ALL unassigned domains to a specific user")
        print("="*50)
        
        choice = input("\nEnter option (1, 2, or 3): ").strip()
        
        if choice == "1":
            # Assign all domains to all admin users
            admin_users = [u for u in users if u["is_admin"]]
            if not admin_users:
                print("No admin users found.")
                return
            
            cur = db_execute(conn, "SELECT id FROM domains")
            all_domain_ids = [dict_row(r)["id"] for r in cur.fetchall()]
            
            for admin in admin_users:
                assigned = 0
                for domain_id in all_domain_ids:
                    try:
                        db_execute(conn, "INSERT INTO user_domains (user_id, domain_id) VALUES (?, ?)", 
                                 (admin["id"], domain_id))
                        assigned += 1
                    except:
                        pass  # Already assigned
                print(f"✓ Assigned {assigned} domains to admin '{admin['username']}'")
        
        elif choice == "2":
            # Assign domains in user's groups to that user
            user_id = input("Enter user ID: ").strip()
            if not user_id.isdigit():
                print("Invalid user ID")
                return
            user_id = int(user_id)
            
            # Get user's groups
            cur = db_execute(conn, """
                SELECT DISTINCT group_id 
                FROM user_groups 
                WHERE user_id = ?
            """, (user_id,))
            group_ids = [dict_row(r)["group_id"] for r in cur.fetchall()]
            
            if not group_ids:
                print(f"User {user_id} has no groups assigned.")
                return
            
            # Get all domains in those groups
            placeholders = ",".join(["?"] * len(group_ids))
            cur = db_execute(conn, f"""
                SELECT id FROM domains 
                WHERE group_id IN ({placeholders})
            """, tuple(group_ids))
            domain_ids = [dict_row(r)["id"] for r in cur.fetchall()]
            
            assigned = 0
            for domain_id in domain_ids:
                try:
                    db_execute(conn, "INSERT INTO user_domains (user_id, domain_id) VALUES (?, ?)", 
                             (user_id, domain_id))
                    assigned += 1
                except:
                    pass  # Already assigned
            
            print(f"✓ Assigned {assigned} domains to user {user_id}")
        
        elif choice == "3":
            # Assign all unassigned domains to a specific user
            user_id = input("Enter user ID: ").strip()
            if not user_id.isdigit():
                print("Invalid user ID")
                return
            user_id = int(user_id)
            
            # Get all domains not assigned to this user
            cur = db_execute(conn, """
                SELECT d.id 
                FROM domains d
                WHERE d.id NOT IN (
                    SELECT domain_id FROM user_domains WHERE user_id = ?
                )
            """, (user_id,))
            domain_ids = [dict_row(r)["id"] for r in cur.fetchall()]
            
            if not domain_ids:
                print(f"All domains are already assigned to user {user_id}")
                return
            
            print(f"\nFound {len(domain_ids)} unassigned domains.")
            confirm = input(f"Assign all {len(domain_ids)} domains to user {user_id}? (yes/no): ").strip().lower()
            
            if confirm == "yes":
                assigned = 0
                for domain_id in domain_ids:
                    try:
                        db_execute(conn, "INSERT INTO user_domains (user_id, domain_id) VALUES (?, ?)", 
                                 (user_id, domain_id))
                        assigned += 1
                    except:
                        pass  # Already assigned
                
                print(f"✓ Assigned {assigned} domains to user {user_id}")
            else:
                print("Cancelled.")
        
        else:
            print("Invalid option")
            return
    
    print("\n✓ Done!")

if __name__ == "__main__":
    main()
