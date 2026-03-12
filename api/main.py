"""
FastAPI backend for the Stanford Major Quiz.

This API wraps the existing inference logic and provides REST endpoints
for quiz initialization, answering questions, and retrieving results.
"""

from __future__ import annotations

import secrets
from typing import Dict, List, Optional
import uuid

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

from src.inference import (
    shannon_entropy,
    update_posterior,
    select_next_question,
)
from src.model import (
    Major,
    Question,
    load_majors,
    load_questions,
    load_major_prior_from_rates,
    predict_likert_distribution,
)

app = FastAPI(
    title="Stanford Major Quiz API",
    description="Adaptive Bayesian inference engine for major recommendations",
    version="1.0.0",
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    # CORS: allow the deployed Vercel frontend + local dev.
    # Note: explicit origins are the most reliable across hosting/proxy setups.
    allow_origins=[
        "https://stanford-majors-quiz.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    # Also allow Vercel preview deployments if you use them:
    # - https://<anything>.vercel.app
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Some hosting/proxy layers can mishandle CORS preflight. Provide an explicit
# catch-all OPTIONS handler so browsers always receive a 200 for preflight.
@app.options("/{full_path:path}")
async def cors_preflight(full_path: str) -> Response:
    return Response(status_code=200)

# Load data once at startup
MAJORS: List[Major] = []
QUESTIONS: List[Question] = []
LIKELIHOOD_CACHE: Dict[str, List[np.ndarray]] = {}


@app.on_event("startup")
async def startup_event():
    """Load majors, questions, and precompute likelihoods on startup."""
    global MAJORS, QUESTIONS, LIKELIHOOD_CACHE

    MAJORS = load_majors()
    QUESTIONS = load_questions()

    # Precompute likelihoods for all question-answer pairs
    num_majors = len(MAJORS)
    for question in QUESTIONS:
        answer_likelihoods = []
        for answer in range(1, 6):  # Likert scale 1-5
            likelihood_vec = np.zeros(num_majors, dtype=float)
            for mi, major in enumerate(MAJORS):
                _, probs = predict_likert_distribution(
                    major_features=major.features,
                    question_weights=question.feature_weights,
                )
                likelihood_vec[mi] = probs[answer - 1]
            answer_likelihoods.append(likelihood_vec)
        LIKELIHOOD_CACHE[question.id] = answer_likelihoods

    print(f"Loaded {len(MAJORS)} majors and {len(QUESTIONS)} questions")


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------


class StartQuizResponse(BaseModel):
    """Response for starting a quiz session."""

    session_id: str
    question_id: str
    question_text: str
    question_number: str = Field(..., description="Random 6-character question ID")
    top_majors: List[Dict[str, float | str]] = Field(
        ..., description="Top 5 majors with probabilities"
    )


class AnswerRequest(BaseModel):
    """Request body for submitting an answer."""

    session_id: str
    question_id: str
    answer: int = Field(..., ge=1, le=5, description="Likert scale answer (1-5)")


class AnswerResponse(BaseModel):
    """Response after submitting an answer."""

    question_id: Optional[str] = Field(
        None, description="Next question ID, or None if quiz is complete"
    )
    question_text: Optional[str] = None
    question_number: Optional[str] = None
    top_majors: List[Dict[str, float | str]]
    entropy: float
    top_probability: float
    questions_asked: int
    is_complete: bool


class ResultsResponse(BaseModel):
    """Response for quiz results."""

    session_id: str
    majors: List[Dict[str, float | str]]
    major_order: List[str] = Field(
        ...,
        description="Major IDs corresponding to indices in posterior_history rows.",
    )
    entropy: float
    top_probability: float
    questions_asked: int
    entropy_history: List[float]
    info_gain_history: List[float]
    posterior_history: List[List[float]] = Field(
        ...,
        description="Posterior probabilities over majors after each step, aligned to major_order.",
    )
    question_number_history: List[str] = Field(
        ...,
        description="Random display codes for each asked question (same order as steps).",
    )


# ---------------------------------------------------------------------------
# Session Management
# ---------------------------------------------------------------------------


class QuizSession:
    """Represents an active quiz session."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.posterior = load_major_prior_from_rates(MAJORS, alpha=0.25)
        self.responses: Dict[str, int] = {}
        self.asked_question_ids: set[str] = set()
        self.entropy_history: List[float] = [shannon_entropy(self.posterior)]
        self.info_gain_history: List[float] = []
        self.question_ids_history: List[str] = []
        # Keep a full posterior history for visualizations on the frontend.
        # Includes the initial prior as the first element.
        self.posterior_history: List[np.ndarray] = [self.posterior.copy()]

    def get_available_questions(self) -> Dict[str, List[np.ndarray]]:
        """Get likelihoods for questions not yet asked."""
        available = {}
        for qid in LIKELIHOOD_CACHE:
            if qid not in self.asked_question_ids:
                available[qid] = LIKELIHOOD_CACHE[qid]
        return available

    def get_top_majors(self, n: int = 5) -> List[Dict[str, float | str]]:
        """Get top N majors with their probabilities."""
        indices = np.argsort(self.posterior)[::-1][:n]
        top = []
        for idx in indices:
            top.append(
                {
                    "id": MAJORS[idx].id,
                    "name": MAJORS[idx].name,
                    "link": MAJORS[idx].link,
                    "probability": float(self.posterior[idx]),
                }
            )
        return top


# In-memory session storage (use Redis/database in production)
sessions: Dict[str, QuizSession] = {}


def generate_question_number() -> str:
    """Generate a random 6-character alphanumeric question ID."""
    return secrets.token_hex(3).upper()


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------


@app.post("/start", response_model=StartQuizResponse)
async def start_quiz() -> StartQuizResponse:
    """
    Initialize a new quiz session and return the first question.

    Returns:
        Session ID, first question, and initial top majors.
    """
    # Create new session
    session_id = str(uuid.uuid4())
    session = QuizSession(session_id)
    sessions[session_id] = session

    # Select first question
    available = session.get_available_questions()
    if not available:
        raise HTTPException(status_code=500, detail="No questions available")

    best_qid, _ = select_next_question(session.posterior, available)
    if best_qid is None:
        raise HTTPException(status_code=500, detail="Failed to select question")

    question = next(q for q in QUESTIONS if q.id == best_qid)
    question_number = generate_question_number()
    session.asked_question_ids.add(best_qid)
    session.question_ids_history.append(question_number)

    return StartQuizResponse(
        session_id=session_id,
        question_id=question.id,
        question_text=question.text,
        question_number=question_number,
        top_majors=session.get_top_majors(),
    )


@app.post("/answer", response_model=AnswerResponse)
async def submit_answer(request: AnswerRequest) -> AnswerResponse:
    """
    Submit an answer to a question and get the next question.

    Args:
        request: Session ID, question ID, and answer (1-5).

    Returns:
        Next question (if any), updated top majors, and quiz status.
    """
    # Get session
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Validate question was asked
    if request.question_id not in session.asked_question_ids:
        raise HTTPException(
            status_code=400, detail="Question was not asked in this session"
        )

    # Skip neutral answers (answer = 3) - no posterior update
    if request.answer != 3:
        # Get likelihood for this answer
        answer_likelihoods = LIKELIHOOD_CACHE[request.question_id]
        likelihood_vec = answer_likelihoods[request.answer - 1]

        # Update posterior
        session.posterior = update_posterior(session.posterior, likelihood_vec)

    # Record response
    session.responses[request.question_id] = request.answer

    # Update entropy history
    current_entropy = shannon_entropy(session.posterior)
    session.entropy_history.append(current_entropy)
    session.posterior_history.append(session.posterior.copy())

    # Check if quiz should continue
    top_prob = float(np.max(session.posterior))
    questions_asked = len(session.responses)
    min_questions = 17
    max_questions = 27
    confidence_threshold = 0.55

    is_complete = False
    if questions_asked >= min_questions:
        if top_prob >= confidence_threshold or questions_asked >= max_questions:
            is_complete = True

    # Select next question if not complete
    next_question_id = None
    next_question_text = None
    next_question_number = None

    if not is_complete:
        available = session.get_available_questions()
        if available:
            # Select next question (this computes info gain internally)
            H_before = shannon_entropy(session.posterior)
            best_qid, info_gains = select_next_question(
                session.posterior, available
            )
            if best_qid:
                question = next(q for q in QUESTIONS if q.id == best_qid)
                next_question_id = question.id
                next_question_text = question.text
                next_question_number = generate_question_number()

                session.asked_question_ids.add(best_qid)
                session.question_ids_history.append(next_question_number)

                # Record info gain for the selected question
                # Info gain = entropy before - expected entropy after
                info_gain = info_gains.get(best_qid, 0.0)
                session.info_gain_history.append(max(0.0, info_gain))
            else:
                # Failed to select a question (shouldn't happen, but handle gracefully)
                is_complete = True
        else:
            # No more questions available
            is_complete = True

    return AnswerResponse(
        question_id=next_question_id,
        question_text=next_question_text,
        question_number=next_question_number,
        top_majors=session.get_top_majors(),
        entropy=current_entropy,
        top_probability=top_prob,
        questions_asked=questions_asked,
        is_complete=is_complete,
    )


@app.get("/results/{session_id}", response_model=ResultsResponse)
async def get_results(session_id: str) -> ResultsResponse:
    """
    Get final results for a completed quiz session.

    Args:
        session_id: The session ID.

    Returns:
        Final major recommendations and quiz statistics.
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get all majors sorted by probability
    indices = np.argsort(session.posterior)[::-1]
    majors = []
    for idx in indices:
        majors.append(
            {
                "id": MAJORS[idx].id,
                "name": MAJORS[idx].name,
                "link": MAJORS[idx].link,
                "probability": float(session.posterior[idx]),
            }
        )

    major_order = [m.id for m in MAJORS]
    posterior_history = [
        [float(x) for x in row.tolist()] for row in session.posterior_history
    ]

    return ResultsResponse(
        session_id=session_id,
        majors=majors,
        major_order=major_order,
        entropy=float(shannon_entropy(session.posterior)),
        top_probability=float(np.max(session.posterior)),
        questions_asked=len(session.responses),
        entropy_history=session.entropy_history,
        info_gain_history=session.info_gain_history,
        posterior_history=posterior_history,
        question_number_history=session.question_ids_history,
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "majors_loaded": len(MAJORS), "questions_loaded": len(QUESTIONS)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
