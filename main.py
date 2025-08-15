from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
score = 0
highscore = 0

class Quiz(BaseModel):
    question: str
    options: list[str]
    rightanswer: str

while True:
    prompt = """
    Create a multiple-choice quiz question about general knowledge.
    Return the question, exactly four answer options, and the correct answer.
    Format the response as a JSON object with the fields: 'question', 'options', and 'rightanswer'.
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": Quiz.model_json_schema()
        }
    )

    response = Quiz.model_validate(response.parsed)

    question = response.question
    options = response.options
    answer = response.rightanswer

    
    if len(options) == 4:
        print(f"Question: {question}")

        print(f"A: {options[0]}\tB: {options[1]}")
        print(f"C: {options[2]}\tD: {options[3]}")
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
                if score > highscore:
                    print(f"New high score: {score}!")
                    highscore = score
            else:
                print(f"Wrong! The correct answer is: {answer}")
            break
        else:
            print("Invalid input. Please enter A, B, C, or D.")