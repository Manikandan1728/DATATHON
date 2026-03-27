"""
product_aspect_analyzer.py
Review-based aspect extraction for products.
Focuses on extracting aspects like performance, price, battery life, design, etc.
"""
import re
import logging
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

# Opinion words for aspect extraction
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
    "hot", "cool", "warm", "cold", "noisy", "silent", "choppy", "nice",
    "solid", "loose", "tight", "flexible", "rigid", "portable", "bulky",
    "compact", "sleek", "ugly", "beautiful", "stylish", "modern", "innovative",
    "basic", "average", "superb", "decent", "okay", "fine", "better", "worse",
    "best", "worst", "high", "low", "cheap", "expensive", "affordable", "overpriced",
    "worth", "broken", "fixed", "working", "failed", "lasted", "worn", "scratched",
    "cracked", "damaged", "intact", "premium", "budget", "professional", "consumer"
}

# Aspect merge map
_ASPECT_MERGE_MAP = {
    "battery life": "battery life",
    "battery backup": "battery life",
    "battery performance": "battery life",
    "battery duration": "battery life",
    "battery lasts": "battery life",
    "battery drain": "battery life",
    "screen quality": "display quality",
    "display quality": "display quality",
    "screen clarity": "display quality",
    "display clarity": "display quality",
    "screen brightness": "display brightness",
    "display brightness": "display brightness",
    "screen size": "display size",
    "display size": "display size",
    "screen resolution": "display resolution",
    "display resolution": "display resolution",
    "sound quality": "sound quality",
    "audio quality": "sound quality",
    "speaker quality": "sound quality",
    "volume quality": "sound quality",
    "call quality": "call quality",
    "voice quality": "call quality",
    "camera quality": "camera quality",
    "picture quality": "camera quality",
    "photo quality": "camera quality",
    "image quality": "camera quality",
    "video quality": "video quality",
    "recording quality": "video quality",
    "build quality": "build quality",
    "build materials": "build quality",
    "construction quality": "build quality",
    "material quality": "build quality",
    "design quality": "design",
    "product design": "design",
    "industrial design": "design",
    "overall design": "design",
    "exterior design": "design",
    "performance speed": "performance",
    "processing speed": "performance",
    "system performance": "performance",
    "overall performance": "performance",
    "device performance": "performance",
    "app performance": "performance",
    "price value": "price",
    "value for money": "price",
    "price point": "price",
    "cost effectiveness": "price",
    "affordability": "price",
    "price range": "price",
    "ease of use": "ease of use",
    "user friendly": "ease of use",
    "user experience": "ease of use",
    "usability": "ease of use",
    "ease of setup": "ease of use",
    "setup process": "ease of use",
    "customer support": "customer support",
    "technical support": "customer support",
    "support service": "customer support",
    "warranty service": "warranty",
    "warranty support": "warranty",
    " warranty coverage": "warranty",
    "heat management": "heat management",
    "thermal performance": "heat management",
    "temperature control": "heat management",
    "overheating": "heat management",
    "noise level": "noise level",
    "fan noise": "noise level",
    "operating noise": "noise level",
    "silent operation": "noise level",
    "portability": "portability",
    "portable design": "portability",
    "compact size": "portability",
    "weight distribution": "portability",
    "storage capacity": "storage",
    "storage space": "storage",
    "memory capacity": "storage",
    "storage size": "storage",
    "connectivity options": "connectivity",
    "connection options": "connectivity",
    "wireless connectivity": "connectivity",
    "network connectivity": "connectivity",
    "charging speed": "charging speed",
    "charging time": "charging speed",
    "fast charging": "charging speed",
    "charge time": "charging speed",
    "software features": "software",
    "app features": "software",
    "operating system": "software",
    "system software": "software",
    "firmware": "software",
    "gaming performance": "gaming performance",
    "game performance": "gaming performance",
    "gaming experience": "gaming performance",
    "color accuracy": "color accuracy",
    "color reproduction": "color accuracy",
    "color quality": "color accuracy",
    "touch response": "touch response",
    "touch sensitivity": "touch response",
    "touch screen response": "touch response",
    "durability": "durability",
    "build durability": "durability",
    "product durability": "durability",
    "long term durability": "durability"
}

# Generic terms to filter out
_GENERIC_TERMS = {
    "product", "item", "thing", "machine", "device", "unit", "stuff", "one",
    "lot", "bit", "way", "time", "day", "month", "year", "week", "use",
    "purchase", "order", "delivery", "shipping", "package", "box", "brand",
    "version", "model", "color", "size", "piece", "set", "pack", "part",
    "place", "point", "side", "end", "top", "bottom", "front", "back",
    "left", "right", "hand", "head", "face", "man", "woman", "people",
    "person", "customer", "buyer", "user", "seller", "company", "store"
}

