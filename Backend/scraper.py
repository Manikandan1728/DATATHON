import sys

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



PRODUCT_COMPONENTS = {

    "stand mixer": ["bowl", "dough hook", "whisk", "beater", "motor", "housing", "controls", "cord"],

    "hand mixer": ["beaters", "motor", "housing", "controls", "cord"],

    "immersion blender": ["blades", "motor", "housing", "controls", "cord"],

    "blender": ["blades", "motor", "pitcher", "lid", "controls", "cord"],

    "food processor": ["motor", "blades", "discs", "bowl", "lid", "controls", "feed tube", "pulse button", "safety lock"],

    "coffee maker": ["water reservoir", "heating element", "pump", "filter basket", "brewing chamber", "carafe", "power cord", "controls", "drip tray", "warming plate"],

    "coffee machine": ["water reservoir", "heating element", "pump", "control panel", "valve", "brew basket", "coffee grounds container", "drip tray", "display screen", "buttons"],

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





def search_products(query: str, max_products: int = 10) -> List[Dict[str, Any]]:

    """

    RapidAPI Real-Time Product Search - /search-light endpoint.

    Returns real products from Google Shopping across all categories.

    """

    api_key = os.getenv("RAPIDAPI_KEY")

    if not api_key:

        logger.warning("RAPIDAPI_KEY not set")

        return []



    products = []

    try:

        resp = requests.get(

            f"https://{RAPIDAPI_HOST}/search-light",

            headers=_rapidapi_headers(),

            params={

                "q": query,

                "country": "us",

                "language": "en",

                "limit": str(min(max_products, 10)),

            },

            timeout=25,

        )

        resp.raise_for_status()

        data = resp.json()



        # data.data.products is the correct path

        items = []

        raw_data = data.get("data", {})

        if isinstance(raw_data, dict):

            items = raw_data.get("products", [])

        elif isinstance(raw_data, list):

            items = raw_data



        for item in items[:max_products]:

            title = item.get("product_title", "Unknown")

            if not title or title == "Unknown":

                continue



            price = item.get("price", "N/A")

            rating = item.get("product_rating", "N/A")

            num_reviews = item.get("product_num_reviews", 0)

            store = item.get("store_name", "google_shopping")

            product_id = item.get("product_id", "")

            url = item.get("product_offer_page_url", "") or ""



            # Build synthetic reviews from available text fields

            reviews = []

            desc = item.get("product_description", "")

            if desc and len(desc) > 20:

                sentences = [s.strip() for s in re.split(r'[.!?]', desc) if len(s.strip()) > 15]

                reviews.extend(sentences[:5])

            for h in item.get("product_highlights", [])[:5]:

                if len(h) > 10:

                    reviews.append(h)



            products.append({

                "source": store.lower().replace(" ", "_") if store else "google_shopping",

                "title": title,

                "url": url,

                "price": str(price),

                "rating": str(rating),

                "num_reviews": str(num_reviews),

                "product_id": product_id,

                "reviews": reviews,

                "scraped_at": _now(),

            })



        logger.info("RapidAPI search-light: %d products for '%s'", len(products), query)

    except requests.exceptions.HTTPError as e:

        logger.error("RapidAPI HTTP %s: %s", e.response.status_code, e.response.text[:200])

        # Check if it's a quota exceeded error

        if "quota" in e.response.text.lower() or "exceeded" in e.response.text.lower():

            logger.warning("RapidAPI quota exceeded, falling back to direct scraping")

            return []  # Return empty to trigger fallback

    except Exception as e:

        logger.error("RapidAPI search error: %s", e)



    return products





def fetch_product_reviews(product_id: str, max_reviews: int = 15) -> List[str]:

    """Fetch reviews for a product via RapidAPI /product-reviews endpoint."""

    api_key = os.getenv("RAPIDAPI_KEY")

    if not api_key or not product_id:

        return []

    reviews = []

    try:

        resp = requests.get(

            f"https://{RAPIDAPI_HOST}/product-reviews",

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

        raw = data.get("data", {})

        review_list = raw.get("reviews", []) if isinstance(raw, dict) else []

        for r in review_list[:max_reviews]:

            body = r.get("review_text", r.get("body", r.get("text", "")))

            if body and len(body) > 15:

                reviews.append(body[:400])

        logger.info("Real reviews fetched: %d for product %s", len(reviews), product_id)

    except Exception as e:

        logger.debug("Reviews fetch error (non-critical): %s", e)

    return reviews





def scrape_ebay_direct(query: str, max_products: int = 6) -> List[Dict[str, Any]]:

    """Direct eBay fallback when no API key."""

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





def scrape_walmart_direct(query: str, max_products: int = 6) -> List[Dict[str, Any]]:

    """Direct Walmart fallback."""

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





def generate_realistic_brands_ai(product: str) -> List[Dict[str, Any]]:

    """Generate realistic brands using AI when no predefined category matches."""

    try:

        # Load environment variables

        try:

            from dotenv import load_dotenv

            load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

        except ImportError:

            pass

        

        groq_key = os.getenv("GROQ_API_KEY")

        openai_key = os.getenv("OPENAI_API_KEY")

        

        brands_text = ""

        

        if groq_key:

            from groq import Groq

            client = Groq(api_key=groq_key)

            

            response = client.chat.completions.create(

                model="llama-3.3-70b-versatile",

                messages=[{

                    "role": "user",

                    "content": f"List 10 real brands that sell {product}. Return only brand names, one per line."

                }]

            )

            brands_text = response.choices[0].message.content

            

        elif openai_key:

            from openai import OpenAI

            client = OpenAI(api_key=openai_key)

            

            response = client.chat.completions.create(

                model="gpt-4o-mini",

                messages=[{

                    "role": "user", 

                    "content": f"List 10 real brands that sell {product}. Return only brand names, one per line."

                }]

            )

            brands_text = response.choices[0].message.content

        

        # Process the AI response

        brands = []

        for line in brands_text.split('\n'):

            line = line.strip()

            # Remove numbering and bullet points

            line = re.sub(r'^[\d\.\-\*\s]+', '', line)

            # Remove quotes
            line = line.strip('"\'')

            if line and len(line) > 1:

                brands.append(line)

        

        brands = brands[:10]  # Limit to 10 brands

        

        # Create product templates from AI-generated brands

        templates = []

        for i, brand in enumerate(brands):

            # Generate reasonable price ranges based on product type

            if any(food_word in product.lower() for food_word in ['food', 'fruit', 'mango', 'banana', 'apple']):

                price_range = (2, 15)  # Food items are cheaper

            elif any(electronic_word in product.lower() for electronic_word in ['laptop', 'phone', 'computer']):

                price_range = (200, 2000)  # Electronics are expensive

            else:

                price_range = (10, 200)  # Default mid-range

            

            templates.append({

                "brand": brand,

                "model": f"{brand.title()} {product.title()} Edition",

                "price_range": price_range

            })

        

        return templates

        

    except Exception as e:

        logger.error(f"AI brand generation failed: {e}")

        # Fallback to generic but more realistic brands

        return [

            {"brand": "Premium Select", "model": f"Premium {product.title()}", "price_range": (20, 50)},

            {"brand": "Quality First", "model": f"Quality {product.title()}", "price_range": (15, 40)},

            {"brand": "Best Choice", "model": f"Best {product.title()}", "price_range": (10, 30)},

            {"brand": "Value Plus", "model": f"Value {product.title()}", "price_range": (8, 25)},

            {"brand": "Pro Grade", "model": f"Professional {product.title()}", "price_range": (25, 60)},

        ]





def generate_sample_products(query: str, max_products: int = 5) -> List[Dict[str, Any]]:

    """Generate realistic sample products when all scraping methods fail."""

    import random

    

    # Sample product templates for different categories

    templates = {

        "laptop": [

            {"brand": "Dell", "model": "XPS 13", "price_range": (800, 1200)},

            {"brand": "HP", "model": "Pavilion 15", "price_range": (600, 900)},

            {"brand": "Lenovo", "model": "ThinkPad X1", "price_range": (1000, 1500)},

            {"brand": "Asus", "model": "ZenBook 14", "price_range": (700, 1000)},

            {"brand": "Apple", "model": "MacBook Air M2", "price_range": (1100, 1400)},

            {"brand": "Microsoft", "model": "Surface Laptop 5", "price_range": (900, 1300)},

            {"brand": "Acer", "model": "Swift 5", "price_range": (650, 950)},

            {"brand": "MSI", "model": "GF63 Thin", "price_range": (700, 1100)},

            {"brand": "Razer", "model": "Blade 15", "price_range": (1200, 1800)},

            {"brand": "LG", "model": "Gram 16", "price_range": (1000, 1400)},

        ],

        "phone": [

            {"brand": "Samsung", "model": "Galaxy S23", "price_range": (700, 1000)},

            {"brand": "Apple", "model": "iPhone 14", "price_range": (800, 1200)},

            {"brand": "Google", "model": "Pixel 7", "price_range": (600, 900)},

            {"brand": "OnePlus", "model": "11 Pro", "price_range": (500, 800)},

            {"brand": "Xiaomi", "model": "13 Pro", "price_range": (400, 700)},

            {"brand": "Sony", "model": "Xperia 1 V", "price_range": (900, 1300)},

            {"brand": "Motorola", "model": "Edge 40", "price_range": (450, 700)},

            {"brand": "Oppo", "model": "Find X5", "price_range": (550, 850)},

            {"brand": "Vivo", "model": "X90 Pro", "price_range": (600, 900)},

            {"brand": "Realme", "model": "GT 3", "price_range": (400, 650)},

        ],

        "knife": [

            {"brand": "Wüsthof", "model": "Classic Chef Knife", "price_range": (100, 200)},

            {"brand": "Victorinox", "model": "Fibrox Pro Chef Knife", "price_range": (40, 80)},

            {"brand": "Shun", "model": "Classic Chef Knife", "price_range": (150, 250)},

            {"brand": "Zwilling", "model": "Four Star Chef Knife", "price_range": (80, 150)},

            {"brand": "Global", "model": "G-2 Chef Knife", "price_range": (120, 180)},

            {"brand": "Henckels", "model": "Classic Chef Knife", "price_range": (70, 130)},

            {"brand": "Mercer", "model": "Renaissance Chef Knife", "price_range": (50, 100)},

            {"brand": "Dalstrong", "model": "Gladiator Series", "price_range": (90, 160)},

            {"brand": "Mac", "model": "Professional Chef Knife", "price_range": (130, 200)},

            {"brand": "Miyabi", "model": "Kaizen Chef Knife", "price_range": (140, 220)},

        ],

        "makeup": [

            {"brand": "MAC", "model": "Studio Fix Foundation", "price_range": (25, 35)},

            {"brand": "Maybelline", "model": "Fit Me Foundation", "price_range": (8, 15)},

            {"brand": "Estée Lauder", "model": "Double Wear Foundation", "price_range": (40, 55)},

            {"brand": "Fenty Beauty", "model": "Pro Filt'r Foundation", "price_range": (30, 40)},

            {"brand": "NARS", "model": "Natural Radiant Foundation", "price_range": (35, 45)},

            {"brand": "L'Oréal", "model": "True Match Foundation", "price_range": (12, 20)},

            {"brand": "Clinique", "model": "Even Better Foundation", "price_range": (28, 38)},

            {"brand": "Urban Decay", "model": "Naked Skin Foundation", "price_range": (32, 42)},

            {"brand": "Smashbox", "model": "Studio Skin Foundation", "price_range": (35, 45)},

            {"brand": "Bobbi Brown", "model": "Skin Foundation Stick", "price_range": (48, 58)},

        ],

        "coffee": [

            {"brand": "Breville", "model": "Barista Express", "price_range": (600, 800)},

            {"brand": "De'Longhi", "model": "EC155", "price_range": (100, 150)},

            {"brand": "Nespresso", "model": "Vertuo Plus", "price_range": (200, 300)},

            {"brand": "Keurig", "model": "K-Elite", "price_range": (150, 250)},

            {"brand": "Cuisinart", "model": "DCC-3200", "price_range": (80, 120)},

            {"brand": "Mr. Coffee", "model": "Easy Measure", "price_range": (40, 60)},

            {"brand": "Bunn", "model": "Velocity Brew", "price_range": (150, 200)},

            {"brand": "Technivorm", "model": "Moccamaster", "price_range": (300, 400)},

            {"brand": "Bonavita", "model": "BV1900TS", "price_range": (150, 200)},

            {"brand": "Gaggia", "model": "Classic Pro", "price_range": (400, 600)},

        ],

        "food": [

            {"brand": "Dole", "model": "Fresh Sliced Mango", "price_range": (3, 6)},

            {"brand": "Del Monte", "model": "Premium Mango Chunks", "price_range": (4, 7)},

            {"brand": "Goya", "model": "Mango in Syrup", "price_range": (2, 4)},

            {"brand": "Nature's Promise", "model": "Organic Mango Slices", "price_range": (5, 8)},

            {"brand": "Great Value", "model": "Frozen Mango Pieces", "price_range": (3, 5)},

            {"brand": "Private Selection", "model": "Fresh Mango Halves", "price_range": (6, 9)},

            {"brand": "Kirkland Signature", "model": "Bulk Frozen Mango", "price_range": (8, 12)},

            {"brand": "Sunfresh", "model": "Ripe Mango Cups", "price_range": (4, 6)},

            {"brand": "Tropical Sun", "model": "Dried Mango Slices", "price_range": (5, 8)},

            {"brand": "Mango Queen", "model": "Fresh Whole Mangoes", "price_range": (2, 4)},

        ],

        "fruit": [

            {"brand": "Dole", "model": "Fresh Fruit Mix", "price_range": (4, 7)},

            {"brand": "Del Monte", "model": "Fruit Cup", "price_range": (3, 5)},

            {"brand": "Chiquita", "model": "Fresh Bananas", "price_range": (2, 3)},

            {"brand": "Dole", "model": "Pineapple Chunks", "price_range": (3, 6)},

            {"brand": "Fresh Express", "model": "Berry Mix", "price_range": (5, 8)},

            {"brand": "Nature's Basket", "model": "Organic Apples", "price_range": (4, 7)},

            {"brand": "Good & Gather", "model": "Fresh Grapes", "price_range": (3, 5)},

            {"brand": "Simple Truth", "model": "Organic Strawberries", "price_range": (5, 8)},

            {"brand": "Green Giant", "model": "Fruit Medley", "price_range": (3, 6)},

            {"brand": "Sunshine Harvest", "model": "Tropical Mix", "price_range": (6, 9)},

        ],

        "default": [

            {"brand": "Generic", "model": "Pro Model X1", "price_range": (100, 500)},

            {"brand": "Premium", "model": "Elite Series", "price_range": (200, 800)},

            {"brand": "Budget", "model": "Basic Edition", "price_range": (50, 200)},

            {"brand": "Professional", "model": "Expert Version", "price_range": (300, 1000)},

            {"brand": "Ultra", "model": "Max Performance", "price_range": (500, 1500)},

            {"brand": "Standard", "model": "Classic Line", "price_range": (150, 400)},

            {"brand": "Advanced", "model": "Tech Pro", "price_range": (250, 600)},

            {"brand": "Deluxe", "model": "Luxury Edition", "price_range": (400, 900)},

            {"brand": "Economy", "model": "Value Pack", "price_range": (80, 180)},

            {"brand": "Signature", "model": "Limited Edition", "price_range": (600, 1200)},

        ]

    }

    

    # Determine category

    query_lower = query.lower()

    if "laptop" in query_lower or "notebook" in query_lower:

        category = "laptop"

    elif "phone" in query_lower or "smartphone" in query_lower:

        category = "phone"

    elif "knife" in query_lower or "knives" in query_lower or "chef" in query_lower:

        category = "knife"

    elif "makeup" in query_lower or "cosmetic" in query_lower or "foundation" in query_lower or "lipstick" in query_lower:

        category = "makeup"

    elif "coffee" in query_lower or "espresso" in query_lower or "cappuccino" in query_lower or "latte" in query_lower:

        category = "coffee"

    elif "mango" in query_lower or "banana" in query_lower or "apple" in query_lower or "orange" in query_lower or "fruit" in query_lower:

        category = "fruit"

    elif "food" in query_lower or "snack" in query_lower or "grocery" in query_lower or "fresh" in query_lower:

        category = "food"

    else:

        # Use AI to generate realistic brands for unknown categories

        logger.info(f"Using AI to generate brands for: {query}")

        template_list = generate_realistic_brands_ai(query)

        products = []

        

        # Generate products using AI-generated brands

        num_products = min(max_products * 2, len(template_list))

        for i in range(num_products):

            template = template_list[i]

            price_range = template["price_range"]

            price = random.uniform(price_range[0], price_range[1])

            rating = random.uniform(3.2, 4.8)

            reviews = random.randint(10, 500)

            

            # Generic sample reviews

            sample_reviews = [

                f"Great {template['model'].lower()}, very satisfied with the purchase.",

                f"Good value for money, {template['brand']} makes quality products.",

                f"Works as expected, no major issues so far.",

                f"Would recommend to others looking for a {query}.",

                f"Decent performance for the price point."

            ]

            

            products.append({

                "source": "ai_generated_brands",

                "title": f"{template['brand']} {template['model']} - {query.title()}",

                "brand": template['brand'],

                "url": f"https://example.com/{template['brand'].lower().replace(' ', '-')}/{template['model'].lower().replace(' ', '-')}",

                "price": f"${price:.2f}",

                "rating": f"{rating:.1f}",

                "num_reviews": str(reviews),

                "product_id": f"ai_{query}_{i}",

                "reviews": [],  # No fake reviews - only real reviews from API

                "scraped_at": _now(),

            })

        

        logger.info(f"Generated {len(products)} products with AI-generated brands for '{query}'")

        return products

    

    template_list = templates[category]

    products = []

    

    # Generate more products to get more brands (up to 10)

    num_products = min(max_products * 2, len(template_list))  # Double the products to get more brands

    

    for i in range(num_products):

        template = template_list[i]

        price_range = template["price_range"]

        price = random.uniform(price_range[0], price_range[1])

        rating = random.uniform(3.2, 4.8)

        reviews = random.randint(10, 500)

        

        # Generate category-specific sample reviews

        if category == "knife":

            sample_reviews = [

                f"Excellent {template['model'].lower()}, very sharp and well-balanced.",

                f"Great quality {template['brand']} knife, holds edge well.",

                f"Perfect for professional kitchen use.",

                f"Comfortable grip, very durable construction.",

                f"Best chef knife I've ever owned."

            ]

        elif category == "makeup":

            sample_reviews = [

                f"Love this {template['model'].lower()}, perfect coverage.",

                f"Great {template['brand']} foundation, lasts all day.",

                f"Natural looking finish, doesn't feel heavy.",

                f"Matches my skin tone perfectly.",

                f"Would definitely buy again."

            ]

        elif category == "coffee":

            sample_reviews = [

                f"Excellent {template['model'].lower()}, brews perfect coffee every time.",

                f"Great {template['brand']} machine, very consistent temperature.",

                f"Easy to clean and maintain, works flawlessly.",

                f"Best espresso I've had outside a coffee shop.",

                f"Love the convenience and quality of this coffee maker."

            ]

        elif category == "fruit" or category == "food":

            sample_reviews = [

                f"Fresh and delicious {template['model'].lower()}, great quality.",

                f"Excellent {template['brand']} product, very flavorful.",

                f"Perfect ripeness, arrived in great condition.",

                f"Great value for money, would buy again.",

                f"Tastes amazing, very fresh and natural."

            ]

        else:

            sample_reviews = [

                f"Great {template['model'].lower()}, very satisfied with the purchase.",

                f"Good value for money, {template['brand']} makes quality products.",

                f"Works as expected, no major issues so far.",

                f"Would recommend to others looking for a {category}.",

                f"Decent performance for the price point."

            ]

        

        products.append({

            "source": "sample_data",

            "title": f"{template['brand']} {template['model']} - {query.title()}",

            "brand": template['brand'],  # Add brand field

            "url": f"https://example.com/{template['brand'].lower()}/{template['model'].lower().replace(' ', '-')}",

            "price": f"${price:.2f}",

            "rating": f"{rating:.1f}",

            "num_reviews": str(reviews),

            "product_id": f"sample_{category}_{i}",

            "reviews": [],  # No fake reviews - only real reviews from API

            "scraped_at": _now(),

        })

    

    logger.info(f"Generated {len(products)} sample products for '{query}'")

    return products





def scrape_all_sites(query: str, max_per_site: int = 5) -> List[Dict[str, Any]]:

    """

    Primary: RapidAPI /search-light (confirmed working)

    Fallback 1: Direct eBay + Walmart (often blocked)

    Fallback 2: Sample data generation

    """

    logger.info("Scraping: '%s'", query)



    # Primary: RapidAPI - Always try to get real reviews first
    if os.getenv("RAPIDAPI_KEY"):
        products = search_products(query, max_products=max_per_site * 3)  # Get more products for better selection
        
        if products:
            # Try to enrich ALL products with real reviews (not just top 3)
            for p in products:
                pid = p.get("product_id", "")
                if pid and not p.get("reviews"):
                    p["reviews"] = fetch_product_reviews(pid, max_reviews=15)  # Get more reviews
                    _delay(0.2, 0.5)
            
            # Filter out products without real reviews
            products_with_reviews = [p for p in products if p.get("reviews")]
            logger.info("Products with real reviews: %d out of %d", len(products_with_reviews), len(products))
            
            if products_with_reviews:
                return products_with_reviews
            else:
                logger.warning("No real reviews found, returning products without reviews for analysis")
                return products  # Return products but without fake reviews
        
        else:
            logger.info("RapidAPI returned no products, falling back...")
    else:
        logger.warning("No RAPIDAPI_KEY found - cannot fetch real reviews")



    # Fallback 1: Direct scraping

    logger.info("Falling back to direct scraping...")

    all_products = []

    try:

        ebay = scrape_ebay_direct(query, max_per_site)

        all_products.extend(ebay)

        _delay()

        walmart = scrape_walmart_direct(query, max_per_site)

        all_products.extend(walmart)

        logger.info("Total via direct scraping: %d products", len(all_products))

    except Exception as e:

        logger.error(f"Direct scraping failed: {e}")



    # Fallback 2: Sample data if direct scraping failed or returned nothing

    if not all_products:

        logger.info("Direct scraping failed, generating sample data...")

        all_products = generate_sample_products(query, max_per_site * 2)

    

    logger.info("Final total: %d products", len(all_products))

    return all_products

