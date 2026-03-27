"""Writes the new scraper.py using RapidAPI Real-Time Product Search."""
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

# Auto-load .env
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
}


def _delay(lo=0.5, hi=1.5):
    time.sleep(random.uniform(lo, hi))


def _now():
    return datetime.now().isoformat()


# ── PRIMARY: RapidAPI Real-Time Product Search (FREE 200/month) ───────────────
def scrape_via_rapidapi(query: str, max_products: int = 10) -> List[Dict[str, Any]]:
    """
    Uses RapidAPI 'Real-Time Product Search' - FREE 200 requests/month.
    Get key at: https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-product-search
    Sign up free at rapidapi.com, subscribe to Basic (free) plan.
    """
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        logger.info("RAPIDAPI_KEY not set - skipping RapidAPI")
        return []

    products = []
    try:
        resp = requests.get(
            "https://real-time-product-search.p.rapidapi.com/search",
            headers={
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": "real-time-product-search.p.rapidapi.com",
            },
            params={
                "q": query,
                "country": "us",
                "language": "en",
                "limit": str(max_products),
            },
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("data", [])[:max_products]:
            # Extract price
            price = "N/A"
            offers = item.get("offers", {})
            if isinstance(offers, dict):
                price = offers.get("price", "N/A")
            elif isinstance(offers, list) and offers:
                price = offers[0].get("price", "N/A")

            # Extract rating
            rating = item.get("product_rating", "N/A")
            num_reviews = item.get("product_num_reviews", "0")

            # Extract reviews from description/highlights
            reviews = []
            desc = item.get("product_description", "")
            if desc and len(desc) > 20:
                reviews.append(desc[:300])
            for highlight in item.get("product_highlights", [])[:5]:
                if len(highlight) > 10:
                    reviews.append(highlight)

            products.append({
                "source": "rapidapi_shopping",
                "title": item.get("product_title", "Unknown"),
                "url": item.get("product_page_url", ""),
                "price": str(price),
                "rating": str(rating),
                "num_reviews": str(num_reviews),
                "reviews": reviews,
                "scraped_at": _now(),
            })

        logger.info("RapidAPI: %d products for '%s'", len(products), query)
    except Exception as e:
        logger.error("RapidAPI error: %s", e)

    return products


# ── SECONDARY: RapidAPI Amazon Search (FREE tier available) ───────────────────
def scrape_via_rapidapi_amazon(query: str, max_products: int = 8) -> List[Dict[str, Any]]:
    """
    Uses RapidAPI 'Amazon Product Search' - FREE tier available.
    Get key at: https://rapidapi.com/search/amazon
    Same RAPIDAPI_KEY works for multiple APIs.
    """
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        return []

    products = []
    try:
        resp = requests.get(
            "https://amazon-product-search1.p.rapidapi.com/search",
            headers={
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": "amazon-product-search1.p.rapidapi.com",
            },
            params={"query": query, "country": "US"},
            timeout=20,
        )
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get("products", [])[:max_products]:
                products.append({
                    "source": "amazon",
                    "title": item.get("title", "Unknown"),
                    "url": item.get("url", ""),
                    "price": item.get("price", {}).get("current_price", "N/A") if isinstance(item.get("price"), dict) else str(item.get("price", "N/A")),
                    "rating": str(item.get("stars", "N/A")),
                    "num_reviews": str(item.get("num_ratings", "0")),
                    "reviews": [],
                    "scraped_at": _now(),
                })
            logger.info("RapidAPI Amazon: %d products", len(products))
    except Exception as e:
        logger.error("RapidAPI Amazon error: %s", e)

    return products


# ── TERTIARY: SerpAPI (optional, if user has it) ──────────────────────────────
def scrape_via_serpapi(query: str, max_products: int = 10) -> List[Dict[str, Any]]:
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return []
    products = []
    try:
        resp = requests.get("https://serpapi.com/search", params={
            "engine": "google_shopping", "q": query,
            "api_key": api_key, "num": max_products, "gl": "us", "hl": "en",
        }, timeout=20)
        resp.raise_for_status()
        for item in resp.json().get("shopping_results", [])[:max_products]:
            products.append({
                "source": item.get("source", "google_shopping"),
                "title": item.get("title", "Unknown"),
                "url": item.get("link", ""),
                "price": item.get("price", "N/A"),
                "rating": str(item.get("rating", "N/A")),
                "num_reviews": str(item.get("reviews", "0")),
                "reviews": [],
                "scraped_at": _now(),
            })
        logger.info("SerpAPI: %d products", len(products))
    except Exception as e:
        logger.error("SerpAPI error: %s", e)
    return products


# ── FALLBACK: Direct eBay scraping ────────────────────────────────────────────
def scrape_ebay_direct(query: str, max_products: int = 8) -> List[Dict[str, Any]]:
    """Direct eBay scraping - works when not blocked."""
    products = []
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        resp = session.get(
            "https://www.ebay.com/sch/i.html",
            params={"_nkw": query, "_sacat": 0, "_sop": 12, "_ipg": 24},
            timeout=15,
        )
        soup = BeautifulSoup(resp.text, "html.parser")

        # CSS selector approach (most reliable for eBay)
        for card in soup.select(".s-item"):
            try:
                title_el = card.select_one(".s-item__title")
                price_el = card.select_one(".s-item__price")
                link_el = card.select_one("a.s-item__link")
                title = title_el.get_text(strip=True) if title_el else ""
                if not title or title.lower() in ("shop on ebay", ""):
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

        logger.info("eBay direct: %d products for '%s'", len(products), query)
    except Exception as e:
        logger.error("eBay direct error: %s", e)
    return products[:max_products]


# ── FALLBACK: Direct Walmart scraping ────────────────────────────────────────
def scrape_walmart_direct(query: str, max_products: int = 8) -> List[Dict[str, Any]]:
    """Direct Walmart scraping via __NEXT_DATA__ JSON."""
    products = []
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        resp = session.get(
            "https://www.walmart.com/search",
            params={"q": query},
            timeout=15,
        )
        match = re.search(r"__NEXT_DATA__\s*=\s*(\{.+?\})\s*;?\s*</script>", resp.text, re.DOTALL)
        if match:
            page_data = json.loads(match.group(1))
            stacks = (
                page_data.get("props", {})
                .get("pageProps", {})
                .get("initialData", {})
                .get("searchResult", {})
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
        logger.info("Walmart direct: %d products for '%s'", len(products), query)
    except Exception as e:
        logger.error("Walmart direct error: %s", e)
    return products[:max_products]


def _parse_jsonld(item: dict, source: str) -> Dict[str, Any]:
    offers = item.get("offers", {})
    if isinstance(offers, list):
        offers = offers[0] if offers else {}
    agg = item.get("aggregateRating", {})
    return {
        "source": source,
        "title": item.get("name", "Unknown"),
        "url": item.get("url", offers.get("url", "")),
        "price": str(offers.get("price", "N/A")),
        "rating": str(agg.get("ratingValue", "N/A")),
        "num_reviews": str(agg.get("reviewCount", "0")),
        "reviews": [],
        "scraped_at": _now(),
    }


# ── MAIN ENTRY POINT ──────────────────────────────────────────────────────────
def scrape_all_sites(query: str, max_per_site: int = 5) -> List[Dict[str, Any]]:
    """
    Scrape products from multiple sources.
    Priority:
      1. RapidAPI Real-Time Product Search (FREE 200/month - best option)
      2. SerpAPI Google Shopping (FREE 100/month - optional)
      3. eBay direct (no key, may be blocked)
      4. Walmart direct (no key, may be blocked)
    """
    logger.info("Scraping all sites for: '%s'", query)
    all_products = []

    # 1. RapidAPI (recommended free option)
    if os.getenv("RAPIDAPI_KEY"):
        products = scrape_via_rapidapi(query, max_products=max_per_site * 2)
        if products:
            all_products.extend(products)
            logger.info("Got %d products via RapidAPI", len(all_products))
            return all_products
        # Try Amazon via RapidAPI as fallback
        amazon = scrape_via_rapidapi_amazon(query, max_per_site)
        all_products.extend(amazon)
        if all_products:
            return all_products

    # 2. SerpAPI (if available)
    if os.getenv("SERPAPI_KEY"):
        products = scrape_via_serpapi(query, max_products=max_per_site * 2)
        if products:
            return products

    # 3. Direct scraping fallbacks
    logger.info("No API keys set - trying direct scraping...")
    ebay = scrape_ebay_direct(query, max_per_site)
    all_products.extend(ebay)

    _delay()
    walmart = scrape_walmart_direct(query, max_per_site)
    all_products.extend(walmart)

    logger.info("Total scraped: %d products", len(all_products))
    return all_products
'''

target = os.path.join(os.path.dirname(__file__), 'scraper.py')
with open(target, 'w', encoding='utf-8') as f:
    f.write(code)
print(f"Written {os.path.getsize(target)} bytes to {target}")