def _normalize_aspect(aspect: str) -> str:
    """Normalize aspect name using merge map."""
    aspect = aspect.lower().strip()
    return _ASPECT_MERGE_MAP.get(aspect, aspect)

def _is_valid_aspect(aspect: str) -> bool:
    """Check if aspect is valid (not generic, minimum length)."""
    if len(aspect) < 3:
        return False
    
    words = aspect.split()
    # Single word: must not be generic
    if len(words) == 1 and words[0] in _GENERIC_TERMS:
        return False
    
    # Multi-word: not all words should be generic
    if all(word in _GENERIC_TERMS for word in words):
        return False
    
    return True

def _split_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    result = []
    for s in sentences:
        parts = re.split(r',\s*(?=[a-z])', s)
        result.extend(p.strip() for p in parts if p.strip())
    return result

def _extract_aspects_spacy(sentences: List[str]) -> List[str]:
    """
    Extract aspects using simple regex patterns (replacing spaCy).
    Looks for nouns connected to opinion words via simple patterns.
    """
    aspects = []
    
    # Simple regex patterns for aspect extraction
    patterns = [
        r'\b(good|great|bad|poor|excellent|terrible|amazing|awful|fantastic|horrible|wonderful|disappointing|perfect|decent|mediocre|outstanding|impressive|weak|strong|fast|slow|long|short|large|small|big|tiny|heavy|light|loud|quiet|bright|dim|sharp|blurry|smooth|rough|even|uneven|flat|curved|straight|bent|twisted|crooked|level|slanted|vertical|horizontal|parallel|perpendicular|diagonal|angular|round|square|rectangular|triangular|circular|oval|elliptical|spherical|cylindrical|conical|pyramidal|cubic|tetrahedral|octahedral|hexagonal|pentagonal|polygonal|irregular|regular|symmetrical|asymmetrical|balanced|unbalanced|stable|unstable|steady|unsteady|firm|loose|tight|slack|tense|relaxed|stiff|limber|rigid|flexible|elastic|plastic|brittle|ductile|malleable|hard|soft|tough|fragile|strong|weak|durable|perishable|lasting|temporary|permanent|transient|stable|unstable|volatile|inert|reactive|active|passive|energetic|lethargic|vigorous|feeble|powerful|powerless|mighty|helpless|dominant|submissive|aggressive|defensive|offensive|protective|destructive|constructive|creative|analytical|logical|rational|irrational|reasonable|unreasonable|sensible|nonsensical|practical|impractical|realistic|unrealistic|optimistic|pessimistic|hopeful|despairing|confident|insecure|sure|unsure|certain|uncertain|definite|indefinite|clear|unclear|obvious|ambiguous|explicit|implicit|direct|indirect|straightforward|complicated|simple|complex|easy|difficult|hard|soft|rough|smooth|coarse|fine|thick|thin|wide|narrow|broad|slim|fat|thin|heavy|light|dense|sparse|full|empty|complete|incomplete|whole|partial|total|fractional|absolute|relative|exact|approximate|precise|imprecise|accurate|inaccurate|correct|incorrect|right|wrong|proper|improper|appropriate|inappropriate|suitable|unsuitable|fit|unfit|perfect|imperfect|flawless|flawed|ideal|realistic|optimal|suboptimal|maximum|minimum|optimal|best|worst|better|worse|superior|inferior|higher|lower|greater|lesser|more|less|most|least|first|last|initial|final|primary|secondary|main|auxiliary|principal|associate|chief|deputy|senior|junior|head|assistant|lead|support|key|minor|major|significant|insignificant|important|unimportant|essential|nonessential|critical|noncritical|vital|nonvital|crucial|noncrucial|fundamental|superficial|deep|shallow|profound|simple|complex|basic|advanced|elementary|sophisticated|primitive|modern|ancient|old|new|young|mature|immature|ripe|unripe|fresh|stale|raw|cooked|natural|processed|organic|synthetic|pure|impure|clean|dirty|sterile|contaminated|hygienic|unhygienic|safe|unsafe|secure|insecure|protected|unprotected|guarded|unguarded|monitored|unmonitored|supervised|unsupervised|controlled|uncontrolled|regulated|unregulated|restricted|unrestricted|limited|unlimited|finite|infinite|bounded|unbounded|closed|open|accessible|inaccessible|available|unavailable|present|absent|existing|nonexistent|real|imaginary|actual|potential|theoretical|practical|experimental|empirical|hypothetical|observed|unobserved|measured|unmeasured|calculated|estimated|approximate|exact|precise|rough|detailed|general|specific|broad|narrow|wide|tight|loose|strict|lenient|hard|soft|tough|easy|simple|difficult|complex|complicated|straightforward|direct|indirect|immediate|delayed|instant|gradual|sudden|abrupt|smooth|jerky|steady|unsteady|regular|irrregular|constant|variable|fixed|flexible|stable|unstable|permanent|temporary|lasting|fleeting|enduring|transient|durable|fragile|strong|weak|powerful|powerless|effective|ineffective|efficient|inefficient|productive|unproductive|useful|useless|helpful|harmful|beneficial|detrimental|advantageous|disadvantageous|positive|negative|favorable|unfavorable|good|bad|right|wrong|correct|incorrect|proper|improper|appropriate|inappropriate)\s+(?:performance|price|quality|design|feature|function|capability|ability|skill|talent|capacity|power|strength|speed|size|weight|dimension|measurement|specification|standard|requirement|condition|state|status|situation|circumstance|factor|element|component|part|section|portion|segment|piece|item|unit|module|system|structure|framework|architecture|layout|format|style|type|kind|sort|variety|category|class|group|set|collection|series|range|spectrum|scale|level|degree|extent|scope|reach|span|length|width|height|depth|thickness|diameter|radius|circumference|perimeter|area|volume|capacity|size|magnitude|amount|quantity|number|count|total|sum|average|mean|median|mode|range|variance|deviation|standard|deviation|error|accuracy|precision|tolerance|margin|buffer|reserve|surplus|deficit|shortage|excess|abundance|scarcity|plenty|wealth|poverty|richness|poorness|success|failure|victory|defeat|win|loss|gain|profit|benefit|advantage|disadvantage|pro|con|positive|negative|good|bad|right|wrong|correct|incorrect|true|false|real|fake|genuine|artificial|natural|synthetic|organic|inorganic|living|dead|alive|lifeless|animate|inanimate|active|passive|dynamic|static|moving|stationary|mobile|immobile|portable|fixed|flexible|rigid|soft|hard|smooth|rough|even|uneven|flat|curved|straight|bent|twisted|crooked|level|slanted|vertical|horizontal|parallel|perpendicular|diagonal|angular|round|square|rectangular|triangular|circular|oval|elliptical|spherical|cylindrical|conical|pyramidal|cubic|tetrahedral|octahedral|hexagonal|pentagonal|polygonal|irregular|regular|symmetrical|asymmetrical|balanced|unbalanced|stable|unstable|steady|unsteady|firm|loose|tight|slack|tense|relaxed|stiff|limber|rigid|flexible|elastic|plastic|brittle|ductile|malleable|hard|soft|tough|fragile|strong|weak|durable|perishable|lasting|temporary|permanent|transient|stable|unstable|volatile|inert|reactive|active|passive|energetic|lethargic|vigorous|feeble|powerful|powerless|mighty|helpless|dominant|submissive|aggressive|defensive|offensive|protective|destructive|constructive|creative|analytical|logical|rational|irrational|reasonable|unreasonable|sensible|nonsensical|practical|impractical|realistic|unrealistic|optimistic|pessimistic|hopeful|despairing|confident|insecure|sure|unsure|certain|uncertain|definite|indefinite|clear|unclear|obvious|ambiguous|explicit|implicit|direct|indirect|straightforward|complicated|simple|complex|easy|difficult|hard|soft|rough|smooth|coarse|fine|thick|thin|wide|narrow|broad|slim|fat|thin|heavy|light|dense|sparse|full|empty|complete|incomplete|whole|partial|total|fractional|absolute|relative|exact|approximate|precise|imprecise|accurate|inaccurate|correct|incorrect|right|wrong|proper|improper|appropriate|inappropriate|suitable|unsuitable|fit|unfit|perfect|imperfect|flawless|flawed|ideal|realistic|optimal|suboptimal|maximum|minimum|optimal|best|worst|better|worse|superior|inferior|higher|lower|greater|lesser|more|less|most|least|first|last|initial|final|primary|secondary|main|auxiliary|principal|associate|chief|deputy|senior|junior|head|assistant|lead|support|key|minor|major|significant|insignificant|important|unimportant|essential|nonessential|critical|noncritical|vital|nonvital|crucial|noncrucial|fundamental|superficial|deep|shallow|profound|simple|complex|basic|advanced|elementary|sophisticated|primitive|modern|ancient|old|new|young|mature|immature|ripe|unripe|fresh|stale|raw|cooked|natural|processed|organic|synthetic|pure|impure|clean|dirty|sterile|contaminated|hygienic|unhygienic|safe|unsafe|secure|insecure|protected|unprotected|guarded|unguarded|monitored|unmonitored|supervised|unsupervised|controlled|uncontrolled|regulated|unregulated|restricted|unrestricted|limited|unlimited|finite|infinite|bounded|unbounded|closed|open|accessible|inaccessible|available|unavailable|present|absent|existing|nonexistent|real|imaginary|actual|potential|theoretical|practical|experimental|empirical|hypothetical|observed|unobserved|measured|unmeasured|calculated|estimated|approximate|exact|precise|rough|detailed|general|specific|broad|narrow|wide|tight|loose|strict|lenient|hard|soft|tough|easy|simple|difficult|complex|complicated|straightforward|direct|indirect|immediate|delayed|instant|gradual|sudden|abrupt|smooth|jerky|steady|unsteady|regular|irrregular|constant|variable|fixed|flexible|stable|unstable|permanent|temporary|lasting|fleeting|enduring|transient|durable|fragile|strong|weak|powerful|powerless|effective|ineffective|efficient|inefficient|productive|unproductive|useful|useless|helpful|harmful|beneficial|detrimental|advantageous|disadvantageous|positive|negative|favorable|unfavorable|good|bad|right|wrong|correct|incorrect|proper|improper|appropriate|inappropriate)\b',
        r'\b(performance|price|quality|design|feature|function|capability|ability|skill|talent|capacity|power|strength|speed|size|weight|dimension|measurement|specification|standard|requirement|condition|state|status|situation|circumstance|factor|element|component|part|section|portion|segment|piece|item|unit|module|system|structure|framework|architecture|layout|format|style|type|kind|sort|variety|category|class|group|set|collection|series|range|spectrum|scale|level|degree|extent|scope|reach|span|length|width|height|depth|thickness|diameter|radius|circumference|perimeter|area|volume|capacity|size|magnitude|amount|quantity|number|count|total|sum|average|mean|median|mode|range|variance|deviation|standard|deviation|error|accuracy|precision|tolerance|margin|buffer|reserve|surplus|deficit|shortage|excess|abundance|scarcity|plenty|wealth|poverty|richness|poorness|success|failure|victory|defeat|win|loss|gain|profit|benefit|advantage|disadvantage|pro|con|positive|negative|good|bad|right|wrong|correct|incorrect|true|false|real|fake|genuine|artificial|natural|synthetic|organic|inorganic|living|dead|alive|lifeless|animate|inanimate|active|passive|dynamic|static|moving|stationary|mobile|immobile|portable|fixed|flexible|rigid|soft|hard|smooth|rough|even|uneven|flat|curved|straight|bent|twisted|crooked|level|slanted|vertical|horizontal|parallel|perpendicular|diagonal|angular|round|square|rectangular|triangular|circular|oval|elliptical|spherical|cylindrical|conical|pyramidal|cubic|tetrahedral|octahedral|hexagonal|pentagonal|polygonal|irregular|regular|symmetrical|asymmetrical|balanced|unbalanced|stable|unstable|steady|unsteady|firm|loose|tight|slack|tense|relaxed|stiff|limber|rigid|flexible|elastic|plastic|brittle|ductile|malleable|hard|soft|tough|fragile|strong|weak|durable|perishable|lasting|temporary|permanent|transient|stable|unstable|volatile|inert|reactive|active|passive|energetic|lethargic|vigorous|feeble|powerful|powerless|mighty|helpless|dominant|submissive|aggressive|defensive|offensive|protective|destructive|constructive|creative|analytical|logical|rational|irrational|reasonable|unreasonable|sensible|nonsensical|practical|impractical|realistic|unrealistic|optimistic|pessimistic|hopeful|despairing|confident|insecure|sure|unsure|certain|uncertain|definite|indefinite|clear|unclear|obvious|ambiguous|explicit|implicit|direct|indirect|straightforward|complicated|simple|complex|easy|difficult|hard|soft|rough|smooth|coarse|fine|thick|thin|wide|narrow|broad|slim|fat|thin|heavy|light|dense|sparse|full|empty|complete|incomplete|whole|partial|total|fractional|absolute|relative|exact|approximate|precise|imprecise|accurate|inaccurate|correct|incorrect|right|wrong|proper|improper|appropriate|inappropriate)\b',
    ]
    
    for sent in sentences:
        for pattern in patterns:
            matches = re.findall(pattern, sent.lower())
            for match in matches:
                aspect = match.strip()
                if len(aspect) >= 3 and aspect not in _GENERIC_TERMS:
                    aspects.append(aspect)
    
    return aspects

