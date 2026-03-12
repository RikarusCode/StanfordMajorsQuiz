# Stanford Major Quiz API

FastAPI backend for the adaptive Stanford major quiz. This API wraps the existing inference logic and provides REST endpoints for quiz initialization, answering questions, and retrieving results.

## Features

- **POST /start** - Initialize a quiz session and return the first question
- **POST /answer** - Submit an answer and get the next question with updated top majors
- **GET /results/{session_id}** - Get final results for a completed quiz
- **GET /health** - Health check endpoint

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints

### POST /start

Initialize a new quiz session.

**Response:**
```json
{
  "session_id": "uuid",
  "question_id": "q1",
  "question_text": "I enjoy using quantitative tools...",
  "question_number": "A1B2C3",
  "top_majors": [
    {
      "id": "computer_science",
      "name": "Computer Science",
      "link": "https://...",
      "probability": 0.15
    }
  ]
}
```

### POST /answer

Submit an answer to a question.

**Request:**
```json
{
  "session_id": "uuid",
  "question_id": "q1",
  "answer": 4
}
```

**Response:**
```json
{
  "question_id": "q2",
  "question_text": "I prefer working with...",
  "question_number": "D4E5F6",
  "top_majors": [...],
  "entropy": 4.2,
  "top_probability": 0.25,
  "questions_asked": 1,
  "is_complete": false
}
```

### GET /results/{session_id}

Get final results for a completed quiz.

**Response:**
```json
{
  "session_id": "uuid",
  "majors": [
    {
      "id": "computer_science",
      "name": "Computer Science",
      "link": "https://...",
      "probability": 0.42
    }
  ],
  "entropy": 3.2,
  "top_probability": 0.42,
  "questions_asked": 17,
  "entropy_history": [6.5, 5.8, ...],
  "info_gain_history": [0.7, 0.5, ...]
}
```

## Architecture

The API layer is cleanly separated from the inference logic:

- **`api/main.py`** - FastAPI application and endpoints
- **`src/inference.py`** - Core Bayesian inference utilities (unchanged)
- **`src/model.py`** - Data models and loading (unchanged)

Session management is currently in-memory. For production, consider using Redis or a database.

## CORS

CORS is configured to allow requests from `http://localhost:3000` (Next.js frontend). Update the `allow_origins` list in `main.py` for production.
