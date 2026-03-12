"""
Core Bayesian inference utilities for the adaptive Stanford major quiz.

This module is intentionally small, focused, and testable. It provides:

- normalize_probs     : turn an arbitrary non-negative vector into a probability
                        vector with safe handling of zeros / underflow.
- shannon_entropy     : compute Shannon entropy (in bits) of a probability
                        distribution.
- update_posterior    : Bayes-rule update for P(major | answers) using a
                        likelihood vector P(answer | major).
- expected_entropy    : expected posterior entropy of a question over all
                        answer choices.
- select_next_question: choose the next question that maximizes information
                        gain (entropy reduction).

Everything here operates on NumPy arrays and plain Python data structures, so
it can be unit tested in isolation from the Streamlit UI.
"""

from __future__ import annotations

from typing import Dict, Mapping, Sequence, Tuple

import numpy as np

ArrayLike = np.ndarray


# ---------------------------------------------------------------------------
# Basic probability utilities
# ---------------------------------------------------------------------------


def normalize_probs(x: ArrayLike, *, eps: float = 1e-12) -> ArrayLike:
    """
    Normalize a non-negative vector into a probability distribution.

    Args:
        x: 1D NumPy array of non-negative values.
        eps: Small constant to avoid division by zero if the sum is tiny.

    Returns:
        1D NumPy array of the same shape as `x` that sums to 1.0.
        If the input sum is 0 (or extremely small), this returns a uniform
        distribution.
    """
    x = np.asarray(x, dtype=float)
    if x.ndim != 1:
        raise ValueError("normalize_probs expects a 1D array.")

    total = float(x.sum())

    if total < eps:
        # All mass is zero or extremely small: fall back to uniform.
        n = x.size
        if n == 0:
            raise ValueError("normalize_probs received an empty vector.")
        return np.full(n, 1.0 / n, dtype=float)

    return x / total


def shannon_entropy(p: ArrayLike, *, base: float = 2.0, eps: float = 1e-12) -> float:
    """
    Compute Shannon entropy H(P) for a probability vector.

    Args:
        p: 1D probability vector that (approximately) sums to 1.
        base: Logarithm base; default is 2 (bits).
        eps: Small constant to avoid log(0). Probabilities below `eps` are
             treated as `eps` for numerical stability.

    Returns:
        Shannon entropy in the specified units (bits if base=2).
    """
    p = normalize_probs(p, eps=eps)  # Ensure valid distribution

    p_clipped = np.clip(p, eps, 1.0)
    log_p = np.log(p_clipped) / np.log(base)
    return float(-np.sum(p_clipped * log_p))


# ---------------------------------------------------------------------------
# Bayesian update
# ---------------------------------------------------------------------------


def update_posterior(
    prior: ArrayLike,
    likelihood: ArrayLike,
    *,  # force keyword-only for clarity
    eps: float = 1e-12,
) -> ArrayLike:
    """
    Update P(major) to P(major | answer) using Bayes' rule.

    Args:
        prior: 1D array of prior probabilities over majors.
        likelihood: 1D array of P(answer | major) for the chosen answer
                    (same shape as `prior`).
        eps: Small constant for numerical stability when normalizing.

    Returns:
        1D NumPy array representing the posterior distribution over majors.

    Notes:
        Posterior is proportional to prior * likelihood:
            posterior[i] ∝ prior[i] * likelihood[i]
        and then renormalized to sum to 1.
    """
    prior = np.asarray(prior, dtype=float)
    likelihood = np.asarray(likelihood, dtype=float)

    if prior.shape != likelihood.shape:
        raise ValueError("prior and likelihood must have the same shape.")
    if prior.ndim != 1:
        raise ValueError("prior and likelihood must be 1D arrays.")

    unnormalized = prior * likelihood
    return normalize_probs(unnormalized, eps=eps)


# ---------------------------------------------------------------------------
# Question selection via expected entropy / information gain
# ---------------------------------------------------------------------------


