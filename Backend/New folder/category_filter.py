import json
import logging
from typing import Dict, List, Any, Set
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CategoryFilter:
    """
    Filter electronics products into key categories for competitive intelligence analysis.
    """
    
    def __init__(self):
        self.target_categories = {
            'Headphones', 'Smartphones', 'Laptops', 'Smartwatches', 'Speakers'
        }
        self.processed_data = {}
        self.filtered_data = {}
        
        # Category-specific keywords for enhanced filtering
        self.category_keywords = {
            'Headphones': [
                'headphone', 'earphone', 'earbud', 'in-ear', 'over-ear', 'on-ear',
                'noise cancelling', 'wireless earbud', 'bluetooth earphone', 'audio'
            ],
            'Smartphones': [
                'phone', 'smartphone', 'mobile', 'cell phone', 'iphone', 'android',
                'galaxy', 'pixel', 'oneplus', 'xiaomi'
            ],
            'Laptops': [
                'laptop', 'notebook', 'computer', 'pc', 'macbook', 'ultrabook',
                'thinkpad', 'dell xps', 'hp pavilion', 'lenovo'
            ],
            'Smartwatches': [
                'watch', 'smartwatch', 'fitness tracker', 'wearable', 'apple watch',
                'galaxy watch', 'fitbit', 'garmin', 'fossil'
            ],
            'Speakers': [
                'speaker', 'bluetooth speaker', 'sound system', 'audio speaker',
                'portable speaker', 'home speaker', 'soundbar', 'echo', 'google home'
            ]
        }
    
    def load_processed_data(self, input_file: str = 'processed_product_reviews.json') -> None:
        """
        Read processed_product_reviews.json file.
        
        Args:
            input_file: Path to the processed JSON file
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                self.processed_data = json.load(f)
            logger.info(f"Successfully loaded processed data from {input_file}")
            
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
            logger.error(f"Error loading processed data: {e}")
            raise
    
    def identify_target_categories(self) -> Dict[str, Dict[str, Any]]:
        """
        Identify products belonging to the 5 target categories.
        
        Returns:
            Dictionary containing only target categories with their products
        """
        target_data = {}
        
        # First, get exact matches from existing categories
        for category in self.target_categories:
            if category in self.processed_data:
                target_data[category] = self.processed_data[category]
                logger.info(f"Found {category}: {len(target_data[category])} products")
        
        # Check if we need to extract from 'Other' category or mixed categories
        if 'Other' in self.processed_data:
            other_products = self.processed_data['Other']
            extracted_products = self._extract_from_other_category(other_products)
            
            for category, products in extracted_products.items():
                if category in self.target_categories:
                    if category not in target_data:
                        target_data[category] = {}
                    target_data[category].update(products)
                    logger.info(f"Extracted {len(products)} products for {category} from 'Other' category")
        
        # Also check for products that might be in different category names
        for existing_category, products in self.processed_data.items():
            if existing_category not in self.target_categories and existing_category != 'Other':
                reclassified = self._reclassify_products(products, existing_category)
                for target_category, reclassified_products in reclassified.items():
                    if target_category in self.target_categories:
                        if target_category not in target_data:
                            target_data[target_category] = {}
                        target_data[target_category].update(reclassified_products)
                        if reclassified_products:
                            logger.info(f"Reclassified {len(reclassified_products)} products from '{existing_category}' to '{target_category}'")
        
        logger.info(f"Identified products for {len(target_data)} target categories")
        return target_data
    
    def _extract_from_other_category(self, other_products: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Extract products from 'Other' category based on product names.
        
        Args:
            other_products: Products in the 'Other' category
            
        Returns:
            Dictionary of reclassified products by target category
        """
        reclassified = defaultdict(dict)
        
        for product_name, product_info in other_products.items():
            product_name_lower = product_name.lower()
            
            # Check against category keywords
            for category, keywords in self.category_keywords.items():
                if category in self.target_categories:
                    for keyword in keywords:
                        if keyword in product_name_lower:
                            reclassified[category][product_name] = product_info
                            break
                    else:
                        continue
                    break
        
        return dict(reclassified)
    
    def _reclassify_products(self, products: Dict[str, Any], original_category: str) -> Dict[str, Dict[str, Any]]:
        """
        Reclassify products from non-target categories based on product names.
        
        Args:
            products: Products to reclassify
            original_category: Original category name
            
        Returns:
            Dictionary of reclassified products by target category
        """
        reclassified = defaultdict(dict)
        
        for product_name, product_info in products.items():
            product_name_lower = product_name.lower()
            
            # Check against category keywords
            for category, keywords in self.category_keywords.items():
                if category in self.target_categories:
                    for keyword in keywords:
                        if keyword in product_name_lower:
                            reclassified[category][product_name] = product_info
                            break
                    else:
                        continue
                    break
        
        return dict(reclassified)
    
    def filter_brands_per_category(self, category_data: Dict[str, Dict[str, Any]], 
                                  min_brands: int = 2, max_brands: int = 5) -> Dict[str, Dict[str, Any]]:
        """
        Filter products to keep at least the specified number of brands per category.
        Selects top brands based on number of reviews and average ratings.
        
        Args:
            category_data: Dictionary of products by category
            min_brands: Minimum number of brands to keep per category
            max_brands: Maximum number of brands to keep per category
            
        Returns:
            Filtered data with brand diversity
        """
        filtered_data = {}
        
        for category, products in category_data.items():
            if category not in self.target_categories:
                continue
            
            logger.info(f"Filtering brands for {category}...")
            
            # Analyze brands in this category
            brand_analysis = self._analyze_brands(products)
            
            # Sort brands by score (combination of review count and average rating)
            sorted_brands = sorted(brand_analysis.items(), 
                                 key=lambda x: (x[1]['review_count'], x[1]['avg_rating']), 
                                 reverse=True)
            
            # Select top brands
            selected_brands = sorted_brands[:max(min_brands, len(sorted_brands))]
            if len(selected_brands) < min_brands and len(sorted_brands) >= min_brands:
                selected_brands = sorted_brands[:min_brands]
            
            # Filter products by selected brands
            filtered_products = {}
            for product_name, product_info in products.items():
                brand = product_info.get('brand', 'Unknown')
                if brand in [brand_info[0] for brand_info in selected_brands]:
                    filtered_products[product_name] = product_info
            
            filtered_data[category] = filtered_products
            
            # Log brand selection
            selected_brand_names = [brand_info[0] for brand_info in selected_brands]
            logger.info(f"Selected {len(selected_brands)} brands for {category}: {', '.join(selected_brand_names)}")
            logger.info(f"Kept {len(filtered_products)} products for {category}")
        
        return filtered_data
    
    def _analyze_brands(self, products: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze brands in a category to determine which ones to keep.
        
        Args:
            products: Products in the category
            
        Returns:
            Dictionary with brand analysis data
        """
        brand_analysis = {}
        
        for product_name, product_info in products.items():
            brand = product_info.get('brand', 'Unknown')
            reviews = product_info.get('reviews', [])
            
            if brand not in brand_analysis:
                brand_analysis[brand] = {
                    'product_count': 0,
                    'review_count': 0,
                    'total_rating': 0,
                    'avg_rating': 0
                }
            
            brand_analysis[brand]['product_count'] += 1
            brand_analysis[brand]['review_count'] += len(reviews)
            
            # Calculate ratings
            if reviews:
                ratings = [review.get('rating', 0) for review in reviews if review.get('rating')]
                if ratings:
                    brand_analysis[brand]['total_rating'] += sum(ratings)
                    brand_analysis[brand]['avg_rating'] = brand_analysis[brand]['total_rating'] / len(ratings)
        
        return brand_analysis
    
    def select_top_products_per_brand(self, category_data: Dict[str, Dict[str, Any]], 
                                    max_products_per_brand: int = 3) -> Dict[str, Dict[str, Any]]:
        """
        Select top products per brand based on review count and ratings.
        
        Args:
            category_data: Filtered category data
            max_products_per_brand: Maximum products to keep per brand
            
        Returns:
            Data with top products selected per brand
        """
        final_data = {}
        
        for category, products in category_data.items():
            logger.info(f"Selecting top products per brand for {category}...")
            
            # Group products by brand
            brand_products = defaultdict(list)
            for product_name, product_info in products.items():
                brand = product_info.get('brand', 'Unknown')
                reviews = product_info.get('reviews', [])
                
                # Calculate product score
                review_count = len(reviews)
                avg_rating = 0
                if reviews:
                    ratings = [review.get('rating', 0) for review in reviews if review.get('rating')]
                    if ratings:
                        avg_rating = sum(ratings) / len(ratings)
                
                product_score = review_count * avg_rating  # Weight by both factors
                
                brand_products[brand].append({
                    'name': product_name,
                    'info': product_info,
                    'score': product_score,
                    'review_count': review_count,
                    'avg_rating': avg_rating
                })
            
            # Select top products per brand
            selected_products = {}
            for brand, brand_prod_list in brand_products.items():
                # Sort by score
                sorted_products = sorted(brand_prod_list, key=lambda x: x['score'], reverse=True)
                top_products = sorted_products[:max_products_per_brand]
                
                for product in top_products:
                    selected_products[product['name']] = product['info']
                
                logger.info(f"  {brand}: Selected {len(top_products)} products")
            
            final_data[category] = selected_products
        
        return final_data
    
    def save_filtered_data(self, output_file: str = 'category_products.json') -> None:
        """
        Save filtered category data as JSON file.
        
        Args:
            output_file: Output file name
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.filtered_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved filtered data to {output_file}")
        except Exception as e:
            logger.error(f"Error saving filtered data: {e}")
            raise
    
    def process_categories(self, input_file: str = 'processed_product_reviews.json', 
                          output_file: str = 'category_products.json',
                          min_brands: int = 2, max_brands: int = 5,
                          max_products_per_brand: int = 3) -> Dict[str, Dict[str, Any]]:
        """
        Complete pipeline to filter and process categories.
        
        Args:
            input_file: Input processed JSON file
            output_file: Output filtered JSON file
            min_brands: Minimum brands per category
            max_brands: Maximum brands per category
            max_products_per_brand: Maximum products per brand
            
        Returns:
            Filtered category data
        """
        try:
            # Load processed data
            self.load_processed_data(input_file)
            
            # Identify target categories
            target_data = self.identify_target_categories()
            
            # Filter brands per category
            brand_filtered = self.filter_brands_per_category(target_data, min_brands, max_brands)
            
            # Select top products per brand
            self.filtered_data = self.select_top_products_per_brand(brand_filtered, max_products_per_brand)
            
            # Save filtered data
            self.save_filtered_data(output_file)
            
            # Print summary
            self._print_summary()
            
            logger.info("Category filtering completed successfully!")
            return self.filtered_data
            
        except Exception as e:
            logger.error(f"Error in category filtering pipeline: {e}")
            raise
    
    def _print_summary(self) -> None:
        """Print summary of filtered data."""
        print("\n" + "="*60)
        print("📊 CATEGORY FILTERING SUMMARY")
        print("="*60)
        
        total_products = 0
        total_brands = set()
        
        for category, products in self.filtered_data.items():
            brands = set(product['brand'] for product in products.values())
            total_products += len(products)
            total_brands.update(brands)
            
            print(f"\n📁 {category}:")
            print(f"   Products: {len(products)}")
            print(f"   Brands: {len(brands)} ({', '.join(sorted(brands))})")
            
            # Show top products
            sorted_products = sorted(products.items(), 
                                   key=lambda x: len(x[1].get('reviews', [])), 
                                   reverse=True)
            
            for i, (product_name, product_info) in enumerate(sorted_products[:3], 1):
                brand = product_info.get('brand', 'Unknown')
                review_count = len(product_info.get('reviews', []))
                print(f"   {i}. {brand} {product_name} ({review_count} reviews)")
        
        print(f"\n📈 Overall Statistics:")
        print(f"   Total Categories: {len(self.filtered_data)}")
        print(f"   Total Products: {total_products}")
        print(f"   Total Brands: {len(total_brands)}")
        print("="*60)

# Example usage
if __name__ == "__main__":
    # Initialize and process
    filter = CategoryFilter()
    filtered_data = filter.process_categories(
        input_file='processed_product_reviews.json',
        output_file='category_products.json',
        min_brands=2,
        max_brands=5,
        max_products_per_brand=3
    )
    
    print(f"\n✅ Filtering complete! Results saved to category_products.json")
    print(f"📊 Processed {len(filtered_data)} categories")
