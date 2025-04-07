from flask import Flask, render_template, request, session, redirect, url_for
import os
import uuid
import sqlite3
from transformers import pipeline, logging as hf_logging

hf_logging.set_verbosity_error()  # Suppress unnecessary warnings

app = Flask(__name__)
app.secret_key = os.urandom(24)  

# Load GPT-Neo model for generating choices
MODEL_NAME = "gpt2"
generator = pipeline("text-generation", model=MODEL_NAME)

DB_PATH = "story_database.db"

# Initialize database
def init_db():
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
    """Save or update the current story in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO stories (user_id, narrative) VALUES (?, ?)", (user_id, narrative))
    conn.commit()
    conn.close()

def get_narrative(user_id):
    """Retrieve the stored narrative for the given user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT narrative FROM stories WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def generate_choices(narrative):
    """Generate 3 unique, logical story continuations."""
    base_prompt = narrative + "\nWhat happens next?"
    choices = set()
    attempts = 0
    while len(choices) < 3 and attempts < 10:
        response = generator(
            base_prompt, max_new_tokens=40, num_return_sequences=1, temperature=0.9, top_p=0.95,
            pad_token_id=generator.tokenizer.eos_token_id
        )
        choice = response[0]["generated_text"].replace(base_prompt, "").strip().split(".")[0].strip()
        if len(choice) > 10:
            choices.add(choice)
        attempts += 1

    if len(choices) < 3:  # Fallback choices
        choices.update(["Investigate the mystery", "Confront the challenge", "Search for clues"])
    return list(choices)[:3]

@app.route("/", methods=["GET", "POST"])
def index():
    """User enters the initial story prompt."""
    if request.method == "POST":
        user_prompt = request.form.get("user_prompt")
        if not user_prompt:
            return "Error: No prompt entered!", 400
        
        user_id = str(uuid.uuid4())
        session["user_id"] = user_id

        # The narrative starts with the user's input
        narrative = user_prompt
        choices = generate_choices(narrative)

        save_narrative(user_id, narrative)
        session["narrative"] = narrative
        
        return render_template("story.html", narrative=narrative, choices=choices, user_id=user_id)
    
    return render_template("index.html")

@app.route("/story", methods=["POST"])
def continue_story():
    """Append user choice to the story and generate new choices."""
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
    """Display the final generated story."""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("index"))
    
    narrative = get_narrative(user_id)
    return render_template("ending.html", narrative=narrative)

if __name__ == "__main__":
    app.run(debug=True)
