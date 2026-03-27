"""
product_component_analyzer.py
Extract physical/logical parts of products from title, description, specifications, and reviews.
"""
import re
import logging
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

# Lazy spaCy loader
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

# Generic terms to filter out
_GENERIC_TERMS = {
    "product", "item", "thing", "machine", "device", "unit", "stuff", "one",
    "lot", "bit", "way", "time", "day", "month", "year", "week", "use",
    "purchase", "order", "delivery", "shipping", "price", "value", "money",
    "star", "stars", "review", "amazon", "walmart", "ebay", "seller", "brand",
    "version", "model", "color", "colour", "size", "piece", "set", "pack",
    "box", "package", "part", "place", "point", "side", "end", "top",
    "bottom", "front", "back", "left", "right", "hand", "head", "face",
    "man", "woman", "people", "person", "customer", "buyer", "user",
    "good", "bad", "great", "poor", "excellent", "terrible", "amazing",
    "awful", "fantastic", "horrible", "wonderful", "disappointing", "perfect",
    "decent", "mediocre", "outstanding", "impressive", "weak", "strong",
    "fast", "slow", "long", "short", "large", "small", "big", "tiny",
    "new", "old", "used", "fresh", "latest", "original", "first", "last"
}

# Component merge map
_COMPONENT_MERGE_MAP = {
    "battery life": "battery",
    "battery backup": "battery",
    "battery performance": "battery",
    "screen display": "display",
    "screen size": "display",
    "touch screen": "display",
    "touchscreen": "display",
    "lcd screen": "display",
    "led display": "display",
    "hard drive": "storage",
    "hard disk": "storage",
    "ssd drive": "storage",
    "solid state drive": "storage",
    "memory ram": "ram",
    "memory card": "storage",
    "graphics card": "gpu",
    "video card": "gpu",
    "processor cpu": "cpu",
    "central processing unit": "cpu",
    "operating system": "os",
    "wifi connectivity": "wifi",
    "wireless connectivity": "wifi",
    "bluetooth connectivity": "bluetooth",
    "usb port": "usb",
    "usb connector": "usb",
    "power adapter": "adapter",
    "charging cable": "cable",
    "power cable": "cable",
    "audio jack": "jack",
    "headphone jack": "jack",
    "speaker system": "speakers",
    "audio speakers": "speakers",
    "cooling fan": "fan",
    "cooling system": "fan",
    "keyboard keys": "keyboard",
    "keypad": "keyboard",
    "trackpad mouse": "trackpad",
    "mouse pad": "trackpad",
    "webcam camera": "webcam",
    "built-in camera": "webcam",
    "microphone mic": "microphone",
    "built-in mic": "microphone"
}

def _normalize_component(component: str) -> str:
    """Normalize component name using merge map."""
    component = component.lower().strip()
    return _COMPONENT_MERGE_MAP.get(component, component)

def _is_valid_component(component: str) -> bool:
    """Check if component is valid (not generic, minimum length)."""
    if len(component) < 3:
        return False
    
    words = component.split()
    # Single word: must not be generic
    if len(words) == 1 and words[0] in _GENERIC_TERMS:
        return False
    
    # Multi-word: not all words should be generic
    if all(word in _GENERIC_TERMS for word in words):
        return False
    
    return True

def _extract_noun_phrases(text: str) -> List[str]:
    """Extract noun phrases using spaCy noun chunks."""
    nlp = _get_nlp()
    if nlp is None:
        return []
    
    doc = nlp(text)
    components = []
    
    for chunk in doc.noun_chunks:
        # Strip determiners and articles
        component = chunk.text.lower().strip()
        component = re.sub(r'^(the|a|an|this|that|these|those|my|your|its)\s+', '', component)
        component = component.strip()
        
        if _is_valid_component(component):
            components.append(component)
    
    return components

