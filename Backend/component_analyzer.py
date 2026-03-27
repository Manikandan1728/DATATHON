"""
component_analyzer.py
Aspect-Based Component Extraction — 3-stage fallback pipeline.
  Stage 1: spaCy dependency parsing (amod/nsubj/dobj → ADJECTIVE + NOUN)
  Stage 2: spaCy noun chunk extraction
  Stage 3: TF-IDF keyword extraction
  Final safety: ["feature", "performance", "quality"]
"""
import re
import logging
import math
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# spaCy lazy loader
# ---------------------------------------------------------------------------
_nlp = None

def _get_nlp():
    global _nlp
    if _nlp is not None:
        return _nlp
    try:
        import spacy
        _nlp = spacy.load("en_core_web_sm")
    except OSError:
        try:
            import spacy
            from spacy.cli import download
            download("en_core_web_sm")
            _nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            logger.warning(f"spaCy model unavailable: {e}")
            _nlp = None
    return _nlp

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_GENERIC_TERMS = {
    "product", "item", "thing", "machine", "device", "unit", "stuff", "one",
    "lot", "bit", "way", "time", "day", "month", "year", "week", "use",
    "purchase", "order", "delivery", "shipping", "price", "value", "money",
    "star", "stars", "review", "amazon", "walmart", "ebay", "seller", "brand",
    "version", "model", "color", "colour", "size", "piece", "set", "pack",
    "box", "package", "part", "place", "point", "side", "end", "top",
    "bottom", "front", "back", "left", "right", "hand", "head", "face",
    "man", "woman", "people", "person", "customer", "buyer", "user",
    "quality",  # alone is too generic; "build quality" is fine as a phrase
}

_OPINION_WORDS = {
    "good", "great", "bad", "poor", "excellent", "terrible", "amazing",
    "awful", "fantastic", "horrible", "wonderful", "disappointing", "perfect",
    "decent", "mediocre", "outstanding", "impressive", "weak", "strong",
    "fast", "slow", "long", "short", "large", "small", "big", "tiny",
    "heavy", "light", "loud", "quiet", "bright", "dim", "sharp", "blurry",
    "smooth", "rough", "soft", "hard", "thick", "thin", "wide", "narrow",
    "clear", "crisp", "dull", "vivid", "accurate", "inaccurate", "reliable",
    "unreliable", "durable", "fragile", "sturdy", "flimsy", "comfortable",
    "uncomfortable", "easy", "difficult", "simple", "complex", "responsive",
    "laggy", "stable", "unstable", "efficient", "inefficient", "powerful",
    "hot", "cool", "warm", "cold", "noisy", "silent", "choppy", "crispy",
    "stale", "fresh", "tasty", "bland", "sweet", "bitter", "effective",
    "ineffective", "useful", "useless", "convenient", "awkward", "premium",
    "cheap", "expensive", "affordable", "overpriced", "worth", "broken",
    "fixed", "working", "failed", "lasted", "worn", "scratched", "cracked",
    "damaged", "intact", "solid", "loose", "tight", "flexible", "rigid",
    "portable", "bulky", "compact", "sleek", "ugly", "beautiful", "stylish",
    "modern", "innovative", "basic", "average", "horrible", "superb",
}

