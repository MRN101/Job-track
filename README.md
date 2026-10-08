# JobPulse — Job Market Intelligence & Skill Gap Dashboard

JobPulse is an analytical dashboard that ingests job listings from live sources, extracts in-demand technical skills against a canonical taxonomy, tracks genuine market trends across historical periods, and computes personalized skill gap coverage.

---

## Key Principles & Methodologies

### 1. Real vs. Demo Data Segregation
- **Strict Data Segregation**: Every job listing and analysis run is categorized as either `real` or `demo` (`data_type` column).
- **Default Real Analytics**: The dashboard and analytics endpoints default to **real data only**. If zero real jobs match a selected filter, the system displays an honest empty state with instructions to run a live collection.
- **Explicit Demo Mode**: Curated sample datasets can be inspected when explicitly activated via Demo Mode, with prominent UI alerts distinguishing demo numbers from live market data.

### 2. Time Period Filtering & Freshness
- **Supported Windows**: 7 Days (`7d`), 30 Days (`30d`), 90 Days (`90d`), 6 Months (`6m`), 1 Year (`1y`), and All Time (`all`).
- **Job Freshness Calculation**: Uses `posted_at` whenever reliably supplied by the source, with fallback to `collected_at`: `COALESCE(posted_at, collected_at)`.
- **Consistent Denominators**: Both numerator (skill count) and denominator (total jobs analyzed) use the exact same filtered query window.

### 3. Statistically Rigorous Salary Analytics
- **Percentiles**: Computes minimum, maximum, median (50th percentile), 25th percentile (Q1), and 75th percentile (Q3) using standard statistical linear interpolation via NumPy.
- **Normalization**: Normalizes compensation to annual equivalents:
  - Hourly: `salary * 2080` (40 hrs/wk × 52 wks)
  - Monthly: `salary * 12`
  - Indian Lakhs Per Annum (LPA): e.g. `₹6–12 LPA` converts to `₹600,000–₹1,200,000`
  - Unclear salaries remain `salary_normalized = NULL` rather than guessing.
- **Multi-Currency Support**: Handles INR, USD, EUR, and GBP with transparent currency conversion.

### 4. Trustworthy Trend Calculations (Zero Simulated Variance)
- **Period-over-Period**: Compares current window (e.g. Last 30 days) against the previous equivalent window (60 to 30 days ago).
- **Percentage Points (`pp`)**: Reports changes in percentage points (`current_pct - previous_pct`), avoiding deceptive percentage growth claims.
- **Insufficient Data Reporting**: If either comparison window has fewer than 2 jobs, the system reports `"Not enough historical data"` rather than manufacturing artificial trends.
- **Emerging & Declining Thresholds**: Requires a minimum job count threshold (configurable, default 5 listings) to qualify as emerging or declining.

### 5. Deterministic Skill Extraction & Normalization
- **Strict False Positive Prevention**: Single-letter and short keywords (e.g. `C`, `Go`) use strict contextual patterns (e.g., `C/C++`, `embedded C`, `Golang`, `Go developer`) to prevent false positives from everyday words or letters.
- **Centralized Normalization**: Canonical alias mapping guarantees uniform tracking:
  - `React.js`, `ReactJS`, `React JS` → `React`
  - `Postgres`, `postgresql`, `psql` → `PostgreSQL`
  - `Amazon Web Services`, `aws` → `AWS`
- **Candidate Skills**: Unrecognized skills detected by heuristics or LLM are logged into `candidate_skills` for human approval rather than automatically corrupting the canonical taxonomy.

### 6. Market Skill Coverage (Skill Gap)
- **Transparent Formula**:
  $$\text{Market Skill Coverage} = \frac{\sum \text{Demand weights for skills you possess}}{\sum \text{Total market demand weights for target role}} \times 100$$
- **Priority Ranking**:
  $$\text{Priority Score} = \text{Demand Percentage} \times \text{Role Relevance Factor}$$
  *(Role Relevance Factor = 1.2 if the skill ranks in top 5 demanded skills for the role, 1.0 otherwise)*

---

## Data Sources

1. **Remotive API** (`source: remotive`):
   - Open developer jobs API (`https://remotive.com/api/remote-jobs`).
   - Live, real remote developer jobs.
   - Requires no API key and works out of the box.
2. **Adzuna API** (`source: adzuna`):
   - Multi-country global search API across India, US, UK, etc.
   - Requires free developer credentials (`ADZUNA_APP_ID`, `ADZUNA_API_KEY`).
3. **Curated Demo Dataset** (`source: sample`, `data_type: demo`):
   - Curated developer jobs across India and remote for testing and development.
   - Strictly tagged as demo data and excluded from real analytics.

---

## Tech Stack

- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.9+, SQLAlchemy 2.0, Pydantic v2
- **Data & Math**: NumPy, pandas, HTTPX
- **Database**: SQLite (dev) / PostgreSQL ready

---

## Quickstart

### 1. Backend Setup

```bash
cd backend

# Create virtual environment (if not already created)
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (macOS / Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend API
python -m uvicorn app.main:app --reload
```

- API Server: `http://localhost:8000`
- Swagger UI Docs: `http://localhost:8000/api/docs`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

- Web Dashboard: `http://localhost:3000`

---

## Automated Test Suite

Run the full analytical verification test suite:

```bash
cd backend
.\venv\Scripts\python -m pytest -v -o pythonpath=. tests/test_analytics.py
```

### Verified Test Cases:
- Date filtering (7d, 30d, 90d strict freshness)
- Centralized skill normalization (`React.js` → `React`, `Postgres` → `PostgreSQL`, `AWS` → `AWS`)
- False positive elimination (no accidental matches for `C` or `Go`)
- Salary statistical percentiles (odd & even lists, Q1, median, Q3)
- Salary normalization (LPA conversion, hourly/monthly to annual)
- Currency conversion (INR, USD, EUR, GBP)
- Real vs. Demo data segregation
- Honest insufficient data handling for trends
- Real period-over-period percentage point trends
- Incremental job deduplication & content hashing

---

## Database Schema Overview

- `jobs`: Stores raw & normalized job listings (`source`, `data_type`, `salary_normalized`, `first_seen_at`, `last_seen_at`, `content_hash`).
- `companies`: Normalizes employer brands.
- `skills`: Canonical taxonomy skills and categories.
- `job_skills`: Many-to-many relationship linking jobs to detected skills.
- `candidate_skills`: Unseen skills detected by heuristics or LLM pending review.
- `analysis_runs`: Snapshots of historical runs (`source`, `data_type`, `time_period_start`, `time_period_end`).
- `skill_demands`: Skill percentage points and counts for each analysis run.
- `user_profiles`: User's skills and target roles for skill gap evaluation.

---

## Limitations & Operational Notes

- **Single-User Scope**: Designed as a personal job market intelligence dashboard; no multi-tenant authentication.
- **Local Storage**: Defaults to SQLite at `backend/data/jobpulse.db`. For production, point `DATABASE_URL` to PostgreSQL.
- **Adzuna API Credentials**: Adzuna requires free API keys in `.env`; Remotive works without credentials.
