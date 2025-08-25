from typing import List, Optional, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import json
import re
import math
from contextlib import contextmanager
from gambling_unifier.guardrails import ProductRecord, ScrapeResult, UnifiedProduct
import logging

logger = logging.getLogger('gambling_unifier.tools')


class ScrapeInput(BaseModel):
    url: str = Field(..., description="Full URL to fetch and parse")


"""
Compatibility note: ProductRecord, ScrapeResult, UnifiedProduct are now imported
from gambling_unifier.guardrails to act as guardrail schemas for agent/tool IO.
"""


class ScrapePolymarketTool(BaseTool):
    name: str = "scrape_polymarket"
    description: str = (
        "Scrape active Polymarket markets. Returns JSON list of products with name and price."
    )
    args_schema: Type[BaseModel] = ScrapeInput

    def _run(self, url: str) -> str:
        try:
            import requests
            logger.info(f"Scraping Polymarket from {url}")
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            data = resp.json() if 'application/json' in resp.headers.get('content-type','') else resp.text
            products: List[ProductRecord] = []
            if isinstance(data, list):
                for item in data:
                    name = item.get('title') or item.get('question') or item.get('name') or ''
                    price = item.get('yesPrice') or item.get('bestBid') or item.get('price')
                    market_id = str(item.get('id') or item.get('slug') or item.get('market_id') or name)
                    products.append(ProductRecord(site='polymarket', product_id=market_id, name=name, price=_safe_float(price), url=item.get('url') or url))
            else:
                for m in re.finditer(r'"title":\s*"(.*?)"', str(data)):
                    name = m.group(1)
                    products.append(ProductRecord(site='polymarket', product_id=name, name=name, price=None, url=url))
            logger.info(f"Polymarket products scraped: {len(products)}")
            return ScrapeResult(products=products).model_dump_json()
        except Exception as e:
            logger.error(f"Polymarket scrape failed: {e}")
            return json.dumps({"error": f"polymarket scrape failed: {e}"})


class ScrapeKalshiTool(BaseTool):
    name: str = "scrape_kalshi"
    description: str = (
        "Scrape Kalshi markets via public catalog endpoint or HTML fallback. Returns JSON list of products."
    )
    args_schema: Type[BaseModel] = ScrapeInput

    def _run(self, url: str) -> str:
        try:
            import requests
            logger.info(f"Scraping Kalshi from {url}")
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            products: List[ProductRecord] = []
            if 'application/json' in resp.headers.get('content-type',''):
                data = resp.json()
                items = data.get('markets') or data.get('data') or []
                for item in items:
                    name = item.get('title') or item.get('name') or ''
                    price = item.get('last_price') or item.get('yes_price') or item.get('price')
                    market_id = str(item.get('id') or item.get('ticker') or name)
                    products.append(ProductRecord(site='kalshi', product_id=market_id, name=name, price=_safe_float(price), url=item.get('url') or url))
            else:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                for a in soup.select('a[href*="/markets/"]'):
                    name = a.get_text(strip=True)
                    if name:
                        products.append(ProductRecord(site='kalshi', product_id=name, name=name, price=None, url=url))
            logger.info(f"Kalshi products scraped: {len(products)}")
            return ScrapeResult(products=products).model_dump_json()
        except Exception as e:
            logger.error(f"Kalshi scrape failed: {e}")
            return json.dumps({"error": f"kalshi scrape failed: {e}"})


class ScrapePredictionMarketTool(BaseTool):
    name: str = "scrape_prediction_market"
    description: str = (
        "Scrape prediction-market data from the provided URL. Returns JSON list of products."
    )
    args_schema: Type[BaseModel] = ScrapeInput

    def _run(self, url: str) -> str:
        try:
            import requests
            logger.info(f"Scraping Prediction Market from {url}")
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            products: List[ProductRecord] = []
            if 'application/json' in resp.headers.get('content-type',''):
                data = resp.json()
                items = data if isinstance(data, list) else (data.get('markets') or data.get('data') or [])
                for item in items:
                    name = item.get('title') or item.get('name') or ''
                    price = item.get('price') or item.get('last')
                    market_id = str(item.get('id') or item.get('slug') or name)
                    products.append(ProductRecord(site='prediction-market', product_id=market_id, name=name, price=_safe_float(price), url=item.get('url') or url))
            else:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                for card in soup.select('[data-market], article, a'):
                    text = card.get_text(" ", strip=True)
                    if len(text) > 10:
                        products.append(ProductRecord(site='prediction-market', product_id=text[:40], name=text, price=None, url=url))
            logger.info(f"Prediction Market products scraped: {len(products)}")
            return ScrapeResult(products=products).model_dump_json()
        except Exception as e:
            logger.error(f"Prediction Market scrape failed: {e}")
            return json.dumps({"error": f"prediction-market scrape failed: {e}"})


