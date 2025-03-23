import sqlite3
import random
import json

DB_PATH = "story_database.db"

def get_story_by_id(story_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT story_id, title, prompt FROM stories WHERE story_id = ?", (story_id,))
        story = cursor.fetchone()
        conn.close()
        return story
    except Exception as e:
        print(f"Error fetching story by ID: {e}")
        return None

def get_choices_for_story(story_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT choice_id, choice_text, outcome, next_story_id FROM choices WHERE story_id = ?", (story_id,))
        choices = cursor.fetchall()
        conn.close()
        return choices
    except Exception as e:
        print(f"Error fetching choices: {e}")
        return []

def update_user_progress(user_id, story_id, narrative):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_progress (user_id, current_story_id, narrative) 
            VALUES (?, ?, ?)
        """, (user_id, story_id, json.dumps(narrative)))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating user progress: {e}")

def get_user_progress(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT current_story_id, narrative FROM user_progress WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            story_id, narrative_json = result
            narrative = json.loads(narrative_json) if narrative_json else []
            return story_id, narrative
        return None, []
    except Exception as e:
        print(f"Error retrieving user progress: {e}")
        return None, []

def choose_random_story():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT story_id FROM stories ORDER BY RANDOM() LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0]
        return None
    except Exception as e:
        print(f"Error choosing random story: {e}")
        return None

def interactive_story():
    user_id = input("Enter your User ID: ").strip()
    if not user_id:
        print("❌ User ID cannot be empty.")
        return

    # Load previous progress if available, otherwise choose a random starting story.
    current_story_id, narrative = get_user_progress(user_id)
    if current_story_id:
        print("\n🔄 Resuming your story...\n")
    else:
        current_story_id = choose_random_story()
        if not current_story_id:
            print("⚠️ No stories available in the database!")
            return
        narrative = []
        update_user_progress(user_id, current_story_id, narrative)

    # Main interactive loop
    while True:
        story = get_story_by_id(current_story_id)
        if not story:
            print("⚠️ Story not found! Ending session.")
            break

        story_id, title, prompt = story
        print("\n----------------------------------")
        print(f"Story: {title}")
        print(prompt)

        # Append the current prompt to the narrative.
        narrative.append(f"Story: {title}\n{prompt}")

        # Fetch and display choices
        choices = get_choices_for_story(story_id)
        if not choices:
            print("🔚 No choices available. The story ends here.")
            break

        print("\n🔹 Choose an option:")
        for idx, (choice_id, choice_text, outcome, next_story_id) in enumerate(choices, start=1):
            print(f"{idx}. {choice_text} -> {outcome}")

        # Get valid user input
        try:
            choice_input = int(input("Enter your choice number: "))
            if choice_input < 1 or choice_input > len(choices):
                print("❌ Invalid choice number. Please try again.")
                continue
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
            continue

        selected_choice = choices[choice_input - 1]
        # Instead of printing a separate confirmation, directly append outcome to narrative.
        outcome = selected_choice[2]
        print(f"\n{outcome}\n")
        narrative[-1] += f" -> {outcome}"  # Append outcome directly to the previous prompt narrative.

        next_story_id = selected_choice[3]
        if next_story_id is None:
            print("🎬 The story has reached an ending. Thank you for playing!")
            update_user_progress(user_id, None, narrative)
            print("\n----- Full Story Narrative -----\n")
            for entry in narrative:
                print(entry)
            break
        else:
            current_story_id = next_story_id
            update_user_progress(user_id, current_story_id, narrative)

if __name__ == "__main__":
    interactive_story()
