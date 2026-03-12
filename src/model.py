"""
Data models and loading utilities for the Stanford major quiz.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Mapping, Tuple
import csv
import json

import numpy as np


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


@dataclass
class Major:
    """
    Representation of a Stanford major as loaded from `majors.json`.

    The JSON schema is:
        {
          "id": "computer_science",
          "name": "Computer Science",
          "link": "https://...",
          "features": { ... 22-feature schema ... }
        }
    """
    id: str
    name: str
    link: str
    features: Dict[str, float]


@dataclass
class Question:
    """
    Representation of a quiz question as loaded from `questions.json`.

    The JSON schema is:
        {
          "id": "q1",
          "text": "...",
          "feature_weights": { ... }
        }
    """
    id: str
    text: str
    feature_weights: Dict[str, float]


def load_majors(path: Path | None = None) -> List[Major]:
    """
    Load majors from `majors.json`.
    """
    path = path or (DATA_DIR / "majors.json")
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    majors: List[Major] = []
    for item in raw:
        majors.append(
            Major(
                id=item["id"],
                name=item["name"],
                link=item.get("link", ""),
                features=item.get("features", {}),
            )
        )
    return majors


def load_questions(path: Path | None = None) -> List[Question]:
    """
    Load questions from `questions.json`.
    """
    path = path or (DATA_DIR / "questions.json")
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    questions: List[Question] = []
    for item in raw:
        questions.append(
            Question(
                id=item["id"],
                text=item["text"],
                feature_weights=item.get("feature_weights", {}),
            )
        )
    return questions


def load_major_prior_from_rates(
    majors: List[Major],
    alpha: float = 0.25,
    rates_path: Path | None = None,
) -> np.ndarray:
    """
    Construct a soft prior over majors using graduation counts from
    `Major Rates.csv`, blended with a uniform prior.

    Args:
        majors: List of Major objects from `majors.json`.
        alpha: Blend weight in [0, 1]. 0 -> purely uniform, 1 -> purely
               popularity-based. We keep this modest (e.g., 0.25) so
               popularity nudges but does not dominate.
        rates_path: Optional override path for the CSV file. Defaults to
                    BASE_DIR / "Major Rates.csv".

    Returns:
        1D NumPy array of length len(majors) giving the prior over majors.
    """
    n = len(majors)
    if n == 0:
        return np.array([], dtype=float)

    uniform = np.full(n, 1.0 / n, dtype=float)

    path = rates_path or (BASE_DIR / "Major Rates.csv")
    if not path.exists():
        # Fall back to uniform if we don't have the rates file.
        return uniform

    # Load rates: Program name -> count
    name_to_count: Dict[str, float] = {}
    try:
        with path.open("r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 2:
                    continue
                program, count_str = row[0].strip(), row[1].strip()
                try:
                    count = float(count_str)
                except ValueError:
                    continue
                name_to_count[program] = max(count, 0.0)
    except Exception:
        return uniform

    if not name_to_count:
        return uniform

    counts = []
    # Fallback: mean of all counts for majors without a direct match.
    global_mean = float(np.mean(list(name_to_count.values())))

    # The CSV uses slightly different program names than Stanford's official
    # major names. For now we use exact name matching where possible and
    # fall back to the global mean otherwise.
    for m in majors:
        counts.append(name_to_count.get(m.name, global_mean))

    counts_arr = np.asarray(counts, dtype=float)
    if counts_arr.sum() <= 0:
        pop = uniform
    else:
        pop = counts_arr / counts_arr.sum()

    # Blend uniform and popularity priors.
    prior = (1.0 - alpha) * uniform + alpha * pop
    prior = prior / prior.sum()
    return prior


def predict_likert_distribution(
    major_features: Mapping[str, float],
    question_weights: Mapping[str, float],
    *,
    min_score: float = 1.0,
    max_score: float = 5.0,
    sigma: float = 0.9,
) -> Tuple[float, np.ndarray]:
    """
    Given a major's feature vector and a question's feature weights, predict
    a Likert-style response distribution over answers 1–5.

    The model is intentionally simple and interpretable:

    1. Normalize major feature values from the 1–5 scale to [0, 1].
    2. Compute a signed alignment score between the major and question:
         score = sum_k w_k * f_k / sum_k |w_k|
       where w_k are question feature weights and f_k are normalized features.
       Features not present in `major_features` default to a neutral value 0.5.
    3. Map the alignment score (roughly in [-1, 1]) to a mean Likert response
       μ in [min_score, max_score].
    4. Use a Gaussian-shaped distribution centered at μ over discrete answers
       {1, 2, 3, 4, 5} with standard deviation `sigma`, then normalize.

    Args:
        major_features: Mapping from feature name to value on the 1–5 scale.
        question_weights: Mapping from feature name to real-valued weight.
            Positive weights indicate that higher feature values increase the
            expected response; negative weights indicate the opposite.
        min_score: Minimum Likert score (normally 1.0).
        max_score: Maximum Likert score (normally 5.0).
        sigma: Standard deviation of the Gaussian over Likert points.
            Smaller values make the distribution more peaked around the mean.

    Returns:
        A tuple (mean_score, probs) where:
            - mean_score is the predicted mean response μ in [min_score, max_score].
            - probs is a length-5 NumPy array giving P(answer = 1..5).
    """
    # If a question has no weights, fall back to a uniform distribution.
    if not question_weights:
        probs = np.full(5, 1.0 / 5.0, dtype=float)
        return float((min_score + max_score) / 2.0), probs

    # Normalize major features from 1–5 to [0, 1].
    def _norm_feature(val: float) -> float:
        return (float(val) - 1.0) / 4.0

    neutral = 0.5  # neutral feature level in [0, 1]

    num = 0.0
    den = 0.0
    for feat, w in question_weights.items():
        v_raw = major_features.get(feat)
        v_norm = _norm_feature(v_raw) if v_raw is not None else neutral
        num += w * v_norm
        den += abs(w)

    if den == 0.0:
        # All weights are zero; treat as uninformative.
        probs = np.full(5, 1.0 / 5.0, dtype=float)
        return float((min_score + max_score) / 2.0), probs

    # Alignment score in roughly [-1, 1].
    alignment = num / den
    alignment = max(-1.0, min(1.0, alignment))

    # Map alignment to mean Likert score μ in [min_score, max_score].
    span = max_score - min_score
    mean_score = min_score + (alignment + 1.0) * (span / 2.0)

    # Gaussian over discrete answers 1..5.
    answers = np.arange(1, 6, dtype=float)
    var = max(sigma, 1e-3) ** 2
    logits = -((answers - mean_score) ** 2) / (2.0 * var)
    # Convert logits to probabilities in a numerically stable way.
    logits -= np.max(logits)
    exp_logits = np.exp(logits)
    probs = exp_logits / exp_logits.sum()

    return float(mean_score), probs


__all__ = [
    "Major",
    "Question",
    "load_majors",
    "load_questions",
    "predict_likert_distribution",
    "load_major_prior_from_rates",
]

