"""
Helper functions for building a CLI or web UI for the quiz.
"""

from __future__ import annotations

from typing import Iterable

from .model import Question


def render_question_cli(question: Question) -> None:
    """
    Simple CLI renderer for a question.
    """
    print(f"\n{question.text}")
    if question.options:
        for idx, opt in enumerate(question.options, start=1):
            print(f"  {idx}. {opt}")


def parse_cli_response(question: Question, raw_input_value: str) -> int:
    """
    Convert a raw CLI response into a numeric score index (0-based).
    """
    try:
        choice = int(raw_input_value)
    except ValueError:
        raise ValueError("Please enter a number corresponding to your choice.")
    if not (1 <= choice <= len(question.options)):
        raise ValueError("Choice out of range.")
    return choice - 1


def summarize_recommendations(recommended_ids: Iterable[str]) -> str:
    """
    Return a human-readable summary string for recommended majors.
    """
    ids_list = list(recommended_ids)
    if not ids_list:
        return "No strong major recommendations based on your answers yet."
    return "Top recommended majors (by ID): " + ", ".join(ids_list)


__all__ = ["render_question_cli", "parse_cli_response", "summarize_recommendations"]

