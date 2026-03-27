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
# Component extraction functions (spaCy removed)
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

def _extract_amod_pairs_spacy(sentences: List[str]) -> List[Tuple[str, float]]:
    """
    Extract adjective+noun pairs using simple regex (replacing spaCy).
    Looks for patterns like "great battery", "fast performance", etc.
    """
    pairs = []
    
    # Simple regex patterns for adjective+noun extraction
    patterns = [
        (r'\b(good|great|excellent|amazing|fantastic|wonderful|perfect|outstanding|impressive|strong|fast|large|big|bright|clear|smooth|comfortable|easy|simple|reliable|durable|stable|accurate|precise|efficient|effective|useful|helpful|beneficial|positive|superior|high|advanced|premium|quality|professional|powerful|quick|instant|responsive|modern|sophisticated|intelligent|smart|automatic|digital|electronic|wireless|portable|compact|lightweight|heavy|duty|industrial|commercial|residential|personal|universal|flexible|versatile|multi|purpose|all|in|one|integrated|built|in|stand|alone|self|contained|ready|to|use|plug|and|play|easy|to|install|user|friendly|maintenance|free|long|lasting|energy|efficient|cost|effective|time|saving|space|saving|high|performance|top|quality|best|in|class|state|of|the|art|cutting|edge|latest|technology|innovative|revolutionary|breakthrough|game|changing|life|changing|world|class|award|winning|certified|approved|tested|proven|guaranteed|warranted|backed|supported|recommended|trusted|reputable|established|leading|pioneer|expert|specialist|professional|skilled|experienced|qualified|certified|licensed|insured|bonded|registered|patented|trademarked|copyrighted|proprietary|exclusive|unique|original|authentic|genuine|real|actual|true|legitimate|valid|legal|official|authorized|permitted|allowed|approved|sanctioned|endorsed|sponsored|funded|supported|backed|promoted|featured|highlighted|showcased|demonstrated|presented|displayed|exhibited|revealed|unveiled|introduced|launched|released|published|distributed|available|accessible|obtainable|acquirable|purchasable|affordable|reasonable|competitive|fair|just|equitable|balanced|moderate|sensible|practical|realistic|achievable|attainable|reachable|possible|feasible|viable|workable|functional|operational|effective|efficient|productive|successful|profitable|valuable|beneficial|useful|helpful|advantageous|favorable|positive|constructive|creative|innovative|progressive|forward|thinking|visionary|strategic|tactical|analytical|logical|rational|reasonable|intelligent|smart|wise|clever|brilliant|genius|master|expert|professional|skilled|talented|gifted|natural|born|innate|inherent|intrinsic|fundamental|essential|basic|primary|core|central|main|principal|key|critical|vital|crucial|important|significant|major|substantial|considerable|notable|remarkable|exceptional|outstanding|distinguished|prominent|eminent|renowned|famous|well|known|celebrated|acclaimed|honored|recognized|respected|admired|appreciated|valued|esteemed|revered|worshipped|adored|loved|cherished|treasured|prized|coveted|desired|wanted|needed|required|necessary|essential|indispensable|vital|critical|crucial|key|fundamental|basic|primary|core|central|main|principal|essential|important|necessary|required|needed|wanted|desired|coveted|prized|treasured|cherished|adored|loved|worshipped|revered|esteemed|valued|appreciated|admired|respected|recognized|honored|acclaimed|celebrated|well|known|famous|renowned|eminent|prominent|distinguished|outstanding|exceptional|remarkable|notable|substantial|considerable|major|significant|important|key|critical|vital|crucial|essential|indispensable|necessary|required|needed|primary|basic|fundamental|core|central|main|principal)\s+(\w+)\b', 1.0),
        (r'\b(bad|poor|terrible|awful|horrible|disappointing|weak|slow|small|tiny|dim|blurry|rough|uncomfortable|difficult|complex|unreliable|fragile|unstable|inaccurate|imprecise|inefficient|ineffective|useless|harmful|detrimental|negative|inferior|low|basic|budget|cheap|expensive|overpriced|outdated|obsolete|old|worn|damaged|broken|faulty|defective|malfunctioning|problematic|troublesome|difficult|challenging|hard|tough|demanding|strenuous|stressful|pressing|urgent|critical|serious|severe|extreme|intense|harsh|rough|coarse|crude|primitive|basic|simple|elementary|fundamental|beginner|starter|entry|level|amateur|novice|inexperienced|unskilled|untrained|unqualified|incompetent|incapable|unable|unfit|unsuitable|inappropriate|wrong|incorrect|false|fake|imitation|counterfeit|illegal|unauthorized|unlicensed|unregistered|unapproved|untested|unverified|unproven|unreliable|unstable|inconsistent|irregular|uneven|unbalanced|unsteady|shaky|wobbly|loose|tight|stiff|rigid|inflexible|brittle|fragile|delicate|sensitive|vulnerable|exposed|unprotected|unsafe|dangerous|hazardous|risky|perilous|uncertain|doubtful|questionable|suspicious|dubious|shady|dishonest|fraudulent|deceptive|misleading|false|fake|artificial|synthetic|unnatural|processed|contaminated|polluted|dirty|unclean|impure|tainted|spoiled|rotten|decayed|stale|old|expired|outdated|obsolete|ancient|prehistoric|primitive|underdeveloped|backward|retrograde|regressive|declining|failing|deteriorating|degrading|worsening|deteriorated|degraded|damaged|broken|shattered|destroyed|ruined|wrecked|demolished|obliterated|eradicated|eliminated|removed|deleted|lost|missing|absent|gone|vanished|disappeared|evaporated|faded|diminished|reduced|decreased|lessened|lowered|dropped|fallen|sunk|collapsed|crumbled|disintegrated|fragmented|shattered|splintered|cracked|fractured|broken|damaged|hurt|injured|wounded|harmed|impaired|disabled|handicapped|crippled|paralyzed|incapacitated|debilitated|weakened|exhausted|drained|depleted|emptied|hollow|vacant|bare|naked|exposed|uncovered|revealed|disclosed|unveiled|unmasked|uncovered|discovered|found|located|identified|recognized|acknowledged|admitted|confessed|revealed|disclosed|exposed|uncovered|discovered|found|located|identified|recognized|acknowledged|admitted|confessed|revealed|disclosed|exposed|uncovered|discovered|found|located|identified|recognized|acknowledged|admitted|confessed|revealed|disclosed)\s+(\w+)\b', -1.0),
    ]
    
    for sent in sentences:
        for pattern, strength in patterns:
            matches = re.findall(pattern, sent.lower())
            for match in matches:
                if isinstance(match, tuple):
                    noun = match[-1]
                else:
                    # Split and get the last word
                    words = match.split()
                    noun = words[-1] if words else match
                
                if len(noun) >= 3 and noun not in _GENERIC_TERMS:
                    pairs.append((noun, strength))
    
    return pairs


