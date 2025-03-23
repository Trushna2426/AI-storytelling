from flask import Flask, render_template, request, session, redirect, url_for
import os
import uuid
import sqlite3
from transformers import pipeline, logging as hf_logging

# Suppress extra warnings from transformers
hf_logging.set_verbosity_error()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure random secret key

# Load GPT-Neo-125M model for generating choices
MODEL_NAME = "distilgpt2"
generator = pipeline("text-generation", model=MODEL_NAME,device=0)

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

def generate_story(prompt):
    """
    Generate a continuation of the story.
    In this implementation, we don't override the narrative; we use AI only to generate plot-based choices.
    """
    response = generator(
        prompt,
        max_new_tokens=20,
        num_return_sequences=1,
        temperature=0.8,
        top_p=0.9,
        pad_token_id=generator.tokenizer.eos_token_id
    )
    text = response[0]["generated_text"].strip()
    # For clarity, limit to the first 3 sentences.
    sentences = text.split(". ")
    if len(sentences) > 3:
        text = ". ".join(sentences[:3]) + "."
    return text

def generate_choices(narrative):
    """
    Generate 3 unique, context-based choices for continuing the story.
    The AI is prompted to provide one distinct, creative plot continuation option each time.
    """
    base_prompt = narrative + "\nProvide one creative continuation:"
    choices = set() 
    attempts = 0
    while len(choices) < 3 and attempts < 10:
        response = generator(
            base_prompt,
            max_new_tokens=40,
            num_return_sequences=1,
            temperature=0.9,
            top_p=0.95,
            pad_token_id=generator.tokenizer.eos_token_id
        )
        choice_text = response[0]["generated_text"].strip()
        # Use only the first sentence as the choice
        choice_sentence = choice_text.split(".")[0].strip()
        if len(choice_sentence) > 10:
            choices.add(choice_sentence)
        attempts += 1
    if len(choices) < 3:
        choices.update(["Investigate the mystery", "Confront the challenge", "Search for clues"])
    return list(choices)[:3]

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Home page: User enters an initial prompt.
    The initial narrative is simply the user's prompt.
    """
    if request.method == "POST":
        user_prompt = request.form.get("user_prompt")
        if not user_prompt:
            return "Error: No prompt entered!", 400
        
        user_id = str(uuid.uuid4())
        session["user_id"] = user_id
        
        # The narrative initially is exactly the user's prompt.
        narrative = user_prompt
        # Generate 3 unique, context-based choices based on the initial prompt.
        choices = generate_choices(narrative)
        
        save_narrative(user_id, narrative)
        session["narrative"] = narrative
        
        return render_template("story.html", narrative=narrative, choices=choices, user_id=user_id)
    
    return render_template("index.html")

@app.route("/story", methods=["POST"])
def continue_story():
    """
    Continue the story: The user's selected choice is appended to the narrative,
    and new, unique choices are generated based on the updated narrative.
    """
    user_id = session.get("user_id")
    if not user_id:
        return "Error: No active story session!", 400
    
    selected_choice = request.form.get("choice")
    if not selected_choice:
        return "Error: No choice selected!", 400
    
    previous_narrative = session.get("narrative", "")
    # Append the selected choice to the existing narrative.
    new_narrative = previous_narrative + " " + selected_choice
    new_choices = generate_choices(new_narrative)
    
    save_narrative(user_id, new_narrative)
    session["narrative"] = new_narrative
    
    return render_template("story.html", narrative=new_narrative, choices=new_choices, user_id=user_id)

@app.route("/ending")
def ending():
    """
    Ending page: Display the final narrative.
    """
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("index"))
    
    narrative = get_narrative(user_id)
    return render_template("ending.html", narrative=narrative)

if __name__ == "__main__":
    app.run(debug=True)
