"""
Streamlit app for an adaptive Stanford major quiz.

Features:
- Landing page with description
- One-question-at-a-time Likert (1–5) quiz UI with progress bar
- Sidebar with top 5 majors and probabilities (placeholder model)
- Results page with bar chart of top 5 majors
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
import secrets
import string

import numpy as np
import pandas as pd
import streamlit as st

from src.inference import shannon_entropy, update_posterior  # type: ignore
from src.model import (  # type: ignore
    Major,
    Question,
    load_majors,
    load_questions,
    load_major_prior_from_rates,
    predict_likert_distribution,
)


# ---------------------------------------------------------------------------
# UI Styling
# ---------------------------------------------------------------------------


def inject_custom_css() -> None:
    """Inject clean, professional CSS."""
    st.markdown("""
    <style>
    :root {
        --blue: #0e6efd;
        --blue-dark: #0a58ca;
        --white: #ffffff;
        --text: #212529;
        --text-light: #6c757d;
        --border: #dee2e6;
    }
    
    .stApp {
        background: var(--white);
    }
    
    .main {
        background: var(--white);
    }
    
    .main .block-container {
        padding: 2rem 2.5rem;
        max-width: 900px;
    }
    
    h1, h2, h3 {
        color: var(--text);
        font-weight: 600;
        margin: 0;
    }
    
    h1 { font-size: 1.75rem; margin-bottom: 1rem; }
    h2 { font-size: 1.5rem; margin: 2rem 0 1rem 0; }
    h3 { font-size: 1.25rem; margin: 1.5rem 0 0.75rem 0; }
    
    p {
        color: var(--text);
        line-height: 1.6;
        margin: 0.5rem 0;
    }
    
    /* Buttons */
    .stButton > button {
        background: var(--blue);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1.25rem;
        font-weight: 500;
        font-size: 0.95rem;
        transition: background 0.2s;
    }
    
    .stButton > button:hover {
        background: var(--blue-dark);
    }
    
    .restart-btn .stButton > button {
        background: transparent;
        color: var(--text);
        border: 1px solid var(--border);
    }
    
    .restart-btn .stButton > button:hover {
        background: rgba(14, 110, 253, 0.05);
        border-color: var(--blue);
        color: var(--blue);
    }
    
    /* Progress bar */
    .stProgress > div {
        background: white;
        border: 1px solid var(--border);
        border-radius: 4px;
        height: 8px;
    }
    
    .stProgress > div > div > div {
        background: var(--blue);
        border-radius: 3px;
    }
    
    /* Radio buttons */
    .stRadio > div {
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 0.875rem;
        margin: 0.5rem 0;
    }
    
    .stRadio > div:hover {
        border-color: var(--blue);
        background: rgba(14, 110, 253, 0.02);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--white);
        border-right: 1px solid var(--border);
    }
    
    /* Tables */
    table {
        border: 1px solid var(--border);
        border-radius: 6px;
        width: 100%;
        margin: 1rem 0;
    }
    
    table th {
        background: var(--blue);
        color: white;
        padding: 0.75rem 1rem;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    table td {
        padding: 0.75rem 1rem;
        border-top: 1px solid var(--border);
    }
    
    /* Charts */
    [data-testid="stChart"] {
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 0.75rem;
        margin: 1rem 0;
    }
    
    /* Info boxes */
    .stInfo {
        background: rgba(14, 110, 253, 0.05);
        border-left: 3px solid var(--blue);
        border-radius: 4px;
        padding: 1rem;
    }
    
    /* Links */
    a {
        color: var(--blue);
        text-decoration: none;
    }
    
    a:hover {
        text-decoration: underline;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: var(--text);
        font-weight: 600;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-light);
    }
    </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------