def _extract_aspects_from_dependencies(sentences: List[str]) -> List[Tuple[str, float]]:
    """
    Extract aspects using simple regex patterns (replacing spaCy dependency parsing).
    Looks for nouns connected to opinion words via simple patterns.
    """
    aspects = []
    
    for sent in sentences:
        # Simple pattern matching for aspect extraction
        patterns = [
            (r'\b(good|great|excellent|amazing|fantastic|wonderful|perfect|outstanding|impressive|strong|fast|large|big|bright|clear|smooth|comfortable|easy|simple|reliable|durable|stable|accurate|precise|efficient|effective|useful|helpful|beneficial|advantageous|positive)\s+(\w+)\b', 1.0),
            (r'\b(bad|poor|terrible|awful|horrible|disappointing|weak|slow|small|tiny|dim|blurry|rough|uncomfortable|difficult|complex|unreliable|fragile|unstable|inaccurate|imprecise|inefficient|ineffective|useless|harmful|detrimental|disadvantageous|negative)\s+(\w+)\b', -1.0),
            (r'\b(\w+)\s+(is|was|are|were)\s+(good|great|excellent|amazing|fantastic|wonderful|perfect|outstanding|impressive|strong|fast|large|big|bright|clear|smooth|comfortable|easy|simple|reliable|durable|stable|accurate|precise|efficient|effective|useful|helpful|beneficial|advantageous|positive)\b', 0.8),
            (r'\b(\w+)\s+(is|was|are|were)\s+(bad|poor|terrible|awful|horrible|disappointing|weak|slow|small|tiny|dim|blurry|rough|uncomfortable|difficult|complex|unreliable|fragile|unstable|inaccurate|imprecise|inefficient|ineffective|useless|harmful|detrimental|disadvantageous|negative)\b', -0.8),
        ]
        
        for pattern, strength in patterns:
            matches = re.findall(pattern, sent.lower())
            for match in matches:
                if isinstance(match, tuple):
                    aspect = match[-1]  # Get the last element (the aspect)
                else:
                    aspect = match
                
                if len(aspect) >= 3 and aspect not in _GENERIC_TERMS:
                    aspects.append((aspect, strength))
    
    return aspects

