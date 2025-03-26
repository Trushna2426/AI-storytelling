import sqlite3

DB_PATH = "story_database.db"

def init_db():
    """Initialize database with tables for user stories and predefined choices."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            theme TEXT,
            narrative TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS story_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            theme TEXT,
            text TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

def save_narrative(user_id, theme, narrative):
    """Save or update the user's current story and theme."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO stories (user_id, theme, narrative) VALUES (?, ?, ?)", (user_id, theme, narrative))
    conn.commit()
    conn.close()

def get_narrative(user_id):
    """Retrieve the user's saved story."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT narrative FROM stories WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_choices_by_theme(theme):
    """Fetch predefined choices based on story theme."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM story_templates WHERE theme = ?", (theme,))
    choices = [row[0] for row in cursor.fetchall()]
    conn.close()
    return choices[:3]  # Return up to 3 choices