def _stage1_dependency(sentences: List[str], top_n: int) -> List[str]:
    """
    Extract aspects where a noun is connected to an opinion word via:
      amod  — adjective modifies noun directly ("great battery")
      nsubj — noun is subject of opinion predicate ("battery is great")
      dobj  — noun is object of opinion verb ("loved the sound")
    """
    pairs = _extract_amod_pairs_spacy(sentences)
    
    # Sort by strength and return top nouns
    pairs.sort(key=lambda x: abs(x[1]), reverse=True)
    return [noun for noun, _ in pairs[:top_n]]


# ---------------------------------------------------------------------------
# STAGE 2 — Noun chunk fallback
# ---------------------------------------------------------------------------

def _stage2_noun_chunks(sentences: List[str], top_n: int) -> List[str]:
    """
    Extract noun phrases using simple regex (replacing spaCy noun chunks).
    Example: "noise cancellation is good" → "noise cancellation"
    """
    freq: Counter = Counter()
    
    # Simple regex patterns for noun phrase extraction
    patterns = [
        r'\b(?:the|a|an)?\s*([a-z]+\s+(?:performance|price|quality|design|feature|function|capability|ability|skill|talent|capacity|power|strength|speed|size|weight|dimension|measurement|specification|standard|requirement|condition|state|status|situation|circumstance|factor|element|component|part|section|portion|segment|piece|item|unit|module|system|structure|framework|architecture|layout|format|style|type|kind|sort|variety|category|class|group|set|collection|series|range|spectrum|scale|level|degree|extent|scope|reach|span|length|width|height|depth|thickness|diameter|radius|circumference|perimeter|area|volume|capacity|size|magnitude|amount|quantity|number|count|total|sum|average|mean|median|mode|range|variance|deviation|standard|deviation|error|accuracy|precision|tolerance|margin|buffer|reserve|surplus|deficit|shortage|excess|abundance|scarcity|plenty|wealth|poverty|richness|poorness|success|failure|victory|defeat|win|loss|gain|profit|benefit|advantage|disadvantage|pro|con|positive|negative|good|bad|right|wrong|correct|incorrect|true|false|real|fake|genuine|artificial|natural|synthetic|organic|inorganic|living|dead|alive|lifeless|animate|inanimate|active|passive|dynamic|static|moving|stationary|mobile|immobile|portable|fixed|flexible|rigid|soft|hard|smooth|rough|even|uneven|flat|curved|straight|bent|twisted|crooked|level|slanted|vertical|horizontal|parallel|perpendicular|diagonal|angular|round|square|rectangular|triangular|circular|oval|elliptical|spherical|cylindrical|conical|pyramidal|cubic|tetrahedral|octahedral|hexagonal|pentagonal|polygonal|irregular|regular|symmetrical|asymmetrical|balanced|unbalanced|stable|unstable|steady|unsteady|firm|loose|tight|slack|tense|relaxed|stiff|limber|rigid|flexible|elastic|plastic|brittle|ductile|malleable|hard|soft|tough|fragile|strong|weak|durable|perishable|lasting|temporary|permanent|transient|stable|unstable|volatile|inert|reactive|active|passive|energetic|lethargic|vigorous|feeble|powerful|powerless|mighty|helpless|dominant|submissive|aggressive|defensive|offensive|protective|destructive|constructive|creative|analytical|logical|rational|irrational|reasonable|unreasonable|sensible|nonsensical|practical|impractical|realistic|unrealistic|optimistic|pessimistic|hopeful|despairing|confident|insecure|sure|unsure|certain|uncertain|definite|indefinite|clear|unclear|obvious|ambiguous|explicit|implicit|direct|indirect|straightforward|complicated|simple|complex|easy|difficult|hard|soft|rough|smooth|coarse|fine|thick|thin|wide|narrow|broad|slim|fat|thin|heavy|light|dense|sparse|full|empty|complete|incomplete|whole|partial|total|fractional|absolute|relative|exact|approximate|precise|imprecise|accurate|inaccurate|correct|incorrect|right|wrong|proper|improper|appropriate|inappropriate|suitable|unsuitable|fit|unfit|perfect|imperfect|flawless|flawed|ideal|realistic|optimal|suboptimal|maximum|minimum|optimal|best|worst|better|worse|superior|inferior|higher|lower|greater|lesser|more|less|most|least|first|last|initial|final|primary|secondary|main|auxiliary|principal|associate|chief|deputy|senior|junior|head|assistant|lead|support|key|minor|major|significant|insignificant|important|unimportant|essential|nonessential|critical|noncritical|vital|nonvital|crucial|noncrucial|fundamental|superficial|deep|shallow|profound|simple|complex|basic|advanced|elementary|sophisticated|primitive|modern|ancient|old|new|young|mature|immature|ripe|unripe|fresh|stale|raw|cooked|natural|processed|organic|synthetic|pure|impure|clean|dirty|sterile|contaminated|hygienic|unhygienic|safe|unsafe|secure|insecure|protected|unprotected|guarded|unguarded|monitored|unmonitored|supervised|unsupervised|controlled|uncontrolled|regulated|unregulated|restricted|unrestricted|limited|unlimited|finite|infinite|bounded|unbounded|closed|open|accessible|inaccessible|available|unavailable|present|absent|existing|nonexistent|real|imaginary|actual|potential|theoretical|practical|experimental|empirical|hypothetical|observed|unobserved|measured|unmeasured|calculated|estimated|approximate|exact|precise|rough|detailed|general|specific|broad|narrow|wide|tight|loose|strict|lenient|hard|soft|tough|easy|simple|difficult|complex|complicated|straightforward|direct|indirect|immediate|delayed|instant|gradual|sudden|abrupt|smooth|jerky|steady|unsteady|regular|irrregular|constant|variable|fixed|flexible|stable|unstable|permanent|temporary|lasting|fleeting|enduring|transient|durable|fragile|strong|weak|powerful|powerless|effective|ineffective|efficient|inefficient|productive|unproductive|useful|useless|helpful|harmful|beneficial|detrimental|advantageous|disadvantageous|positive|negative|favorable|unfavorable|good|bad|right|wrong|correct|incorrect|proper|improper|appropriate|inappropriate)s)\b',
        r'\b([a-z]+\s+(?:performance|price|quality|design|feature|function|capability|ability|skill|talent|capacity|power|strength|speed|size|weight|dimension|measurement|specification|standard|requirement|condition|state|status|situation|circumstance|factor|element|component|part|section|portion|segment|piece|item|unit|module|system|structure|framework|architecture|layout|format|style|type|kind|sort|variety|category|class|group|set|collection|series|range|spectrum|scale|level|degree|extent|scope|reach|span|length|width|height|depth|thickness|diameter|radius|circumference|perimeter|area|volume|capacity|size|magnitude|amount|quantity|number|count|total|sum|average|mean|median|mode|range|variance|deviation|standard|deviation|error|accuracy|precision|tolerance|margin|buffer|reserve|surplus|deficit|shortage|excess|abundance|scarcity|plenty|wealth|poverty|richness|poorness|success|failure|victory|defeat|win|loss|gain|profit|benefit|advantage|disadvantage|pro|con|positive|negative|good|bad|right|wrong|correct|incorrect|true|false|real|fake|genuine|artificial|natural|synthetic|organic|inorganic|living|dead|alive|lifeless|animate|inanimate|active|passive|dynamic|static|moving|stationary|mobile|immobile|portable|fixed|flexible|rigid|soft|hard|smooth|rough|even|uneven|flat|curved|straight|bent|twisted|crooked|level|slanted|vertical|horizontal|parallel|perpendicular|diagonal|angular|round|square|rectangular|triangular|circular|oval|elliptical|spherical|cylindrical|conical|pyramidal|cubic|tetrahedral|octahedral|hexagonal|pentagonal|polygonal|irregular|regular|symmetrical|asymmetrical|balanced|unbalanced|stable|unstable|steady|unsteady|firm|loose|tight|slack|tense|relaxed|stiff|limber|rigid|flexible|elastic|plastic|brittle|ductile|malleable|hard|soft|tough|fragile|strong|weak|durable|perishable|lasting|temporary|permanent|transient|stable|unstable|volatile|inert|reactive|active|passive|energetic|lethargic|vigorous|feeble|powerful|powerless|mighty|helpless|dominant|submissive|aggressive|defensive|offensive|protective|destructive|constructive|creative|analytical|logical|rational|irrational|reasonable|unreasonable|sensible|nonsensical|practical|impractical|realistic|unrealistic|optimistic|pessimistic|hopeful|despairing|confident|insecure|sure|unsure|certain|uncertain|definite|indefinite|clear|unclear|obvious|ambiguous|explicit|implicit|direct|indirect|straightforward|complicated|simple|complex|easy|difficult|hard|soft|rough|smooth|coarse|fine|thick|thin|wide|narrow|broad|slim|fat|thin|heavy|light|dense|sparse|full|empty|complete|incomplete|whole|partial|total|fractional|absolute|relative|exact|approximate|precise|imprecise|accurate|inaccurate|correct|incorrect|right|wrong|proper|improper|appropriate|inappropriate|suitable|unsuitable|fit|unfit|perfect|imperfect|flawless|flawed|ideal|realistic|optimal|suboptimal|maximum|minimum|optimal|best|worst|better|worse|superior|inferior|higher|lower|greater|lesser|more|less|most|least|first|last|initial|final|primary|secondary|main|auxiliary|principal|associate|chief|deputy|senior|junior|head|assistant|lead|support|key|minor|major|significant|insignificant|important|unimportant|essential|nonessential|critical|noncritical|vital|nonvital|crucial|noncrucial|fundamental|superficial|deep|shallow|profound|simple|complex|basic|advanced|elementary|sophisticated|primitive|modern|ancient|old|new|young|mature|immature|ripe|unripe|fresh|stale|raw|cooked|natural|processed|organic|synthetic|pure|impure|clean|dirty|sterile|contaminated|hygienic|unhygienic|safe|unsafe|secure|insecure|protected|unprotected|guarded|unguarded|monitored|unmonitored|supervised|unsupervised|controlled|uncontrolled|regulated|unregulated|restricted|unrestricted|limited|unlimited|finite|infinite|bounded|unbounded|closed|open|accessible|inaccessible|available|unavailable|present|absent|existing|nonexistent|real|imaginary|actual|potential|theoretical|practical|experimental|empirical|hypothetical|observed|unobserved|measured|unmeasured|calculated|estimated|approximate|exact|precise|rough|detailed|general|specific|broad|narrow|wide|tight|loose|strict|lenient|hard|soft|tough|easy|simple|difficult|complex|complicated|straightforward|direct|indirect|immediate|delayed|instant|gradual|sudden|abrupt|smooth|jerky|steady|unsteady|regular|irrregular|constant|variable|fixed|flexible|stable|unstable|permanent|temporary|lasting|fleeting|enduring|transient|durable|fragile|strong|weak|powerful|powerless|effective|ineffective|efficient|inefficient|productive|unproductive|useful|useless|helpful|harmful|beneficial|detrimental|advantageous|disadvantageous|positive|negative|favorable|unfavorable|good|bad|right|wrong|correct|incorrect|proper|improper|appropriate|inappropriate)s)\b',
    ]
    
    for sent in sentences:
        for pattern in patterns:
            matches = re.findall(pattern, sent.lower())
            for match in matches:
                text = match.strip()
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
