# Stanford Major Quiz - Frontend

Modern Next.js frontend for the adaptive Stanford major quiz with a polished dark gradient design and glassmorphism UI.

## Tech Stack

- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **Framer Motion**

## Design Features

- Dark gradient background (deep blue/purple tones)
- Glassmorphism cards with backdrop blur
- Smooth animations and transitions
- Responsive design (mobile-first)
- Modern, minimal aesthetic

## Getting Started

### Prerequisites

1. **FastAPI Backend**: Make sure the FastAPI backend is running on `http://localhost:8000`
   ```bash
   # From project root
   cd api
   pip install -r requirements.txt
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend Setup**:
   ```bash
   # Navigate to frontend directory
   cd frontend

   # Install dependencies
   npm install

   # (Optional) Configure API URL
   # Copy .env.local.example to .env.local and update if needed
   # Default: http://localhost:8000

   # Run development server
   npm run dev
   ```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/
│   ├── globals.css          # Global styles with glassmorphism utilities
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Landing page
│   ├── quiz/
│   │   └── page.tsx         # Quiz page with question flow
│   └── results/
│       └── page.tsx         # Results page with major recommendations
├── components/
│   ├── AnimatedBackground.tsx  # Animated gradient background
│   ├── AnswerChoice.tsx        # Answer choice tiles
│   ├── Button.tsx              # Reusable button component
│   ├── CenteredContainer.tsx   # Responsive centered container
│   ├── ErrorMessage.tsx        # Error display component
│   ├── GlassCard.tsx           # Glassmorphism card wrapper
│   ├── LoadingSpinner.tsx     # Loading indicator
│   ├── ProgressBar.tsx         # Animated progress bar
│   ├── QuestionCard.tsx        # Question display card
│   └── TopResultsCard.tsx      # Top majors sidebar card
├── lib/
│   ├── api.ts             # API client for FastAPI backend
│   └── mockData.ts        # (Legacy) mock data used early in development
└── public/                  # Static assets (if needed)
```

## Pages

### Landing Page (`/`)
- Hero section with gradient title
- "How It Works" explanation
- Start quiz button

### Quiz Page (`/quiz`)
- Adaptive question display (from API)
- Likert scale (1-5) answer options
- Progress bar with real-time updates
- Sidebar with top 5 majors (live from API)
- Smooth question transitions with loading states
- Error handling with retry functionality

### Results Page (`/results`)
- Ranked major recommendations (from API)
- Clickable links to program pages
- Statistics (questions asked, confidence, entropy)
- Loading states and error handling
- Disclaimer
- Retake quiz option

## API Integration

The frontend is fully integrated with the FastAPI backend:

- **POST /start** - Initializes quiz session on page load
- **POST /answer** - Submits answers and gets next question
- **GET /results/{session_id}** - Fetches final results

All API calls include:
- Loading states with spinners
- Error handling with user-friendly messages
- Retry functionality
- Smooth animations during state transitions

## Configuration

Set the API URL via environment variable:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Default is `http://localhost:8000` if not set.

## Next Steps

1. **Enhanced Visualizations**: Add charts and graphs for entropy reduction, information gain, etc.
2. **User Persistence**: Add ability to save/resume quiz sessions
3. **Analytics**: Track quiz completion rates and popular majors
4. **Optimization**: Implement request caching and optimistic updates

## Building for Production

```bash
npm run build
npm start
```
