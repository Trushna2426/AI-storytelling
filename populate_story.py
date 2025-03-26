import sqlite3

DB_PATH = "story_database.db"

def init_story_templates():
    """Pre-populate the database with predefined story choices based on themes."""
    stories = {
        "magic": [
            "A mysterious voice whispers a forgotten spell.",
            "The wizard finds an ancient rune with hidden power.",
            "The book glows, revealing a hidden world inside."
        ],
        "sci-fi": [
            "The spaceship's AI wakes up and speaks for the first time.",
            "A distress signal from deep space suddenly appears.",
            "The scientist accidentally activates an alien artifact."
        ],
        "mystery": [
            "A coded letter arrives at the detective’s desk.",
            "A hidden door creaks open in the abandoned mansion.",
            "The protagonist finds an old diary with missing pages."
        ]
    }

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM story_templates")  # Clear existing templates
    for theme, options in stories.items():
        for option in options:
            cursor.execute("INSERT INTO story_templates (theme, text) VALUES (?, ?)", (theme, option))

    conn.commit()
    conn.close()

init_story_templates()
print("Story templates initialized.")