class BrowserScrapeInput(BaseModel):
    url: str = Field(..., description="Page to open in the headless browser")
    selector: str = Field('a, article, div', description="CSS selector to extract text elements")


class BrowserScrapeTool(BaseTool):
    name: str = "browser_scrape"
    description: str = (
        "Use a headless browser to open a page and extract visible text for product detection."
    )
    args_schema: Type[BaseModel] = BrowserScrapeInput

    def _run(self, url: str, selector: str = 'a, article, div') -> str:
        try:
            from browser_use import Browser
            import asyncio

            async def scrape() -> List[str]:
                async with Browser() as browser:
                    page = await browser.get(url)
                    contents = await page.query_selector_all(selector)
                    texts: List[str] = []
                    for el in contents:
                        try:
                            txt = await el.inner_text()
                            if txt and len(txt.strip()) > 10:
                                texts.append(re.sub(r"\s+", " ", txt.strip()))
                        except Exception:
                            continue
                    return texts

            texts = asyncio.run(scrape())
            # Heuristic: turn texts into ProductRecords by picking distinct lines
            seen = set()
            products: List[ProductRecord] = []
            for t in texts[:200]:
                key = _normalize(t)[:80]
                if key in seen:
                    continue
                seen.add(key)
                products.append(ProductRecord(site='browser', product_id=key[:40], name=t[:140], price=None, url=url))
            return ScrapeResult(products=products).model_dump_json()
        except Exception as e:
            return json.dumps({"error": f"browser scrape failed: {e}"})


class MatchProductsInput(BaseModel):
    records: List[ProductRecord]


"""
See guardrails.UnifiedProduct
"""


class MatchProductsTool(BaseTool):
    name: str = "match_products"
    description: str = "Match products across sites by fuzzy name similarity and return unified groups with confidence [0,1]."
    args_schema: Type[BaseModel] = MatchProductsInput

    def _similarity(self, a: str, b: str) -> float:
        a_n = _normalize(a)
        b_n = _normalize(b)
        if not a_n or not b_n:
            return 0.0
        try:
            from rapidfuzz.fuzz import partial_ratio
            return partial_ratio(a_n, b_n) / 100.0
        except Exception:
            from difflib import SequenceMatcher
            return SequenceMatcher(None, a_n, b_n).ratio()

    def _run(self, records: List[ProductRecord]) -> str:
        groups: List[UnifiedProduct] = []
        logger.info(f"Matching {len(records)} product records")
        for rec in records:
            placed = False
            for grp in groups:
                sim = self._similarity(grp.name, rec.name)
                if sim >= 0.78:
                    grp.entries.append(rec)
                    if rec.name not in grp.aliases:
                        grp.aliases.append(rec.name)
                    grp.confidence = min(1.0, max(grp.confidence, sim))
                    placed = True
                    break
            if not placed:
                groups.append(UnifiedProduct(name=rec.name, aliases=[rec.name], entries=[rec], confidence=0.6))
        logger.info(f"Created {len(groups)} unified groups")
        return json.dumps([g.model_dump() for g in groups])


class ToCSVInput(BaseModel):
    groups: List[UnifiedProduct]


class ToCSVTool(BaseTool):
    name: str = "groups_to_csv"
    description: str = "Convert unified product groups to CSV rows: name, site, product_id, price, confidence."
    args_schema: Type[BaseModel] = ToCSVInput

    def _run(self, groups: List[UnifiedProduct]) -> str:
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["name", "site", "product_id", "price", "confidence"])
        for g in groups:
            for e in g.entries:
                writer.writerow([g.name, e.site, e.product_id, _safe_float(e.price), f"{g.confidence:.2f}"])
        return output.getvalue()


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())).strip()


def _safe_float(v) -> Optional[float]:
    try:
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return None
        return float(v)
    except Exception:
        return None
