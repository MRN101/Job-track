# Job-Track — Job Market Intelligence & Skill Gap Dashboard

Job-Track analyzes current job listings to identify in-demand skills, analyze industry trends, and calculate skill gaps tailored to your target roles.

---

## Features

- **Automated Job Ingestion**: Collect listings via integrations (Adzuna, Remotive) or seed data.
- **Skill Extraction Engine**: Fast regex taxonomy matching and optional LLM-assisted extraction.
- **Market Trends & Analytics**: Track rising vs. cooling skills, cross-role requirements, and historical trends.
- **Personalized Skill Gap Analysis**: Compare your profile skills directly against market expectations.
- **Modern Dashboard**: Responsive web UI built with Next.js and interactive charts.

---

## Tech Stack

- **Frontend**: Next.js 15, React, TypeScript, Tailwind CSS, Recharts
- **Backend**: FastAPI, Python 3.11+, SQLAlchemy 2.0, Pydantic v2
- **Database**: SQLite (local) / PostgreSQL ready
- **Data & Processing**: pandas, HTTPX

---

## Quickstart

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend API
python -m uvicorn app.main:app --reload
```

- API Server: `http://localhost:8000`
- Interactive Swagger Docs: `http://localhost:8000/api/docs`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

- Frontend App: `http://localhost:3000`

---

## Environment Variables

Copy `.env.example` to `backend/.env` to configure:

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | Database connection string | `sqlite:///./data/jobpulse.db` |
| `BACKEND_PORT` | Backend port | `8000` |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:3000` |
| `ADZUNA_APP_ID` | (Optional) Adzuna API ID | — |
| `ADZUNA_API_KEY` | (Optional) Adzuna API Key | — |
| `LLM_ENABLED` | LLM-based skill extraction | `false` |
| `OPENAI_API_KEY` | (Optional) OpenAI API Key | — |
