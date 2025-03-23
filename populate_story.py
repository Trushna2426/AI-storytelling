import sqlite3

def create_database():
    conn = sqlite3.connect("story_database.db")
    cursor = conn.cursor()

    # Create stories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prompt TEXT NOT NULL,
        choice_1 TEXT NOT NULL,
        choice_2 TEXT NOT NULL,
        choice_3 TEXT NOT NULL,
        outcome_1 TEXT NOT NULL,
        outcome_2 TEXT NOT NULL,
        outcome_3 TEXT NOT NULL
    )
    ''')

    # Create user progress table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_progress (
        user_id TEXT PRIMARY KEY,
        current_story_id INTEGER,
        narrative TEXT
    )
    ''')

    # Sample story prompts with choices
    sample_stories = [
        ("You find an ancient book in a library.", 
         "Open the book.", "Give it to the librarian.", "Ignore it.",
         "The book glows, revealing a hidden map.",
         "The librarian warns you about the book's dark magic.",
         "You leave it, but later, a shadowy figure takes it."),
        
        ("You discover a hidden cave while hiking.", 
         "Enter the cave.", "Take a picture and leave.", "Call for help.",
         "Inside, you find glowing crystals that hum with energy.",
         "Your picture captures a mysterious silhouette in the darkness.",
         "Rescuers find old carvings of an unknown civilization.")
    ]

    # Insert sample stories into the database
    for story in sample_stories:
        cursor.execute('''
        INSERT INTO stories (prompt, choice_1, choice_2, choice_3, outcome_1, outcome_2, outcome_3)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', story)

    conn.commit()
    conn.close()
    print("📚 Database created and populated successfully!")

if __name__ == "__main__":
    create_database()
