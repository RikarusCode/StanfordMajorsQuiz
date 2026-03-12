"""
Utility script to (re)build `data/questions.json` from another source.

This is a stub; adapt it to your actual pipeline (e.g. from CSV, Google Sheet, etc.).
"""

from __future__ import annotations

from pathlib import Path
import json


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def main() -> None:
    """
    Stub implementation that just rewrites `questions.json` with a single example.
    Replace this with your real build process.
    """
    questions = [
        {
            "id": "q1",
            "text": "Do you enjoy solving abstract, logical problems?",
            "type": "likert",
            "options": ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"],
        }
    ]

    out_path = DATA_DIR / "questions.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(questions)} questions to {out_path}")


if __name__ == "__main__":
    main()

