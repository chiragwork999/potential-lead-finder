from dataclasses import dataclass
import logging
from urllib.parse import quote

import feedparser
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsProactorEventLoopPolicy()
    )
logger = logging.getLogger(__name__)

import json
import re
import html


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
    async def fetch_full_article(
        self,
        url: str
    ) -> str:

        try:

            async with async_playwright() as p:

                browser = await p.chromium.launch(
                    headless=True
                )

                page = await browser.new_page(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0 Safari/537.36"
                    )
                )

                # open page
                await page.goto(
                    url,
                    wait_until="networkidle",
                    timeout=60000
                )

                # extra wait for lazy-loaded content
                await page.wait_for_timeout(5000)

                # get FULL rendered HTML
                html = await page.content()

                await browser.close()

            soup = BeautifulSoup(
                html,
                "html.parser"
            )

            # target your main container
            main = soup.select_one("main.container")

            # fallback
            if not main:
                main = soup.find("body")

            if not main:
                return ""

            # remove junk
            for tag in main([
                "script",
                "style",
                "noscript",
                "svg",
                "img",
                "video",
                "iframe",
                "header",
                "footer",
                "nav",
                "aside",
                "form",
                "button"
            ]):
                tag.decompose()

            # extract ALL nested text recursively
            text = main.get_text(
                separator=" ",
                strip=True
            )

            # cleanup spaces
            text = re.sub(
                r"\s+",
                " ",
                text
            ).strip()

            print(text[:5000])

            return text

        except Exception as e:
            print("SCRAPE ERROR:", e)
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

        RELEVANT_KEYWORDS = [
            "real estate",
            "project",
            "infrastructure",
            "investment",
            "development",
            "office",
            "commercial",
            "construction",
            "land",
            "leasing",
            "metro",
            "township",
            "housing",
            "property",
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
                feed = feedparser.parse(rss_url)

                for entry in feed.entries[:5]:

                    text = (
                        entry.title
                        + " "
                        + entry.get("summary", "")
                    ).lower()

                    # Filter irrelevant news
                    if not any(
                        keyword in text
                        for keyword in RELEVANT_KEYWORDS
                    ):
                        continue

                    # Skip duplicates
                    if entry.link in seen_urls:
                        continue

                    seen_urls.add(entry.link)

                    # Fetch full article text
                    full_article_text = (
                        await self.fetch_full_article(
                            entry.link
                        )
                    )

                    articles.append(
                        RawArticle(
                            title=entry.title,
                            url=entry.link,
                            source="google_news",
                            published_at=entry.get(
                                "published",
                                ""
                            ),
                            content=(
                                full_article_text
                                or entry.get(
                                    "summary",
                                    ""
                                )
                            ),
                        )
                    )

            except Exception as e:
                logger.error(
                    f"Google News scrape failed: {e}"
                )

        return articles[:25]


class SecFilingsScraper:
    """
    SEC filings for expansion/capex signals
    """

    async def run(
        self,
        query: str
    ) -> list[RawArticle]:
        logger.info(
            f"SEC query: {query}"
        )

        headers = {
            "User-Agent":
            "PotentialLeadFinder chirag@example.com"
        }

        url = (
            "https://data.sec.gov/"
            "submissions/"
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
                data.get(
                    "filings",
                    {}
                ).get(
                    "recent",
                    {}
                )
            )

            forms = recent.get(
                "form",
                []
            )

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
                min(
                    5,
                    len(forms)
                )
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
                            "or investment "
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
    Government tender opportunities
    """

    async def run(
        self,
        query: str
    ) -> list[RawArticle]:
        logger.info(
            f"Tender query: {query}"
        )

        return [
            RawArticle(
                title=(
                    f"CPPP Tender related to "
                    f"{query}"
                ),
                url=(
                    "https://eprocure.gov.in/"
                ),
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
                url=(
                    "https://gem.gov.in/"
                ),
                source="gem_portal",
                published_at="",
                content=(
                    "Government "
                    "e-Marketplace "
                    "opportunity."
                ),
            ),
        ]