def expected_entropy(
    prior: ArrayLike,
    answer_likelihoods: Sequence[ArrayLike],
    *,  # force keyword-only args for readability
    eps: float = 1e-12,
) -> float:
    """
    Compute the expected posterior entropy for a single question.

    A question has multiple possible answers (e.g., 5-point Likert scale).
    For each *answer option* a, we assume we know the vector of
    likelihoods P(answer=a | major=i) over majors.

    For each answer option `a`:
        - Compute P(answer=a) = sum_i P(answer=a | major=i) * P(major=i)
        - Compute posterior P(major | answer=a) via Bayes' rule
        - Compute entropy H(P(major | answer=a))

    The expected entropy is:
        E[H] = sum_a P(answer=a) * H(P(major | answer=a))

    Args:
        prior: 1D array of current probabilities over majors.
        answer_likelihoods: Sequence of 1D arrays, one per answer option
                            (e.g., 5 for Likert 1–5). Each is
                            P(answer=a | major) over majors.
        eps: Numerical stability constant.

    Returns:
        Expected posterior entropy (in bits) after asking this question.
    """
    prior = normalize_probs(prior, eps=eps)
    num_majors = prior.size

    if num_majors == 0:
        raise ValueError("expected_entropy received an empty prior.")

    # Ensure all likelihood vectors are compatible.
    likelihoods = [np.asarray(l, dtype=float) for l in answer_likelihoods]
    for l in likelihoods:
        if l.shape != prior.shape:
            raise ValueError(
                "Each likelihood vector must have the same shape as prior."
            )

    expected_H = 0.0
    for likelihood in likelihoods:
        # P(answer=a) = sum_i P(a|i) * P(i)
        p_answer = float(np.dot(likelihood, prior))

        if p_answer < eps:
            # This answer is effectively impossible under the current model.
            # It contributes ~0 to the expectation.
            continue

        # Posterior given this answer option.
        posterior = update_posterior(prior, likelihood, eps=eps)
        H_post = shannon_entropy(posterior, base=2.0)

        expected_H += p_answer * H_post

    return float(expected_H)


def select_next_question(
    prior: ArrayLike,
    question_likelihoods: Mapping[str, Sequence[ArrayLike]],
    *,  # keyword-only
    eps: float = 1e-12,
) -> Tuple[str | None, Dict[str, float]]:
    """
    Select the question that maximizes expected information gain.

    Args:
        prior: 1D array of current probabilities over majors.
        question_likelihoods: Mapping from question_id to a sequence of
            likelihood vectors, one per answer option, for that question:

                question_likelihoods[qid][a] = P(answer=a | major)

            For a 5-point Likert question, the sequence length is 5.
        eps: Numerical stability constant.

    Returns:
        A pair (best_question_id, info_gain_by_question) where:
            - best_question_id is the ID of the question with the largest
              information gain (or None if `question_likelihoods` is empty).
            - info_gain_by_question is a dict mapping qid -> information gain
              (non-negative float, in bits).

    Notes:
        Information gain for question q is:

            IG(q) = H(prior) - E[H(posterior | q)]

        where E[H(·)] is computed by `expected_entropy`.
    """
    prior = normalize_probs(prior, eps=eps)
    H_prior = shannon_entropy(prior, base=2.0)

    if not question_likelihoods:
        return None, {}

    info_gain_by_q: Dict[str, float] = {}

    for qid, answer_likelihoods in question_likelihoods.items():
        E_H_q = expected_entropy(prior, answer_likelihoods, eps=eps)
        info_gain = max(H_prior - E_H_q, 0.0)  # clip tiny negatives
        info_gain_by_q[qid] = float(info_gain)

    # Choose question with maximum information gain.
    best_qid = max(info_gain_by_q, key=info_gain_by_q.get) if info_gain_by_q else None
    return best_qid, info_gain_by_q


__all__ = [
    "normalize_probs",
    "shannon_entropy",
    "update_posterior",
    "expected_entropy",
    "select_next_question",
]

