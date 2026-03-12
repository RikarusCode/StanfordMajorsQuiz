## Stanford Major Quiz

An adaptive “Which Stanford major should I choose?” web app that uses **Bayesian inference** and **information theory** to recommend Stanford majors.  
Instead of a fixed personality quiz with vague outputs, this system dynamically chooses questions to **maximize information gain** and produces **probabilistic, Stanford-specific recommendations** with confidence scores and educational visualizations.

---

## Overview

This project is a full‑stack application built for exploration of Stanford majors:

- A **Next.js / React** frontend provides a polished, glassmorphism-inspired UI with:
  - Landing page explaining the methodology
  - One-question-at-a-time adaptive quiz
  - Rich results page with charts and explanations
- A **FastAPI** backend serves as the Bayesian inference engine:
  - Maintains a posterior distribution over majors
  - Selects the next question via expected entropy reduction
  - Tracks entropy, information gain, and probability evolution over time
- An original **Streamlit** app (`app.py`) is kept as a reference implementation and exploratory interface.

Under the hood, each Stanford major is represented as a feature vector over cognitive/disciplinary attributes, and each question is tagged with feature weights. The backend uses these to estimate how likely each major is to produce a given answer on a 1–5 Likert scale, then applies **Bayes’ Rule** after each response.

---

## Tech Stack

**Frontend**
- Next.js 16 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- Framer Motion (animations)
- Recharts (results visualizations)

**Backend**
- FastAPI
- Uvicorn
- NumPy
- Pandas

**Core Logic & Data**
- Python modules in `src/`:
  - `inference.py` — probability utilities, entropy, information gain, question selection
  - `model.py` — dataclasses, data loading, Likert likelihood model, popularity prior
- Data files in `data/`:
  - `majors.json` — Stanford majors + 22‑dimensional feature vectors
  - `questions.json` — question bank with feature weights
  - `Major Rates.csv` — graduation count data for popularity prior

**Legacy / Reference**
- Streamlit app (`app.py`) for the original UI and experimentation.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/stanford-major-quiz.git
cd stanford-major-quiz
```

### Backend (FastAPI)

Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS / Linux
```

Install backend dependencies:

```bash
cd api
pip install -r requirements.txt
cd ..
```

### Frontend (Next.js)

```bash
cd frontend
npm install
cd ..
```

### (Optional) Streamlit App

From the project root, using the same Python environment:

```bash
pip install -r requirements.txt
```

---

## Running the Project Locally

### Recommended: One‑shot scripts

From the project root:

#### Windows (PowerShell / CMD)

```bash
.\start.bat
```

This starts:
- FastAPI backend at `http://localhost:8000`
- Next.js frontend at `http://localhost:3000` (or `3001` if 3000 is taken)

#### Cross‑platform (Python)

```bash
python start.py
```

This will:
- Prefer `.venv\Scripts\python.exe` if present
- Start Uvicorn for the API
- Start `npm run dev` for the frontend

Press `Ctrl+C` in that terminal to stop both.

### Manual Start (for clarity)

**Backend**

```bash
cd api
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**

In a second terminal:

```bash
cd frontend
npm run dev
```

Then open `http://localhost:3000` (or the port shown) in your browser.

### Streamlit App Only (Legacy UI)

```bash
streamlit run app.py
```

---

## Project Structure

```text
stanford-major-quiz/
├── api/                    # FastAPI backend
│   ├── main.py             # API endpoints and session logic
│   ├── requirements.txt    # Backend dependencies
│   ├── run.bat / run.sh    # Helper scripts (Windows / *nix)
│   └── test_api.py         # Simple API test script
│
├── frontend/               # Next.js + React frontend
│   ├── app/
│   │   ├── layout.tsx      # Root layout
│   │   ├── page.tsx        # Landing page
│   │   ├── quiz/page.tsx   # Quiz flow
│   │   └── results/page.tsx# Results & explanations
│   ├── components/
│   │   ├── Button.tsx
│   │   ├── PageShell.tsx
│   │   ├── AnswerChoice.tsx
│   │   ├── TopResultsCard.tsx
│   │   ├── charts/
│   │   │   ├── EntropyChart.tsx
│   │   │   ├── InfoGainChart.tsx
│   │   │   └── TopMajorsEvolutionChart.tsx
│   │   └── index.ts        # Barrel exports
│   ├── lib/
│   │   └── api.ts          # Typed API client for FastAPI backend
│   ├── public/
│   │   └── class-logo-gen.png  # Class logo used across pages
│   ├── package.json
│   └── tailwind.config.ts
│
├── src/                    # Shared Python logic
│   ├── inference.py        # Entropy, information gain, question selection
│   └── model.py            # Dataclasses, data loading, likelihood model, popularity prior
│
├── data/
│   ├── majors.json         # 100 Stanford majors + 22-dim feature vectors
│   ├── questions.json      # 60+ calibrated Likert questions with feature weights
│   └── Major Rates.csv     # Graduation counts for popularity prior
│
├── app.py                  # Original Streamlit app (reference)
├── start.bat               # Windows: start backend + frontend
├── start.sh                # *nix: start backend + frontend
├── start.py                # Cross-platform Python launcher
├── README_START.md         # Quick start for local development
└── PROJECT_STATUS.md       # Internal project status / checklist
```

---

## Key Features

- **Stanford‑Specific Recommendations**
  - Models actual Stanford majors and interdisciplinary programs.
  - Uses major feature profiles (math, coding, lab, writing, policy, creativity, etc.).

- **Adaptive Question Selection**
  - Large bank of Likert‑scale questions.
  - Each next question is chosen to maximize **expected information gain**.
  - Results in shorter, more personalized quizzes.

