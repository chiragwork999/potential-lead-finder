# Potential Lead Finder

Enterprise lead-intelligence platform with manual-first scraping, event intelligence, and Grok-powered NLP enrichment.

## Run Locally (No Docker)
### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## Business Workflow
1. Admin triggers one or more sources (`google_news`, `sec_filings`, `state_rfp`) via `POST /api/v1/scrape/trigger`.
2. Scrapers return normalized raw articles.
3. Pipeline performs cleaning, entity extraction, classification, sentiment, geo-tagging, and impact scoring.
4. Optional Grok NLP enrichment summarizes events and improves entity context.
5. Dashboard pages render opportunities, events, and regional intelligence.

## UI + Component Interaction
- `frontend/components/layout/app-shell.tsx` is the shared shell: sidebar, top nav, search, theme switch, notifications.
- `frontend/app/(dashboard)/layout.tsx` wraps all feature pages in the shared shell.
- Feature routes (`overview`, `sources`, `events`, `geography`, `opportunities`, `admin`) each own a business slice.
- Frontend calls backend APIs under `NEXT_PUBLIC_API_URL` and presents KPI cards, tables, and charts.

## APIs You Need (including Grok)
### Core platform APIs
- `GET /api/v1/health`
- `GET /api/v1/dashboard`
- `POST /api/v1/scrape/trigger`
- `POST /api/v1/sources/{source_id}/trigger`
- `POST /api/v1/admin/tasks/{task_name}`

### Grok NLP API integration endpoint
- `POST /api/v1/nlp/grok/summarize`
  - body:
  ```json
  { "title": "New metro rail expansion announced", "content": "...article body..." }
  ```

## Environment Variables
### Backend (`backend/.env`)
- `APP_NAME=Potential Lead Finder API`
- `DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/potential_leads`
- `REDIS_URL=redis://localhost:6379/0`
- `ENABLE_SCHEDULER=false`
- `GROK_API_KEY=your_grok_api_key`
- `GROK_BASE_URL=https://api.x.ai/v1`
- `GROK_MODEL=grok-3-mini`
- `DEFAULT_SCRAPE_SOURCES=google_news,sec_filings,state_rfp`

### Frontend (`frontend/.env.local`)
- `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`
- `NEXT_PUBLIC_APP_NAME=Potential Lead Finder`
