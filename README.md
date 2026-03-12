# Stanford Major Quiz

This project is intended to host a "Stanford major quiz" application that helps users discover suitable majors based on their answers to a series of questions.

## Project Structure

- `app.py` — main entrypoint for running the quiz application.
- `requirements.txt` — Python dependencies.
- `data/` — JSON data files for majors and questions.
  - `majors.json`
  - `questions.json`
- `src/` — core logic for the quiz.
  - `inference.py`
  - `model.py`
  - `ui_helpers.py`
- `scripts/` — helper/utility scripts.
  - `build_questions.py`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running

```bash
python app.py
```