- **Bayesian Inference Engine**
  - Maintains a probability distribution over majors.
  - Updates probabilities using **Bayes’ Rule** after each answer.
  - Integrates a **popularity prior** from graduation data (soft bias, quickly overridden by evidence).

- **Modern Frontend UI**
  - Dark gradient + glassmorphism design.
  - Smooth but performant animations (Framer Motion where it matters).
  - Responsive layout suitable for desktop and mobile.

- **Educational Results Page**
  - Top majors with probabilities and links to program pages.
  - Number of questions asked + entropy (uncertainty) at the end.
  - Charts showing:
    - Entropy reduction over time.
    - Information gain per question.
    - Probability evolution for top majors.
    - Comparison between adaptive vs hypothetical linear test.
  - Narrative explanation of Bayesian updating and information theory in plain language.

---

## Algorithm & System Explanation

### 1. Representing Majors and Questions

Each major is modeled as a vector over 22 interpretable features, e.g.:

- `mathematical_rigor`
- `computational_intensity`
- `experimental_lab_work`
- `human_behavior_focus`
- `policy_relevance`
- `creative_design`
- `ambiguity_tolerance`
- … and more.

Each feature is scored on a **1–5 scale** (1 = low, 5 = very high).  

Each question has a set of **feature weights** (positive/negative) describing what it probes, e.g.:

- “I enjoy using quantitative tools to understand social or economic behavior.”
  - High weight on `mathematical_rigor`, `statistical_reasoning`, `human_behavior_focus`, etc.

### 2. Likert Likelihood Model

For each `(major, question)` pair, the backend predicts a distribution over Likert answers 1–5:

1. Normalize major features from `[1, 5]` → `[0, 1]`.
2. Compute an alignment score between major and question:

   ```python
   score = sum_k w_k * f_k / sum_k |w_k|
   ```

   where:
   - `w_k` are question feature weights
   - `f_k` are normalized feature values

3. Map this alignment (≈ in `[-1, 1]`) to a mean Likert value `μ` in `[1, 5]`.
4. Place a Gaussian‑shaped distribution around `μ` over the discrete points `{1,2,3,4,5}`.

This yields `P(answer = a | major)` for `a = 1..5`.

### 3. Bayesian Updating

The system maintains a **posterior over majors**:

- Start with a prior `P(major)`:
  - Blend of:
    - Uniform over all majors.
    - Popularity distribution from `Major Rates.csv` (counts normalized).
- For each answer:
  - Look up `P(answer | major)` from the likelihood model.
  - Apply Bayes’ Rule:

    ```python
    posterior[i] ∝ prior[i] * likelihood[i]
    posterior = normalize(posterior)
    ```

  - Neutral answers (3) are treated as approximately non‑informative.

### 4. Measuring Uncertainty with Shannon Entropy

Uncertainty in the current posterior is measured using **Shannon entropy**:

```python
H(P) = -Σ_i P(i) * log2 P(i)
```

- High entropy → we’re very uncertain over majors.
- Low entropy → distribution is peaked around a few majors.

The backend tracks:
- `entropy_history`: entropy after each step.
- `posterior_history`: full posterior after each step.

### 5. Selecting the Next Question (Information Gain)

For each candidate question `q`, and each possible answer `a`:

1. Compute `P(answer = a)` under the current posterior:

   ```python
   P(a) = Σ_i P(a | i) * P(i)
   ```

2. Compute the posterior if that answer were observed: `P(i | a)`.
3. Compute its entropy `H(P(· | a))`.
4. Compute **expected posterior entropy**:

   ```python
   E[H | q] = Σ_a P(a) * H(P(· | a))
   ```

5. Information gain for question `q`:

   ```python
   IG(q) = H(current) - E[H | q]
   ```

The system selects the question with the **maximum information gain** among those not yet asked.

### 6. Stopping Criteria

The quiz stops when:

- At least a **minimum number of questions** have been asked (e.g. 17), and
- Either:
  - Top major probability ≥ threshold (e.g. 0.55), or
  - A maximum number of questions (e.g. 27) has been reached.

This balances robustness (enough evidence) with user time.

### 7. Results & Educational Visualizations

The results page pulls a full session summary from the API:

- Final posterior over majors.
- Entropy history.
- Information gain history.
- Posterior history (for top majors over time).

It then renders:

- Top majors table with:
  - Major name
  - Clickable link to the official program page
  - Probability (percentage, with 2 decimal places)
- Summary stats:
  - Questions asked
  - Top match confidence
  - Final entropy
- Charts:
  - **Entropy vs Question Index** (adaptive):
    - Shows how uncertainty falls as the quiz proceeds.
  - **Information Gain per Question**:
    - Bars showing how much each question reduced uncertainty.
  - **Probability Evolution for Top Majors**:
    - Lines showing how the main contenders rose/fell over time.
  - **Adaptive vs Linear Comparison**:
    - Overlays the adaptive entropy curve with a hypothetical linear test curve to illustrate the efficiency advantage of adaptive selection.

All of this is accompanied by explanatory text so users (and reviewers) can see not only **what** the recommendation is, but **how** the algorithm arrived there.

---

## Additional Documentation

- `README_START.md` — Quick commands for local development.
- `api/README.md` — Detailed API docs (endpoints, payloads).
- `frontend/README.md` — Frontend-specific notes, design details.
- `PROJECT_STATUS.md` — Internal project log and status.

For questions or suggestions, feel free to open an issue or PR. This project is designed both as a practical recommendation tool and as a teaching artifact for Bayesian inference and information theory in an applied setting.**
