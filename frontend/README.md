# Stanford Major Quiz — Frontend

Modern **Next.js (App Router)** frontend for the Stanford Major Quiz. It provides the landing page, adaptive quiz UI, and a rich results experience (charts + explanations) powered by the FastAPI backend.

For the full system overview (algorithm, repo-wide structure, one-shot start scripts), see the root [`README.md`](../README.md).

## Tech stack

- **Next.js 16** (App Router) + **React 18**
- **TypeScript**
- **Tailwind CSS**
- **Framer Motion**
- **Recharts** (results visualizations)

## Quick start (local development)

### Prerequisites

- **Node.js 18+**
- A running **FastAPI backend** (see `api/README.md`)

### 1) Start the backend

From the repo root:

```bash
cd api
pip install -r requirements.txt
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Confirm it’s up:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

### 2) Start the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Configuration

### `NEXT_PUBLIC_API_URL`

The frontend reads the API base URL from `NEXT_PUBLIC_API_URL`.

- **Local**: set it to your local FastAPI server
- **Production**: set it to your deployed FastAPI URL (must be `https://...`)

Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Notes:

- If you **do not** set `NEXT_PUBLIC_API_URL`, the app falls back to the production URL hardcoded in `frontend/lib/api.ts`.
- If your site is served over **HTTPS** (e.g. Vercel), your API URL must also be **HTTPS** or the browser will block requests (mixed content).

## Key pages

- **`/`**: landing page + methodology overview
- **`/quiz`**: one-question-at-a-time quiz experience
- **`/results?session_id=...`**: final results + charts + “CS109-level” explanation

## UI architecture (where things live)

```text
frontend/
  app/
    page.tsx              # landing
    quiz/page.tsx         # quiz flow + API calls
    results/page.tsx      # results + charts + narrative
    globals.css           # global styles + utility classes
  components/
    PageShell.tsx         # shared layout + header
    AnimatedBackground.tsx# used on landing only (perf)
    AnswerChoice.tsx      # quiz answer tile
    ProgressBar.tsx       # progress indicator
    TopResultsCard.tsx    # live top-5 majors sidebar
    charts/               # Recharts components used on results page
  lib/
    api.ts                # typed FastAPI client (fetch wrapper + models)
  public/
    class-logo-gen.png    # logo used in the UI
```

## API integration (contract summary)

The UI talks to the FastAPI backend via:

- `POST /start`
- `POST /answer`
- `GET /results/{session_id}`
- `GET /health`

The typed client lives in `frontend/lib/api.ts`. Detailed request/response docs are in `api/README.md`.

## Scripts

From `frontend/`:

- `npm run dev`: run dev server
- `npm run build`: production build
- `npm start`: run production server (after build)
- `npm run lint`: Next.js lint

## Deployment (Vercel)

High-level checklist:

- **Root directory** in Vercel: `frontend`
- **Environment variable** in Vercel:
  - `NEXT_PUBLIC_API_URL = https://<your-backend-domain>`
- Ensure the backend allows your Vercel origin via CORS (see `api/main.py`)

This repo includes `frontend/vercel.json` for build/install defaults, but Vercel project settings still matter (especially Root Directory + env vars).

## Troubleshooting

### “Network error: Failed to fetch”

This is almost always one of:

- `NEXT_PUBLIC_API_URL` is missing/wrong (e.g. points to `localhost` in production)
- API URL is `http://...` while the frontend is `https://...` (mixed content)
- Backend is down / wrong domain
- CORS is blocking the browser request

Fastest way to debug:

- Confirm API health in a browser: `https://<backend>/health`
- In the frontend, open DevTools → **Network** and inspect the failing request URL + console errors

