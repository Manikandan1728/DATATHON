"""Writes final scraper.py with RapidAPI primary + robust direct fallback."""
import os

code = r'''import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import re
import time
import json
import random
import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RAPIDAPI_HOST = "real-time-product-search.p.rapidapi.com"

# Rotate user agents to avoid blocks
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]


def _headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
    }


def _delay(lo=1.0, hi=2.5):
    time.sleep(random.uniform(lo, hi))


def _now():
    return datetime.now().isoformat()


# ── PRIMARY: RapidAPI Real-Time Product Search ────────────────────────────────
def search_via_rapidapi(query: str, max_products: int = 10) -> List[Dict[str, Any]]:
    """
    RapidAPI Real-Time Product Search - FREE 200/month.
    Subscribe at: https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-product-search
    """
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        return []

    products = []
    try:
        resp = requests.get(
            "https://real-time-product-search.p.rapidapi.com/search",
            headers={
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": RAPIDAPI_HOST,
            },
            params={
                "q": query,
                "country": "us",
                "language": "en",
                "limit": str(min(max_products, 10)),
                "sort_by": "BEST_MATCH",
            },
            timeout=25,
        )

        if resp.status_code == 429:
            logger.warning("RapidAPI rate limited - waiting 2s and retrying")
            time.sleep(2)
            resp = requests.get(resp.url, headers=resp.request.headers, timeout=25)

        resp.raise_for_status()
        data = resp.json()
        items = data.get("data", [])

        for item in items[:max_products]:
            title = item.get("product_title", item.get("title", ""))
            if not title:
                continue

            # Price
            price = "N/A"
            price_range = item.get("typical_price_range", [])
            if price_range:
                price = price_range[0]
            elif item.get("offer", {}).get("price"):
                price = str(item["offer"]["price"])

            # Reviews from description + highlights
            reviews = []
            desc = item.get("product_description", "")
            if desc and len(desc) > 20:
                sentences = [s.strip() for s in re.split(r'[.!?]', desc) if len(s.strip()) > 15]
                reviews.extend(sentences[:4])
            for h in item.get("product_highlights", [])[:5]:
                if len(h) > 10:
                    reviews.append(h)

            products.append({
                "source": "google_shopping",
                "title": title,
                "url": item.get("product_page_url", ""),
                "price": str(price),
                "rating": str(item.get("product_rating", "N/A")),
                "num_reviews": str(item.get("product_num_reviews", "0")),
                "reviews": reviews,
                "scraped_at": _now(),
            })

        logger.info("RapidAPI: %d products for '%s'", len(products), query)
    except requests.exceptions.HTTPError as e:
        logger.error("RapidAPI error %s: %s", e.response.status_code, e.response.text[:150])
    except Exception as e:
        logger.error("RapidAPI error: %s", e)

    return products


# ── FALLBACK 1: eBay direct ───────────────────────────────────────────────────
def scrape_ebay(query: str, max_products: int = 8) -> List[Dict[str, Any]]:
    products = []
    try:
        session = requests.Session()
        session.headers.update(_headers())
        resp = session.get(
            "https://www.ebay.com/sch/i.html",
            params={"_nkw": query, "_sacat": 0, "_sop": 12, "_ipg": 24},
            timeout=15,
        )
        soup = BeautifulSoup(resp.text, "html.parser")

        for card in soup.select(".s-item"):
            try:
                title_el = card.select_one(".s-item__title")
                price_el = card.select_one(".s-item__price")
                link_el = card.select_one("a.s-item__link")
                title = title_el.get_text(strip=True) if title_el else ""
                if not title or title.lower() == "shop on ebay":
                    continue
                products.append({
                    "source": "ebay",
                    "title": title,
                    "url": link_el["href"].split("?")[0] if link_el else "",
                    "price": price_el.get_text(strip=True) if price_el else "N/A",
                    "rating": "N/A",
                    "num_reviews": "0",
                    "reviews": [],
                    "scraped_at": _now(),
                })
                if len(products) >= max_products:
                    break
            except Exception:
                pass

        logger.info("eBay: %d products for '%s'", len(products), query)
    except Exception as e:
        logger.error("eBay error: %s", e)
    return products[:max_products]


# ── FALLBACK 2: Walmart direct ────────────────────────────────────────────────
def scrape_walmart(query: str, max_products: int = 8) -> List[Dict[str, Any]]:
    products = []
    try:
        session = requests.Session()
        session.headers.update(_headers())
        resp = session.get(
            "https://www.walmart.com/search",
            params={"q": query},
            timeout=15,
        )
        match = re.search(r"__NEXT_DATA__\s*=\s*(\{.+?\})\s*;?\s*</script>", resp.text, re.DOTALL)
        if match:
            page_data = json.loads(match.group(1))
            stacks = (
                page_data.get("props", {}).get("pageProps", {})
                .get("initialData", {}).get("searchResult", {})
                .get("itemStacks", [])
            )
            for stack in stacks:
                for item in stack.get("items", []):
                    name = item.get("name", "")
                    if not name:
                        continue
                    price_info = item.get("priceInfo", {}) or {}
                    current = price_info.get("currentPrice", {}) or {}
                    products.append({
                        "source": "walmart",
                        "title": name,
                        "url": "https://www.walmart.com" + (item.get("canonicalUrl") or ""),
                        "price": str(current.get("price", "N/A")),
                        "rating": str(item.get("averageRating", "N/A")),
                        "num_reviews": str(item.get("numberOfReviews", "0")),
                        "reviews": [],
                        "scraped_at": _now(),
                    })
                    if len(products) >= max_products:
                        break
        logger.info("Walmart: %d products for '%s'", len(products), query)
    except Exception as e:
        logger.error("Walmart error: %s", e)
    return products[:max_products]


# ── FALLBACK 3: Amazon direct ─────────────────────────────────────────────────
def scrape_amazon(query: str, max_products: int = 6) -> List[Dict[str, Any]]:
    products = []
    try:
        session = requests.Session()
        session.headers.update(_headers())
        # Get cookies first
        session.get("https://www.amazon.com", timeout=10)
        _delay(1, 2)
        resp = session.get(
            "https://www.amazon.com/s",
            params={"k": query, "ref": "nb_sb_noss"},
            timeout=15,
        )
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        for card in soup.select("div[data-component-type='s-search-result']")[:max_products]:
            try:
                title_el = card.select_one("h2 a span")
                link_el = card.select_one("h2 a")
                price_el = card.select_one("span.a-price span.a-offscreen")
                rating_el = card.select_one("span.a-icon-alt")
                reviews_el = card.select_one("span.a-size-base.s-underline-text")
                title = title_el.get_text(strip=True) if title_el else ""
                if not title:
                    continue
                products.append({
                    "source": "amazon",
                    "title": title,
                    "url": "https://www.amazon.com" + link_el["href"] if link_el else "",
                    "price": price_el.get_text(strip=True) if price_el else "N/A",
                    "rating": rating_el.get_text(strip=True) if rating_el else "N/A",
                    "num_reviews": reviews_el.get_text(strip=True) if reviews_el else "0",
                    "reviews": [],
                    "scraped_at": _now(),
                })
            except Exception:
                pass
        logger.info("Amazon: %d products for '%s'", len(products), query)
    except Exception as e:
        logger.error("Amazon error: %s", e)
    return products[:max_products]


# ── MAIN ENTRY POINT ──────────────────────────────────────────────────────────
def scrape_all_sites(query: str, max_per_site: int = 5) -> List[Dict[str, Any]]:
    """
    1. RapidAPI (primary - free 200/month, subscribe at rapidapi.com)
    2. eBay direct fallback
    3. Walmart direct fallback
    4. Amazon direct fallback
    """
    logger.info("Scraping: '%s'", query)
    all_products = []

    # Primary: RapidAPI
    if os.getenv("RAPIDAPI_KEY"):
        products = search_via_rapidapi(query, max_products=max_per_site * 2)
        if products:
            logger.info("Returning %d products from RapidAPI", len(products))
            return products
        logger.warning("RapidAPI returned 0 products - falling back to direct scraping")

    # Fallback: direct scraping
    logger.info("Trying direct scraping (eBay + Walmart + Amazon)...")

    ebay = scrape_ebay(query, max_per_site)
    all_products.extend(ebay)

    _delay()
    walmart = scrape_walmart(query, max_per_site)
    all_products.extend(walmart)

    if len(all_products) < 3:
        _delay()
        amazon = scrape_amazon(query, max_per_site)
        all_products.extend(amazon)

    logger.info("Total scraped: %d products", len(all_products))
    return all_products
'''

target = os.path.join(os.path.dirname(__file__), 'scraper.py')
with open(target, 'w', encoding='utf-8') as f:
    f.write(code)
print(f"Written {os.path.getsize(target)} bytes to {target}")
