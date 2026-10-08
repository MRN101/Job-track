# JobPulse — Personal Job Market Intelligence Dashboard

JobPulse analyzes current job listings and identifies which skills are currently in demand, trending up or down, and most relevant to your career goals.

## Architecture

```
frontend/          Next.js 15 (TypeScript, Tailwind CSS)
backend/           FastAPI (Python, SQLAlchemy, Pydantic)
  app/
    api/           API route handlers
    models/        SQLAlchemy database models
    schemas/       Pydantic request/response schemas
    collectors/    Job data source adapters
    analyzers/     Skill extraction and analysis
    services/      Business logic
scripts/           Data collection and maintenance scripts
data/              Local database (SQLite)
```

## Tech Stack

| Layer            | Technology                              |
|------------------|-----------------------------------------|
| Frontend         | Next.js 15, React, TypeScript           |
| Styling          | Tailwind CSS                            |
| Charts           | Recharts (Phase 6)                      |
| Backend          | FastAPI, Python 3.11+                   |
| ORM              | SQLAlchemy 2.0                          |
| Validation       | Pydantic v2                             |
| Database         | SQLite (dev) → PostgreSQL (production)  |
| Data Processing  | pandas, regex                           |
| HTTP Client      | httpx / aiohttp                         |

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.  
API docs at `http://localhost:8000/api/docs`.

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

The frontend will be available at `http://localhost:3000`.  
API calls from the frontend are proxied to `http://localhost:8000`.

## Environment Variables

Copy `.env.example` to `backend/.env` and configure:

| Variable              | Description                        | Default                     |
|-----------------------|------------------------------------|-----------------------------|
| `DATABASE_URL`        | SQLAlchemy database URL            | `sqlite:///./data/jobpulse.db` |
| `BACKEND_HOST`        | API server host                    | `0.0.0.0`                  |
| `BACKEND_PORT`        | API server port                    | `8000`                      |
| `FRONTEND_URL`        | Frontend URL for CORS              | `http://localhost:3000`     |
| `ADZUNA_APP_ID`       | Adzuna API app ID                  | —                           |
| `ADZUNA_API_KEY`      | Adzuna API key                     | —                           |
| `LLM_ENABLED`         | Enable LLM skill extraction        | `false`                     |
| `OPENAI_API_KEY`      | OpenAI API key (optional)          | —                           |
| `COLLECTION_SCHEDULE` | Auto-collection frequency          | `manual`                    |
| `LOG_LEVEL`           | Logging level                      | `INFO`                      |

## Database

SQLite database is created automatically at `backend/data/jobpulse.db` on first startup.

### Tables

- `jobs` — Collected job listings
- `companies` — Companies found in listings
- `skills` — Canonical skill taxonomy
- `job_skills` — Job ↔ Skill associations with confidence
- `candidate_skills` — LLM-detected skills pending approval
- `analysis_runs` — Historical analysis snapshots
- `skill_demands` — Skill demand data per analysis run
- `user_profiles` — Personal profile for skill gap analysis

## API Endpoints

| Method | Endpoint                       | Description              |
|--------|--------------------------------|--------------------------|
| GET    | `/api/health`                  | Health check             |
| GET    | `/api/jobs`                    | List jobs (paginated)    |
| GET    | `/api/jobs/{id}`               | Get job details          |
| GET    | `/api/skills`                  | List skills              |
| GET    | `/api/skills/{id}`             | Get skill details        |
| GET    | `/api/analytics/dashboard`     | Dashboard metrics        |
| GET    | `/api/analytics/top-skills`    | Top skills by demand     |
| GET    | `/api/analytics/trends`        | Skill trends             |
| GET    | /api/analytics/skill-gap     | Skill gap against market |
| GET    | /api/analytics/role-comparison| Cross-role skill comparison |
| GET    | /api/analytics/collectors    | List data source status  |
| POST   | /api/analytics/collect       | Trigger job collection   |
| POST   | /api/analytics/seed-sample   | Seed sample dataset      |
| POST   | /api/analytics/run-snapshot  | Snapshot demand trends   |
| GET    | `/api/profile`                 | Get user profile         |
| PUT    | `/api/profile`                 | Update user profile      |

## Development Phases

- [x] **Phase 1** — Project setup (frontend, backend, database, config)
- [x] **Phase 2** — Database models, Alembic migrations, and canonical skills seeding
- [x] **Phase 3** — Job data source integration (Adzuna API + Curated Sample Tech Jobs)
- [x] **Phase 4** — Skill extraction (dictionary regex matching + LLM support)
- [x] **Phase 5** — Analytics calculations & data pipeline services
- [x] **Phase 6** — Interactive Dashboard UI & Jobs Explorer
- [x] **Phase 7** — Historical trends tracking with snapshot comparisons
- [x] **Phase 8** — Skill gap analysis against live market requirements
- [x] **Phase 9** — Data pipeline triggers & collection automation endpoints

## Known Limitations

- Phase 1: No real job data yet — dashboard shows empty state
- No authentication (personal use, single user)
- SQLite only (PostgreSQL support structured but not tested)
