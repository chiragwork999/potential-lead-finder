from dataclasses import dataclass
import logging
from urllib.parse import quote
from datetime import datetime

import feedparser
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class RawArticle:
    title: str
    url: str
    source: str
    published_at: str
    content: str


class GoogleNewsScraper:
    """
    Scrapes:
    - infrastructure projects
    - real estate launches
    - land acquisition
    - commercial leasing
    - office expansion
    - zoning approvals
    - permits
    """

    async def fetch_full_article(self, url: str) -> str:
        """
        Fetch actual article body from source URL
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            async with httpx.AsyncClient(
                timeout=15,
                follow_redirects=True
            ) as client:
                response = await client.get(url, headers=headers)

            soup = BeautifulSoup(response.text, "html.parser")

            paragraphs = soup.find_all("p")
            text = " ".join(
                p.get_text(strip=True)
                for p in paragraphs
            )

            return text[:4000]

        except Exception as e:
            logger.warning(f"Could not fetch full article: {url} | {e}")
            return ""

    async def run(self, query: str) -> list[RawArticle]:
        logger.info(f"Google News query: {query}")

        search_queries = [
            query,
            f"{query} real estate development",
            f"{query} infrastructure project",
            f"{query} commercial expansion",
            f"{query} office leasing",
            f"{query} land acquisition",
            f"{query} zoning approval",
            f"{query} construction permit",
            f"{query} new project launch",
            f"{query} investment announcement",
        ]

        articles = []
        seen_urls = set()

        for q in search_queries:
            rss_url = (
                "https://news.google.com/rss/search?"
                f"q={quote(q)}"
                "&hl=en-IN&gl=IN&ceid=IN:en"
            )

            try:
                logger.info(f"RSS: {rss_url}")

                async with httpx.AsyncClient(timeout=20) as client:
                    response = await client.get(rss_url)

                feed = feedparser.parse(response.text)

                for entry in feed.entries[:5]:
                    if entry.link in seen_urls:
                        continue

                    seen_urls.add(entry.link)

                    full_content = await self.fetch_full_article(
                        entry.link
                    )

                    article = RawArticle(
                        title=entry.title,
                        url=entry.link,
                        source="google_news",
                        published_at=entry.get(
                            "published",
                            datetime.utcnow().isoformat()
                        ),
                        content=full_content
                        or entry.get("summary", "")
                    )

                    articles.append(article)

                    logger.info(
                        f"Added article: {article.title}"
                    )

            except Exception as e:
                logger.error(
                    f"Google News scrape failed: {e}"
                )

        logger.info(
            f"Total Google articles: {len(articles)}"
        )

        return articles[:25]


class SecFilingsScraper:
    """
    SEC filings for expansion/capex signals
    """

    async def run(self, query: str) -> list[RawArticle]:
        logger.info(f"SEC query: {query}")

        headers = {
            "User-Agent":
                "PotentialLeadFinder/1.0 "
                "chiragagarwal@example.com"
        }

        url = (
            "https://data.sec.gov/submissions/"
            "CIK0000320193.json"
        )

        try:
            async with httpx.AsyncClient(
                timeout=20
            ) as client:
                response = await client.get(
                    url,
                    headers=headers
                )

            data = response.json()

            recent = (
                data.get("filings", {})
                .get("recent", {})
            )

            forms = recent.get("form", [])
            dates = recent.get(
                "filingDate",
                []
            )
            accession = recent.get(
                "accessionNumber",
                []
            )

            filings = []

            for i in range(
                min(5, len(forms))
            ):
                filing_url = (
                    "https://www.sec.gov/"
                    "Archives/edgar/data/"
                    f"320193/"
                    f"{accession[i].replace('-', '')}"
                    "/index.html"
                )

                filings.append(
                    RawArticle(
                        title=(
                            f"{forms[i]} "
                            f"filing: {query}"
                        ),
                        url=filing_url,
                        source="sec_filings",
                        published_at=dates[i],
                        content=(
                            "Potential expansion "
                            "signal from SEC filing."
                        ),
                    )
                )

            return filings

        except Exception as e:
            logger.error(
                f"SEC scrape failed: {e}"
            )
            return []


class IndiaTenderScraper:
    """
    Future project opportunities
    """

    async def run(self, query: str) -> list[RawArticle]:
        logger.info(
            f"India Tender query: {query}"
        )

        return [
            RawArticle(
                title=(
                    f"CPPP Tender related "
                    f"to {query}"
                ),
                url="https://eprocure.gov.in/",
                source="cppp_tenders",
                published_at="",
                content=(
                    "Central Public "
                    "Procurement Portal "
                    "tender."
                ),
            ),
            RawArticle(
                title=(
                    f"GeM procurement "
                    f"related to {query}"
                ),
                url="https://gem.gov.in/",
                source="gem_portal",
                published_at="",
                content=(
                    "Government "
                    "e-Marketplace "
                    "opportunity."
                ),
            ),
        ]


# -----------------------------------
# TODO later database integration
# -----------------------------------
# save_articles_to_db(articles)
#
# from app.db.models import Article
# session.add(...)
# session.commit()
#
# -----------------------------------
# TODO NLP pipeline later
# -----------------------------------
# extract_entities(article.content)
# classify_event(article.content)
# sentiment_analysis(article.content)
# geo_tagging(article.content)
# impact_scoring(article.content)