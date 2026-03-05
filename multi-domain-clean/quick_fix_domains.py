"""
Quick fix: Assign all existing domains to a specific user
"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from db import get_connection, execute as db_execute, dict_row

def main():
    print("=== Quick Domain Assignment Fix ===\n")
    
    with get_connection() as conn:
        # Get all users
        cur = db_execute(conn, "SELECT id, username, is_admin FROM users ORDER BY id")
        users = [dict_row(r) for r in cur.fetchall()]
        
        print("Available users:")
        for u in users:
            admin_label = " (ADMIN)" if u["is_admin"] else ""
            
            # Count their current domains
            cur = db_execute(conn, "SELECT COUNT(*) as cnt FROM user_domains WHERE user_id = ?", (u["id"],))
            domain_count = dict_row(cur.fetchone())["cnt"]
            
            print(f"  {u['id']}: {u['username']}{admin_label} - currently has {domain_count} domains")
        
        user_id = input("\nEnter user ID to assign ALL domains to: ").strip()
        if not user_id.isdigit():
            print("Invalid user ID")
            return
        user_id = int(user_id)
        
        # Get all domains
        cur = db_execute(conn, "SELECT id, domain_url FROM domains")
        all_domains = [dict_row(r) for r in cur.fetchall()]
        
        print(f"\nFound {len(all_domains)} total domains in database")
        
        assigned = 0
        skipped = 0
        for domain in all_domains:
            try:
                db_execute(conn, "INSERT INTO user_domains (user_id, domain_id) VALUES (?, ?)", 
                         (user_id, domain["id"]))
                assigned += 1
                print(f"  ✓ Assigned: {domain['domain_url']}")
            except:
                skipped += 1
                print(f"  - Already assigned: {domain['domain_url']}")
        
        print(f"\n✓ Done! Assigned {assigned} domains, skipped {skipped} (already assigned)")

if __name__ == "__main__":
    main()
