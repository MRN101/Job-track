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
- Collection History: `http://localhost:3000/collection-history`

---

## Automated Test Suite

Run the full automated test suite directly:

```bash
cd backend
pytest
```

### Verified Test Cases (15/15 Passing):
1. **Skill Normalization**: Maps variants to canonical names (`React.js` → `React`, `Postgres` → `PostgreSQL`).
2. **False Positive Elimination**: Strict word boundary matching prevents false positives for `C`, `R`, `Go`, `.NET`, `AI`, `SQL`, `AWS`.
3. **Salary Percentiles**: Statistical NumPy percentiles (min, max, median, 25th percentile, 75th percentile).
4. **Salary Normalization & LPA**: LPA conversion (e.g. ₹6–12 LPA → ₹600k–₹1.2M), hourly/monthly to annual.
5. **Multi-Currency Conversion**: Transparent conversion across INR, USD, EUR, and GBP.
6. **Date Filtering**: Strict freshness scoping across 7d, 30d, 90d, 6m, 1y, all.
7. **Real vs. Demo Separation**: Demo data is never mixed into default analytics queries.
8. **Honest Insufficient History**: Reports insufficient data when `< 2` jobs exist, never fabricating trends.
9. **Trend Calculation**: Equivalent real period comparison reporting delta in percentage points (`pp`).
10. **Duplicate Job Detection**: Content hashing and external ID deduplication prevent duplicate entries.
11. **Short Skill Boundary Matching**: Verifies positive technical contexts and negative colloquial contexts for short terms.
12. **Role Taxonomy & Classification**: Deterministic classification into Role Family and Normalized Role.
13. **Location Normalization**: Normalizes Bangalore/Bombay/Calcutta/Madras variants and geocodes tech hubs and remote flags.
14. **Candidate Skill Discovery**: Lightweight NLP extracts uncatalogued tools (`MCP`, `WASM`) without corrupting taxonomy.
15. **End-to-End Pipeline Integration**: Full collector → DB → taxonomy & location normalization → snapshot → trends pipeline.

---

## Automated Background Scheduler

JobPulse includes a background scheduler (`APScheduler`) that continuously runs the job intelligence pipeline:

```text
Scheduled collection
        ↓
Get enabled sources (Remotive, Adzuna)
        ↓
Normalize roles & locations
        ↓
Deduplicate against existing records
        ↓
Extract canonical & candidate skills
        ↓
Update analysis & create historical snapshot
```

- **Cadences**: Daily (default), Weekly, or Manual (paused).
- **Trigger on demand**: Trigger collection directly from `/collection-history` or `/settings`.

---

## Production Deployment Readiness

### 1. Environment Variables

Create `.env` in `backend/`:

```env
# Application
APP_ENV=production
DEBUG=false
SECRET_KEY=your-production-secret-key

# Database (SQLite by default, or PostgreSQL)
DATABASE_URL=sqlite:///./data/jobpulse.db
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/jobpulse

# Collector API Keys
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_API_KEY=your_adzuna_api_key

# Server & CORS
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000
```

### 2. Running in Production

**Backend Production Run**:
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

**Frontend Production Build & Start**:
```bash
cd frontend
npm run build
npm start
```

### 3. Database Notes: SQLite vs PostgreSQL
- **SQLite (Default)**: Ideal for personal local use with zero setup. Supports ACID transactions and auto-migrations. SQLite limits concurrent writes, so for multi-threaded cloud deployments, point `DATABASE_URL` to a PostgreSQL instance.
- **PostgreSQL**: JobPulse's SQLAlchemy models and query services are fully PostgreSQL-compatible without code changes. Install `psycopg2-binary` if connecting to PostgreSQL.
