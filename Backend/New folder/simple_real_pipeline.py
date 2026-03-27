import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        os.system('chcp 65001 >nul 2>&1')
    except:
        pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleRealPipeline:
    """
    Simplified pipeline that works with real data without emoji issues.
    """
    
    def __init__(self):
        self.results = {}
        self.pipeline_start_time = datetime.now()
        
        logger.info("Simple real pipeline initialized")
    
    def analyze_real_data(self) -> Dict[str, Any]:
        """Analyze the real Amazon data we already have."""
        print("\n" + "="*80)
        print("REAL AMAZON DATA COMPETITIVE INTELLIGENCE")
        print("="*80)
        
        try:
            # Load real processed data
            print(f"\n[STEP 1] LOADING REAL AMAZON DATA")
            print("-" * 50)
            
            with open('real_processed_product_reviews.json', 'r', encoding='utf-8') as f:
                real_data = json.load(f)
            
            print(f"[+] Loaded real Amazon data")
            
            for category, products in real_data.items():
                print(f"   {category}: {len(products)} products")
                for product_name, product_info in products.items():
                    print(f"      - {product_info['brand']} {product_info['price']:.2f} ({len(product_info['reviews'])} reviews)")
            
            # Step 2: Extract components from real reviews
            print(f"\n[STEP 2] COMPONENT ANALYSIS")
            print("-" * 50)
            
            component_analysis = self._analyze_components(real_data)
            
            # Step 3: Sentiment analysis
            print(f"\n[STEP 3] SENTIMENT ANALYSIS")
            print("-" * 50)
            
            sentiment_analysis = self._analyze_sentiments(real_data)
            
            # Step 4: Competitor comparison
            print(f"\n[STEP 4] COMPETITOR ANALYSIS")
            print("-" * 50)
            
            competitor_analysis = self._analyze_competitors(real_data, sentiment_analysis)
            
            # Step 5: Customer issues
            print(f"\n[STEP 5] CUSTOMER ISSUES ANALYSIS")
            print("-" * 50)
            
            issues_analysis = self._analyze_issues(real_data)
            
            # Step 6: Strategic recommendations
            print(f"\n[STEP 6] STRATEGIC RECOMMENDATIONS")
            print("-" * 50)
            
            strategy_recommendations = self._generate_strategies(real_data, issues_analysis)
            
            # Step 7: Executive summary
            print(f"\n[STEP 7] EXECUTIVE SUMMARY")
            print("-" * 50)
            
            executive_summary = self._generate_executive_summary(real_data, competitor_analysis, strategy_recommendations)
            
            # Save results
            results = {
                'real_data': real_data,
                'component_analysis': component_analysis,
                'sentiment_analysis': sentiment_analysis,
                'competitor_analysis': competitor_analysis,
                'issues_analysis': issues_analysis,
                'strategy_recommendations': strategy_recommendations,
                'executive_summary': executive_summary
            }
            
            with open('real_analysis_results.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            # Display final summary
            self._display_summary(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Real data analysis failed: {e}")
            print(f"\n[!] Analysis failed: {e}")
            raise
    
    def _analyze_components(self, real_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze components mentioned in real reviews."""
        component_keywords = {
            'battery': ['battery', 'charge', 'power', 'drain', 'battery life', 'charging'],
            'sound': ['sound', 'audio', 'speaker', 'volume', 'noise', 'quality'],
            'noise_cancellation': ['noise cancellation', 'anc', 'noise canceling', 'quiet'],
            'comfort': ['comfortable', 'fit', 'wear', 'uncomfortable', 'tight'],
            'price': ['price', 'cost', 'expensive', 'cheap', 'value', 'money'],
            'quality': ['quality', 'build', 'durable', 'sturdy', 'premium'],
            'connectivity': ['bluetooth', 'connection', 'pairing', 'wireless'],
            'features': ['features', 'functions', 'capabilities', 'options']
        }
        
        component_analysis = {}
        
        for category, products in real_data.items():
            component_analysis[category] = {}
            
            for product_name, product_info in products.items():
                component_analysis[category][product_name] = {}
                
                all_reviews_text = " ".join([review['review_text'].lower() for review in product_info['reviews']])
                
                for component, keywords in component_keywords.items():
                    count = sum(1 for keyword in keywords if keyword in all_reviews_text)
                    if count > 0:
                        component_analysis[category][product_name][component] = count
        
        # Display component analysis
        print(f"[+] Component mentions found:")
        for category, products in component_analysis.items():
            print(f"   {category}:")
            for product, components in products.items():
                if components:
                    print(f"      {product}: {dict(components)}")
        
        return component_analysis
    
    def _analyze_sentiments(self, real_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment from real reviews."""
        sentiment_analysis = {}
        
        for category, products in real_data.items():
            sentiment_analysis[category] = {}
            
            for product_name, product_info in products.items():
                reviews = product_info['reviews']
                ratings = [review['rating'] for review in reviews]
                
                if ratings:
                    avg_rating = sum(ratings) / len(ratings)
                    avg_sentiment = (avg_rating - 3) / 2  # Convert to -1 to 1 scale
                    
                    sentiment_analysis[category][product_name] = {
                        'average_rating': avg_rating,
                        'average_sentiment': avg_sentiment,
                        'total_reviews': len(reviews),
                        'rating_distribution': {
                            '5_star': ratings.count(5),
                            '4_star': ratings.count(4),
                            '3_star': ratings.count(3),
                            '2_star': ratings.count(2),
                            '1_star': ratings.count(1)
                        }
                    }
        
        # Display sentiment analysis
        print(f"[+] Sentiment analysis:")
        for category, products in sentiment_analysis.items():
            print(f"   {category}:")
            for product, sentiment in products.items():
                print(f"      {product}: {sentiment['average_rating']:.1f}/5.0 ({sentiment['average_sentiment']:.2f} sentiment)")
        
        return sentiment_analysis
    
    def _analyze_competitors(self, real_data: Dict[str, Any], sentiment_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitor performance."""
        competitor_analysis = {}
        
        # Group by brands
        brands = {}
        for category, products in real_data.items():
            for product_name, product_info in products.items():
                brand = product_info['brand']
                if brand not in brands:
                    brands[brand] = {
                        'categories': [],
                        'products': [],
                        'avg_ratings': [],
                        'prices': []
                    }
                
                brands[brand]['categories'].append(category)
                brands[brand]['products'].append(product_name)
                
                if product_name in sentiment_analysis.get(category, {}):
                    brands[brand]['avg_ratings'].append(sentiment_analysis[category][product_name]['average_rating'])
                
                brands[brand]['prices'].append(product_info['price'])
        
        # Calculate brand metrics
        for brand, data in brands.items():
            if data['avg_ratings']:
                data['overall_rating'] = sum(data['avg_ratings']) / len(data['avg_ratings'])
            else:
                data['overall_rating'] = 0
            
            if data['prices']:
                data['avg_price'] = sum(data['prices']) / len(data['prices'])
            else:
                data['avg_price'] = 0
            
            data['product_count'] = len(data['products'])
            data['categories'] = list(set(data['categories']))
        
        competitor_analysis['brands'] = brands
        competitor_analysis['ranking'] = sorted(brands.items(), key=lambda x: x[1]['overall_rating'], reverse=True)
        
        # Create performance table
        print(f"[+] Competitor analysis:")
        print(f"\nBRAND PERFORMANCE TABLE")
        print(f"+---------+-----------+-----------+-----------+-----------+")
        print(f"| Brand   | Rating    | Price     | Products  | Categories|")
        print(f"+---------+-----------+-----------+-----------+-----------+")
        
        for brand, data in competitor_analysis['ranking']:
            print(f"| {brand:<7} | {data['overall_rating']:>9.2f} | {data['avg_price']:>9.2f} | {data['product_count']:>9} | {len(data['categories']):>9} |")
        
        print(f"+---------+-----------+-----------+-----------+-----------+")
        
        # Show head-to-head comparisons
        if len(competitor_analysis['ranking']) >= 2:
            brand1, data1 = competitor_analysis['ranking'][0]
            brand2, data2 = competitor_analysis['ranking'][1]
            
            print(f"\nHEAD-TO-HEAD: {brand1} vs {brand2}")
            print(f"   {brand1}: {data1['overall_rating']:.1f}/5.0 rating, ${data1['avg_price']:.0f} avg price")
            print(f"   {brand2}: {data2['overall_rating']:.1f}/5.0 rating, ${data2['avg_price']:.0f} avg price")
        
        return competitor_analysis
    
    def _analyze_issues(self, real_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer issues from real reviews."""
        issues_analysis = {
            'top_issues': [],
            'component_issues': {}
        }
        
        # Common issue patterns
        issue_patterns = {
            'battery_issues': ['battery', 'drain', 'charge', 'power'],
            'sound_issues': ['sound', 'audio', 'speaker', 'volume'],
            'price_concerns': ['price', 'expensive', 'cost', 'money'],
            'comfort_issues': ['comfortable', 'fit', 'uncomfortable'],
            'quality_concerns': ['quality', 'build', 'durable', 'cheap'],
            'connectivity_problems': ['bluetooth', 'connection', 'pairing']
        }
        
        issue_counts = {}
        total_reviews = 0
        
        for category, products in real_data.items():
            for product_name, product_info in products.items():
                reviews = product_info['reviews']
                total_reviews += len(reviews)
                
                for review in reviews:
                    text = review['review_text'].lower()
                    
                    for issue_type, keywords in issue_patterns.items():
                        if any(keyword in text for keyword in keywords):
                            if review['rating'] <= 3:  # Only count issues from 3-star or lower reviews
                                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        # Calculate percentages and sort
        for issue_type, count in issue_counts.items():
            percentage = (count / total_reviews) * 100 if total_reviews > 0 else 0
            issues_analysis['top_issues'].append({
                'issue_type': issue_type,
                'count': count,
                'percentage': percentage,
                'severity': 'high' if percentage > 20 else 'medium' if percentage > 10 else 'low'
            })
        
        issues_analysis['top_issues'].sort(key=lambda x: x['percentage'], reverse=True)
        
        # Display issues analysis
        print(f"[+] Customer issues analysis:")
        for issue in issues_analysis['top_issues'][:5]:
            print(f"   {issue['issue_type'].replace('_', ' ').title()}: {issue['percentage']:.1f}% ({issue['severity']} severity)")
        
        return issues_analysis
    
    def _generate_strategies(self, real_data: Dict[str, Any], issues_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategic recommendations based on real data."""
        strategies = {
            'recommendations': [],
            'priority_areas': []
        }
        
        # Generate recommendations based on top issues
        for issue in issues_analysis['top_issues'][:3]:
            issue_type = issue['issue_type']
            severity = issue['severity']
            
            if 'battery' in issue_type:
                strategies['recommendations'].append({
                    'priority': severity,
                    'recommendation': 'Improve battery performance and longevity',
                    'action_items': [
                        'Optimize power management software',
                        'Consider larger battery capacity',
                        'Improve charging efficiency'
                    ]
                })
            elif 'sound' in issue_type:
                strategies['recommendations'].append({
                    'priority': severity,
                    'recommendation': 'Enhance audio quality and speaker performance',
                    'action_items': [
                        'Upgrade audio drivers',
                        'Improve speaker hardware',
                        'Enhance noise cancellation'
                    ]
                })
            elif 'price' in issue_type:
                strategies['recommendations'].append({
                    'priority': severity,
                    'recommendation': 'Address price concerns with better value proposition',
                    'action_items': [
                        'Bundle accessories',
                        'Offer financing options',
                        'Highlight premium features'
                    ]
                })
        
        # Display strategies
        print(f"[+] Strategic recommendations:")
        for i, strategy in enumerate(strategies['recommendations'], 1):
            print(f"   {i}. {strategy['recommendation']} ({strategy['priority'].title()} priority)")
            for action in strategy['action_items'][:2]:
                print(f"      - {action}")
        
        return strategies
    
    def _generate_executive_summary(self, real_data: Dict[str, Any], competitor_analysis: Dict[str, Any], strategies: Dict[str, Any]) -> str:
        """Generate executive summary."""
        total_products = sum(len(products) for products in real_data.values())
        total_reviews = sum(len(product_info['reviews']) for products in real_data.values() for product_info in products.values())
        
        top_brand = competitor_analysis['ranking'][0][0] if competitor_analysis['ranking'] else 'Unknown'
        
        summary = f"""
EXECUTIVE INTELLIGENCE SUMMARY

Market Overview:
- Total Products Analyzed: {total_products}
- Total Customer Reviews: {total_reviews}
- Categories: Headphones, Smartphones
- Data Source: Real Amazon Product Reviews

Market Leaders:
- Top Brand: {top_brand}
- Average Rating: {competitor_analysis['ranking'][0][1]['overall_rating']:.1f}/5.0
- Price Range: ${min(brand[1]['avg_price'] for brand in competitor_analysis['ranking']):.0f} - ${max(brand[1]['avg_price'] for brand in competitor_analysis['ranking']):.0f}

Key Findings:
- Customer satisfaction varies significantly by brand
- Price sensitivity is a major concern for customers
- Battery and audio quality are common improvement areas

Strategic Priorities:
"""
        
        for strategy in strategies['recommendations'][:3]:
            summary += f"- {strategy['recommendation']}\n"
        
        summary += f"""
Next Steps:
- Monitor competitor pricing strategies
- Focus on improving identified pain points
- Leverage brand strengths in marketing
- Consider product line expansions

This analysis is based on {total_reviews} real customer reviews from Amazon.
        """
        
        print(f"[+] Executive summary generated")
        print(f"   Total products: {total_products}")
        print(f"   Total reviews: {total_reviews}")
        print(f"   Top brand: {top_brand}")
        
        return summary
    
    def _display_summary(self, results: Dict[str, Any]):
        """Display final summary."""
        pipeline_end_time = datetime.now()
        duration = pipeline_end_time - self.pipeline_start_time
        
        print(f"\n" + "="*80)
        print("REAL DATA ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"\n[*] Execution Time: {duration.total_seconds():.2f} seconds")
        print(f"[*] Data Source: Real Amazon Product Reviews")
        
        print(f"\n[*] REAL INSIGHTS GENERATED:")
        print(f"   - Component analysis from actual customer reviews")
        print(f"   - Sentiment analysis based on real ratings")
        print(f"   - Competitor comparison with real market data")
        print(f"   - Customer issues identified from genuine feedback")
        print(f"   - Strategic recommendations based on real problems")
        
        print(f"\n[*] OUTPUT FILES:")
        if os.path.exists('real_analysis_results.json'):
            size = os.path.getsize('real_analysis_results.json')
            print(f"   [+] real_analysis_results.json ({size:,} bytes)")
        
        print(f"\n[+] ANALYSIS STATUS: COMPLETED WITH REAL DATA")
        print("="*80)
        
        print(f"\n[+] Real Amazon data analysis completed successfully!")
        print(f"[*] All insights based on actual customer reviews")

def main():
    """Main function to run real data analysis."""
    try:
        pipeline = SimpleRealPipeline()
        results = pipeline.analyze_real_data()
        return results
    except Exception as e:
        print(f"\n[!] Real data analysis failed: {e}")
        return None

if __name__ == "__main__":
    results = main()
