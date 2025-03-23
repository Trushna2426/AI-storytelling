import sqlite3

DB_PATH = "story_database.db"

def add_narrative_column():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get the table info for user_progress
    cursor.execute("PRAGMA table_info(user_progress)")
    columns = cursor.fetchall()
    
    # Extract column names from the returned info
    column_names = [col[1] for col in columns]
    
    # Check if 'narrative' column exists
    if 'narrative' not in column_names:
        try:
            cursor.execute("ALTER TABLE user_progress ADD COLUMN narrative TEXT")
            conn.commit()
            print("✅ 'narrative' column added successfully.")
        except sqlite3.OperationalError as e:
            print(f"⚠️ Could not add column: {e}")
    else:
        print("ℹ️ 'narrative' column already exists.")
        
    conn.close()

if __name__ == "__main__":
    add_narrative_column()
