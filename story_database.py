import sqlite3

DB_PATH = "Dataset/story_database.db"

def get_story(story_id):
    """Retrieve a story prompt and choices from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM stories WHERE story_id = ?", (story_id,))
    story = cursor.fetchone()
    conn.close()
    
    if story:
        return {
            "story_id": story[1],
            "prompt": story[2],
            "choices": [
                {"text": story[3], "next_story_id": story[6]},
                {"text": story[4], "next_story_id": story[7]},
                {"text": story[5], "next_story_id": story[8]}
            ]
        }
    return None
