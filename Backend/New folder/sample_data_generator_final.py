import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

class SampleDataGenerator:
    """Generate sample data in the correct format for the competitive intelligence pipeline."""
    
    def __init__(self):
        self.categories = ['Headphones', 'Smartphones', 'Laptops']
        
        self.products = {
            'Headphones': [
                {'name': 'Sony WH-1000XM4', 'brand': 'Sony', 'price': 349.99},
                {'name': 'Sony WH-1000XM3', 'brand': 'Sony', 'price': 299.99},
                {'name': 'Bose QuietComfort 45', 'brand': 'Bose', 'price': 329.99},
                {'name': 'Bose QuietComfort 35 II', 'brand': 'Bose', 'price': 279.99},
                {'name': 'Apple AirPods Pro', 'brand': 'Apple', 'price': 249.99},
                {'name': 'Apple AirPods Max', 'brand': 'Apple', 'price': 549.99}
            ],
            'Smartphones': [
                {'name': 'iPhone 14 Pro', 'brand': 'Apple', 'price': 999.99},
                {'name': 'iPhone 14', 'brand': 'Apple', 'price': 799.99},
                {'name': 'Samsung Galaxy S23 Ultra', 'brand': 'Samsung', 'price': 1199.99},
                {'name': 'Samsung Galaxy S23', 'brand': 'Samsung', 'price': 899.99},
                {'name': 'Google Pixel 7 Pro', 'brand': 'Google', 'price': 899.99},
                {'name': 'Google Pixel 7', 'brand': 'Google', 'price': 599.99}
            ],
            'Laptops': [
                {'name': 'Dell XPS 15', 'brand': 'Dell', 'price': 1499.99},
                {'name': 'Dell Inspiron 14', 'brand': 'Dell', 'price': 799.99},
                {'name': 'HP Spectre x360', 'brand': 'HP', 'price': 1299.99},
                {'name': 'HP Envy 13', 'brand': 'HP', 'price': 999.99},
                {'name': 'Apple MacBook Pro 16', 'brand': 'Apple', 'price': 2499.99},
                {'name': 'Apple MacBook Air M2', 'brand': 'Apple', 'price': 1199.99}
            ]
        }
        
        self.components = ['battery', 'sound', 'camera', 'display', 'performance', 'build_quality', 'comfort', 'connectivity', 'software', 'price']
        
        self.review_templates = {
            'battery': [
                "The battery life is amazing, lasts all day",
                "Battery drains too quickly, needs improvement",
                "Decent battery performance, could be better",
                "Excellent battery capacity, no issues",
                "Battery life is shorter than expected"
            ],
            'sound': [
                "Sound quality is crystal clear and immersive",
                "Audio is disappointing, lacks bass",
                "Good sound for the price point",
                "Outstanding audio performance",
                "Sound could be more balanced"
            ],
            'camera': [
                "Camera takes stunning photos in all conditions",
                "Camera quality is below expectations",
                "Decent camera for daily use",
                "Photography capabilities are impressive",
                "Camera struggles in low light"
            ],
            'display': [
                "Display is bright and vibrant",
                "Screen quality could be improved",
                "Good display for the price",
                "Excellent visual experience",
                "Display colors are accurate"
            ],
            'performance': [
                "Performance is lightning fast",
                "System is slow and laggy",
                "Decent performance for everyday tasks",
                "Outstanding speed and responsiveness",
                "Performance meets expectations"
            ],
            'build_quality': [
                "Build quality feels premium and durable",
                "Construction feels cheap and flimsy",
                "Good build quality for the price",
                "Solid construction, very well made",
                "Build quality is acceptable"
            ],
            'comfort': [
                "Very comfortable to use for extended periods",
                "Uncomfortable after short use",
                "Decent comfort level",
                "Extremely comfortable design",
                "Comfort could be improved"
            ],
            'connectivity': [
                "Connectivity options are excellent",
                "Connection issues are frustrating",
                "Good connectivity features",
                "Reliable connection performance",
                "Connectivity is average"
            ],
            'software': [
                "Software is intuitive and user-friendly",
                "Software is buggy and unstable",
                "Decent software experience",
                "Outstanding software optimization",
                "Software needs updates"
            ],
            'price': [
                "Great value for the money",
                "Too expensive for what you get",
                "Reasonably priced",
                "Excellent value proposition",
                "Price is competitive"
            ]
        }
    
    def generate_sample_reviews(self, num_reviews_per_product: int = 30) -> Dict[str, Any]:
        """Generate sample product reviews in the correct format."""
        reviews = {}
        
        for category in self.categories:
            reviews[category] = {}
            
            for product_info in self.products[category]:
                product_name = product_info['name']
                brand = product_info['brand']
                price = product_info['price']
                
                product_reviews = []
                
                for _ in range(num_reviews_per_product):
                    # Generate random review
                    component = random.choice(self.components)
                    review_text = random.choice(self.review_templates[component])
                    
                    # Generate random date within last 6 months
                    days_ago = random.randint(0, 180)
                    review_date = (datetime.now() - timedelta(days=days_ago)).isoformat()
                    
                    # Generate random rating (1-5 stars)
                    rating = random.randint(1, 5)
                    
                    # Generate random reviewer name
                    reviewer = f"User_{random.randint(1000, 9999)}"
                    
                    # Create review object
                    review = {
                        'review_text': review_text,
                        'rating': rating,
                        'date': review_date,
                        'reviewer': reviewer,
                        'verified_purchase': random.choice([True, False])
                    }
                    
                    product_reviews.append(review)
                
                # Create product info in the expected format
                reviews[category][product_name] = {
                    'brand': brand,
                    'price': price,
                    'category': category,
                    'reviews': product_reviews
                }
        
        return reviews
    
    def save_sample_data(self):
        """Save all sample data files."""
        print("[*] Generating sample data for pipeline testing...")
        
        # Generate and save sample reviews
        print("[*] Generating sample reviews...")
        sample_reviews = self.generate_sample_reviews(30)
        
        with open('processed_product_reviews.json', 'w', encoding='utf-8') as f:
            json.dump(sample_reviews, f, indent=2, ensure_ascii=False)
        
        print("[+] Sample reviews saved to processed_product_reviews.json")
        
        # Generate and save component reviews
        print("[*] Processing component extraction...")
        component_reviews = {}
        
        for category, products in sample_reviews.items():
            component_reviews[category] = {}
            
            for product_name, product_info in products.items():
                component_reviews[category][product_name] = {}
                
                for component in self.components:
                    # Find reviews that mention this component
                    component_review_list = []
                    
                    for review in product_info['reviews']:
                        if component.lower() in review['review_text'].lower():
                            component_review_list.append(review)
                    
                    if component_review_list:
                        component_reviews[category][product_name][component] = component_review_list
        
        with open('component_reviews.json', 'w', encoding='utf-8') as f:
            json.dump(component_reviews, f, indent=2, ensure_ascii=False)
        
        print("[+] Component reviews saved to component_reviews.json")
        
        # Generate and save sentiment scores
        print("[*] Calculating sentiment scores...")
        sentiment_scores = {}
        
        for category, products in component_reviews.items():
            sentiment_scores[category] = {}
            
            for product_name, components in products.items():
                sentiment_scores[category][product_name] = {}
                
                for component, reviews in components.items():
                    if reviews:
                        # Calculate average sentiment from ratings
                        ratings = [r.get('rating', 3) for r in reviews if 'rating' in r]
                        if ratings:
                            avg_rating = sum(ratings) / len(ratings)
                            # Convert rating (1-5) to sentiment (-1 to 1)
                            avg_sentiment = (avg_rating - 3) / 2
                            
                            sentiment_scores[category][product_name][component] = {
                                'average_sentiment': avg_sentiment,
                                'review_count': len(reviews),
                                'sentiment_scores': [(r - 3) / 2 for r in ratings]
                            }
        
        with open('component_sentiment_scores.json', 'w', encoding='utf-8') as f:
            json.dump(sentiment_scores, f, indent=2, ensure_ascii=False)
        
        print("[+] Sentiment scores saved to component_sentiment_scores.json")
        
        print("[+] Sample data generation completed!")
        print("[*] You can now run: python main_pipeline_simple.py")

if __name__ == "__main__":
    generator = SampleDataGenerator()
    generator.save_sample_data()