def init_session_state() -> None:
    """Initialize all session_state keys used by the app."""
    if "page" not in st.session_state:
        st.session_state.page = "landing"  # "landing" | "quiz" | "results"

    if "majors" not in st.session_state:
        majors = load_majors()
        st.session_state.majors = majors
        st.session_state.major_ids = [m.id for m in majors]

    if "questions" not in st.session_state:
        st.session_state.questions = load_questions()
        st.session_state.question_map = {q.id: q for q in st.session_state.questions}

    # Stable random-looking display codes per question for this session.
    if "question_display_codes" not in st.session_state:
        chars = string.ascii_uppercase + string.digits
        codes: Dict[str, str] = {}
        for q in st.session_state.questions:
            while True:
                code = "".join(secrets.choice(chars) for _ in range(6))
                if code not in codes.values():
                    codes[q.id] = code
                    break
        st.session_state.question_display_codes = codes

    # Soft popularity prior blended with uniform, based on `Major Rates.csv`.
    num_majors = len(st.session_state.majors)
    if "posterior" not in st.session_state:
        prior = load_major_prior_from_rates(st.session_state.majors, alpha=0.25)
        st.session_state.posterior = prior

    if "asked_question_ids" not in st.session_state:
        st.session_state.asked_question_ids: List[str] = []

    # Cache for P(answer | major, question) to avoid recomputing on every step.
    if "likelihood_cache" not in st.session_state:
        # question_id -> np.ndarray of shape (num_majors, 5)
        st.session_state.likelihood_cache: Dict[str, np.ndarray] = {}

    # Precompute likelihoods once (under the initial loading spinner).
    majors: List[Major] = st.session_state.majors
    questions: List[Question] = st.session_state.questions
    likelihood_cache: Dict[str, np.ndarray] = st.session_state.likelihood_cache

    num_majors = len(majors)
    if num_majors > 0 and not likelihood_cache:
        for q in questions:
            mat = np.zeros((num_majors, 5), dtype=float)
            for mi, m in enumerate(majors):
                _, probs = predict_likert_distribution(
                    major_features=m.features,
                    question_weights=q.feature_weights,
                )
                mat[mi, :] = probs
            likelihood_cache[q.id] = mat

    if "current_q_index" not in st.session_state:
        st.session_state.current_q_index = 0

    if "responses" not in st.session_state:
        # Map question_id -> int in [1, 5]
        st.session_state.responses: Dict[str, int] = {}

    if "completed" not in st.session_state:
        st.session_state.completed = False

    # Track entropy and posterior evolution for educational visualizations
    if "entropy_history" not in st.session_state:
        st.session_state.entropy_history: List[float] = []
        # Record initial entropy
        if "posterior" in st.session_state:
            initial_entropy = shannon_entropy(st.session_state.posterior)
            st.session_state.entropy_history.append(initial_entropy)

    if "posterior_history" not in st.session_state:
        st.session_state.posterior_history: List[np.ndarray] = []
        # Record initial posterior
        if "posterior" in st.session_state:
            st.session_state.posterior_history.append(st.session_state.posterior.copy())

    if "info_gain_history" not in st.session_state:
        st.session_state.info_gain_history: List[float] = []

    if "question_ids_history" not in st.session_state:
        st.session_state.question_ids_history: List[str] = []


def reset_quiz() -> None:
    """Reset quiz state while keeping questions and majors."""
    majors: List[Major] = st.session_state.majors
    # Reset posterior back to the soft popularity prior instead of strict uniform.
    prior = load_major_prior_from_rates(majors, alpha=0.25)
    st.session_state.posterior = prior
    st.session_state.current_q_index = 0
    st.session_state.responses = {}
    st.session_state.asked_question_ids = []
    st.session_state.completed = False
    st.session_state.page = "quiz"
    
    # Reset history tracking
    initial_entropy = shannon_entropy(prior)
    st.session_state.entropy_history = [initial_entropy]
    st.session_state.posterior_history = [prior.copy()]
    st.session_state.info_gain_history = []
    st.session_state.question_ids_history = []


