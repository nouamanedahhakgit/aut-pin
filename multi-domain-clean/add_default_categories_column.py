"""
Add default_categories column to user_api_keys table
"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from db import get_connection, execute as db_execute

def main():
    print("=== Adding default_categories column to user_api_keys table ===\n")
    
    with get_connection() as conn:
        try:
            # Check if column exists
            cur = db_execute(conn, "SHOW COLUMNS FROM user_api_keys LIKE 'default_categories'")
            if cur.fetchone():
                print("✓ Column 'default_categories' already exists")
                return
            
            # Add the column
            print("Adding column 'default_categories'...")
            db_execute(conn, "ALTER TABLE user_api_keys ADD COLUMN default_categories TEXT AFTER local_models")
            print("✓ Column added successfully!")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return
    
    print("\n✓ Migration complete!")

if __name__ == "__main__":
    main()