def _extract_technical_specs(text: str) -> List[str]:
    """Extract technical specifications from text."""
    # Common patterns for technical specs
    patterns = [
        r'\b(\d+\s*(?:gb|tb|mb|kb|hz|ghz|mhz|w|v|amp|mah|wh|mm|cm|inch|pixel|mp)\b)',
        r'\b(intel\s+i\d+\s*(?:processor|cpu))\b',
        r'\b(amd\s+ryzen\s+\d+)\b',
        r'\b(nvidia\s+geforce\s+rtx\s+\d+)\b',
        r'\b(nvidia\s+gtx\s+\d+)\b',
        r'\b(amd\s+radeon\s+\w+)\b',
        r'\b(windows\s+\d+)\b',
        r'\b(mac\s+os\s+\w+)\b',
        r'\b(android\s+\d+)\b',
        r'\b(ios\s+\d+)\b',
        r'\b(usb\s+[a-c])\b',
        r'\b(hdmi\s+\d+\.\d+)\b',
        r'\b(wifi\s+\d)\b',
        r'\b(bluetooth\s+\d+\.\d+)\b',
        r'\b(4k|5k|8k)\b',
        r'\b(hd|full\s*hd|uhd)\b',
        r'\b(led|lcd|oled)\b',
        r'\b(ssd|hdd)\b',
        r'\b(ddr\d+\s*ram)\b',
        r'\b(gpu|cpu|ram|rom|bios)\b'
    ]
    
    components = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0] if match[0] else match[1]
            if _is_valid_component(match):
                components.append(match.lower())
    
    return components

def _merge_similar_components(components: List[str]) -> List[str]:
    """Merge similar components using the merge map."""
    merged = {}
    
    for component in components:
        normalized = _normalize_component(component)
        if normalized not in merged:
            merged[normalized] = []
        merged[normalized].append(component)
    
    return list(merged.keys())

def _rank_by_frequency(components: List[str], top_n: int = 10) -> List[str]:
    """Rank components by frequency."""
    counter = Counter(components)
    ranked = [comp for comp, _ in counter.most_common(top_n)]
    return ranked

class ProductComponentAnalyzer:
    """Analyzer for extracting product components from various text sources."""
    
    def __init__(self, top_n: int = 10):
        self.top_n = top_n
    
    def extract_components(
        self,
        title: str = "",
        description: str = "",
        specifications: str = "",
        reviews: List[str] = None
    ) -> List[str]:
        """
        Extract product components from title, description, specifications, and reviews.
        
        Args:
            title: Product title
            description: Product description
            specifications: Product specifications
            reviews: List of review texts
            
        Returns:
            List of top components ranked by frequency
        """
        if reviews is None:
            reviews = []
        
        # Step 1: Combine text
        combined_text = f"{title} {description} {specifications}".strip()
        
        # Step 2: Extract noun phrases from combined text
        all_components = []
        
        if combined_text:
            all_components.extend(_extract_noun_phrases(combined_text))
            all_components.extend(_extract_technical_specs(combined_text))
        
        # Step 3: Extract from reviews
        for review in reviews:
            if isinstance(review, str) and review.strip():
                all_components.extend(_extract_noun_phrases(review))
                all_components.extend(_extract_technical_specs(review))
        
        # Step 4: Filter invalid components
        filtered_components = [
            comp for comp in all_components 
            if _is_valid_component(comp)
        ]
        
        # Step 5: Merge similar components
        merged_components = _merge_similar_components(filtered_components)
        
        # Step 6: Frequency ranking
        top_components = _rank_by_frequency(merged_components, self.top_n)
        
        logger.info(f"Extracted {len(top_components)} components from {len(all_components)} candidates")
        
        return top_components
    
    def analyze_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single product and return components with metadata.
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            Dictionary with components and analysis metadata
        """
        title = product_data.get("title", "")
        description = product_data.get("description", "")
        specifications = product_data.get("specifications", "")
        reviews = product_data.get("reviews", [])
        
        components = self.extract_components(title, description, specifications, reviews)
        
        return {
            "product_title": title,
            "components": components,
            "component_count": len(components),
            "sources_used": {
                "title": bool(title.strip()),
                "description": bool(description.strip()),
                "specifications": bool(specifications.strip()),
                "reviews": len(reviews) > 0
            }
        }

# Convenience function for quick usage
def extract_product_components(
    title: str = "",
    description: str = "",
    specifications: str = "",
    reviews: List[str] = None,
    top_n: int = 10
) -> List[str]:
    """
    Quick function to extract product components.
    
    Returns:
        List of top components
    """
    analyzer = ProductComponentAnalyzer(top_n=top_n)
    return analyzer.extract_components(title, description, specifications, reviews)
