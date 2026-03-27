"""
product_component_analyzer.py
Extract physical/logical parts of products from title, description, specifications, and reviews.
"""
import re
import logging
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

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
    """Extract noun phrases using simple regex patterns."""
    # Simple regex-based noun phrase extraction
    components = []
    
    # Pattern for adjectives + nouns
    patterns = [
        r'\b([a-z]+\s+(?:processor|memory|storage|screen|display|battery|camera| speaker|keyboard|mouse|trackpad|port|connector|adapter|charger|case|cover|stand|mount|bracket|cable|wire|slot|drive|disk|fan|cooler|heatsink|motherboard|graphics|video|audio|network|wifi|bluetooth|usb|hdmi|displayport|thunderbolt|ethernet|headphone|microphone|sim|sd|card|reader|fingerprint|face|iris|sensor|button|dial|switch|light|led|backlight|touch|gesture|voice|assistant|gps|nfc|infrared|laser|radar|sonar|ultrasonic|pressure|temperature|humidity|motion|accelerometer|gyroscope|magnetometer|compass|altimeter|barometer|thermometer|hygrometer|photometer|spectrometer|microscope|telescope|binoculars|camera|lens|filter|tripod|monopod|gimbal|stabilizer|drone|robot|actuator|motor|servo|stepper|linear|piston|gear|bearing|spring|shock|absorber|damper|coupling|clutch|brake|caliper|rotor|stator|alternator|generator|transformer|inductor|capacitor|resistor|diode|transistor|chip|processor|memory|storage|drive|disk|ssd|hdd|optical|dvd|blu|ray|cd|rom|ram|rom|eprom|eeprom|flash|cache|register|buffer|controller|interface|port|connector|cable|adapter|converter|expander|hub|switch|router|modem|gateway|bridge|repeater|extender|antenna|satellite|receiver|transmitter|amplifier|equalizer|mixer|speaker|headphone|microphone|camera|webcam|projector|monitor|display|screen|touch|panel|lcd|led|oled|amoled|ips|va|tn|qled|mini|led|micro|led|quantum|dot|retina|force|touch|3d|touch|haptic|feedback|vibration|force|pressure|temperature|humidity|light|proximity|motion|gesture|voice|face|iris|fingerprint|palm|vein|dna|heart|rate|blood|pressure|oxygen|glucose|ketone|lactate|ph|salinity|conductivity|turbidity|flow|level|volume|weight|mass|density|viscosity|surface|tension|hardness|softness|elasticity|plasticity|brittleness|ductility|malleability|tensile|strength|compressive|strength|shear|strength|yield|strength|ultimate|strength|fatigue|creep|stress|strain|modulus|young|modulus|bulk|modulus|shear|modulus|poisson|ratio|thermal|expansion|coefficient|thermal|conductivity|electrical|conductivity|resistivity|permittivity|permeability|magnetic|susceptibility|dielectric|constant|loss|tangent|refractive|index|absorption|coefficient|emission|coefficient|reflectance|transmittance|absorbance|scattering|cross|section|optical|depth|penetration|depth|attenuation|length|path|length|mean|free|path|collision|frequency|relaxation|time|spin|lattice|time|correlation|time|coherence|time|decoherence|time|lifetime|decay|time|half|life|mean|life|radiation|dose|exposure|activity|intensity|flux|power|energy|work|heat|enthalpy|entropy|gibbs|free|energy|helmholtz|free|energy|chemical|potential|electrochemical|potential|fermi|level|band|gap|work|function|electron|affinity|ionization|energy|electron|negativity|electronegativity|atomic|radius|ionic|radius|covalent|radius|van|der|waals|radius|bond|length|bond|angle|bond|energy|dipole|moment|polarizability|magnetic|moment|spin|quantum|number|angular|momentum|orbital|energy|level|valence|electron|core|electron|conduction|electron|hole|electron|phonon|photon|exciton|polariton|plasmon|magnon|soliton|polaron|bipolaron|trion|quasiparticle|elementary|particle|composite|particle|subatomic|particle|fundamental|particle|force|carrier|gauge|boson|lepton|quark|gluon|w|boson|z|boson|higgs|boson|graviton|photon|gluon|w|z|higgs|graviton))\b',
        r'\b(\d+\s*(?:core|cores|thread|threads|bit|bits|byte|bytes|gb|tb|mb|kb|hz|ghz|mhz|w|v|amp|mah|wh|mm|cm|inch|pixel|mp|gb|tb|mb|kb|hz|ghz|mhz|w|v|amp|mah|wh|mm|cm|inch|pixel|mp))\b',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        for match in matches:
            component = match.strip()
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
