# Quizle

Quizle is an infinite quiz game powered by the Google Gemini API. It generates unique, increasingly difficult multiple-choice questions across a wide range of topics. Scores are tracked in a leaderboard.

## Features

- AI-generated quiz questions with 4 answer options
- Difficulty increases with each question
- Wide variety of topics and question styles
- Score tracking and leaderboard (tierlist)
- Persistent leaderboard stored in `tierlist.json`

## Requirements

- Python 3.10+

## Setup

1. Clone the repository.
2. Install dependencies:

```sh
pip install google-genai python-dotenv
```

3. Create a `.env` file with your Google API key:

```bash
GOOGLE_API_KEY=your_api_key_here
```

4. Run the game:

```sh
python main.py
```

## Leaderboard

Scores are saved in `tierlist.json`. The top 10 scores are displayed and updated automatically.

## TODO's

- website

## License

MIT License