# Canonical merge map for multi-word aspects
_MERGE_MAP = {
    "battery life": "battery life",
    "battery backup": "battery life",
    "battery drain": "battery life",
    "battery performance": "battery life",
    "water tank": "water tank",
    "build quality": "build quality",
    "image quality": "image quality",
    "picture quality": "picture quality",
    "sound quality": "sound quality",
    "audio quality": "sound quality",
    "call quality": "call quality",
    "video quality": "video quality",
    "screen quality": "screen quality",
    "display quality": "display quality",
    "color accuracy": "color accuracy",
    "touch response": "touch response",
    "touch screen": "touchscreen",
    "charging speed": "charging speed",
    "charging time": "charging speed",
    "noise cancellation": "noise cancellation",
    "noise cancelling": "noise cancellation",
    "active noise": "noise cancellation",
    "fan noise": "fan noise",
    "heat management": "heat management",
    "thermal performance": "heat management",
    "keyboard feel": "keyboard",
    "keyboard layout": "keyboard",
    "key travel": "keyboard",
    "trackpad feel": "trackpad",
    "arch support": "arch support",
    "ankle support": "ankle support",
    "back support": "back support",
    "lumbar support": "lumbar support",
    "brewing quality": "brewing",
    "brew time": "brewing",
    "water pressure": "water pressure",
    "milk frother": "milk frother",
    "grind quality": "grind",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _split_sentences(text: str) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    result = []
    for s in sentences:
        parts = re.split(r',\s*(?=[a-z])', s)
        result.extend(p.strip() for p in parts if p.strip())
    return result


def _normalize(phrase: str) -> str:
    p = phrase.lower().strip()
    return _MERGE_MAP.get(p, p)


def _is_valid(phrase: str) -> bool:
    words = phrase.split()
    if len(phrase) < 3:
        return False
    # Single-word: must not be generic
    if len(words) == 1 and words[0] in _GENERIC_TERMS:
        return False
    # Multi-word: last word must not be generic alone (but "build quality" is ok via merge map)
    return True


def _score_and_rank(pairs: List[Tuple[str, float]], top_n: int) -> List[str]:
    """Aggregate (aspect, strength) pairs → sorted unique list."""
    freq: Counter = Counter()
    strength_sum: Dict[str, float] = defaultdict(float)
    for aspect, strength in pairs:
        norm = _normalize(aspect)
        if not _is_valid(norm):
            continue
        freq[norm] += 1
        strength_sum[norm] += strength

    scored = sorted(
        [(a, freq[a] * (strength_sum[a] / freq[a])) for a in freq],
        key=lambda x: x[1], reverse=True
    )
    seen, result = set(), []
    for aspect, _ in scored:
        if aspect not in seen:
            result.append(aspect)
            seen.add(aspect)
        if len(result) >= top_n:
            break
    return result


# ---------------------------------------------------------------------------
# STAGE 1 — Dependency parsing: ADJECTIVE + NOUN via amod/nsubj/dobj
# ---------------------------------------------------------------------------

def _stage1_dependency(sentences: List[str], top_n: int) -> List[str]:
    """
    Extract aspects where a noun is connected to an opinion word via:
      amod  — adjective modifies noun directly ("great battery")
      nsubj — noun is subject of opinion predicate ("battery is great")
      dobj  — noun is object of opinion verb ("loved the sound")
    """
    nlp = _get_nlp()
    if nlp is None:
        return []

    pairs: List[Tuple[str, float]] = []

    for sent in sentences:
        doc = nlp(sent)
        for token in doc:
            if token.pos_ not in ("NOUN", "PROPN"):
                continue
            if len(token.text) < 3:
                continue

            strength = 0.0

            # amod: "great battery" → battery
            for child in token.children:
                if child.dep_ == "amod" and child.lemma_.lower() in _OPINION_WORDS:
                    strength = max(strength, 1.0)

            # nsubj / dobj: "battery is great" or "loved the sound"
            if token.dep_ in ("nsubj", "dobj", "nsubjpass"):
                head = token.head
                if head.lemma_.lower() in _OPINION_WORDS:
                    strength = max(strength, 0.8)
                for sibling in head.children:
                    if sibling.dep_ in ("acomp", "attr") and sibling.lemma_.lower() in _OPINION_WORDS:
                        strength = max(strength, 0.9)

            if strength == 0.0:
                continue

            # Build phrase — include compound children ("battery life", "noise cancellation")
            compounds = [
                c.text.lower() for c in token.children
                if c.dep_ == "compound" and len(c.text) > 2
            ]
            phrase = (" ".join(compounds) + " " + token.lemma_.lower()).strip()
            pairs.append((phrase, strength))

    return _score_and_rank(pairs, top_n)


# ---------------------------------------------------------------------------
# STAGE 2 — Noun chunk fallback
# ---------------------------------------------------------------------------

def _stage2_noun_chunks(sentences: List[str], top_n: int) -> List[str]:
    """
    Extract all noun chunks from spaCy, keep the most frequent ones.
    Example: "noise cancellation is good" → "noise cancellation"
    """
    nlp = _get_nlp()
    if nlp is None:
        return []

    freq: Counter = Counter()
    for sent in sentences:
        doc = nlp(sent)
        for chunk in doc.noun_chunks:
            # Strip determiners/articles from the start
            text = chunk.text.lower().strip()
            text = re.sub(r'^(the|a|an|this|that|these|those|my|your|its)\s+', '', text)
            text = text.strip()
            if not _is_valid(text):
                continue
            words = text.split()
            if all(w in _GENERIC_TERMS for w in words):
                continue
            norm = _normalize(text)
            freq[norm] += 1

    if not freq:
        return []

    ranked = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    seen, result = set(), []
    for aspect, _ in ranked:
        if aspect not in seen and _is_valid(aspect):
            result.append(aspect)
            seen.add(aspect)
        if len(result) >= top_n:
            break
    return result


# ---------------------------------------------------------------------------
# STAGE 3 — TF-IDF keyword fallback
# ---------------------------------------------------------------------------

def _stage3_tfidf(all_reviews: List[str], top_n: int) -> List[str]:
    """
    Use sklearn TfidfVectorizer on review corpus.
    Falls back to manual TF-IDF if sklearn unavailable.
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        import numpy as np

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=50,
            min_df=1,
        )
        matrix = vectorizer.fit_transform(all_reviews)
        scores = np.asarray(matrix.mean(axis=0)).flatten()
        terms = vectorizer.get_feature_names_out()
        ranked = sorted(zip(terms, scores), key=lambda x: x[1], reverse=True)

        result = []
        seen = set()
        for term, _ in ranked:
            norm = _normalize(term)
            if not _is_valid(norm):
                continue
            words = norm.split()
            if all(w in _GENERIC_TERMS for w in words):
                continue
            if norm not in seen:
                result.append(norm)
                seen.add(norm)
            if len(result) >= top_n:
                break
        return result

    except ImportError:
        # Manual TF-IDF fallback
        return _stage3_manual_tfidf(all_reviews, top_n)


def _stage3_manual_tfidf(all_reviews: List[str], top_n: int) -> List[str]:
    """Manual TF-IDF without sklearn."""
    stop = {
        "the", "a", "an", "is", "it", "its", "this", "that", "and", "or",
        "but", "for", "with", "from", "to", "of", "in", "on", "at", "was",
        "were", "are", "not", "no", "my", "i", "we", "they", "you", "very",
        "really", "just", "so", "too", "also", "have", "has", "been", "would",
        "could", "should", "get", "got", "buy", "bought",
    } | _GENERIC_TERMS

    tf: Counter = Counter()
    df: Counter = Counter()
    n = len(all_reviews)

    for review in all_reviews:
        words = re.findall(r'\b[a-z]{3,}\b', review.lower())
        seen_in_doc = set()
        # unigrams
        for w in words:
            if w not in stop:
                tf[w] += 1
                if w not in seen_in_doc:
                    df[w] += 1
                    seen_in_doc.add(w)
        # bigrams
        for i in range(len(words) - 1):
            bg = words[i] + " " + words[i + 1]
            if words[i] not in stop and words[i + 1] not in stop:
                tf[bg] += 1
                if bg not in seen_in_doc:
                    df[bg] += 1
                    seen_in_doc.add(bg)

    scored = []
    for term, freq in tf.items():
        tfidf = (1 + math.log(freq)) * math.log((n + 1) / (df.get(term, 1) + 1))
        scored.append((term, tfidf))
    scored.sort(key=lambda x: x[1], reverse=True)

    result, seen = [], set()
    for term, _ in scored:
        norm = _normalize(term)
        if _is_valid(norm) and norm not in seen:
            result.append(norm)
            seen.add(norm)
        if len(result) >= top_n:
            break
    return result


# ---------------------------------------------------------------------------
# Main public API
# ---------------------------------------------------------------------------

def extract_dynamic_components(
    all_reviews: List[str],
    top_n: int = 8,
    category: str = "General"
) -> List[str]:
    """
    3-stage fallback pipeline:
      Stage 1 → dependency parsing (amod/nsubj/dobj)
      Stage 2 → noun chunk frequency
      Stage 3 → TF-IDF keywords
      Final   → ["feature", "performance", "quality"]
    Never returns empty.
    """
    reviews = [r for r in all_reviews if isinstance(r, str) and r.strip()]
    if not reviews:
        return ["feature", "performance", "quality"]

    sentences = []
    for r in reviews:
        sentences.extend(_split_sentences(r))

    top_n = max(3, min(top_n, 10))

    # Stage 1
    components = _stage1_dependency(sentences, top_n)
    if len(components) >= 3:
        logger.info(f"Stage 1 extracted {len(components)} components")
        return components

    # Stage 2
    logger.info("Stage 1 insufficient, trying Stage 2 (noun chunks)")
    stage2 = _stage2_noun_chunks(sentences, top_n)
    # Merge with any stage1 results
    seen = set(components)
    for c in stage2:
        if c not in seen:
            components.append(c)
            seen.add(c)
    if len(components) >= 3:
        logger.info(f"Stage 2 extracted {len(components)} components")
        return components[:top_n]

    # Stage 3
    logger.info("Stage 2 insufficient, trying Stage 3 (TF-IDF)")
    stage3 = _stage3_tfidf(reviews, top_n)
    for c in stage3:
        if c not in seen:
            components.append(c)
            seen.add(c)
    if components:
        logger.info(f"Stage 3 extracted {len(components)} components")
        return components[:top_n]

    # Final safety
    logger.warning("All stages empty — using safety defaults")
    return ["feature", "performance", "quality"]


# ---------------------------------------------------------------------------
# Category inference
# ---------------------------------------------------------------------------

def infer_category(query: str) -> str:
    q = query.lower().strip()
    if any(w in q for w in ["chips", "crisps", "popcorn", "snack", "cookie", "biscuit",
                              "candy", "chocolate", "gummy", "pretzel", "nuts", "granola bar",
                              "protein bar", "jerky", "dried fruit"]):
        return "Snacks"
    if any(w in q for w in ["coffee", "espresso", "latte", "cappuccino", "cold brew", "instant coffee"]):
        return "Coffee"
    if any(w in q for w in ["juice", "soda", "drink", "beverage", "tea", "smoothie",
                              "energy drink", "sports drink", "protein shake"]):
        return "Beverages"
    if any(w in q for w in ["food", "meal", "rice", "pasta", "bread", "cereal", "oats",
                              "sauce", "condiment", "spice", "soup", "noodle", "pizza"]):
        return "Food"
    if any(w in q for w in ["headphone", "earphone", "earbud", "airpod"]):
        return "Audio"
    if re.search(r'\bspeaker\b', q):
        return "Audio"
    if any(w in q for w in ["smartphone", "iphone", "pixel", "android phone"]) or re.search(r'\bphone\b', q):
        return "Smartphones"
    if re.search(r'\bsamsung\b', q) and "tv" not in q and "monitor" not in q:
        return "Smartphones"
    if any(w in q for w in ["laptop", "notebook", "macbook", "chromebook"]):
        return "Laptops"
    if any(w in q for w in ["tv", "television", "monitor", "display"]):
        return "Displays"
    if any(w in q for w in ["tablet", "ipad", "kindle", "e-reader"]):
        return "Tablets"
    if any(w in q for w in ["camera", "dslr", "mirrorless", "gopro", "webcam"]):
        return "Cameras"
    if any(w in q for w in ["smartwatch", "fitness tracker", "fitbit", "garmin watch"]):
        return "Wearables"
    if any(w in q for w in ["shoe", "sneaker", "boot", "sandal", "slipper", "heel", "loafer"]):
        return "Footwear"
    if any(w in q for w in ["shirt", "pant", "dress", "jacket", "clothing", "jeans",
                              "hoodie", "sweater", "coat", "shorts", "skirt", "legging"]):
        return "Clothing"
    if any(w in q for w in ["sofa", "couch", "chair", "table", "desk", "bed", "mattress",
                              "furniture", "shelf", "bookcase", "wardrobe"]):
        return "Furniture"
    if any(w in q for w in ["blender", "mixer", "microwave", "oven", "toaster", "air fryer",
                              "cookware", "pan", "pot", "coffee maker", "rice cooker"]):
        return "Kitchen"
    if any(w in q for w in ["shampoo", "moisturizer", "serum", "sunscreen", "foundation",
                              "lipstick", "perfume", "deodorant", "face wash", "skincare",
                              "body wash", "soap", "makeup"]):
        return "Beauty"
    if any(w in q for w in ["yoga mat", "dumbbell", "barbell", "treadmill", "bicycle",
                              "workout", "exercise", "fitness equipment"]):
        return "Fitness"
    if any(w in q for w in ["dog food", "cat food", "pet food", "dog treat", "cat treat",
                              "pet toy", "pet bed", "pet collar"]):
        return "Pets"
    if any(w in q for w in ["drill", "screwdriver", "wrench", "hammer", "saw", "power tool"]):
        return "Tools"
    if any(w in q for w in ["book", "novel", "textbook", "comic", "manga"]):
        return "Books"
    if any(w in q for w in ["supplement", "vitamin", "protein powder", "probiotic", "multivitamin"]):
        return "Health"
    if any(w in q for w in ["toy", "lego", "puzzle", "doll", "board game", "rc car"]):
        return "Toys"
    return "General"


# ---------------------------------------------------------------------------
# Review splitting by component (used by pipeline)
# ---------------------------------------------------------------------------

def split_reviews_by_component(
    products: List[Dict[str, Any]],
    category: str = "General"
) -> Dict[str, Dict[str, List[str]]]:
    """
    Split each product's reviews by dynamically extracted components.
    Returns: { product_title: { component: [review_texts] } }
    """
    all_reviews_flat = []
    for product in products:
        reviews = product.get("reviews", [])
        if reviews:
            all_reviews_flat.extend(reviews)
        else:
            all_reviews_flat.append(
                f"Product: {product.get('title', '')}. "
                f"Price: {product.get('price', 'N/A')}. "
                f"Rating: {product.get('rating', 'N/A')}."
            )

    global_components = extract_dynamic_components(all_reviews_flat, top_n=10, category=category)
    result: Dict[str, Dict[str, List[str]]] = {}

    for product in products:
        title = product.get("title", "Unknown")
        reviews = product.get("reviews", [])
        if not reviews:
            reviews = [
                f"Product: {title}. "
                f"Price: {product.get('price', 'N/A')}. "
                f"Rating: {product.get('rating', 'N/A')}."
            ]

        component_map: Dict[str, List[str]] = defaultdict(list)

        for review in reviews:
            if not isinstance(review, str):
                continue
            sentences = _split_sentences(review)
            nlp = _get_nlp()
            pairs = (
                [(p, s) for p, s in _stage1_dependency(sentences, 20)]
                if nlp else []
            )
            if not pairs:
                # Use noun chunks as aspect signals
                chunks = _stage2_noun_chunks(sentences, 20)
                pairs = [(c, 1.0) for c in chunks]

            found = set()
            for aspect, _ in pairs:
                norm = _normalize(aspect)
                for gc in global_components:
                    if gc in norm or norm in gc or norm == gc:
                        found.add(gc)
                        break
                else:
                    if _is_valid(norm) and norm not in _GENERIC_TERMS:
                        found.add(norm)

            if not found:
                component_map["general"].append(review)
            else:
                for comp in found:
                    component_map[comp].append(review)

        result[title] = dict(component_map)

    return result


# ---------------------------------------------------------------------------
# Legacy shims
# ---------------------------------------------------------------------------

def get_category_components(category: str) -> List[str]:
    return []


def extract_components(review_text: str, allowed_components: List[str] = None) -> List[str]:
    sentences = _split_sentences(review_text)
    nlp = _get_nlp()
    if nlp:
        pairs = [(p, s) for p, s in zip(_stage1_dependency(sentences, 8), [1.0] * 8)]
    else:
        pairs = []
    if not pairs:
        chunks = _stage2_noun_chunks(sentences, 8)
        return chunks or _stage3_tfidf([review_text], 8)
    return [p for p, _ in pairs]
