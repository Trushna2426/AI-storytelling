from flask import Flask, render_template, request, session, redirect, url_for
import os
import uuid
import sqlite3
import random
from transformers import pipeline, logging as hf_logging

# Suppress extra warnings from transformers
hf_logging.set_verbosity_error()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure random secret key

# Load GPT2 model for generating choices
MODEL_NAME = "gpt2"
generator = pipeline("text-generation", model=MODEL_NAME, device=0)

# SQLite database file path
DB_PATH = "story_database.db"

def init_db():
    """Initialize the SQLite database with the required table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            narrative TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_narrative(user_id, narrative):
    """Save or update the narrative for a given user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO stories (user_id, narrative) VALUES (?, ?)", (user_id, narrative))
    conn.commit()
    conn.close()

def get_narrative(user_id):
    """Retrieve the narrative for a given user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT narrative FROM stories WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def filter_ai_response(response):
    """Clean AI-generated responses to remove vagueness or incomplete sentences."""
    if len(response.split()) < 10 or "something" in response.lower():
        return "The story takes an unexpected turn, but nothing clear happens."
    if response[-1] not in ".!?":
        response += "."
    return response

def enforce_theme_rules(theme, response):
    """Ensure AI-generated text aligns with the selected theme."""
    theme_rules = {
        "adventure": ["brave", "explore", "danger"],
        "mystery": ["clue", "detective", "hidden"],
        "sci-fi": ["robot", "alien", "future"],
        "horror": ["dark", "ghost", "fear"]
    }
    for word in theme_rules.get(theme, []):
        if word in response.lower():
            return response  # Valid response
    return "The story needs to follow the selected theme."

def generate_choices(narrative):
    """
    Generate 3 unique, context-based choices based on the evolving story.
    Ensures each choice continues the story logically.
    """
    base_prompt = narrative + "\nGenerate three unique and logical next steps in the story:"
    choices = set()
    
    while len(choices) < 3:
        response = generator(
            base_prompt,
            max_new_tokens=40,
            num_return_sequences=1,
            temperature=0.9,
            top_p=0.95,
            pad_token_id=generator.tokenizer.eos_token_id
        )
        choice_text = response[0]["generated_text"].strip()
        choice_sentence = choice_text.split(".")[0].strip()

        if len(choice_sentence) > 10:  
            choices.add(choice_sentence)  # Add only meaningful choices
    
    return list(choices)

def generate_summary(user_id):
    """
    Fetch the full story narrative for the user.
    This will be displayed as a summary.
    """
    narrative = get_narrative(user_id)
    return "📖 Your Story Summary:\n" + narrative if narrative else "No story yet!"


@app.route("/", methods=["GET", "POST"])
def index():
    """Home page: User enters an initial prompt."""
    if request.method == "POST":
        user_prompt = request.form.get("user_prompt")
        if not user_prompt:
            return "Error: No prompt entered!", 400
        user_id = str(uuid.uuid4())
        session["user_id"] = user_id
        narrative = user_prompt
        choices = generate_choices(narrative)
        save_narrative(user_id, narrative)
        session["narrative"] = narrative
        return render_template("story.html", narrative=narrative, choices=choices, user_id=user_id)
    return render_template("index.html")

@app.route("/story", methods=["POST"])
def continue_story():
    """Continue the story: Append the selected choice and generate new choices."""
    user_id = session.get("user_id")
    if not user_id:
        return "Error: No active story session!", 400
    selected_choice = request.form.get("choice")
    if not selected_choice:
        return "Error: No choice selected!", 400
    previous_narrative = session.get("narrative", "")
    new_narrative = previous_narrative + " " + selected_choice
    new_choices = generate_choices(new_narrative)
    save_narrative(user_id, new_narrative)
    session["narrative"] = new_narrative
    return render_template("story.html", narrative=new_narrative, choices=new_choices, user_id=user_id)

@app.route("/ending")
def ending():
    """Ending page: Display the final narrative."""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("index"))
    narrative = get_narrative(user_id)
    return render_template("ending.html", narrative=narrative)

if __name__ == "__main__":
    app.run(debug=True)
