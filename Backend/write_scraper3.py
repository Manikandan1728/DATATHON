"""Writes scraper.py using the correct RapidAPI Real-Time Product Search endpoints."""
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

HEADERS_BROWSER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
}


def _delay(lo=0.3, hi=1.0):
    time.sleep(random.uniform(lo, hi))


def _now():
    return datetime.now().isoformat()


def _rapidapi_headers():
    return {
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY", ""),
        "X-RapidAPI-Host": RAPIDAPI_HOST,
    }


# ── Product Search ────────────────────────────────────────────────────────────
def search_products(query: str, max_products: int = 10) -> List[Dict[str, Any]]:
    """
    RapidAPI Real-Time Product Search - /search endpoint.
    Returns products from Google Shopping across all categories.
    """
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        logger.warning("RAPIDAPI_KEY not set")
        return []

    products = []
    try:
        resp = requests.get(
            "https://real-time-product-search.p.rapidapi.com/search",
            headers=_rapidapi_headers(),
            params={
                "q": query,
                "country": "us",
                "language": "en",
                "limit": str(min(max_products, 10)),
                "sort_by": "BEST_MATCH",
            },
            timeout=25,
        )
        resp.raise_for_status()
        data = resp.json()

        items = data.get("data", [])
        if not items:
            # Some versions return directly as list
            items = data if isinstance(data, list) else []

        for item in items[:max_products]:
            title = item.get("product_title", item.get("title", "Unknown"))
            if not title or title == "Unknown":
                continue

            # Price extraction
            price = "N/A"
            typical_price = item.get("typical_price_range", [])
            if typical_price and isinstance(typical_price, list):
                price = typical_price[0] if typical_price else "N/A"
            elif item.get("offer", {}).get("price"):
                price = item["offer"]["price"]

            # Rating
            rating = item.get("product_rating", item.get("rating", "N/A"))
            num_reviews = item.get("product_num_reviews", item.get("reviews_count", "0"))

            # Reviews from description + highlights
            reviews = []
            desc = item.get("product_description", "")
            if desc and len(desc) > 20:
                # Split description into sentences as pseudo-reviews
                sentences = [s.strip() for s in re.split(r'[.!?]', desc) if len(s.strip()) > 15]
                reviews.extend(sentences[:5])
            for h in item.get("product_highlights", [])[:5]:
                if len(h) > 10:
                    reviews.append(h)

            products.append({
                "source": "google_shopping",
                "title": title,
                "url": item.get("product_page_url", item.get("url", "")),
                "price": str(price),
                "rating": str(rating),
                "num_reviews": str(num_reviews),
                "reviews": reviews,
                "scraped_at": _now(),
            })

        logger.info("RapidAPI search: %d products for '%s'", len(products), query)
    except requests.exceptions.HTTPError as e:
        logger.error("RapidAPI HTTP error %s: %s", e.response.status_code, e.response.text[:200])
    except Exception as e:
        logger.error("RapidAPI search error: %s", e)

    return products


# ── Product Reviews ───────────────────────────────────────────────────────────
def fetch_product_reviews(product_id: str, max_reviews: int = 15) -> List[str]:
    """
    Fetch reviews for a specific product using RapidAPI /product-reviews endpoint.
    """
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key or not product_id:
        return []

    reviews = []
    try:
        resp = requests.get(
            "https://real-time-product-search.p.rapidapi.com/product-reviews",
            headers=_rapidapi_headers(),
            params={
                "product_id": product_id,
                "country": "us",
                "language": "en",
                "limit": str(min(max_reviews, 20)),
                "sort_by": "TOP_REVIEWS",
            },
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        for review in data.get("data", [])[:max_reviews]:
            body = review.get("review_text", review.get("body", ""))
            if body and len(body) > 15:
                reviews.append(body[:400])
        logger.info("RapidAPI reviews: %d for product %s", len(reviews), product_id[:20])
    except Exception as e:
        logger.error("RapidAPI reviews error: %s", e)

    return reviews


# ── Product Details (for richer data) ────────────────────────────────────────
def fetch_product_details(product_id: str) -> Dict[str, Any]:
    """Fetch detailed product info including specs and offers."""
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key or not product_id:
        return {}
    try:
        resp = requests.get(
            "https://real-time-product-search.p.rapidapi.com/product-details",
            headers=_rapidapi_headers(),
            params={"product_id": product_id, "country": "us", "language": "en"},
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json().get("data", {})
    except Exception as e:
        logger.error("RapidAPI details error: %s", e)
        return {}


# ── Direct eBay fallback ──────────────────────────────────────────────────────
def scrape_ebay_direct(query: str, max_products: int = 6) -> List[Dict[str, Any]]:
    """Direct eBay scraping fallback when no API key."""
    products = []
    try:
        session = requests.Session()
        session.headers.update(HEADERS_BROWSER)
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
        logger.info("eBay direct: %d products", len(products))
    except Exception as e:
        logger.error("eBay error: %s", e)
    return products[:max_products]


# ── Direct Walmart fallback ───────────────────────────────────────────────────
def scrape_walmart_direct(query: str, max_products: int = 6) -> List[Dict[str, Any]]:
    """Direct Walmart scraping fallback."""
    products = []
    try:
        session = requests.Session()
        session.headers.update(HEADERS_BROWSER)
        resp = session.get("https://www.walmart.com/search", params={"q": query}, timeout=15)
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
        logger.info("Walmart direct: %d products", len(products))
    except Exception as e:
        logger.error("Walmart error: %s", e)
    return products[:max_products]


# ── MAIN ENTRY POINT ──────────────────────────────────────────────────────────
def scrape_all_sites(query: str, max_per_site: int = 5) -> List[Dict[str, Any]]:
    """
    Primary: RapidAPI Real-Time Product Search (free 200/month)
    Fallback: Direct eBay + Walmart scraping
    """
    logger.info("Scraping: '%s'", query)
    all_products = []

    # Primary: RapidAPI
    if os.getenv("RAPIDAPI_KEY"):
        products = search_products(query, max_products=max_per_site * 2)
        if products:
            # Enrich with reviews for top products
            for p in products[:5]:
                if not p["reviews"]:
                    # Extract product_id from URL if possible
                    url = p.get("url", "")
                    pid_match = re.search(r'product[_-]?id[=:]([^&\s]+)', url, re.IGNORECASE)
                    if pid_match:
                        p["reviews"] = fetch_product_reviews(pid_match.group(1), max_reviews=10)
                        _delay(0.2, 0.5)
            logger.info("Total via RapidAPI: %d products", len(products))
            return products

    # Fallback: direct scraping
    logger.info("No RAPIDAPI_KEY - trying direct scraping...")
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