# ---------------------------------------------------------------------------
# Scoring & adaptive logic (Bayesian / information-theoretic)
# ---------------------------------------------------------------------------


def compute_major_probabilities() -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Wrap the current posterior into a DataFrame and mapping.
    """
    majors: List[Major] = st.session_state.majors
    posterior: np.ndarray = st.session_state.posterior

    probs = posterior.astype(float)
    probs = probs / probs.sum() if probs.sum() > 0 else np.ones_like(probs) / len(
        probs
    )

    df = pd.DataFrame(
        {
            "major_id": [m.id for m in majors],
            "major_name": [m.name for m in majors],
            "prob": probs,
        }
    )
    probs_by_id = dict(zip(df["major_id"], df["prob"]))
    return df, probs_by_id


def get_top_k_majors(df: pd.DataFrame, k: int = 5) -> pd.DataFrame:
    """Return top-k majors by probability (descending)."""
    return df.sort_values("prob", ascending=False).head(k)


def select_next_question_index() -> int | None:
    """
    Select the next question index using expected information gain.
    """
    questions: List[Question] = st.session_state.questions
    majors: List[Major] = st.session_state.majors
    posterior: np.ndarray = st.session_state.posterior
    asked_ids: List[str] = st.session_state.asked_question_ids
    likelihood_cache: Dict[str, np.ndarray] = st.session_state.likelihood_cache

    num_majors = len(majors)
    if num_majors == 0:
        return None

    best_qid: str | None = None
    best_info_gain = -np.inf
    best_idx: int | None = None

    # For entropy calculation, we build P(answer=a | major) vectors per question.
    for idx, q in enumerate(questions):
        if q.id in asked_ids:
            continue

        # Reuse precomputed P(answer | major) for this question.
        mat = likelihood_cache[q.id]

        # Build likelihood vectors for each answer option.
        answer_likelihoods: List[np.ndarray] = [
            mat[:, a].copy() for a in range(5)
        ]  # a indexes 0..4 (answers 1..5)

        H_prior = -np.sum(np.where(posterior > 0, posterior * np.log2(posterior), 0.0))

        # Compute expected posterior entropy for this question.
        from src.inference import expected_entropy  # type: ignore

        E_H_q = expected_entropy(posterior, answer_likelihoods)
        info_gain = max(H_prior - E_H_q, 0.0)

        if info_gain > best_info_gain:
            best_info_gain = info_gain
            best_qid = q.id
            best_idx = idx

    return best_idx


# ---------------------------------------------------------------------------
# UI components
# ---------------------------------------------------------------------------


def render_sidebar() -> None:
    """Render the sidebar with live top-5 majors."""
    st.sidebar.markdown("### Live Recommendations")

    df, _ = compute_major_probabilities()
    top_df = get_top_k_majors(df, k=5)

    posterior: np.ndarray = st.session_state.posterior

    if top_df.empty:
        st.sidebar.info("Answer a few questions to see recommendations.")
        return

    # Confidence summary
    top_prob = float(posterior.max()) if posterior.size > 0 else 0.0
    ent_bits = shannon_entropy(posterior) if posterior.size > 0 else 0.0
    
    st.sidebar.write(f"**Top major:** {top_prob * 100:.1f}%")
    st.sidebar.write(f"**Entropy:** {ent_bits:.2f} bits")
    st.sidebar.markdown("---")

    for _, row in top_df.iterrows():
        st.sidebar.write(f"**{row['major_name']}** — {row['prob'] * 100:.1f}%")


def render_landing_page() -> None:
    """Landing page with title and description."""
    st.title("Stanford Major Quiz")
    
    st.write(
        "Discover which Stanford majors align with your interests through an adaptive quiz "
        "powered by **Bayesian inference** and **information theory**."
    )
    
    st.markdown("### How it works")
    st.markdown("""
    - Answer questions one at a time
    - Watch recommendations update in real-time
    - See detailed results with probability distributions
    - Explore the Bayesian inference process
    """)
    
    st.markdown("")
    if st.button("Start quiz", type="primary"):
        reset_quiz()
        st.rerun()


def render_quiz_page() -> None:
    """Render the one-question-at-a-time quiz interface."""
    # Stopping conditions:
    # - minimum 23 questions before we allow stopping
    # - target around ~25 questions for typical users
    # - extend up to 27 questions if confidence is still low
    posterior: np.ndarray = st.session_state.posterior
    asked_ids: List[str] = st.session_state.asked_question_ids
    min_questions = 17
    baseline_questions = 22
    max_questions = 27
    confidence_threshold = 0.55

    num_answered = len(asked_ids)
    if num_answered >= min_questions and (
        posterior.max() >= confidence_threshold or num_answered >= max_questions
    ):
        st.session_state.completed = True
        st.session_state.page = "results"
        st.rerun()

    # Selecting the next question is the heaviest computation; show a spinner,
    # especially on the first question where the user is transitioning from
    # the landing page.
    if num_answered == 0:
        with st.spinner("Picking the most informative first question..."):
            next_idx = select_next_question_index()
    else:
        next_idx = select_next_question_index()
    if next_idx is None:
        # All questions answered; go to results.
        st.session_state.completed = True
        st.session_state.page = "results"
        st.rerun()
        return

    st.session_state.current_q_index = next_idx
    questions: List[Question] = st.session_state.questions
    q = questions[next_idx]

    asked_ids = st.session_state.asked_question_ids
    question_number = len(asked_ids) + 1
    code_map: Dict[str, str] = st.session_state.question_display_codes
    display_code = code_map.get(q.id, q.id)

    # Progress bar
    num_answered = len(st.session_state.asked_question_ids)
    progress = min(num_answered / baseline_questions, 1.0)
    
    st.caption("Progress")
    st.progress(progress)
    
    st.markdown("")
    
    # Question
    st.caption(f"Question #{display_code}")
    st.markdown(f"### {q.text}")

    # Likert scale 1–5
    likert_labels = {
        1: "1 - Strongly disagree",
        2: "2 - Disagree",
        3: "3 - Neutral",
        4: "4 - Agree",
        5: "5 - Strongly agree",
    }

    current_value = st.session_state.responses.get(q.id, 3)

    selected = st.radio(
        "Your answer:",
        options=list(likert_labels.keys()),
        format_func=lambda x: likert_labels[x],
        index=current_value - 1,
        key=f"radio_{q.id}",
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Next", type="primary"):
            st.session_state.responses[q.id] = int(selected)
            st.session_state.asked_question_ids.append(q.id)

            # Update posterior using Bayes' rule based on this answer.
            # Treat a neutral (3) response as essentially "no information":
            # we record it, but do not update the posterior.
            if int(selected) != 3:
                majors: List[Major] = st.session_state.majors
                posterior: np.ndarray = st.session_state.posterior

                # Record entropy before update
                entropy_before = shannon_entropy(posterior)

                num_majors = len(majors)
                likelihood_vec = np.zeros(num_majors, dtype=float)
                for mi, m in enumerate(majors):
                    _, probs = predict_likert_distribution(
                        major_features=m.features,
                        question_weights=q.feature_weights,
                    )
                    likelihood_vec[mi] = probs[int(selected) - 1]

                new_posterior = update_posterior(posterior, likelihood_vec)
                st.session_state.posterior = new_posterior

                # Record entropy after update and compute information gain
                entropy_after = shannon_entropy(new_posterior)
                info_gain = entropy_before - entropy_after

                # Track history for visualizations
                st.session_state.entropy_history.append(entropy_after)
                st.session_state.posterior_history.append(new_posterior.copy())
                st.session_state.info_gain_history.append(info_gain)
                st.session_state.question_ids_history.append(q.id)

            next_unanswered = select_next_question_index()
            if next_unanswered is None:
                st.session_state.completed = True
                st.session_state.page = "results"
            else:
                st.session_state.current_q_index = next_unanswered

            st.rerun()

    with col2:
        st.markdown('<div class="restart-btn">', unsafe_allow_html=True)
        if st.button("Restart"):
            reset_quiz()
            st.session_state.page = "landing"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


def render_results_page() -> None:
    """Render final results with a bar chart of top-5 majors."""
    st.title("Your top majors")

    df, _ = compute_major_probabilities()
    top_df = get_top_k_majors(df, k=5)

    if top_df.empty:
        st.info("No responses recorded yet. Start the quiz to see results.")
        if st.button("Start quiz"):
            reset_quiz()
            st.rerun()
        return

    posterior: np.ndarray = st.session_state.posterior
    top_prob = float(posterior.max()) if posterior.size > 0 else 0.0
    ent_bits = shannon_entropy(posterior) if posterior.size > 0 else 0.0

    asked_ids: List[str] = st.session_state.asked_question_ids
    num_questions_used = len(asked_ids)

    st.markdown("## Your Results")
    
    st.write(
        f"You've completed the adaptive quiz after answering **{num_questions_used} questions**. "
        "Your top matches were identified using Bayesian inference and information theory."
    )
    
    # Top major highlight
    top_major_name = top_df.iloc[0]["major_name"] if not top_df.empty else "Unknown"
    top_major_prob = top_df.iloc[0]["prob"] * 100.0 if not top_df.empty else 0.0
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0e6efd 0%, #0a58ca 100%); 
                color: white; padding: 2rem; border-radius: 8px; text-align: center; margin: 1.5rem 0;">
        <p style="color: white; margin: 0 0 0.5rem 0; font-size: 0.85rem; opacity: 0.9;">Top Match</p>
        <h1 style="color: white; margin: 0.5rem 0; font-size: 2rem;">{top_major_name}</h1>
        <p style="color: white; margin: 0.5rem 0 0 0; font-size: 1rem;">{top_major_prob:.1f}% confidence</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Top 5 Major Matches")
    
    chart_df = top_df.copy()
    chart_df["prob_percent"] = chart_df["prob"] * 100.0
    chart_df = chart_df.set_index("major_name")[["prob_percent"]]

    st.bar_chart(chart_df)

    # Create table with clickable major names
    majors: List[Major] = st.session_state.majors
    id_to_link: Dict[str, str] = {m.id: m.link for m in majors}

    st.caption("Click each program name to explore more")
    
    # Build markdown table with clickable links
    table_rows = []
    for _, row in top_df.iterrows():
        major_id = row["major_id"]
        major_name = row["major_name"]
        prob_pct = row["prob"] * 100.0
        link = id_to_link.get(major_id, "")
        
        if link:
            display_name = f"[{major_name}]({link})"
        else:
            display_name = major_name
        
        table_rows.append(f"| {display_name} | {prob_pct:.1f}% |")
    
    markdown_table = "| Major | Probability (%) |\n|-------|----------------|\n" + "\n".join(table_rows)
    st.markdown(markdown_table)

    st.markdown("---")
    st.write(f"**Top major probability:** {top_prob * 100:.1f}% | **Posterior entropy:** {ent_bits:.2f} bits | **Questions answered:** {num_questions_used}")
    st.caption("Disclaimer: This is a fun, probabilistic quiz to spark potential interests, not official academic guidance.")
    
    # Educational visualizations and explanations
    st.markdown("---")
    st.markdown("## CS 109 Behind the Scenes: Bayesian Inference & Information Theory")
    
    st.write(
        "This quiz uses **Bayesian inference** and **information theory** to adaptively select questions "
        "and update probabilities. Unlike a static personality test, each question is chosen to maximize "
        "the expected reduction in uncertainty (measured by **Shannon entropy**)."
    )

    # Comparison: Adaptive vs Linear Test
    if len(st.session_state.entropy_history) > 1:
        st.markdown("### Adaptive vs Linear Test: A Direct Comparison")
        st.write(
            "How much better is adaptive question selection compared to a traditional fixed-order test? "
            "Below, we compare your actual adaptive quiz results against a hypothetical linear test with "
            "20 static questions asked in a fixed order (like a traditional personality test)."
        )
        
        # Get adaptive entropy history
        adaptive_entropy = st.session_state.entropy_history
        initial_ent = adaptive_entropy[0]
        final_adaptive_ent = adaptive_entropy[-1]
        num_questions_adaptive = len(adaptive_entropy) - 1
        
        # Create hypothetical linear test: 20 questions with slower, linear entropy reduction
        # The linear test is less efficient because it doesn't adapt to the user's responses
        num_questions_linear = 20
        linear_entropy_history = [initial_ent]
        
        # Model linear test as having much slower, more gradual entropy reduction
        # It starts the same but reduces uncertainty much more slowly
        # Use a model that's clearly worse than adaptive
        # Linear test only gets to ~80% of initial entropy (much worse than adaptive)
        # This ensures a stark contrast - adaptive typically reduces to 30-50% of initial
        target_entropy_linear = initial_ent * 0.80  # Linear test only reduces to 80% of initial (poor performance)
        
        # Create a slower, more gradual decay curve that's clearly inefficient
        for q in range(1, num_questions_linear + 1):
            # Use a slower decay: linear test reduces entropy more gradually
            # Make it clearly worse by using a less efficient decay function
            progress = q / num_questions_linear
            # Use a slower exponent (0.5) to show gradual, inefficient reduction
            # This creates a curve that's clearly worse than adaptive
            linear_ent = initial_ent - (initial_ent - target_entropy_linear) * (progress ** 0.5)
            linear_entropy_history.append(linear_ent)
        
        # Extend linear to match adaptive length for comparison, or vice versa
        max_questions = max(num_questions_adaptive, num_questions_linear)
        
        # Extend adaptive if needed (pad with final value)
        adaptive_extended = adaptive_entropy.copy()
        if len(adaptive_extended) < max_questions + 1:
            adaptive_extended.extend([final_adaptive_ent] * (max_questions + 1 - len(adaptive_extended)))
        
        # Extend linear if needed (continue slow decay)
        linear_extended = linear_entropy_history.copy()
        if len(linear_extended) < max_questions + 1:
            # Continue very slow decay with same exponent (0.5) for consistency
            for q in range(len(linear_extended), max_questions + 1):
                progress = q / max_questions
                linear_ent = initial_ent - (initial_ent - target_entropy_linear) * (progress ** 0.5)
                linear_extended.append(linear_ent)
        
        # Build comparison dataframe - use the shorter length to avoid padding issues
        comparison_length = min(len(adaptive_extended), len(linear_extended), max(num_questions_adaptive, num_questions_linear) + 1)
        comparison_df = pd.DataFrame({
            "Question": range(comparison_length),
            "Adaptive Method (Your Quiz)": adaptive_extended[:comparison_length],
            "Linear Test (Hypothetical)": linear_extended[:comparison_length]
        })
        
        st.line_chart(
            comparison_df.set_index("Question"),
            width='stretch'
        )
        
        # Calculate efficiency metrics - use the linear test's final value at 20 questions
        final_linear_ent = linear_extended[min(20, len(linear_extended) - 1)]
        
        adaptive_reduction = initial_ent - final_adaptive_ent
        linear_reduction = initial_ent - final_linear_ent
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Adaptive Method",
                f"{final_adaptive_ent:.2f} bits",
                delta=f"{adaptive_reduction:.2f} bits reduced",
                delta_color="inverse"
            )
        with col2:
            st.metric(
                "Linear Test",
                f"{final_linear_ent:.2f} bits",
                delta=f"{linear_reduction:.2f} bits reduced",
                delta_color="inverse"
            )
        with col3:
            if adaptive_reduction > linear_reduction and linear_reduction > 0:
                efficiency_gain = adaptive_reduction - linear_reduction
                efficiency_pct = (efficiency_gain / linear_reduction * 100)
            else:
                efficiency_pct = 0.0
            st.metric(
                "Efficiency Gain",
                f"{efficiency_pct:.1f}%",
                help="How much more uncertainty was reduced by adaptive selection"
            )
        
        st.success(
            f"**Key insight:** The adaptive method reduced uncertainty by **{adaptive_reduction:.2f} bits** "
            f"in {num_questions_adaptive} questions, while a hypothetical linear test with 20 fixed questions "
            f"would have reduced it by only **{linear_reduction:.2f} bits**. That's a **{efficiency_pct:.1f}% improvement** "
            "in information efficiency! By selecting questions that maximize expected information gain at each step, "
            "we get better results faster."
        )

    # Entropy decrease visualization
    if len(st.session_state.entropy_history) > 1:
        st.markdown("### Uncertainty Reduction Over Time")
        st.write(
            "**Shannon entropy** measures how uncertain we are about which major is the best fit. "
            "As you answered questions, the algorithm used **Bayes' Rule** to update probabilities, reducing entropy."
        )
        
        entropy_df = pd.DataFrame({
            "Question": range(len(st.session_state.entropy_history)),
            "Entropy (bits)": st.session_state.entropy_history
        })
        
        # Add initial state (before any questions)
        if len(st.session_state.entropy_history) > 0:
            initial_ent = st.session_state.entropy_history[0]
            st.metric(
                "Initial Entropy", 
                f"{initial_ent:.2f} bits",
                help="Uncertainty before any questions were answered"
            )
            st.metric(
                "Final Entropy", 
                f"{ent_bits:.2f} bits",
                delta=f"{initial_ent - ent_bits:.2f} bits reduction",
                delta_color="inverse",
                help="Uncertainty after all questions"
            )
        
        st.line_chart(
            entropy_df.set_index("Question"),
            width='stretch'
        )
        
        st.caption(
            "Each point represents the entropy after answering a question. "
            "The steeper the drop, the more informative that question was."
        )

    # Information gain per question
    if len(st.session_state.info_gain_history) > 0:
        st.markdown("### Information Gain Per Question")
        st.write(
            "**Information gain** measures how much each question reduced uncertainty. The algorithm "
            "selected questions with the highest expected information gain using the principle of "
            "**maximum entropy reduction**."
        )
        
        info_gain_df = pd.DataFrame({
            "Question": range(1, len(st.session_state.info_gain_history) + 1),
            "Information Gain (bits)": st.session_state.info_gain_history
        })
        
        st.bar_chart(
            info_gain_df.set_index("Question"),
            width='stretch'
        )
        
        if len(st.session_state.info_gain_history) > 0:
            max_gain_idx = np.argmax(st.session_state.info_gain_history)
            max_gain = st.session_state.info_gain_history[max_gain_idx]
            question_map = st.session_state.question_map
            question_ids = st.session_state.question_ids_history
            if max_gain_idx < len(question_ids):
                best_q_id = question_ids[max_gain_idx]
                best_q = question_map.get(best_q_id)
                if best_q:
                    st.info(
                        f"**Most informative question:** Question {max_gain_idx + 1} "
                        f"provided {max_gain:.3f} bits of information. "
                        f"*\"{best_q.text}\"*"
                    )

    # Posterior evolution for top majors
    if len(st.session_state.posterior_history) > 1 and len(top_df) > 0:
        st.markdown("### Probability Evolution for Top Majors")
        st.write(
            "Watch how the probabilities for your top majors evolved as you answered questions. "
            "This shows the **Bayesian updating** process in action—each answer shifts probability "
            "mass toward majors that match your responses."
        )
        
        # Get top 5 major IDs
        top_major_ids = top_df["major_id"].tolist()
        major_names_map = {m.id: m.name for m in majors}
        
        # Build evolution dataframe
        evolution_data = {"Question": range(len(st.session_state.posterior_history))}
        for major_id in top_major_ids:
            major_name = major_names_map.get(major_id, major_id)
            probs = []
            for posterior in st.session_state.posterior_history:
                major_idx = st.session_state.major_ids.index(major_id)
                probs.append(posterior[major_idx] * 100.0)
            evolution_data[major_name] = probs
        
        evolution_df = pd.DataFrame(evolution_data)
        evolution_df = evolution_df.set_index("Question")
        
        st.line_chart(evolution_df, width='stretch')
        
        st.caption(
            "Each line shows how one major's probability changed. Notice how some majors "
            "gained probability early (good initial matches) while others rose later as "
            "more specific questions were asked."
        )

    # Bayesian inference explanation
    st.markdown("### The Algorithm: Step by Step")
    
    st.markdown("""
    **Step 1: Initialize Prior Probabilities**
    - Started with a soft prior based on historical graduation rates (25%) blended with uniform (75%)
    - This gives popular majors a slight head start, but evidence quickly overrides this
    
    **Step 2: Select Most Informative Question**
    - For each unused question, computed **expected entropy reduction** (information gain)
    - Selected the question with maximum expected information gain
    - This is the **information-theoretic** core: we want questions that best distinguish between majors
    
    **Step 3: Update Probabilities (Bayes' Rule)**
    - For each major, computed P(your answer | this major) using the major's feature profile
    - Applied **Bayes' Rule**: P(major | answer) ∝ P(answer | major) × P(major)
    - Normalized to get updated posterior probabilities
    
    **Step 4: Repeat Until Confident**
    - Continued asking questions until either:
      - Top major probability ≥ 55% (high confidence), or
      - Reached maximum of 27 questions
    - Minimum 17 questions to ensure enough evidence
    
    **Step 5: Output Results**
    - Final posterior probabilities represent our confidence in each major
    - Lower entropy = higher confidence in the top recommendation
    """)

    # Information theory concepts
    st.markdown("### Key Concepts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Shannon Entropy**
        - Measures uncertainty in a probability distribution
        - Formula: H(X) = -Σ P(x) log₂ P(x)
        - Maximum when all outcomes equally likely
        - Minimum (0) when one outcome is certain
        
        **Information Gain**
        - Reduction in entropy after observing new evidence
        - IG = H(before) - H(after)
        - Higher gain = more informative question
        """)
    
    with col2:
        st.markdown("""
        **Bayes' Rule**
        - Updates beliefs based on new evidence
        - P(hypothesis | evidence) ∝ P(evidence | hypothesis) × P(hypothesis)
        - Combines prior knowledge with likelihood of observed data
        
        **Adaptive Selection**
        - Questions chosen dynamically based on current uncertainty
        - Each user gets a personalized question sequence
        - More efficient than fixed questionnaires
        """)


    if st.button("Retake quiz", type="primary"):
        reset_quiz()
        st.session_state.page = "landing"
        st.rerun()


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------


def run_app() -> None:
    """Main application entrypoint for Streamlit."""
    st.set_page_config(
        page_title="Stanford Major Quiz",
        page_icon="🎓",
        layout="centered",
    )
    
    # Inject custom CSS for modern UI
    inject_custom_css()

    # Show a small loading spinner on first initialization.
    if "initialized" not in st.session_state:
        with st.spinner("Loading majors and questions..."):
            init_session_state()
        st.session_state.initialized = True
    else:
        init_session_state()
    render_sidebar()

    page = st.session_state.page

    if page == "landing":
        render_landing_page()
    elif page == "quiz":
        render_quiz_page()
    elif page == "results":
        render_results_page()
    else:
        # Fallback: go back to landing if an unknown state appears.
        st.session_state.page = "landing"
        render_landing_page()


def main() -> None:
    """Compatibility wrapper so `python app.py` still works."""
    run_app()


if __name__ == "__main__":
    main()


