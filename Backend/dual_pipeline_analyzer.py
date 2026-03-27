"""
dual_pipeline_analyzer.py
Correct Architecture: Two independent pipelines
1. Component Generator (from search query ONLY)
2. Aspect Analyzer (from reviews ONLY)
"""
import re
import logging
from typing import Dict, List, Any, Optional
from product_aspect_analyzer import ProductAspectAnalyzer

logger = logging.getLogger(__name__)

class DualPipelineAnalyzer:
    """
    Two independent pipelines:
    - Component Generator: uses ONLY search_query
    - Aspect Analyzer: uses ONLY reviews
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize dual pipeline analyzer.
        
        Args:
            llm_client: Optional LLM client for component generation
        """
        self.llm_client = llm_client
        self.aspect_analyzer = ProductAspectAnalyzer()
        
        # Fallback component knowledge base
        self.component_knowledge = {
            # Electronics
            "laptop": ["CPU", "RAM", "motherboard", "battery", "display", "keyboard", "trackpad", "storage", "graphics card", "cooling system", "chassis", "power adapter", "webcam", "speakers", "ports"],
            "smartphone": ["processor", "RAM", "storage", "display", "camera", "battery", "speakers", "microphone", "ports", "sensors", "glass", "frame", "buttons", "charging port", "antenna", "vibration motor"],
            "headphones": ["drivers", "cable", "ear pads", "headband", "microphone", "controls", "battery", "charging port", "connectivity module", "ear cups", "audio jack"],
            "tablet": ["processor", "RAM", "storage", "display", "battery", "cameras", "speakers", "microphones", "ports", "sensors", "glass", "frame", "connectivity", "stylus"],
            "tv": ["display panel", "processor", "RAM", "storage", "speakers", "ports", "stand", "remote", "power supply", "tuner", "smart tv module", "connectivity", "backlight", "bezel"],
            "camera": ["sensor", "lens", "processor", "viewfinder", "display", "battery", "memory card slot", "ports", "body", "dial", "buttons", "flash", "image stabilization", "shutter", "aperture", "focus ring"],
            "smartwatch": ["processor", "RAM", "storage", "display", "sensors", "battery", "band", "crown", "buttons", "connectivity", "charging port", "glass", "frame", "heart rate monitor", "accelerometer", "gyroscope"],
            "desktop": ["CPU", "motherboard", "RAM", "storage", "graphics card", "power supply", "case", "cooling system", "ports", "fans", "cables", "optical drive", "expansion slots"],
            "monitor": ["display panel", "stand", "ports", "power supply", "controls", "speakers", "bezel", "panel technology", "backlight", "resolution", "refresh rate"],
            "speaker": ["drivers", "cabinet", "crossover", "ports", "grille", "amplifier", "power supply", "controls", "connectivity", "tweeter", "woofer", "enclosure"],
            
            # Kitchen Appliances
            "coffee maker": ["water reservoir", "heating element", "pump", "filter basket", "brewing chamber", "carafe", "power cord", "controls", "drip tray", "warming plate"],
            "blender": ["motor", "blades", "jar", "lid", "base", "controls", "power cord", "gasket", "pulse button", "speed settings"],
            "microwave": ["magnetron", "waveguide", "turntable", "control panel", "door", "interior cavity", "power supply", "timer", "safety sensors"],
            "refrigerator": ["compressor", "condenser", "evaporator", "thermostat", "door seals", "shelves", "drawers", "light", "ice maker", "water dispenser"],
            "toaster": ["heating elements", "timer", "bread slots", "lever", "crumb tray", "controls", "power cord", "temperature sensor"],
            "oven": ["heating element", "thermostat", "door", "racks", "timer", "controls", "interior cavity", "convection fan", "temperature sensor"],
            "dishwasher": ["motor", "pump", "spray arms", "heating element", "door", "racks", "controls", "detergent dispenser", "drain valve"],
            "kettle": ["heating element", "water chamber", "lid", "handle", "base", "power cord", "temperature sensor", "auto shut-off"],
            "mixer": ["motor", "beaters", "bowl", "stand", "controls", "speed settings", "tilt mechanism", "power cord"],
            "food processor": ["motor", "blades", "discs", "bowl", "lid", "controls", "feed tube", "pulse button", "safety lock"],
            "knife": ["blade", "handle", "tang", "bolster", "heel", "tip", "edge", "spine", "guard", "rivets", "steel", "balance", "sharpness", "grip", "weight"],
            
            # Home Appliances
            "washing machine": ["motor", "drum", "agitator", "pump", "door", "controls", "detergent dispenser", "water inlet valve", "timer", "safety lock"],
            "dryer": ["heating element", "drum", "motor", "lint filter", "door", "controls", "timer", "temperature sensor", "exhaust vent"],
            "vacuum cleaner": ["motor", "suction hose", "brush roll", "filter", "bag or bin", "power cord", "controls", "attachments", "height adjustment"],
            "air conditioner": ["compressor", "condenser", "evaporator", "fan", "filter", "thermostat", "remote", "timer", "vents", "drain pan"],
            "fan": ["motor", "blades", "base", "controls", "oscillation mechanism", "power cord", "speed settings", "grille"],
            "heater": ["heating element", "thermostat", "fan", "controls", "power cord", "safety features", "timer", "temperature settings"],
            "humidifier": ["water tank", "ultrasonic membrane", "fan", "controls", "filter", "power cord", "humidity sensor", "mister"],
            
            # Clothing & Accessories
            "shirt": ["collar", "sleeve", "cuff", "placket", "buttons", "fabric", "hem", "yoke", "pocket", "shoulder", "buttonholes", "interfacing", "lining"],
            "pants": ["waistband", "fly", "pockets", "belt loops", "hem", "seams", "fabric", "zipper", "button", "inseam", "outseam", "rise", "leg opening"],
            "shoes": ["sole", "upper", "laces", "tongue", "insole", "outsole", "heel", "toe box", "eyelets", "quarter", "midsole", "shank", "last", "welt"],
            "jacket": ["collar", "sleeves", "zipper", "pockets", "lining", "fabric", "hem", "cuffs", "hood", "shoulders", "storm flap", "interfacing", "buttons"],
            "dress": ["bodice", "skirt", "waistline", "hemline", "sleeves", "neckline", "back", "zipper", "buttons", "lining", "fabric", "seams", "darts", "pleats"],
            "hat": ["brim", "crown", "band", "sweatband", "material", "trim", "lining", "eyelets", "decoration"],
            "gloves": ["fingers", "palm", "cuff", "wrist opening", "material", "lining", "seams", "grip", "closure"],
            "scarf": ["fabric", "fringe", "hem", "length", "material", "weave", "pattern", "tassels"],
            "belt": ["strap", "buckle", "holes", "keeper", "material", "stitching", "tip", "loop"],
            
            # Beauty & Makeup
            "makeup": ["pigment", "base", "preservatives", "emulsifiers", "texture", "coverage", "longevity", "finish", "applicator", "packaging", "ingredients", "formula", "shade", "blendability", "wear time"],
            "foundation": ["pigment", "base", "preservatives", "emulsifiers", "coverage", "finish", "longevity", "spf", "shade range", "formula", "texture", "blendability", "wear time", "oil control", "hydration"],
            "lipstick": ["pigment", "wax", "oils", "emollients", "color", "finish", "longevity", "packaging", "bullet", "case", "formula", "texture", "hydration", "wear time", "shade"],
            "mascara": ["pigment", "wax", "oils", "brush", "formula", "volume", "length", "curl", "waterproof", "packaging", "tube", "wand", "smudge proof", "clump free", "wear time"],
            "eyeshadow": ["pigment", "base", "binders", "formula", "texture", "finish", "blendability", "longevity", "packaging", "palette", "applicator", "shade", "crease proof", "intensity", "blendability"],
            
            # Sports & Fitness
            "bicycle": ["frame", "wheels", "tires", "brakes", "gears", "pedals", "handlebars", "seat", "chain", "fork", "shock absorbers"],
            "treadmill": ["motor", "belt", "deck", "console", "handrails", "incline mechanism", "safety key", "speed controls", "heart rate monitor"],
            "dumbbells": ["handle", "weight plates", "collars", "grip", "material", "finish"],
            "yoga mat": ["material", "texture", "thickness", "non-slip surface", "edges", "carrying strap"],
            "tennis racket": ["frame", "strings", "grip", "head", "throat", "butt cap", "grommets", "vibration dampener"],
            "football": ["panels", "stitching", "bladder", "valve", "material", "texture", "shape", "weight"],
            "basketball": ["panels", "pebbled surface", "valve", "rim", "material", "bounce", "grip", "weight"],
            
            # Office & Study
            "desk": ["desktop", "legs", "drawers", "keyboard tray", "cable management", "surface", "edges", "hardware", "frame", "support beams", "drawer slides", "handles", "back panel"],
            "chair": ["seat", "backrest", "legs", "armrests", "casters", "height adjustment", "lumbar support", "material", "base", "tilt mechanism", "swivel base"],
            "pen": ["ink cartridge", "tip", "barrel", "cap", "clip", "grip", "mechanism", "refill", "ballpoint", "rollerball"],
            "notebook": ["cover", "pages", "spiral", "binding", "ruling", "paper quality", "size", "dividers", "spine", "corners", "elastic closure"],
            "backpack": ["main compartment", "front pocket", "side pockets", "shoulder straps", "back panel", "zipper", "material", "compression straps", "padded back", "chest strap", "water bottle holder"],
            
            # Kitchen Utensils & Cookware
            "water bottle": ["bottle", "cap", "seal", "mouthpiece", "material", "lid", "carrying loop", "insulation", "volume markings", "base", "neck"],
            "cooker": ["heating element", "pot", "lid", "handle", "temperature control", "timer", "safety valve", "power cord", "indicator lights", "inner pot", "outer body"],
            "cupboard": ["doors", "shelves", "hinges", "handles", "back panel", "sides", "top", "adjustable feet", "mounting brackets", "interior lining"],
            "wardrobe": ["doors", "hanging rod", "shelves", "drawers", "mirror", "handles", "hinges", "back panel", "sides", "top", "adjustable feet"],
            "broom": ["bristles", "handle", "head", "grip", "dustpan", "connection joint", "hanging loop", "tip", "ferrule"],
            "broom stick": ["handle", "grip", "bristle head", "connection joint", "hanging loop", "tip"],
            
            # Electronics Accessories
            "phone case": ["material", "buttons", "ports", "screen protector", "kickstand", "camera cutout", "magnetic closure"],
            "screen protector": ["material", "adhesive", "thickness", "clarity", "oleophobic coating", "edge coverage"],
            "charger": ["cable", "adapter", "USB connector", "power rating", "indicator light", "material", "length"],
            "cable management": ["ties", "clips", "sleeves", "organizers", "material", "length", "color", "durability"],
            "power bank": ["battery", "USB ports", "indicator lights", "capacity", "charging port", "material", "size", "weight"],
            "wireless charger": ["coil", "base", "power adapter", "indicator", "material", "charging area", "compatibility"],
            "tablet stand": ["base", "adjustment", "material", "stability", "cable routing", "angle settings", "non-slip feet"],
            "laptop stand": ["base", "adjustment", "material", "ventilation", "cable management", "ergonomics", "stability"],
            "monitor mount": ["arm", "base", "VESA plate", "adjustment", "material", "weight capacity", "cable management"],
            
            # Travel
            "luggage": ["shell", "wheels", "handle", "zippers", "locks", "compartments", "material", "size", "weight", "expandable sections"],
            "suitcase": ["hard shell", "soft shell", "wheels", "handle", "locks", "compartments", "material", "size", "weight"],
            "travel pillow": ["inflatable", "memory foam", "cover", "material", "compressibility", "size", "carrying case"],
            "travel organizer": ["compartments", "zippers", "material", "transparent sections", "labels", "hooks", "size"],
            "toiletry bag": ["compartments", "hook", "material", "water-resistant", "mirror", "hanging loop", "size"],
            "passport holder": ["sleeve", "material", "RFID blocking", "slots", "closure", "size", "protection"],
            
            # Seasonal & Holiday
            "christmas lights": ["bulbs", "wire", "plug", "fuse", "controller", "material", "length", "color", "indoor/outdoor rating"],
            "decorations": ["material", "hooks", "stands", "lights", "power source", "assembly", "storage", "weather resistance"],
            "holiday ornaments": ["material", "hook", "paint", "glitter", "size", "packaging", "fragility", "theme"],
            "wreath": ["base", "frame", "material", "decorations", "lights", "hanging mechanism", "size", "theme"],
            "garland": ["material", "lights", "wire", "connectors", "length", "color", "pattern", "power source"],
            "inflatables": ["material", "air valve", "seams", "reinforcement", "pump", "stakes", "repair kit", "size"],
            "outdoor decorations": ["weather-resistant material", "stakes", "lights", "power source", "assembly", "storage", "UV protection"],
            
            # Eatables & Food Items
            "noodles": ["flour", "water", "eggs", "salt", "shape", "texture", "cooking time", "drying method", "thickness", "length"],
            "pasta": ["flour", "water", "eggs", "salt", "shape", "texture", "cooking time", "drying method", "thickness", "type"],
            "rice": ["grains", "starch", "water content", "cooking method", "variety", "texture", "length", "aroma", "milling process"],
            "bread": ["flour", "yeast", "water", "salt", "crust", "crumb", "texture", "shape", "preservatives", "additives", "baking time", "oven temperature"],
            "biscuits": ["flour", "butter", "sugar", "leavening", "shape", "texture", "baking time", "thickness", "surface", "edges"],
            "cookies": ["flour", "butter", "sugar", "eggs", "flavorings", "shape", "texture", "baking time", "chips", "decorations"],
            "chips": ["potatoes", "oil", "salt", "seasoning", "thickness", "crispness", "shape", "packaging", "flavor coating"],
            "chocolate": ["cocoa", "sugar", "milk", "cocoa butter", "tempering", "shape", "texture", "filling", "wrapping", "cocoa percentage"],
            "candy": ["sugar", "flavorings", "colorings", "shape", "texture", "wrapping", "hardness", "filling", "coating"],
            "ice cream": ["milk", "cream", "sugar", "flavorings", "air content", "texture", "temperature", "scoop", "cone", "toppings"],
            "yogurt": ["milk", "cultures", "sugar", "fruit", "texture", "consistency", "flavor", "container", "live cultures", "fat content"],
            "cheese": ["milk", "culture", "rennet", "fat content", "aging", "texture", "flavor", "rind", "shape", "wax coating"],
            "butter": ["cream", "salt", "churning", "texture", "flavor", "consistency", "packaging", "fat content", "color"],
            "eggs": ["shell", "white", "yolk", "membrane", "size", "color", "freshness", "grade", "nutrition", "cooking properties"],
            "milk": ["fat content", "protein", "lactose", "vitamins", "pasteurization", "packaging", "freshness", "source", "homogenization"],
            "juice": ["fruit", "water", "sugar", "preservatives", "pulp", "acidity", "vitamins", "pasteurization", "packaging", "concentration"],
            "soda": ["water", "sugar", "flavorings", "carbonation", "acidulants", "preservatives", "color", "packaging", "carbonation level"],
            "tea": ["leaves", "water", "flavor compounds", "caffeine", "tannins", "aroma", "color", "steeping time", "packaging", "variety"],
            "coffee": ["beans", "roast level", "grind", "water", "caffeine", "aroma", "acidity", "brewing method", "origin", "processing"],
            "honey": ["nectar", "enzymes", "pollen", "water content", "crystallization", "color", "flavor", "texture", "viscosity", "source"],
            "jam": ["fruit", "sugar", "pectin", "acid", "flavor", "texture", "consistency", "color", "preservation", "packaging"],
            "pickles": ["vegetable", "vinegar", "salt", "spices", "fermentation", "texture", "crunch", "flavor", "brine", "jar"],
            "sauce": ["base", "seasonings", "thickener", "acid", "flavor", "consistency", "color", "aroma", "ingredients", "cooking method"],
            "soup": ["broth", "vegetables", "meat", "seasonings", "noodles", "consistency", "temperature", "garnish", "serving size", "nutrition"],
            "salad": ["greens", "vegetables", "dressing", "protein", "toppings", "freshness", "texture", "flavor combination", "seasoning", "presentation"],
            "sandwich": ["bread", "filling", "spread", "vegetables", "meat", "cheese", "sauce", "layering", "cut", "toasting"],
            "pizza": ["dough", "sauce", "cheese", "toppings", "seasonings", "baking", "crust", "temperature", "cooking time", "slicing"],
            "burger": ["patty", "bun", "lettuce", "tomato", "onion", "cheese", "sauce", "pickles", "seasoning", "grilling"],
            "pasta dishes": ["pasta", "sauce", "cheese", "meat", "vegetables", "herbs", "seasoning", "cooking method", "presentation", "serving size"],
            "curry": ["spices", "vegetables", "meat", "sauce", "cooking method", "aroma", "heat level", "thickness", "garnish", "serving"],
            "stir fry": ["vegetables", "meat", "sauce", "oil", "seasonings", "cooking method", "texture", "aroma", "wok", "high heat"],
            "roast": ["meat", "vegetables", "seasonings", "cooking method", "temperature", "time", "marinade", "crust", "juices", "tenderness"],
            "grilled items": ["meat", "vegetables", "marinade", "grill marks", "smoke flavor", "temperature", "cooking time", "seasonings", "charring", "juices"],
            "baked goods": ["flour", "sugar", "fat", "leavening", "oven temperature", "baking time", "texture", "crust", "filling", "decoration"],
            "fried items": ["batter", "oil", "temperature", "cooking time", "crispness", "drainage", "seasoning", "golden color", "texture", "flavor"],
            "steamed items": ["steamer", "water", "basket", "temperature", "cooking time", "moisture", "texture", "flavor retention", "nutrients", "aroma"],
            "boiled items": ["water", "temperature", "cooking time", "texture", "flavor", "nutrients", "seasoning", "softness", "ingredients", "aroma"],
            "frozen foods": ["freezer", "temperature", "packaging", "preservation", "ice crystals", "texture", "reheating", "flavor", "nutrition", "shelf life"],
            "canned foods": ["can", "preservatives", "liquid", "sealing", "shelf life", "nutrition", "flavor", "texture", "ingredients", "processing"],
            "dried foods": ["dehydration", "preservation", "texture", "rehydration", "flavor concentration", "shelf life", "packaging", "nutrition", "weight", "storage"],
            "fermented foods": ["bacteria", "yeast", "fermentation time", "flavor development", "texture", "preservation", "aroma", "nutrition", "packaging", "aging"],
            "pickled items": ["vinegar", "salt", "spices", "fermentation", "texture", "flavor", "preservation", "jar", "brine", "time"],
            "smoked foods": ["smoke", "wood type", "temperature", "time", "flavor infusion", "preservation", "texture", "aroma", "color", "curing"],
            "cured foods": ["salt", "sugar", "nitrates", "curing time", "preservation", "flavor", "texture", "color", "safety", "packaging"],
            
            # Food & Beverages
            "food": ["ingredients", "nutrients", "protein", "carbohydrates", "fats", "vitamins", "minerals", "fiber", "calories", "serving size", "preservatives", "additives", "flavorings"],
            "snacks": ["ingredients", "nutrition facts", "protein", "carbs", "fat", "sodium", "sugar", "calories", "serving size", "flavor", "texture", "packaging"],
            "drink": ["ingredients", "water", "sugar", "caffeine", "flavorings", "preservatives", "carbonation", "nutrients", "vitamins", "minerals", "calories"],
            "fruit": ["skin", "flesh", "seeds", "core", "stem", "nutrients", "vitamins", "fiber", "sugar", "water content", "ripeness", "texture"],
            "vegetables": ["skin", "flesh", "seeds", "leaves", "roots", "nutrients", "vitamins", "fiber", "water content", "texture", "freshness"],
            "meat": ["muscle", "fat", "bones", "skin", "protein", "nutrients", "texture", "marbling", "cut", "cooking method"],
            "bread": ["flour", "yeast", "water", "salt", "crust", "crumb", "texture", "shape", "preservatives", "additives"],
            "cheese": ["milk", "culture", "rennet", "fat content", "aging", "texture", "flavor", "rind", "shape"],
            
            # Vehicles
            "car": ["engine", "transmission", "wheels", "brakes", "steering", "suspension", "frame", "body", "interior", "seats", "dashboard", "battery", "fuel system", "exhaust"],
            "motorcycle": ["engine", "frame", "wheels", "brakes", "handlebars", "seat", "fuel tank", "exhaust", "suspension", "transmission"],
            "bicycle": ["frame", "wheels", "tires", "brakes", "gears", "pedals", "handlebars", "seat", "chain", "fork", "shock absorbers"],
            "scooter": ["deck", "wheels", "handlebars", "brakes", "folding mechanism", "grip tape", "bearings", "kickstand"],
            "skateboard": ["deck", "wheels", "trucks", "bearings", "grip tape", "nose", "tail", "hardware"],
            
            # Books & Media
            "book": ["cover", "pages", "spine", "binding", "chapters", "illustrations", "index", "table of contents", "foreword", "afterword"],
            "magazine": ["cover", "pages", "binding", "articles", "advertisements", "photographs", "table of contents", "masthead"],
            "newspaper": ["headlines", "articles", "photographs", "advertisements", "sections", "date", "pages", "fold"],
            
            # Beauty & Personal Care
            "perfume": ["fragrance notes", "bottle", "cap", "spray mechanism", "liquid", "concentration", "base notes", "middle notes", "top notes"],
            "cosmetics": ["pigments", "base", "applicator", "container", "preservatives", "fragrance", "texture", "coverage", "finish"],
            "shampoo": ["surfactants", "conditioners", "fragrance", "preservatives", "water", "bottle", "cap", "label"],
            "soap": ["fats", "lye", "additives", "fragrance", "color", "shape", "texture", "packaging"],
            "toothbrush": ["bristles", "handle", "head", "grip", "power source", "timer", "pressure sensor"],
            "razor": ["blades", "handle", "lubrication strip", "pivot", "cartridge", "safety guard"],
            
            # Toys & Games
            "toys": ["plastic", "batteries", "motors", "wheels", "buttons", "sounds", "lights", "remote control", "parts", "assembly"],
            "board game": ["board", "pieces", "dice", "cards", "rules", "box", "timer", "score pad"],
            "video game": ["software", "console", "controller", "graphics", "sound", "story", "characters", "levels"],
            
            # Tools & Hardware
            "hammer": ["head", "handle", "claw", "face", "weight", "balance", "grip", "material"],
            "screwdriver": ["handle", "shaft", "tip", "magnetic tip", "torque", "grip", "material"],
            "drill": ["motor", "chuck", "bit", "trigger", "handle", "battery", "power cord", "speed control"],
            "saw": ["blade", "handle", "guard", "motor", "power source", "cutting depth", "guide"],
            
            # Furniture
            "furniture": ["frame", "cushions", "upholstery", "legs", "arms", "back", "seat", "mechanism", "wood", "metal", "fabric", "hardware"],
            "sofa": ["frame", "cushions", "upholstery", "legs", "arms", "back", "seat", "mechanism", "wood", "metal", "fabric", "hardware"],
            "chair": ["frame", "cushions", "upholstery", "legs", "arms", "back", "seat", "mechanism", "wood", "metal", "fabric", "hardware"],
            "table": ["frame", "cushions", "upholstery", "legs", "arms", "back", "seat", "mechanism", "wood", "metal", "fabric", "hardware"],
            "bed": ["frame", "cushions", "upholstery", "legs", "arms", "back", "seat", "mechanism", "wood", "metal", "fabric", "hardware"],
            
            # Appliances
            "appliances": ["motor", "heating element", "controls", "timer", "power cord", "housing", "filters", "display", "sensors", "safety features"],
            
            # Office Supplies (expanded)
            "stapler": ["base", "magazine", "staples", "handle", "spring", "material", "capacity", "staple size"],
            "paper clips": ["metal", "spring", "finish", "size", "capacity", "material", "coating"],
            "binders": ["rings", "spine", "covers", "material", "capacity", "mechanism", "label area"],
            "file folders": ["folder", "tab", "material", "reinforcement", "label area", "expansion capacity"],
            "pens": ["ink", "ballpoint", "tip", "barrel", "cap", "clip", "grip", "material", "refill mechanism"],
            "markers": ["tip", "ink", "barrel", "cap", "material", "color", "tip type", "eraser"],
            "highlighters": ["ink", "chisel tip", "barrel", "cap", "material", "fluorescent color", "water-based"],
            "scissors": ["blades", "handles", "pivot", "screw", "material", "blade length", "handle grip"],
            "tape dispenser": ["roll", "cutting blade", "base", "material", "tape type", "tension control"],
            "calculator": ["display", "buttons", "battery", "solar panel", "case", "functions", "memory", "power source"],
            
            # Bags (expanded)
            "bag": ["material", "straps", "closure", "pockets", "lining", "base", "size", "hardware"],
            "handbag": ["material", "straps", "closure", "pockets", "lining", "base", "size", "hardware", "zipper"],
            "purse": ["material", "strap", "closure", "compartments", "lining", "size", "hardware", "clasp"],
            "wallet": ["material", "card slots", "bill compartment", "coin pocket", "closure", "size", "ID window", "RFID blocking"],
            
            # Watch variations
            "watch": ["case", "dial", "hands", "crown", "strap", "buckle", "crystal", "movement", "lugs", "bezel"],
            "timepiece": ["case", "dial", "hands", "crown", "strap", "buckle", "crystal", "movement", "lugs", "bezel"]
        }
    
    def generate_components(self, query: str) -> List[str]:
        """
        Generate components using ONLY the search query.
        This is the KEY FIX - components depend ONLY on query, NOT reviews.
        
        Args:
            query: Search query (e.g., "laptop")
            
        Returns:
            List of component names
        """
        query = query.lower().strip()
        
        if not query:
            return ["CPU", "RAM", "storage", "display", "battery"]
        
        # Try LLM first if available
        if self.llm_client:
            try:
                components = self._generate_components_with_llm(query)
                if components:
                    logger.info(f"Generated {len(components)} components using LLM for: {query}")
                    return components
            except Exception as e:
                logger.warning(f"LLM component generation failed: {e}")
        
        # Fallback to knowledge base
        components = self._get_fallback_components(query)
        logger.info(f"Generated {len(components)} components using knowledge base for: {query}")
        return components
    
    def _generate_components_with_llm(self, query: str) -> List[str]:
        """
        Generate components using LLM with the exact prompt format specified.
        
        Args:
            query: Product query
            
        Returns:
            List of component names
        """
        prompt = f"""
List the main physical components of a {query}.
Return only comma separated component names.
Do not include performance metrics.
Example:
Laptop → CPU, RAM, battery, display
"""
        
        try:
            response = self._call_llm(prompt)
            components = self._parse_llm_response(response)
            return components
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return []
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM with the prompt."""
        if hasattr(self.llm_client, 'chat'):
            response = self.llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0
            )
            return response.choices[0].message.content
        
        elif hasattr(self.llm_client, 'generate'):
            response = self.llm_client.generate(
                prompt=prompt,
                max_tokens=100,
                temperature=0
            )
            return response.text
        else:
            raise ValueError("Unsupported LLM client type")
    
    def _parse_llm_response(self, response: str) -> List[str]:
        """Parse LLM response into component list."""
        if not response:
            return []
        
        # Clean response
        response = response.strip()
        
        # Split by comma
        if ',' in response:
            components = [c.strip() for c in response.split(',')]
        else:
            # Fallback: split by newlines or spaces
            components = [c.strip() for c in response.replace('\n', ',').split(',')]
        
        # Clean components
        cleaned = []
        for component in components:
            component = component.strip('\'".,;:()[]{}')
            component = re.sub(r'^\d+\.\s*', '', component)  # Remove numbering
            component = re.sub(r'^[-*•]\s*', '', component)  # Remove bullets
            
            if component and len(component) > 2:
                cleaned.append(component)
        
        return cleaned
    
    def _get_fallback_components(self, query: str) -> List[str]:
        """
        Get components from fallback knowledge base.
        
        Args:
            query: Product query
            
        Returns:
            List of component names
        """
        query = query.lower().strip()
        
        # Special handling for common variations
        special_mappings = {
            # Electronics variations
            "laptop": "laptop",
            "notebook": "laptop",
            "ultrabook": "laptop",
            "smartphone": "smartphone",
            "phone": "smartphone",
            "mobile": "smartphone",
            "cell": "smartphone",
            "cellphone": "smartphone",
            "tablet": "tablet",
            "ipad": "tablet",
            "tv": "tv",
            "television": "tv",
            "headphone": "headphones",
            "earphone": "headphones",
            "earbud": "headphones",
            "earbuds": "headphones",
            "speaker": "speaker",
            "speakers": "speaker",
            "camera": "camera",
            "smartwatch": "smartwatch",
            "watch": "smartwatch",
            "desktop": "desktop",
            "computer": "desktop",
            "pc": "desktop",
            "monitor": "monitor",
            
            # Kitchen appliances variations
            "coffee maker": "coffee maker",
            "coffee": "coffee maker",
            "coffeemaker": "coffee maker",
            "espresso": "coffee maker",
            "blender": "blender",
            "mixer": "mixer",
            "microwave": "microwave",
            "refrigerator": "refrigerator",
            "fridge": "refrigerator",
            "toaster": "toaster",
            "oven": "oven",
            "dishwasher": "dishwasher",
            "kettle": "kettle",
            "food processor": "food processor",
            "knife": "knife",
            "knives": "knife",
            "chef knife": "knife",
            "kitchen knife": "knife",
            "cutting knife": "knife",
            
            # Beauty & Makeup variations
            "makeup": "makeup",
            "cosmetics": "makeup",
            "cosmetic": "makeup",
            "foundation": "foundation",
            "foundations": "foundation",
            "lipstick": "lipstick",
            "lipsticks": "lipstick",
            "lip": "lipstick",
            "mascara": "mascara",
            "eyeshadow": "eyeshadow",
            "eye shadow": "eyeshadow",
            "shadow": "eyeshadow",
            
            # Home appliances variations
            "washing machine": "washing machine",
            "washer": "washing machine",
            "dryer": "dryer",
            "vacuum cleaner": "vacuum cleaner",
            "vacuum": "vacuum cleaner",
            "air conditioner": "air conditioner",
            "ac": "air conditioner",
            "fan": "fan",
            "heater": "heater",
            "humidifier": "humidifier",
            
            # Clothing variations
            "shirt": "shirt",
            "shirts": "shirt",
            "dress": "dress",
            "dresses": "dress", 
            "gown": "dress",
            "gowns": "dress",
            "pants": "pants",
            "trousers": "pants",
            "jeans": "pants",
            "shoes": "shoes",
            "shoe": "shoes",
            "footwear": "shoes",
            "boots": "shoes",
            "sneakers": "shoes",
            "sandals": "shoes",
            "jacket": "jacket",
            "jackets": "jacket",
            "coat": "jacket",
            "hat": "hat",
            "hats": "hat",
            "cap": "hat",
            "gloves": "gloves",
            "glove": "gloves",
            "scarf": "scarf",
            "scarves": "scarf",
            "belt": "belt",
            "belts": "belt",
            "clothing": "shirt",
            "clothes": "shirt",
            "apparel": "shirt",
            "garment": "shirt",
            
            # Sports & fitness variations
            "bicycle": "bicycle",
            "bike": "bicycle",
            "motorcycle": "motorcycle",
            "motorbike": "motorcycle",
            "treadmill": "treadmill",
            "dumbbells": "dumbbells",
            "weights": "dumbbells",
            "yoga mat": "yoga mat",
            "tennis racket": "tennis racket",
            "racket": "tennis racket",
            "football": "football",
            "basketball": "basketball",
            
            # Office & study variations
            "desk": "desk",
            "desks": "desk",
            "chair": "chair",
            "chairs": "chair",
            "pen": "pen",
            "pens": "pen",
            "notebook": "notebook",
            "notebooks": "notebook",
            "backpack": "backpack",
            "backpacks": "backpack",
            
            # Food & beverages variations
            "food": "food",
            "foods": "food",
            "snacks": "snacks",
            "snack": "snacks",
            "drink": "drink",
            "drinks": "drink",
            "beverage": "drink",
            "beverages": "drink",
            "fruit": "fruit",
            "fruits": "fruit",
            "vegetables": "vegetables",
            "vegetable": "vegetables",
            "meat": "meat",
            "meats": "meat",
            "bread": "bread",
            "cheese": "cheese",
            "eat": "food",
            "eatable": "food",
            "eatables": "food",
            "edible": "food",
            "edibles": "food",
            
            # Vehicles variations
            "car": "car",
            "cars": "car",
            "automobile": "car",
            "auto": "car",
            "vehicle": "car",
            "scooter": "scooter",
            "skateboard": "skateboard",
            
            # Books & media variations
            "book": "book",
            "books": "book",
            "magazine": "magazine",
            "magazines": "magazine",
            "newspaper": "newspaper",
            "newspapers": "newspaper",
            
            # Beauty & personal care variations
            "perfume": "perfume",
            "perfumes": "perfume",
            "cosmetics": "cosmetics",
            "makeup": "cosmetics",
            "skincare": "cosmetics",
            "skin care": "cosmetics",
            "skin-care": "cosmetics",
            "lotion": "cosmetics",
            "shampoo": "shampoo",
            "soap": "soap",
            "toothbrush": "toothbrush",
            "razor": "razor",
            "scent": "perfume",
            "fragrance": "perfume",
            
            # Toys & games variations
            "toys": "toys",
            "toy": "toys",
            "game": "toys",
            "games": "toys",
            "board game": "board game",
            "video game": "video game",
            
            # Tools & hardware variations
            "hammer": "hammer",
            "screwdriver": "screwdriver",
            "drill": "drill",
            "saw": "saw",
            
            # Furniture variations
            "furniture": "furniture",
            "furnishing": "furniture",
            "sofa": "furniture",
            "sofas": "furniture",
            "chair": "furniture",
            "chairs": "furniture",
            "table": "furniture",
            "tables": "furniture",
            "bed": "furniture",
            "beds": "furniture",
            
            # Appliances variations
            "appliances": "appliances",
            "appliance": "appliances",
            "refrigerator": "appliances",
            "fridge": "appliances",
            "oven": "appliances",
            "stove": "appliances",
            "microwave": "appliances",
            "washing": "appliances",
            "dryer": "appliances",
            
            # Bags variations
            "bag": "bag",
            "bags": "bag",
            "handbag": "bag",
            "purse": "bag",
            "wallet": "bag",
            "backpack": "bag",
            
            # Watch variations
            "watch": "watch",
            "watches": "watch",
            "timepiece": "watch"
        }
        
        # Check special mappings FIRST (before other logic)
        for variant, standard in special_mappings.items():
            if variant == query or query == variant:
                return self.component_knowledge.get(standard, ["CPU", "RAM", "storage", "display", "battery"])
        
        # Direct match
        if query in self.component_knowledge:
            return self.component_knowledge[query]
        
        # Enhanced matching with multiple strategies
        for key, components in self.component_knowledge.items():
            # Strategy 1: Exact match
            if key == query:
                return components
            
            # Strategy 2: Key contains query or query contains key
            if key in query or query in key:
                return components
            
            # Strategy 3: Word-based matching
            query_words = set(query.split())
            key_words = set(key.split())
            
            # If query contains most of key words or vice versa
            if len(query_words & key_words) >= 1:
                # Check for significant overlap
                if len(query_words) > 1 and len(key_words) > 1:
                    overlap_ratio = len(query_words & key_words) / min(len(query_words), len(key_words))
                    if overlap_ratio >= 0.5:  # 50% overlap
                        return components
                else:
                    # Single word match - prioritize exact matches
                    if len(key_words) == 1 and len(query_words) == 1:
                        return components
                    elif len(key_words) == 1:
                        # If key is single word and query contains it
                        if list(key_words)[0] in query:
                            return components
        
        # Default components
        return ["CPU", "RAM", "storage", "display", "battery"]
    
    def extract_aspects_from_reviews(self, reviews: List[str]) -> List[str]:
        """
        Extract aspects from reviews ONLY.
        This is the second independent pipeline.
        
        Args:
            reviews: List of review texts
            
        Returns:
            List of aspect names
        """
        return self.aspect_analyzer.extract_aspects(reviews)
    
    def analyze_product(self, search_query: str, reviews: List[str]) -> Dict[str, Any]:
        """
        Analyze product using both independent pipelines.
        
        Args:
            search_query: Product search query
            reviews: List of review texts
            
        Returns:
            Dictionary with components and aspects
        """
        components = self.generate_components(search_query)
        aspects = self.extract_aspects_from_reviews(reviews)
        
        return {
            "query": search_query,
            "components": components,
            "aspects": aspects,
            "component_count": len(components),
            "aspect_count": len(aspects),
            "components_from_query": True,
            "aspects_from_reviews": True
        }