def _extract_aspects_from_noun_chunks(sentences: List[str]) -> List[str]:
    """
    Extract aspects using simple regex patterns (replacing spaCy noun chunks).
    Finds noun phrases that might represent aspects.
    """
    aspects = []
    
    # Simple regex patterns for noun phrase extraction
    patterns = [
        r'\b(?:the|a|an)?\s*([a-z]+\s+(?:performance|price|quality|design|feature|function|capability|ability|skill|talent|capacity|power|strength|speed|size|weight|dimension|measurement|specification|standard|requirement|condition|state|status|situation|circumstance|factor|element|component|part|section|portion|segment|piece|item|unit|module|system|structure|framework|architecture|layout|format|style|type|kind|sort|variety|category|class|group|set|collection|series|range|spectrum|scale|level|degree|extent|scope|reach|span|length|width|height|depth|thickness|diameter|radius|circumference|perimeter|area|volume|capacity|size|magnitude|amount|quantity|number|count|total|sum|average|mean|median|mode|range|variance|deviation|standard|deviation|error|accuracy|precision|tolerance|margin|buffer|reserve|surplus|deficit|shortage|excess|abundance|scarcity|plenty|wealth|poverty|richness|poorness|success|failure|victory|defeat|win|loss|gain|profit|benefit|advantage|disadvantage|pro|con|positive|negative|good|bad|right|wrong|correct|incorrect|true|false|real|fake|genuine|artificial|natural|synthetic|organic|inorganic|living|dead|alive|lifeless|animate|inanimate|active|passive|dynamic|static|moving|stationary|mobile|immobile|portable|fixed|flexible|rigid|soft|hard|smooth|rough|even|uneven|flat|curved|straight|bent|twisted|crooked|level|slanted|vertical|horizontal|parallel|perpendicular|diagonal|angular|round|square|rectangular|triangular|circular|oval|elliptical|spherical|cylindrical|conical|pyramidal|cubic|tetrahedral|octahedral|hexagonal|pentagonal|polygonal|irregular|regular|symmetrical|asymmetrical|balanced|unbalanced|stable|unstable|steady|unsteady|firm|loose|tight|slack|tense|relaxed|stiff|limber|rigid|flexible|elastic|plastic|brittle|ductile|malleable|hard|soft|tough|fragile|strong|weak|durable|perishable|lasting|temporary|permanent|transient|stable|unstable|volatile|inert|reactive|active|passive|energetic|lethargic|vigorous|feeble|powerful|powerless|mighty|helpless|dominant|submissive|aggressive|defensive|offensive|protective|destructive|constructive|creative|analytical|logical|rational|irrational|reasonable|unreasonable|sensible|nonsensical|practical|impractical|realistic|unrealistic|optimistic|pessimistic|hopeful|despairing|confident|insecure|sure|unsure|certain|uncertain|definite|indefinite|clear|unclear|obvious|ambiguous|explicit|implicit|direct|indirect|straightforward|complicated|simple|complex|easy|difficult|hard|soft|rough|smooth|coarse|fine|thick|thin|wide|narrow|broad|slim|fat|thin|heavy|light|dense|sparse|full|empty|complete|incomplete|whole|partial|total|fractional|absolute|relative|exact|approximate|precise|imprecise|accurate|inaccurate|correct|incorrect|right|wrong|proper|improper|appropriate|inappropriate|suitable|unsuitable|fit|unfit|perfect|imperfect|flawless|flawed|ideal|realistic|optimal|suboptimal|maximum|minimum|optimal|best|worst|better|worse|superior|inferior|higher|lower|greater|lesser|more|less|most|least|first|last|initial|final|primary|secondary|main|auxiliary|principal|associate|chief|deputy|senior|junior|head|assistant|lead|support|key|minor|major|significant|insignificant|important|unimportant|essential|nonessential|critical|noncritical|vital|nonvital|crucial|noncrucial|fundamental|superficial|deep|shallow|profound|simple|complex|basic|advanced|elementary|sophisticated|primitive|modern|ancient|old|new|young|mature|immature|ripe|unripe|fresh|stale|raw|cooked|natural|processed|organic|synthetic|pure|impure|clean|dirty|sterile|contaminated|hygienic|unhygienic|safe|unsafe|secure|insecure|protected|unprotected|guarded|unguarded|monitored|unmonitored|supervised|unsupervised|controlled|uncontrolled|regulated|unregulated|restricted|unrestricted|limited|unlimited|finite|infinite|bounded|unbounded|closed|open|accessible|inaccessible|available|unavailable|present|absent|existing|nonexistent|real|imaginary|actual|potential|theoretical|practical|experimental|empirical|hypothetical|observed|unobserved|measured|unmeasured|calculated|estimated|approximate|exact|precise|rough|detailed|general|specific|broad|narrow|wide|tight|loose|strict|lenient|hard|soft|tough|easy|simple|difficult|complex|complicated|straightforward|direct|indirect|immediate|delayed|instant|gradual|sudden|abrupt|smooth|jerky|steady|unsteady|regular|irrregular|constant|variable|fixed|flexible|stable|unstable|permanent|temporary|lasting|fleeting|enduring|transient|durable|fragile|strong|weak|powerful|powerless|effective|ineffective|efficient|inefficient|productive|unproductive|useful|useless|helpful|harmful|beneficial|detrimental|advantageous|disadvantageous|positive|negative|favorable|unfavorable|good|bad|right|wrong|correct|incorrect|proper|improper|appropriate|inappropriate)s)\b',
        r'\b([a-z]+\s+(?:performance|price|quality|design|feature|function|capability|ability|skill|talent|capacity|power|strength|speed|size|weight|dimension|measurement|specification|standard|requirement|condition|state|status|situation|circumstance|factor|element|component|part|section|portion|segment|piece|item|unit|module|system|structure|framework|architecture|layout|format|style|type|kind|sort|variety|category|class|group|set|collection|series|range|spectrum|scale|level|degree|extent|scope|reach|span|length|width|height|depth|thickness|diameter|radius|circumference|perimeter|area|volume|capacity|size|magnitude|amount|quantity|number|count|total|sum|average|mean|median|mode|range|variance|deviation|standard|deviation|error|accuracy|precision|tolerance|margin|buffer|reserve|surplus|deficit|shortage|excess|abundance|scarcity|plenty|wealth|poverty|richness|poorness|success|failure|victory|defeat|win|loss|gain|profit|benefit|advantage|disadvantage|pro|con|positive|negative|good|bad|right|wrong|correct|incorrect|true|false|real|fake|genuine|artificial|natural|synthetic|organic|inorganic|living|dead|alive|lifeless|animate|inanimate|active|passive|dynamic|static|moving|stationary|mobile|immobile|portable|fixed|flexible|rigid|soft|hard|smooth|rough|even|uneven|flat|curved|straight|bent|twisted|crooked|level|slanted|vertical|horizontal|parallel|perpendicular|diagonal|angular|round|square|rectangular|triangular|circular|oval|elliptical|spherical|cylindrical|conical|pyramidal|cubic|tetrahedral|octahedral|hexagonal|pentagonal|polygonal|irregular|regular|symmetrical|asymmetrical|balanced|unbalanced|stable|unstable|steady|unsteady|firm|loose|tight|slack|tense|relaxed|stiff|limber|rigid|flexible|elastic|plastic|brittle|ductile|malleable|hard|soft|tough|fragile|strong|weak|durable|perishable|lasting|temporary|permanent|transient|stable|unstable|volatile|inert|reactive|active|passive|energetic|lethargic|vigorous|feeble|powerful|powerless|mighty|helpless|dominant|submissive|aggressive|defensive|offensive|protective|destructive|constructive|creative|analytical|logical|rational|irrational|reasonable|unreasonable|sensible|nonsensical|practical|impractical|realistic|unrealistic|optimistic|pessimistic|hopeful|despairing|confident|insecure|sure|unsure|certain|uncertain|definite|indefinite|clear|unclear|obvious|ambiguous|explicit|implicit|direct|indirect|straightforward|complicated|simple|complex|easy|difficult|hard|soft|rough|smooth|coarse|fine|thick|thin|wide|narrow|broad|slim|fat|thin|heavy|light|dense|sparse|full|empty|complete|incomplete|whole|partial|total|fractional|absolute|relative|exact|approximate|precise|imprecise|accurate|inaccurate|correct|incorrect|right|wrong|proper|improper|appropriate|inappropriate|suitable|unsuitable|fit|unfit|perfect|imperfect|flawless|flawed|ideal|realistic|optimal|suboptimal|maximum|minimum|optimal|best|worst|better|worse|superior|inferior|higher|lower|greater|lesser|more|less|most|least|first|last|initial|final|primary|secondary|main|auxiliary|principal|associate|chief|deputy|senior|junior|head|assistant|lead|support|key|minor|major|significant|insignificant|important|unimportant|essential|nonessential|critical|noncritical|vital|nonvital|crucial|noncrucial|fundamental|superficial|deep|shallow|profound|simple|complex|basic|advanced|elementary|sophisticated|primitive|modern|ancient|old|new|young|mature|immature|ripe|unripe|fresh|stale|raw|cooked|natural|processed|organic|synthetic|pure|impure|clean|dirty|sterile|contaminated|hygienic|unhygienic|safe|unsafe|secure|insecure|protected|unprotected|guarded|unguarded|monitored|unmonitored|supervised|unsupervised|controlled|uncontrolled|regulated|unregulated|restricted|unrestricted|limited|unlimited|finite|infinite|bounded|unbounded|closed|open|accessible|inaccessible|available|unavailable|present|absent|existing|nonexistent|real|imaginary|actual|potential|theoretical|practical|experimental|empirical|hypothetical|observed|unobserved|measured|unmeasured|calculated|estimated|approximate|exact|precise|rough|detailed|general|specific|broad|narrow|wide|tight|loose|strict|lenient|hard|soft|tough|easy|simple|difficult|complex|complicated|straightforward|direct|indirect|immediate|delayed|instant|gradual|sudden|abrupt|smooth|jerky|steady|unsteady|regular|irrregular|constant|variable|fixed|flexible|stable|unstable|permanent|temporary|lasting|fleeting|enduring|transient|durable|fragile|strong|weak|powerful|powerless|effective|ineffective|efficient|inefficient|productive|unproductive|useful|useless|helpful|harmful|beneficial|detrimental|advantageous|disadvantageous|positive|negative|favorable|unfavorable|good|bad|right|wrong|correct|incorrect|proper|improper|appropriate|inappropriate)s)\b',
    ]
    
    for sent in sentences:
        for pattern in patterns:
            matches = re.findall(pattern, sent.lower())
            for match in matches:
                aspect = match.strip()
                aspect = re.sub(r'^(the|a|an|this|that|these|those|my|your|its)\s+', '', aspect)
                aspect = aspect.strip()
                
                if _is_valid_aspect(aspect):
                    aspects.append(aspect)
    
    return aspects

