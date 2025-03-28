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

def save_narrative(user_id, new_text):
    """Append only new narrative text without duplicating choices."""
    existing_narrative = get_narrative(user_id)
    if not existing_narrative:
        updated_narrative = new_text
    else:
        updated_narrative = existing_narrative + " " + new_text  # Append only new part

    # Save the updated narrative
    with open(f"narratives/{user_id}.txt", "w") as file:
        file.write(updated_narrative)

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
    """Generate three unique, logical next steps in the story based on user input."""
    base_prompt = f"Continue the story logically:\n{narrative}\n\nGenerate three unique and logical next steps:"
    
    # Rule-based predefined templates for better choices
    templates = [
        "1️⃣ [Character] decides to {action}, leading to {consequence}.",
        "2️⃣ A sudden {event} happens, forcing [Character] to {reaction}.",
        "3️⃣ As [Character] moves forward, they encounter {obstacle}, which must be overcome."
    ]
    
    # Ensure diverse, rule-based choices
    choices = set()
    attempts = 0
    
    while len(choices) < 3 and attempts < 5:
        response = generator(
            base_prompt,
            max_new_tokens=40,
            num_return_sequences=1,
            temperature=0.8,
            top_p=0.9,
            pad_token_id=generator.tokenizer.eos_token_id
        )
        
        # Extract only one logical step from the response
        choice_text = response[0]["generated_text"].strip()
        choice_sentence = choice_text.split(".")[0].strip()
        
        # Ensure choices are unique and not just repeating the input prompt
        if choice_sentence not in choices and 10 < len(choice_sentence) < 100:
            choices.add(choice_sentence)
        
        attempts += 1

    return list(choices)[:3]  # Ensure exactly 3 choices

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
