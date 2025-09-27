from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json

load_dotenv()
model = "gemini-2.5-flash-lite"
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
chat = client.chats.create(model=model)
score = 0
highscore = 0

class Quiz(BaseModel):
    question: str
    options: list[str]
    rightanswer: str

print("Welcome to Quizle!")

name = input("Enter your nickname: ")

if os.path.exists("tierlist.json"):
    with open("tierlist.json", "r") as f:
        tierlist = json.load(f)

    if not tierlist:
        tierlist = []
else:
    with open("tierlist.json", "w") as f:
        json.dump([], f)

    tierlist = []

while True: 
    prompt = """
    Generate a single multiple-choice quiz question about general knowledge.
    Requirements:
    - Exactly 4 answer options and indicate the correct answer.
    - The first question should be easy, and the difficulty should increase with each subsequent question.
    - Vary topics widely: history, science, arts, geography, pop culture, literature, technology, etc.
    - Vary the question style: direct, scenario-based, riddle-like, humorous, tricky, or puzzle-style.
    - Make each question unique in topic, style, and wording.
    - Avoid overly common or repetitive questions.
    - Format the response as a JSON object with 'question', 'options', 'rightanswer'.
    """
    game_over = False
    response = chat.send_message(
        prompt,
        config={
            "temperature": 1.5,
            "top_p": 0.95,
            "response_mime_type": "application/json",
            "response_schema": Quiz.model_json_schema()
        }
    )

    response = Quiz.model_validate(response.parsed)

    question = response.question
    options = response.options
    answer = response.rightanswer

    print("")

    if len(options) == 4:
        max_len = max(len(opt) for opt in options) + 2  # +2 für etwas Abstand
        print(f"Question: {question}")
        print(f"A: {options[0].ljust(max_len)} B: {options[1].ljust(max_len)}")
        print(f"C: {options[2].ljust(max_len)} D: {options[3].ljust(max_len)}")
    else:
        continue

    while True:
        user_answer = input("Enter your answer (A, B, C, D): ").strip().upper()
        if user_answer in ["A", "B", "C", "D"]:
            if user_answer == "A":
                selected_option = options[0]
            elif user_answer == "B":
                selected_option = options[1]
            elif user_answer == "C":
                selected_option = options[2]
            else:
                selected_option = options[3]

            if selected_option == answer:
                print("Correct!")
                score += 1
                print(f"Your score: {score}")
                if score > highscore:
                    print(f"New high score: {score}!")
                    highscore = score  
            else:
                print(f"Wrong! The correct answer is: {answer}")
                if len(tierlist) < 10:
                    tierlist.append({"name": name, "score": score})
                    with open("tierlist.json", "w") as f:
                        tierlist = sorted(tierlist, key=lambda x: x["score"], reverse=True)
                        json.dump(tierlist, f, indent=4)
                else:
                    if highscore > tierlist[-1]["score"]:
                        tierlist[-1] = {"name": name, "score": highscore}
                        tierlist = sorted(tierlist, key=lambda x: x["score"], reverse=True)
                        with open("tierlist.json", "w") as f:
                            json.dump(tierlist, f, indent=4)
                score = 0
                game_over = True
                chat = client.chats.create(model=model)
            break
        else:
            print("Invalid input. Please enter A, B, C, or D.")

    if len(chat._comprehensive_history) >= 4:
        pop_i = len(chat._comprehensive_history) - 2
        chat._comprehensive_history.pop(pop_i)
        chat._curated_history.pop(pop_i)

    if game_over:
        while True:
            replay = input("Do you want to play again? (Y/n): ").strip().lower()
            if replay == "y" or not replay:
                break
            elif replay == "n":
                print("Thanks for playing!")
                exit()
            else:
                print("Invalid input. Please enter Y or n.")
