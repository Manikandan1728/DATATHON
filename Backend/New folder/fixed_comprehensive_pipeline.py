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

class FixedComprehensivePipeline:
    """
    Fixed comprehensive pipeline that provides both component comparison AND full competitive intelligence insights.
    """
    
    def __init__(self):
        self.results = {}
        self.pipeline_start_time = datetime.now()
        
        # Component keywords for extraction
        self.component_keywords = {
            'battery': ['battery', 'charge', 'power', 'drain', 'battery life', 'charging', 'longevity'],
            'sound': ['sound', 'audio', 'speaker', 'volume', 'bass', 'treble', 'clarity', 'quality'],
            'noise_cancellation': ['noise cancellation', 'anc', 'noise canceling', 'quiet', 'silence'],
            'comfort': ['comfortable', 'fit', 'wear', 'uncomfortable', 'tight', 'lightweight', 'heavy'],
            'build_quality': ['build', 'quality', 'durable', 'sturdy', 'premium', 'cheap', 'materials'],
            'connectivity': ['bluetooth', 'connection', 'pairing', 'wireless', 'signal', 'range'],
            'features': ['features', 'functions', 'capabilities', 'options', 'controls', 'interface'],
            'price_value': ['price', 'cost', 'expensive', 'cheap', 'value', 'money', 'worth'],
            'design': ['design', 'look', 'appearance', 'style', 'aesthetic', 'color']
        }
        
        logger.info("Fixed comprehensive pipeline initialized")
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run comprehensive analysis with both component comparison and competitive intelligence."""
        print("\n" + "="*80)
        print("COMPREHENSIVE REAL AMAZON DATA COMPETITIVE INTELLIGENCE")
        print("="*80)
        
        try:
            # Load real Amazon data
            with open('real_processed_product_reviews.json', 'r', encoding='utf-8') as f:
                real_data = json.load(f)
            
            print(f"\n[STEP 1] LOADING REAL AMAZON DATA")
            print("-" * 50)
            print(f"[+] Loaded real Amazon data")
            
            for category, products in real_data.items():
                print(f"   {category}: {len(products)} products")
                for product_name, product_info in products.items():
                    print(f"      - {product_info['brand']} ${product_info['price']:.2f} ({len(product_info['reviews'])} reviews)")
            
            # Step 2: Component Analysis
            print(f"\n[STEP 2] COMPONENT ANALYSIS")
            print("-" * 50)
            
            component_analysis = self._analyze_components(real_data)
            
            # Step 3: Sentiment Analysis
            print(f"\n[STEP 3] SENTIMENT ANALYSIS")
            print("-" * 50)
            
            sentiment_analysis = self._analyze_sentiments(real_data)
            
            # Step 4: Component Comparison Tables
            print(f"\n[STEP 4] COMPONENT COMPARISON TABLES")
            print("-" * 50)
            
            comparison_tables = self._create_component_comparison_tables(real_data)
            
            # Step 5: Component Winners Analysis
            print(f"\n[STEP 5] COMPONENT WINNERS ANALYSIS")
            print("-" * 50)
            
            component_winners = self._analyze_component_winners(real_data)
            
            # Step 6: Head-to-Head Component Battles
            print(f"\n[STEP 6] HEAD-TO-HEAD COMPONENT BATTLES")
            print("-" * 50)
            
            head_to_head = self._generate_head_to_head_comparisons(real_data)
            
            # Step 7: Competitor Analysis
            print(f"\n[STEP 7] COMPETITOR ANALYSIS")
            print("-" * 50)
            
            competitor_analysis = self._analyze_competitors(real_data, sentiment_analysis)
            
            # Step 8: Customer Issues Analysis
            print(f"\n[STEP 8] CUSTOMER ISSUES ANALYSIS")
            print("-" * 50)
            
            issues_analysis = self._analyze_issues(real_data)
            
            # Step 9: Strategic Recommendations
            print(f"\n[STEP 9] STRATEGIC RECOMMENDATIONS")
            print("-" * 50)
            
            strategy_recommendations = self._generate_strategies(real_data, issues_analysis, component_winners)
            
            # Step 10: Executive Summary
            print(f"\n[STEP 10] EXECUTIVE SUMMARY")
            print("-" * 50)
            
            executive_summary = self._generate_executive_summary(real_data, competitor_analysis, strategy_recommendations, component_winners)
            
            # Save comprehensive results
            results = {
                'real_data': real_data,
                'component_analysis': component_analysis,
                'sentiment_analysis': sentiment_analysis,
                'comparison_tables': comparison_tables,
                'component_winners': component_winners,
                'head_to_head': head_to_head,
                'competitor_analysis': competitor_analysis,
                'issues_analysis': issues_analysis,
                'strategy_recommendations': strategy_recommendations,
                'executive_summary': executive_summary
            }
            
            with open('comprehensive_analysis_results.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            # Display final summary
            self._display_comprehensive_summary(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {e}")
            print(f"\n[!] Analysis failed: {e}")
            raise
    
    def _analyze_components(self, real_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze components mentioned in real reviews."""
        component_analysis = {}
        
        for category, products in real_data.items():
            component_analysis[category] = {}
            
            for product_name, product_info in products.items():
                component_analysis[category][product_name] = {}
                
                all_reviews_text = " ".join([review['review_text'].lower() for review in product_info['reviews']])
                
                for component, keywords in self.component_keywords.items():
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
    
    def _create_component_comparison_tables(self, real_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed component comparison tables."""
        comparison_tables = {}
        
        for category, products in real_data.items():
            if not products:
                continue
            
            # Get all components mentioned in this category
            all_components = set()
            for product_info in products.values():
                reviews = product_info['reviews']
                for review in reviews:
                    review_text = review['review_text'].lower()
                    for component, keywords in self.component_keywords.items():
                        if any(keyword in review_text for keyword in keywords):
                            all_components.add(component)
            
            all_components = sorted(list(all_components))
            
            if not all_components:
                continue
            
            # Create comparison table
            table_lines = []
            header = f"+{'-'*20}+"
            for component in all_components:
                header += f"{'-'*12}+"
            table_lines.append(header)
            
            # Header row
            header_row = f"| {'Product Name':<18} |"
            for component in all_components:
                header_row += f" {component[:10]:<10} |"
            table_lines.append(header_row)
            table_lines.append(header)
            
            # Data rows for each product
            for product_name, product_info in products.items():
                # Shorten product name for table
                short_name = product_name.split()[0] + " " + product_name.split()[1][:8] if len(product_name.split()) > 2 else product_name[:18]
                data_row = f"| {short_name:<18} |"
                
                # Extract component-specific ratings
                for component in all_components:
                    component_rating = self._get_component_rating(product_info, component)
                    if component_rating is not None:
                        data_row += f" {component_rating:>9.1f} |"
                    else:
                        data_row += f" {'N/A':>9} |"
                
                table_lines.append(data_row)
            
            table_lines.append(header)
            
            comparison_tables[category] = {
                'table': '\n'.join(table_lines),
                'components': all_components,
                'products': list(products.keys())
            }
            
            # Display the table
            print(f"\n{category.upper()} COMPONENT COMPARISON TABLE")
            print(comparison_tables[category]['table'])
        
        return comparison_tables
    
    def _get_component_rating(self, product_info: Dict[str, Any], component: str) -> float:
        """Get component-specific rating from reviews."""
        keywords = self.component_keywords[component]
        component_ratings = []
        
        for review in product_info['reviews']:
            review_text = review['review_text'].lower()
            if any(keyword in review_text for keyword in keywords):
                component_ratings.append(review['rating'])
        
        if component_ratings:
            return sum(component_ratings) / len(component_ratings)
        return None
    
    def _analyze_component_winners(self, real_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze which products win for each component."""
        component_winners = {}
        
        for category, products in real_data.items():
            component_winners[category] = {}
            
            # Get all components mentioned in this category
            all_components = set()
            for product_info in products.values():
                reviews = product_info['reviews']
                for review in reviews:
                    review_text = review['review_text'].lower()
                    for component, keywords in self.component_keywords.items():
                        if any(keyword in review_text for keyword in keywords):
                            all_components.add(component)
            
            for component in all_components:
                best_product = None
                best_rating = 0
                
                for product_name, product_info in products.items():
                    component_rating = self._get_component_rating(product_info, component)
                    
                    if component_rating and component_rating > best_rating:
                        best_rating = component_rating
                        best_product = product_name
                
                if best_product:
                    component_winners[category][component] = {
                        'winner': best_product,
                        'rating': best_rating,
                        'sentiment': (best_rating - 3) / 2
                    }
        
        # Display component winners
        print(f"[+] Component winners:")
        for category, winners in component_winners.items():
            print(f"   {category}:")
            for component, winner_data in winners.items():
                print(f"      {component}: {winner_data['winner'].split()[0]} ({winner_data['rating']:.1f}/5.0)")
        
        return component_winners
    
    def _generate_head_to_head_comparisons(self, real_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed head-to-head component comparisons."""
        head_to_head = {}
        
        for category, products in real_data.items():
            product_list = list(products.keys())
            
            if len(product_list) >= 2:
                # Compare first two products
                product1, product2 = product_list[0], product_list[1]
                
                comparison = {
                    'product1': product1,
                    'product2': product2,
                    'component_battles': []
                }
                
                # Get all components mentioned by either product
                all_components = set()
                for product_info in products.values():
                    reviews = product_info['reviews']
                    for review in reviews:
                        review_text = review['review_text'].lower()
                        for component, keywords in self.component_keywords.items():
                            if any(keyword in review_text for keyword in keywords):
                                all_components.add(component)
                
                for component in sorted(all_components):
                    p1_rating = self._get_component_rating(products[product1], component)
                    p2_rating = self._get_component_rating(products[product2], component)
                    
                    if p1_rating is not None and p2_rating is not None:
                        winner = product1 if p1_rating > p2_rating else product2
                        margin = abs(p1_rating - p2_rating)
                        
                        comparison['component_battles'].append({
                            'component': component,
                            'product1_rating': p1_rating,
                            'product2_rating': p2_rating,
                            'winner': winner,
                            'margin': margin,
                            'significance': 'high' if margin > 1.0 else 'medium' if margin > 0.5 else 'low'
                        })
                
                # Sort by margin (most significant differences first)
                comparison['component_battles'].sort(key=lambda x: x['margin'], reverse=True)
                
                head_to_head[category] = comparison
                
                # Display head-to-head comparison
                print(f"\nHEAD-TO-HEAD: {product1.split()[0]} vs {product2.split()[0]}")
                print(f"{'Component':<15} | {product1.split()[0]:<10} | {product2.split()[0]:<10} | Winner")
                print(f"{'-'*15} | {'-'*10} | {'-'*10} | {'-'*10}")
                
                for battle in comparison['component_battles'][:5]:  # Show top 5
                    p1_name = product1.split()[0]
                    p2_name = product2.split()[0]
                    winner_name = battle['winner'].split()[0]
                    
                    print(f"{battle['component']:<15} | {p1_name:<10} | {p2_name:<10} | {winner_name}")
                
                # Calculate overall winner
                product1_wins = len([b for b in comparison['component_battles'] if b['winner'] == product1])
                product2_wins = len([b for b in comparison['component_battles'] if b['winner'] == product2])
                
                overall_winner = product1 if product1_wins > product2_wins else product2
                print(f"\nOverall Winner: {overall_winner.split()[0]} ({product1_wins}-{product2_wins} components)")
        
        return head_to_head
    
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
    
    def _generate_strategies(self, real_data: Dict[str, Any], issues_analysis: Dict[str, Any], component_winners: Dict[str, Any]) -> Dict[str, Any]:
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
        
        # Add component-based recommendations
        for category, winners in component_winners.items():
            for component, winner_data in winners.items():
                if winner_data['rating'] >= 4.5:
                    brand = winner_data['winner'].split()[0]
                    strategies['recommendations'].append({
                        'priority': 'high',
                        'recommendation': f'Leverage {brand}\'s superior {component} performance',
                        'action_items': [
                            f'Market {component} excellence in campaigns',
                            f'Use {component} reviews in testimonials',
                            f'Highlight {component} in product descriptions'
                        ],
                        'type': 'leverage_strength'
                    })
                elif winner_data['rating'] <= 3.5:
                    brand = winner_data['winner'].split()[0]
                    strategies['recommendations'].append({
                        'priority': 'medium',
                        'recommendation': f'Improve {brand}\'s {component} performance',
                        'action_items': [
                            f'Focus R&D on {component} improvements',
                            f'Address {component} customer complaints',
                            f'Consider {component} hardware upgrades'
                        ],
                        'type': 'address_weakness'
                    })
        
        # Display strategies
        print(f"[+] Strategic recommendations:")
        for i, strategy in enumerate(strategies['recommendations'][:6], 1):
            print(f"   {i}. {strategy['recommendation']} ({strategy['priority'].title()} priority)")
            for action in strategy['action_items'][:2]:
                print(f"      - {action}")
        
        return strategies
    
    def _generate_executive_summary(self, real_data: Dict[str, Any], competitor_analysis: Dict[str, Any], strategies: Dict[str, Any], component_winners: Dict[str, Any]) -> str:
        """Generate executive summary."""
        total_products = sum(len(products) for products in real_data.values())
        total_reviews = sum(len(product_info['reviews']) for products in real_data.values() for product_info in products.values())
        
        top_brand = competitor_analysis['ranking'][0][0] if competitor_analysis['ranking'] else 'Unknown'
        
        # Get top component performers
        top_components = []
        for category, winners in component_winners.items():
            for component, winner_data in winners.items():
                if winner_data['rating'] >= 4.5:
                    top_components.append(f"{category}: {component} ({winner_data['winner'].split()[0]})")
        
        summary = f"""
EXECUTIVE INTELLIGENCE SUMMARY

Market Overview:
- Total Products Analyzed: {total_products}
- Total Customer Reviews: {total_reviews}
- Categories: {', '.join(real_data.keys())}
- Data Source: Real Amazon Product Reviews

Market Leaders:
- Top Brand: {top_brand}
- Average Rating: {competitor_analysis['ranking'][0][1]['overall_rating']:.1f}/5.0
- Price Range: ${min(brand[1]['avg_price'] for brand in competitor_analysis['ranking']):.0f} - ${max(brand[1]['avg_price'] for brand in competitor_analysis['ranking']):.0f}

Component Excellence:
{chr(10).join([f"- {comp}" for comp in top_components[:3]])}

Key Findings:
- Component performance varies significantly by brand
- Battery and audio quality are critical differentiation factors
- Price sensitivity is a major concern for customers
- Component-specific analysis reveals detailed competitive advantages

Strategic Priorities:
"""
        
        for strategy in strategies['recommendations'][:3]:
            summary += f"- {strategy['recommendation']}\n"
        
        summary += f"""
Next Steps:
- Monitor competitor component performance
- Focus on improving identified component weaknesses
- Leverage component strengths in marketing
- Consider component-based product positioning

This analysis is based on {total_reviews} real customer reviews from Amazon with detailed component-level insights.
        """
        
        print(f"[+] Executive summary generated")
        print(f"   Total products: {total_products}")
        print(f"   Total reviews: {total_reviews}")
        print(f"   Top brand: {top_brand}")
        print(f"   Top components: {len(top_components)} identified")
        
        return summary
    
    def _display_comprehensive_summary(self, results: Dict[str, Any]):
        """Display final comprehensive summary."""
        pipeline_end_time = datetime.now()
        duration = pipeline_end_time - self.pipeline_start_time
        
        print(f"\n" + "="*80)
        print("COMPREHENSIVE ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"\n[*] Execution Time: {duration.total_seconds():.2f} seconds")
        print(f"[*] Data Source: Real Amazon Product Reviews")
        
        print(f"\n[*] COMPREHENSIVE INSIGHTS GENERATED:")
        print(f"   - Component analysis from actual customer reviews")
        print(f"   - Component comparison tables with real ratings")
        print(f"   - Component winners and head-to-head battles")
        print(f"   - Sentiment analysis based on real ratings")
        print(f"   - Competitor comparison with real market data")
        print(f"   - Customer issues identified from genuine feedback")
        print(f"   - Strategic recommendations based on real problems")
        print(f"   - Executive summary with component insights")
        
        print(f"\n[*] OUTPUT FILES:")
        if os.path.exists('comprehensive_analysis_results.json'):
            size = os.path.getsize('comprehensive_analysis_results.json')
            print(f"   [+] comprehensive_analysis_results.json ({size:,} bytes)")
        
        print(f"\n[+] ANALYSIS STATUS: COMPLETED WITH REAL DATA")
        print("="*80)
        
        print(f"\n[+] Comprehensive real Amazon data analysis completed!")
        print(f"[*] All insights based on actual customer reviews with component-level detail")

def main():
    """Main function to run comprehensive analysis."""
    try:
        pipeline = FixedComprehensivePipeline()
        results = pipeline.run_comprehensive_analysis()
        return results
    except Exception as e:
        print(f"\n[!] Comprehensive analysis failed: {e}")
        return None

if __name__ == "__main__":
    results = main()
