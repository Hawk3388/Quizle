from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
import os
import json
from pydantic import BaseModel
from google import genai

load_dotenv()

# Flask App
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallbacksecret")

# Gemini Setup
model = "gemini-2.0-flash-lite"
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Global dict für aktive Spieler-Chats
active_chats = {}

chat = client.chats.create(model=model)

class Quiz(BaseModel):
    question: str
    options: list[str]
    rightanswer: str

# Leaderboard laden
if os.path.exists("tierlist.json"):
    with open("tierlist.json", "r") as f:
        leaderboard = json.load(f)
else:
    leaderboard = []

def save_leaderboard():
    with open("tierlist.json", "w") as f:
        json.dump(leaderboard, f, indent=4)

def get_question_from_chat(chat):
    prompt = """
    Generate a single multiple-choice quiz question about general knowledge.
    Requirements:
    - Exactly 4 answer options and indicate the correct answer.
    - Vary topics widely: history, science, arts, geography, pop culture, literature, technology, etc.
    - Vary the question style: direct, scenario-based, riddle-like, humorous, tricky, or puzzle-style.
    - Make each question unique in topic, style, and wording.
    - Avoid overly common or repetitive questions.
    - Format the response as a JSON object with 'question', 'options', 'rightanswer'.
    - Do not make duplicate questions.
    """

    response = chat.send_message(
        prompt,
        config={
            "temperature": 1.9,
            "top_p": 0.95,
            "response_mime_type": "application/json",
            "response_schema": Quiz.model_json_schema()
        }
    )
    return Quiz.model_validate(response.parsed)

@app.route("/", methods=["GET", "POST"])
def start():
    if request.method == "POST":
        name = request.form["name"]
        session["name"] = name
        session["score"] = 0
        return redirect(url_for("question"))
    return render_template("start.html")

@app.route("/question")
def question():
    player = session.get("name")
    if not player:
        return redirect(url_for("start"))
    
    if len(chat._comprehensive_history) >= 4:
        pop_i = len(chat._comprehensive_history) - 2
        chat._comprehensive_history.pop(pop_i)
        chat._curated_history.pop(pop_i)

    if len(chat._comprehensive_history) >= 500:
        over = len(chat._comprehensive_history) - 500
        for i in range(over):
            i += 1
            i *= -1
            chat._comprehensive_history.pop(i)
            chat._curated_history.pop(i)

    q = get_question_from_chat(chat)
    session["current_answer"] = q.rightanswer
    return render_template("question.html", q=q)

@app.route("/check", methods=["POST"])
def check():
    player = session.get("name")
    if not player:
        return redirect(url_for("start"))

    selected = request.form["option"]
    correct = session.get("current_answer")

    if selected == correct:
        session["score"] += 1
        return redirect(url_for("question"))
    else:
        # Score ins Leaderboard eintragen
        leaderboard.append({"name": player, "score": session["score"]})
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        if len(leaderboard) > 10:
            leaderboard.pop()  # nur Top 10
        save_leaderboard()
        return redirect(url_for("gameover"))

@app.route("/gameover")
def gameover():
    render = render_template("gameover.html", score=session.get("score", 0), leaderboard=leaderboard)
    name = session.get("name")
    session.clear()
    if name:
        session["name"] = name
        session["score"] = 0
    return render

@app.route("/leaderboard")
def show_leaderboard():
    return render_template("leaderboard.html", leaderboard=leaderboard)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
