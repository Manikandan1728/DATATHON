"""Helper script to write scraper.py"""
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


def _delay(lo=1.0, hi=2.5):
    time.sleep(random.uniform(lo, hi))


def _now():
    return datetime.now().isoformat()


def _get(url, params=None, timeout=15):
    """GET with optional ScraperAPI proxy for bot bypass."""
    key = os.getenv("SCRAPER_API_KEY")
    if key:
        import urllib.parse
        proxied = "https://api.scraperapi.com?api_key=" + key + "&url=" + urllib.parse.quote(url, safe="")
        return requests.get(proxied, timeout=timeout)
    return requests.get(url, headers=HEADERS, params=params, timeout=timeout)


def scrape_ebay(query, max_products=8):
    """Scrape eBay - most reliable without any API key."""
    products = []
    try:
        resp = _get("https://www.ebay.com/sch/i.html",
                    params={"_nkw": query, "_sacat": 0, "_sop": 12, "_ipg": 24})
        soup = BeautifulSoup(resp.text, "html.parser")

        # JSON-LD structured data
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if item.get("@type") == "ItemList":
                        for el in item.get("itemListElement", []):
                            p = el.get("item", el)
                            parsed = _parse_jsonld(p, "ebay")
                            if parsed["title"] != "Unknown":
                                products.append(parsed)
                    elif item.get("@type") == "Product":
                        parsed = _parse_jsonld(item, "ebay")
                        if parsed["title"] != "Unknown":
                            products.append(parsed)
            except Exception:
                pass

        # CSS fallback
        if not products:
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
                except Exception:
                    pass

        logger.info("eBay: %d products for '%s'", len(products), query)
    except Exception as e:
        logger.error("eBay error: %s", e)
    return products[:max_products]


def scrape_walmart(query, max_products=8):
    """Scrape Walmart via __NEXT_DATA__ JSON embedded in page."""
    products = []
    try:
        resp = _get("https://www.walmart.com/search", params={"q": query})
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
        logger.info("Walmart: %d products for '%s'", len(products), query)
    except Exception as e:
        logger.error("Walmart error: %s", e)
    return products[:max_products]


def scrape_amazon(query, max_products=6):
    """Amazon scraping - works best with SCRAPER_API_KEY."""
    products = []
    try:
        resp = _get("https://www.amazon.com/s", params={"k": query})
        if resp.status_code != 200:
            logger.warning("Amazon returned %d", resp.status_code)
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


def scrape_amazon_reviews(product_url, max_reviews=15):
    reviews = []
    if not product_url or "amazon.com" not in product_url:
        return reviews
    try:
        _delay()
        resp = _get(product_url)
        soup = BeautifulSoup(resp.text, "html.parser")
        for el in soup.select("span[data-hook='review-body'] span"):
            text = el.get_text(strip=True)
            if len(text) > 20:
                reviews.append(text)
                if len(reviews) >= max_reviews:
                    break
    except Exception as e:
        logger.error("Amazon reviews error: %s", e)
    return reviews


def scrape_via_serpapi(query, max_products=10):
    """Optional SerpAPI - only used if SERPAPI_KEY is set."""
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


def _parse_jsonld(item, source):
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


def scrape_all_sites(query, max_per_site=5):
    """
    Scrape eBay + Walmart (no API key needed) + Amazon (optional).
    Add SCRAPER_API_KEY (free 5000/month at scrapeapi.com) for Amazon.
    Add SERPAPI_KEY for Google Shopping (optional).
    """
    logger.info("Scraping all sites for: '%s'", query)
    all_products = []

    # SerpAPI if available
    if os.getenv("SERPAPI_KEY"):
        products = scrape_via_serpapi(query, max_products=max_per_site * 2)
        if products:
            return products

    # eBay (most reliable, no key needed)
    ebay = scrape_ebay(query, max_per_site)
    all_products.extend(ebay)

    # Walmart
    _delay()
    walmart = scrape_walmart(query, max_per_site)
    all_products.extend(walmart)

    # Amazon (try if we have ScraperAPI key or still need more products)
    if len(all_products) < 3 or os.getenv("SCRAPER_API_KEY"):
        _delay()
        amazon = scrape_amazon(query, max_per_site)
        for p in amazon:
            if p.get("url"):
                p["reviews"] = scrape_amazon_reviews(p["url"], max_reviews=10)
                _delay(0.5, 1.5)
        all_products.extend(amazon)

    logger.info("Total scraped: %d products", len(all_products))
    return all_products
'''

target = os.path.join(os.path.dirname(__file__), 'scraper.py')
with open(target, 'w', encoding='utf-8') as f:
    f.write(code)
print(f"Written {os.path.getsize(target)} bytes to {target}")
