from fastapi import APIRouter
from app.schemas.intelligence import ScrapeRequest
from app.scrapers.sources.google_news import (
    GoogleNewsScraper,
    SecFilingsScraper,
    IndiaTenderScraper,
)

router = APIRouter()


@router.post("/scrape/trigger")
async def trigger_scrape(payload: ScrapeRequest):
    all_items = []

    for source in payload.sources:
        try:
            if source == "google_news":
                scraper = GoogleNewsScraper()
            elif source == "sec_filings":
                scraper = SecFilingsScraper()
            elif source in ["state_rfp", "india_tenders"]:
                scraper = IndiaTenderScraper()
            else:
                continue

            articles = await scraper.run(payload.query)

            for article in articles:
                all_items.append({
                    "title": article.title,
                    "url": article.url,
                    "source": article.source,
                    "published_at": article.published_at,
                    "content": article.content,
                })

        except Exception as e:
            print(f"Scraper failed for {source}: {e}")

    return {
        "queued": True,
        "count": len(all_items),
        "items": all_items,
    }


@router.get("/articles")
async def get_articles():
    return {"items": []}


@router.get("/events")
async def get_events():
    return {"items": []}


@router.get("/hotspots")
async def get_hotspots():
    return {"items": []}


@router.get("/sentiment")
async def get_sentiment():
    return {"items": []}


@router.get("/ai-summaries")
async def get_ai_summaries():
    return {"items": []}


@router.get("/search")
async def search_intelligence(q: str):
    return {"query": q, "items": []}


@router.get("/companies/{company_id}/insights")
async def company_insights(company_id: str):
    return {"company_id": company_id, "insights": []}


@router.get("/locations/{location_id}/insights")
async def location_insights(location_id: str):
    return {"location_id": location_id, "insights": []}