def _extract_aspects_from_patterns(reviews: List[str]) -> List[str]:
    """
    Extract aspects using regex patterns for common aspect phrases.
    """
    patterns = [
        r'\b(battery\s+life|battery\s+backup|battery\s+performance|battery\s+duration)\b',
        r'\b(screen\s+quality|display\s+quality|screen\s+clarity|display\s+clarity)\b',
        r'\b(sound\s+quality|audio\s+quality|speaker\s+quality|volume\s+quality)\b',
        r'\b(camera\s+quality|picture\s+quality|photo\s+quality|image\s+quality)\b',
        r'\b(build\s+quality|build\s+materials|construction\s+quality|material\s+quality)\b',
        r'\b(design\s+quality|product\s+design|industrial\s+design|overall\s+design)\b',
        r'\b(performance\s+speed|processing\s+speed|system\s+performance|overall\s+performance)\b',
        r'\b(price\s+value|value\s+for\s+money|price\s+point|cost\s+effectiveness)\b',
        r'\b(ease\s+of\s+use|user\s+friendly|user\s+experience|usability)\b',
        r'\b(customer\s+support|technical\s+support|support\s+service)\b',
        r'\b(warranty\s+service|warranty\s+support|warranty\s+coverage)\b',
        r'\b(heat\s+management|thermal\s+performance|temperature\s+control|overheating)\b',
        r'\b(noise\s+level|fan\s+noise|operating\s+noise|silent\s+operation)\b',
        r'\b(portability|portable\s+design|compact\s+size|weight\s+distribution)\b',
        r'\b(storage\s+capacity|storage\s+space|memory\s+capacity|storage\s+size)\b',
        r'\b(connectivity\s+options|connection\s+options|wireless\s+connectivity)\b',
        r'\b(charging\s+speed|charging\s+time|fast\s+charging|charge\s+time)\b',
        r'\b(software\s+features|app\s+features|operating\s+system|system\s+software)\b',
        r'\b(gaming\s+performance|game\s+performance|gaming\s+experience)\b',
        r'\b(color\s+accuracy|color\s+reproduction|color\s+quality)\b',
        r'\b(touch\s+response|touch\s+sensitivity|touch\s+screen\s+response)\b',
        r'\b(durability|build\s+durability|product\s+durability|long\s+term\s+durability)\b'
    ]
    
    aspects = []
    for review in reviews:
        if isinstance(review, str) and review.strip():
            for pattern in patterns:
                matches = re.findall(pattern, review, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0] if match[0] else match[1] if len(match) > 1 else ""
                    if _is_valid_aspect(match):
                        aspects.append(match.lower())
    
    return aspects

