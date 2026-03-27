import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

class SampleDataGenerator:
    """Generate sample data for testing the competitive intelligence pipeline."""
    
    def __init__(self):
        self.categories = ['Headphones', 'Smartphones', 'Laptops']
        
        self.brands = {
            'Headphones': ['Sony', 'Bose', 'Apple'],
            'Smartphones': ['Apple', 'Samsung', 'Google'],
            'Laptops': ['Dell', 'HP', 'Apple']
        }
        
        self.products = {
            'Headphones': {
                'Sony': ['WH-1000XM4', 'WH-1000XM3'],
                'Bose': ['QuietComfort 45', 'QuietComfort 35 II'],
                'Apple': ['AirPods Pro', 'AirPods Max']
            },
            'Smartphones': {
                'Apple': ['iPhone 14 Pro', 'iPhone 14'],
                'Samsung': ['Galaxy S23 Ultra', 'Galaxy S23'],
                'Google': ['Pixel 7 Pro', 'Pixel 7']
            },
            'Laptops': {
                'Dell': ['XPS 15', 'Inspiron 14'],
                'HP': ['Spectre x360', 'Envy 13'],
                'Apple': ['MacBook Pro 16', 'MacBook Air M2']
            }
        }
        
        self.components = ['battery', 'sound', 'camera', 'display', 'performance', 'build_quality', 'comfort', 'connectivity', 'software', 'price']
        
        self.review_templates = {
            'battery': [
                "The battery life is amazing, lasts all day",
                "Battery drains too quickly, needs improvement",
                "Decent battery performance, could be better",
                "Excellent battery capacity, no issues"
            ],
            'sound': [
                "Sound quality is crystal clear and immersive",
                "Audio is disappointing, lacks bass",
                "Good sound for the price point",
                "Outstanding audio performance"
            ],
            'camera': [
                "Camera takes stunning photos in all conditions",
                "Camera quality is below expectations",
                "Decent camera for daily use",
                "Photography capabilities are impressive"
            ],
            'display': [
                "Display is bright and vibrant",
                "Screen quality could be improved",
                "Good display for the price",
                "Excellent visual experience"
            ],
            'performance': [
                "Performance is lightning fast",
                "System is slow and laggy",
                "Decent performance for everyday tasks",
                "Outstanding speed and responsiveness"
            ],
            'build_quality': [
                "Build quality feels premium and durable",
                "Construction feels cheap and flimsy",
                "Good build quality for the price",
                "Solid construction, very well made"
            ],
            'comfort': [
                "Very comfortable to use for extended periods",
                "Uncomfortable after short use",
                "Decent comfort level",
                "Extremely comfortable design"
            ],
            'connectivity': [
                "Connectivity options are excellent",
                "Connection issues are frustrating",
                "Good connectivity features",
                "Reliable connection performance"
            ],
            'software': [
                "Software is intuitive and user-friendly",
                "Software is buggy and unstable",
                "Decent software experience",
                "Outstanding software optimization"
            ],
            'price': [
                "Great value for the money",
                "Too expensive for what you get",
                "Reasonably priced",
                "Excellent value proposition"
            ]
        }
    
    def generate_sample_reviews(self, num_reviews_per_product: int = 50) -> Dict[str, Any]:
        """Generate sample product reviews in the correct format."""
        reviews = {}
        
        for category in self.categories:
            reviews[category] = {}
            
            brands = self.brands[category]
            
            for brand in brands:
                products = self.products[category][brand]
                
                for product in products:
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
                    
                    reviews[category][f"{brand} {product}"] = product_reviews
        
        return reviews
    
    def save_sample_data(self):
        """Save all sample data files."""
        print("[*] Generating sample data for pipeline testing...")
        
        # Generate and save sample reviews
        print("[*] Generating sample reviews...")
        sample_reviews = self.generate_sample_reviews(50)
        
        with open('processed_product_reviews.json', 'w', encoding='utf-8') as f:
            json.dump(sample_reviews, f, indent=2, ensure_ascii=False)
        
        print("[+] Sample reviews saved to processed_product_reviews.json")
        
        # Generate and save component reviews
        print("[*] Processing component extraction...")
        component_reviews = {}
        
        for category, products in sample_reviews.items():
            component_reviews[category] = {}
            
            for product, reviews in products.items():
                component_reviews[category][product] = {}
                
                for component in self.components:
                    # Find reviews that mention this component
                    component_review_list = []
                    
                    for review in reviews:
                        if component.lower() in review['review_text'].lower():
                            component_review_list.append(review)
                    
                    if component_review_list:
                        component_reviews[category][product][component] = component_review_list
        
        with open('component_reviews.json', 'w', encoding='utf-8') as f:
            json.dump(component_reviews, f, indent=2, ensure_ascii=False)
        
        print("[+] Component reviews saved to component_reviews.json")
        
        # Generate and save sentiment scores
        print("[*] Calculating sentiment scores...")
        sentiment_scores = {}
        
        for category, products in component_reviews.items():
            sentiment_scores[category] = {}
            
            for product, components in products.items():
                sentiment_scores[category][product] = {}
                
                for component, reviews in components.items():
                    if reviews:
                        # Calculate average sentiment from ratings
                        ratings = [r.get('rating', 3) for r in reviews if 'rating' in r]
                        if ratings:
                            avg_rating = sum(ratings) / len(ratings)
                            # Convert rating (1-5) to sentiment (-1 to 1)
                            avg_sentiment = (avg_rating - 3) / 2
                            
                            sentiment_scores[category][product][component] = {
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
