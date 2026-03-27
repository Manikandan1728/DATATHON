import json
import re
import logging
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComponentExtractor:
    """
    Extract product components mentioned in reviews for competitive intelligence analysis.
    """
    
    def __init__(self):
        self.category_components = {
            'Headphones': {
                'sound': [
                    'sound', 'audio', 'bass', 'treble', 'sound quality', 'audio quality',
                    'music', 'soundstage', 'clarity', 'volume', 'loudness', 'acoustics',
                    'frequency', 'highs', 'lows', 'mids', 'stereo', 'mono', 'noise'
                ],
                'battery': [
                    'battery', 'battery life', 'charge', 'charging', 'battery duration',
                    'power', 'battery backup', 'battery performance', 'hours', 'lasts',
                    'battery time', 'quick charge', 'fast charging', 'wireless charging'
                ],
                'comfort': [
                    'comfort', 'comfortable', 'fit', 'ear pads', 'cushions', 'lightweight',
                    'weight', 'ear pressure', 'headband', 'adjustable', 'size', 'wear',
                    'long hours', 'all day', 'ear fit', 'over ear', 'on ear'
                ],
                'noise_cancellation': [
                    'noise cancellation', 'noise canceling', 'anc', 'active noise',
                    'noise reduction', 'quiet', 'silence', 'background noise', 'isolation',
                    'noise blocking', 'ambient noise', 'noise suppression'
                ],
                'design': [
                    'design', 'look', 'appearance', 'style', 'aesthetics', 'color',
                    'materials', 'build', 'construction', 'finish', 'portable', 'foldable',
                    'case', 'cable', 'wireless', 'bluetooth', 'connection'
                ],
                'price': [
                    'price', 'cost', 'expensive', 'cheap', 'affordable', 'value',
                    'money', 'worth', 'budget', 'investment', 'deal', 'discount',
                    'overpriced', 'reasonable', 'cost effective'
                ]
            },
            'Smartphones': {
                'camera': [
                    'camera', 'photo', 'picture', 'video', 'photos', 'pictures',
                    'selfie', 'rear camera', 'front camera', 'lens', 'megapixel',
                    'zoom', 'flash', 'night mode', 'portrait', 'image quality',
                    'photography', 'shutter', 'focus', 'aperture'
                ],
                'battery': [
                    'battery', 'battery life', 'charge', 'charging', 'battery duration',
                    'power', 'battery backup', 'battery performance', 'hours', 'lasts',
                    'battery time', 'quick charge', 'fast charging', 'wireless charging',
                    'battery percentage', 'power bank', 'battery drain'
                ],
                'display': [
                    'display', 'screen', 'lcd', 'oled', 'amoled', 'resolution',
                    'brightness', 'color', 'touch', 'touchscreen', 'size', 'pixel',
                    'refresh rate', 'hd', 'full hd', '4k', 'screen quality', 'vibrant'
                ],
                'processor': [
                    'processor', 'cpu', 'chip', 'chipset', 'performance', 'speed',
                    'fast', 'slow', 'lag', 'processing', 'computing', 'snapdragon',
                    'apple silicon', 'mediatek', 'qualcomm', 'octa core', 'quad core'
                ],
                'software': [
                    'software', 'os', 'operating system', 'android', 'ios', 'updates',
                    'apps', 'applications', 'user interface', 'ui', 'features',
                    'bloatware', 'system', 'firmware', 'bugs', 'crashes'
                ],
                'build_quality': [
                    'build', 'quality', 'durability', 'sturdy', 'robust', 'materials',
                    'glass', 'metal', 'plastic', 'waterproof', 'water resistant',
                    'scratch', 'drop', 'damage', 'construction', 'premium feel'
                ]
            },
            'Laptops': {
                'processor': [
                    'processor', 'cpu', 'chip', 'chipset', 'performance', 'speed',
                    'fast', 'slow', 'lag', 'processing', 'computing', 'intel',
                    'amd', 'core i3', 'core i5', 'core i7', 'core i9', 'ryzen'
                ],
                'battery': [
                    'battery', 'battery life', 'charge', 'charging', 'battery duration',
                    'power', 'battery backup', 'battery performance', 'hours', 'lasts',
                    'battery time', 'quick charge', 'fast charging', 'portable'
                ],
                'display': [
                    'display', 'screen', 'lcd', 'led', 'oled', 'resolution',
                    'brightness', 'color', 'touch', 'touchscreen', 'size', 'pixel',
                    'refresh rate', 'hd', 'full hd', '4k', 'screen quality', 'matte',
                    'glossy', 'monitor', 'panel'
                ],
                'keyboard': [
                    'keyboard', 'keys', 'typing', 'keypad', 'backlit', 'touchpad',
                    'trackpad', 'mouse', 'click', 'key travel', 'layout', 'ergonomic',
                    'mechanical', 'membrane', 'key response', 'typing experience'
                ],
                'performance': [
                    'performance', 'speed', 'fast', 'slow', 'lag', 'multitasking',
                    'gaming', 'graphics', 'gpu', 'video', 'rendering', 'productivity',
                    'smooth', 'responsive', 'powerful', 'efficient', 'memory', 'ram'
                ],
                'build_quality': [
                    'build', 'quality', 'durability', 'sturdy', 'robust', 'materials',
                    'metal', 'plastic', 'carbon fiber', 'aluminum', 'chassis',
                    'hinge', 'portable', 'weight', 'thin', 'lightweight', 'premium'
                ]
            },
            'Smartwatches': {
                'battery': [
                    'battery', 'battery life', 'charge', 'charging', 'battery duration',
                    'power', 'battery backup', 'battery performance', 'hours', 'lasts',
                    'battery time', 'quick charge', 'fast charging', 'all day'
                ],
                'display': [
                    'display', 'screen', 'lcd', 'oled', 'amoled', 'resolution',
                    'brightness', 'color', 'touch', 'touchscreen', 'size', 'pixel',
                    'always on', 'face', 'watch face', 'screen quality', 'visible'
                ],
                'health_features': [
                    'health', 'fitness', 'heart rate', 'steps', 'exercise', 'workout',
                    'tracking', 'activity', 'calories', 'sleep', 'spo2', 'ecg',
                    'blood pressure', 'health monitoring', 'fitness tracking'
                ],
                'smart_features': [
                    'smart', 'notifications', 'calls', 'messages', 'apps', 'connectivity',
                    'bluetooth', 'wifi', 'cellular', 'gps', 'music', 'payments',
                    'voice assistant', 'siri', 'google assistant', 'smart features'
                ],
                'design': [
                    'design', 'look', 'appearance', 'style', 'aesthetics', 'color',
                    'materials', 'build', 'construction', 'finish', 'band', 'strap',
                    'case', 'size', 'weight', 'comfortable', 'premium'
                ],
                'compatibility': [
                    'compatibility', 'iphone', 'android', 'ios', 'phone', 'sync',
                    'integration', 'connection', 'pairing', 'app', 'software',
                    'ecosystem', 'works with', 'compatible with'
                ]
            },
            'Speakers': {
                'sound': [
                    'sound', 'audio', 'bass', 'treble', 'sound quality', 'audio quality',
                    'music', 'soundstage', 'clarity', 'volume', 'loudness', 'acoustics',
                    'frequency', 'highs', 'lows', 'mids', 'stereo', 'mono', 'noise',
                    'distortion', 'crisp', 'clear', 'rich', 'deep bass'
                ],
                'battery': [
                    'battery', 'battery life', 'charge', 'charging', 'battery duration',
                    'power', 'battery backup', 'battery performance', 'hours', 'lasts',
                    'battery time', 'quick charge', 'fast charging', 'wireless charging',
                    'portable'
                ],
                'connectivity': [
                    'bluetooth', 'wifi', 'wireless', 'connection', 'pairing', 'range',
                    'stable', 'connectivity', 'wireless connection', 'signal',
                    'drop', 'disconnect', 'reconnect', 'compatibility'
                ],
                'design': [
                    'design', 'look', 'appearance', 'style', 'aesthetics', 'color',
                    'materials', 'build', 'construction', 'finish', 'portable', 'size',
                    'weight', 'compact', 'waterproof', 'water resistant'
                ],
                'features': [
                    'features', 'voice assistant', 'siri', 'google assistant', 'alexa',
                    'microphone', 'hands free', 'calls', 'speakerphone', 'multiroom',
                    'stereo pairing', 'app', 'controls', 'buttons', 'touch controls'
                ],
                'price': [
                    'price', 'cost', 'expensive', 'cheap', 'affordable', 'value',
                    'money', 'worth', 'budget', 'investment', 'deal', 'discount',
                    'overpriced', 'reasonable', 'cost effective'
                ]
            }
        }
        
        self.processed_data = {}
        self.component_data = {}
    
    def load_category_data(self, input_file: str = 'category_products.json') -> None:
        """
        Load filtered category products data.
        
        Args:
            input_file: Path to the category products JSON file
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                self.processed_data = json.load(f)
            logger.info(f"Successfully loaded category data from {input_file}")
            
            total_categories = len(self.processed_data)
            total_products = sum(len(products) for products in self.processed_data.values())
            logger.info(f"Loaded {total_categories} categories with {total_products} total products")
            
        except FileNotFoundError:
            logger.error(f"File not found: {input_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading category data: {e}")
            raise
    
    def extract_components_from_review(self, review_text: str, category: str) -> Set[str]:
        """
        Extract components mentioned in a review text.
        
        Args:
            review_text: The review text to analyze
            category: Product category (Headphones, Smartphones, etc.)
            
        Returns:
            Set of components found in the review
        """
        if category not in self.category_components:
            return set()
        
        found_components = set()
        review_lower = review_text.lower()
        
        # Check each component and its keywords
        for component, keywords in self.category_components[category].items():
            for keyword in keywords:
                if keyword in review_lower:
                    found_components.add(component)
                    break  # Found this component, move to next one
        
        return found_components
    
    def scan_reviews_for_components(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Scan all reviews and assign them to components.
        
        Returns:
            Dictionary structure: {product: {component: [review_text]}}
        """
        component_data = defaultdict(lambda: defaultdict(list))
        total_reviews = 0
        processed_reviews = 0
        
        for category, products in self.processed_data.items():
            logger.info(f"Scanning reviews for {category}...")
            
            for product_name, product_info in products.items():
                reviews = product_info.get('reviews', [])
                total_reviews += len(reviews)
                
                for review in reviews:
                    review_text = review.get('review_text', '')
                    if not review_text or not review_text.strip():
                        continue
                    
                    # Extract components from this review
                    found_components = self.extract_components_from_review(review_text, category)
                    
                    if found_components:
                        # Assign review to each found component
                        for component in found_components:
                            component_data[product_name][component].append(review_text.strip())
                        processed_reviews += 1
        
        self.component_data = dict(component_data)
        
        logger.info(f"Processed {processed_reviews} out of {total_reviews} total reviews")
        logger.info(f"Found component mentions in {len(self.component_data)} products")
        
        return self.component_data
    
    def enhance_keyword_detection(self) -> None:
        """
        Enhance keyword detection with more sophisticated patterns.
        """
        # Add common variations and patterns
        enhancements = {
            'sound': [
                r'\bsound(s?)\b', r'\baudio(s?)\b', r'\bbass\b', r'\btreble\b',
                r'\bvolume\b', r'\bloudness\b', r'\bclear\b.*\sound', r'\bcrisp\b.*\audio'
            ],
            'battery': [
                r'\bbattery\b.*\blife\b', r'\bcharge(s?)\b', r'\bhours\b', r'\blast(s?)\b',
                r'\bpower\b', r'\bquick\b.*\charge', r'\bfast\b.*\charge'
            ],
            'camera': [
                r'\bcamera(s?)\b', r'\bphoto(s?)\b', r'\bpicture(s?)\b', r'\bvideo(s?)\b',
                r'\bselfie(s?)\b', r'\blens\b', r'\bmegapixel\b', r'\bzoom\b'
            ],
            'display': [
                r'\bscreen\b', r'\bdisplay\b', r'\blcd\b', r'\boled\b', r'\bamoled\b',
                r'\bbrightness\b', r'\bresolution\b', r'\brefresh rate\b', r'\bhd\b'
            ],
            'processor': [
                r'\bprocessor\b', r'\bcpu\b', r'\bchip(s?)\b', r'\bperformance\b',
                r'\bspeed\b', r'\blag\b', r'\bfast\b', r'\bslow\b'
            ],
            'design': [
                r'\bdesign\b', r'\blook(s?)\b', r'\bappearance\b', r'\bstyle\b',
                r'\bmaterials?\b', r'\bbuild\b', r'\bconstruction\b', r'\bfinish\b'
            ],
            'price': [
                r'\bprice\b', r'\bcost\b', r'\bexpensive\b', r'\bcheap\b',
                r'\baffordable\b', r'\bvalue\b', r'\bworth\b', r'\bbudget\b'
            ]
        }
        
        # Apply enhancements to all categories
        for category in self.category_components:
            for component, patterns in enhancements.items():
                if component in self.category_components[category]:
                    self.category_components[category][component].extend(patterns)
    
    def filter_component_reviews(self, min_reviews_per_component: int = 5) -> Dict[str, Dict[str, List[str]]]:
        """
        Filter components to keep only those with sufficient reviews.
        
        Args:
            min_reviews_per_component: Minimum number of reviews required per component
            
        Returns:
            Filtered component data
        """
        filtered_data = {}
        
        for product_name, components in self.component_data.items():
            filtered_components = {}
            
            for component, reviews in components.items():
                if len(reviews) >= min_reviews_per_component:
                    filtered_components[component] = reviews
            
            if filtered_components:
                filtered_data[product_name] = filtered_components
        
        logger.info(f"Filtered to {len(filtered_data)} products with sufficient component reviews")
        return filtered_data
    
    def save_component_data(self, output_file: str = 'component_reviews.json') -> None:
        """
        Save component data as JSON file.
        
        Args:
            output_file: Output file name
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.component_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved component data to {output_file}")
        except Exception as e:
            logger.error(f"Error saving component data: {e}")
            raise
    
    def process_components(self, input_file: str = 'category_products.json',
                          output_file: str = 'component_reviews.json',
                          min_reviews_per_component: int = 5,
                          enhance_detection: bool = True) -> Dict[str, Dict[str, List[str]]]:
        """
        Complete pipeline to extract components from reviews.
        
        Args:
            input_file: Input category products JSON file
            output_file: Output component reviews JSON file
            min_reviews_per_component: Minimum reviews required per component
            enhance_detection: Whether to use enhanced keyword detection
            
        Returns:
            Component data structure
        """
        try:
            # Load category data
            self.load_category_data(input_file)
            
            # Enhance keyword detection if requested
            if enhance_detection:
                self.enhance_keyword_detection()
                logger.info("Enhanced keyword detection enabled")
            
            # Scan reviews for components
            self.scan_reviews_for_components()
            
            # Filter components with sufficient reviews
            self.component_data = self.filter_component_reviews(min_reviews_per_component)
            
            # Save component data
            self.save_component_data(output_file)
            
            # Print summary
            self._print_summary()
            
            logger.info("Component extraction completed successfully!")
            return self.component_data
            
        except Exception as e:
            logger.error(f"Error in component extraction pipeline: {e}")
            raise
    
    def _print_summary(self) -> None:
        """Print summary of component extraction results."""
        print("\n" + "="*60)
        print("🔧 COMPONENT EXTRACTION SUMMARY")
        print("="*60)
        
        total_products = len(self.component_data)
        total_components = 0
        total_reviews = 0
        component_stats = defaultdict(int)
        
        for product_name, components in self.component_data.items():
            for component, reviews in components.items():
                total_components += 1
                total_reviews += len(reviews)
                component_stats[component] += len(reviews)
        
        print(f"\n📊 Overall Statistics:")
        print(f"   Products with component data: {total_products}")
        print(f"   Total component types found: {total_components}")
        print(f"   Total component reviews: {total_reviews}")
        
        print(f"\n🔧 Component Distribution:")
        for component, count in sorted(component_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"   {component}: {count} reviews")
        
        print(f"\n📁 Products by Category:")
        category_product_count = defaultdict(int)
        for product_name in self.component_data.keys():
            # Find which category this product belongs to
            for category, products in self.processed_data.items():
                if product_name in products:
                    category_product_count[category] += 1
                    break
        
        for category, count in category_product_count.items():
            print(f"   {category}: {count} products")
        
        print("="*60)

# Example usage
if __name__ == "__main__":
    # Initialize and process
    extractor = ComponentExtractor()
    component_data = extractor.process_components(
        input_file='category_products.json',
        output_file='component_reviews.json',
        min_reviews_per_component=5,
        enhance_detection=True
    )
    
    print(f"\n✅ Component extraction complete! Results saved to component_reviews.json")
    print(f"🔧 Processed components for {len(component_data)} products")