def _merge_similar_aspects(aspects: List[str]) -> List[str]:
    """Merge similar aspects using the merge map."""
    merged = {}
    
    for aspect in aspects:
        normalized = _normalize_aspect(aspect)
        if normalized not in merged:
            merged[normalized] = []
        merged[normalized].append(aspect)
    
    return list(merged.keys())

def _score_and_rank_aspects(aspect_pairs: List[Tuple[str, float]], top_n: int) -> List[str]:
    """Score and rank aspects by frequency and strength."""
    freq = Counter()
    strength_sum = defaultdict(float)
    
    for aspect, strength in aspect_pairs:
        norm = _normalize_aspect(aspect)
        if not _is_valid_aspect(norm):
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

class ProductAspectAnalyzer:
    """Analyzer for extracting product aspects from reviews."""
    
    def __init__(self, top_n: int = 10):
        self.top_n = top_n
    
    def extract_aspects(self, reviews: List[str]) -> List[str]:
        """
        Extract product aspects from reviews using multiple methods.
        
        Args:
            reviews: List of review texts
            
        Returns:
            List of top aspects ranked by importance
        """
        if not reviews:
            return ["performance", "price", "quality"]
        
        # Filter valid reviews
        valid_reviews = [r for r in reviews if isinstance(r, str) and r.strip()]
        
        if not valid_reviews:
            return ["performance", "price", "quality"]
        
        # Split reviews into sentences
        all_sentences = []
        for review in valid_reviews:
            all_sentences.extend(_split_sentences(review))
        
        # Method 1: Dependency parsing
        dependency_aspects = _extract_aspects_from_dependencies(all_sentences)
        
        # Method 2: Noun chunk extraction
        noun_chunk_aspects = _extract_aspects_from_noun_chunks(all_sentences)
        
        # Method 3: Pattern matching
        pattern_aspects = _extract_aspects_from_patterns(valid_reviews)
        
        # Combine all aspects
        all_aspects = []
        
        # Add dependency aspects with strength scores
        all_aspects.extend(dependency_aspects)
        
        # Add noun chunk aspects with default strength
        for aspect in noun_chunk_aspects:
            all_aspects.append((aspect, 0.5))
        
        # Add pattern aspects with default strength
        for aspect in pattern_aspects:
            all_aspects.append((aspect, 0.7))
        
        # Score and rank
        top_aspects = _score_and_rank_aspects(all_aspects, self.top_n)
        
        # If still not enough aspects, add defaults
        if len(top_aspects) < 3:
            defaults = ["performance", "price", "quality"]
            for default in defaults:
                if default not in top_aspects:
                    top_aspects.append(default)
                if len(top_aspects) >= 3:
                    break
        
        logger.info(f"Extracted {len(top_aspects)} aspects from {len(valid_reviews)} reviews")
        
        return top_aspects[:self.top_n]
    
    def analyze_product_aspects(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze aspects for a single product.
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            Dictionary with aspects and analysis metadata
        """
        title = product_data.get("title", "")
        reviews = product_data.get("reviews", [])
        
        aspects = self.extract_aspects(reviews)
        
        return {
            "product_title": title,
            "aspects": aspects,
            "aspect_count": len(aspects),
            "review_count": len(reviews),
            "extraction_methods": {
                "dependency_parsing": True,
                "noun_chunks": True,
                "pattern_matching": True
            }
        }

# Convenience function for quick usage
def extract_product_aspects(reviews: List[str], top_n: int = 10) -> List[str]:
    """
    Quick function to extract product aspects from reviews.
    
    Args:
        reviews: List of review texts
        top_n: Number of top aspects to return
        
    Returns:
        List of top aspects
    """
    analyzer = ProductAspectAnalyzer(top_n=top_n)
    return analyzer.extract_aspects(reviews)
