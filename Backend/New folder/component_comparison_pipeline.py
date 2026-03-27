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

class ComponentComparisonPipeline:
    """
    Pipeline that compares products based on component performance extracted from real reviews.
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
        
        logger.info("Component comparison pipeline initialized")
    
    def extract_component_sentiments(self, real_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract component-specific sentiments from real reviews."""
        print(f"\n[STEP 1] EXTRACTING COMPONENT SENTIMENTS")
        print("-" * 50)
        
        component_analysis = {}
        
        for category, products in real_data.items():
            component_analysis[category] = {}
            
            for product_name, product_info in products.items():
                component_analysis[category][product_name] = {}
                
                reviews = product_info['reviews']
                
                for component, keywords in self.component_keywords.items():
                    component_reviews = []
                    component_ratings = []
                    
                    for review in reviews:
                        review_text = review['review_text'].lower()
                        rating = review['rating']
                        
                        # Check if review mentions this component
                        if any(keyword in review_text for keyword in keywords):
                            component_reviews.append(review)
                            component_ratings.append(rating)
                    
                    if component_ratings:
                        # Calculate component-specific sentiment
                        avg_rating = sum(component_ratings) / len(component_ratings)
                        avg_sentiment = (avg_rating - 3) / 2  # Convert to -1 to 1 scale
                        
                        component_analysis[category][product_name][component] = {
                            'average_rating': avg_rating,
                            'sentiment_score': avg_sentiment,
                            'review_count': len(component_ratings),
                            'reviews': component_ratings,
                            'positive_reviews': len([r for r in component_ratings if r >= 4]),
                            'negative_reviews': len([r for r in component_ratings if r <= 2])
                        }
        
        # Display component extraction results
        print(f"[+] Component sentiments extracted:")
        for category, products in component_analysis.items():
            print(f"   {category}:")
            for product, components in products.items():
                if components:
                    print(f"      {product}:")
                    for component, data in components.items():
                        print(f"        {component}: {data['average_rating']:.1f}/5.0 ({data['sentiment_score']:.2f})")
        
        return component_analysis
    
    def create_component_comparison_table(self, component_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed component comparison tables."""
        print(f"\n[STEP 2] CREATING COMPONENT COMPARISON TABLES")
        print("-" * 50)
        
        comparison_tables = {}
        
        for category, products in component_analysis.items():
            if not products:
                continue
            
            # Get all components mentioned in this category
            all_components = set()
            for product_data in products.values():
                all_components.update(product_data.keys())
            
            all_components = sorted(list(all_components))
            
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
            for product_name, product_data in products.items():
                # Shorten product name for table
                short_name = product_name.split()[0] + " " + product_name.split()[1][:8] if len(product_name.split()) > 2 else product_name[:18]
                data_row = f"| {short_name:<18} |"
                
                for component in all_components:
                    if component in product_data:
                        rating = product_data[component]['average_rating']
                        data_row += f" {rating:>9.1f} |"
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
    
    def analyze_component_winners(self, component_analysis: Dict[str, Any], comparison_tables: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze which products win for each component."""
        print(f"\n[STEP 3] ANALYZING COMPONENT WINNERS")
        print("-" * 50)
        
        component_winners = {}
        
        for category, table_data in comparison_tables.items():
            component_winners[category] = {}
            
            for component in table_data['components']:
                best_product = None
                best_rating = 0
                
                for product_name in table_data['products']:
                    product_data = component_analysis[category][product_name]
                    
                    if component in product_data:
                        rating = product_data[component]['average_rating']
                        if rating > best_rating:
                            best_rating = rating
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
                print(f"      {component}: {winner_data['winner']} ({winner_data['rating']:.1f}/5.0)")
        
        return component_winners
    
    def generate_head_to_head_comparisons(self, component_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed head-to-head component comparisons."""
        print(f"\n[STEP 4] HEAD-TO-HEAD COMPONENT COMPARISONS")
        print("-" * 50)
        
        head_to_head = {}
        
        for category, products in component_analysis.items():
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
                all_components = set(products[product1].keys()) | set(products[product2].keys())
                
                for component in sorted(all_components):
                    p1_data = products[product1].get(component, {})
                    p2_data = products[product2].get(component, {})
                    
                    if p1_data and p2_data:
                        p1_rating = p1_data['average_rating']
                        p2_rating = p2_data['average_rating']
                        
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
    
    def generate_component_insights(self, component_analysis: Dict[str, Any], component_winners: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights based on component analysis."""
        print(f"\n[STEP 5] COMPONENT INSIGHTS")
        print("-" * 50)
        
        insights = {
            'strengths': {},
            'weaknesses': {},
            'opportunities': {},
            'recommendations': []
        }
        
        for category, winners in component_winners.items():
            insights['strengths'][category] = {}
            insights['weaknesses'][category] = {}
            
            # Find which brands dominate which components
            brand_component_wins = {}
            
            for component, winner_data in winners.items():
                brand = winner_data['winner'].split()[0]
                if brand not in brand_component_wins:
                    brand_component_wins[brand] = []
                brand_component_wins[brand].append({
                    'component': component,
                    'rating': winner_data['rating'],
                    'sentiment': winner_data['sentiment']
                })
            
            # Identify brand strengths
            for brand, components in brand_component_wins.items():
                if len(components) >= 2:
                    insights['strengths'][category][brand] = {
                        'dominant_components': [c['component'] for c in components],
                        'avg_rating': sum(c['rating'] for c in components) / len(components),
                        'component_count': len(components)
                    }
            
            # Identify weak components (low ratings)
            for product_name, product_data in component_analysis[category].items():
                weak_components = []
                for component, data in product_data.items():
                    if data['average_rating'] <= 3.0:  # Poor performance
                        weak_components.append({
                            'component': component,
                            'rating': data['average_rating'],
                            'sentiment': data['sentiment_score']
                        })
                
                if weak_components:
                    brand = product_name.split()[0]
                    if brand not in insights['weaknesses'][category]:
                        insights['weaknesses'][category][brand] = []
                    insights['weaknesses'][category][brand].extend(weak_components)
        
        # Generate recommendations
        for category, strengths in insights['strengths'].items():
            for brand, data in strengths.items():
                insights['recommendations'].append({
                    'category': category,
                    'brand': brand,
                    'type': 'leverage_strength',
                    'recommendation': f"Leverage {brand}'s strength in {', '.join(data['dominant_components'][:2])}",
                    'action': f"Highlight {data['dominant_components'][0]} in marketing campaigns"
                })
        
        for category, weaknesses in insights['weaknesses'].items():
            for brand, weak_components in weaknesses.items():
                if len(weak_components) > 0:
                    worst_component = min(weak_components, key=lambda x: x['rating'])
                    insights['recommendations'].append({
                        'category': category,
                        'brand': brand,
                        'type': 'address_weakness',
                        'recommendation': f"Improve {brand}'s {worst_component['component']} performance",
                        'action': f"Focus R&D on {worst_component['component']} improvements"
                    })
        
        # Display insights
        print(f"[+] Component insights generated:")
        
        for category, strengths in insights['strengths'].items():
            if strengths:
                print(f"   {category} Strengths:")
                for brand, data in strengths.items():
                    print(f"      {brand}: Dominant in {', '.join(data['dominant_components'])}")
        
        for category, weaknesses in insights['weaknesses'].items():
            if weaknesses:
                print(f"   {category} Areas for Improvement:")
                for brand, components in weaknesses.items():
                    worst = min(components, key=lambda x: x['rating'])
                    print(f"      {brand}: {worst['component']} ({worst['rating']:.1f}/5.0)")
        
        print(f"\n[+] Strategic Recommendations:")
        for i, rec in enumerate(insights['recommendations'][:3], 1):
            print(f"   {i}. {rec['recommendation']}")
            print(f"      Action: {rec['action']}")
        
        return insights
    
    def run_component_comparison(self) -> Dict[str, Any]:
        """Run the complete component comparison pipeline."""
        print("\n" + "="*80)
        print("COMPONENT-BASED PRODUCT COMPARISON")
        print("="*80)
        
        try:
            # Load real Amazon data
            with open('real_processed_product_reviews.json', 'r', encoding='utf-8') as f:
                real_data = json.load(f)
            
            print(f"[+] Loaded real Amazon data")
            
            # Step 1: Extract component sentiments
            component_analysis = self.extract_component_sentiments(real_data)
            
            # Step 2: Create comparison tables
            comparison_tables = self.create_component_comparison_table(component_analysis)
            
            # Step 3: Analyze component winners
            component_winners = self.analyze_component_winners(component_analysis, comparison_tables)
            
            # Step 4: Head-to-head comparisons
            head_to_head = self.generate_head_to_head_comparisons(component_analysis)
            
            # Step 5: Generate insights
            insights = self.generate_component_insights(component_analysis, component_winners)
            
            # Save results
            results = {
                'component_analysis': component_analysis,
                'comparison_tables': comparison_tables,
                'component_winners': component_winners,
                'head_to_head': head_to_head,
                'insights': insights
            }
            
            with open('component_comparison_results.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            # Display final summary
            self._display_summary(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Component comparison failed: {e}")
            print(f"\n[!] Analysis failed: {e}")
            raise
    
    def _display_summary(self, results: Dict[str, Any]):
        """Display final summary."""
        pipeline_end_time = datetime.now()
        duration = pipeline_end_time - self.pipeline_start_time
        
        print(f"\n" + "="*80)
        print("COMPONENT COMPARISON SUMMARY")
        print("="*80)
        
        print(f"\n[*] Execution Time: {duration.total_seconds():.2f} seconds")
        print(f"[*] Analysis Type: Component-based product comparison")
        
        # Count total components analyzed
        total_components = 0
        for category_data in results['component_analysis'].values():
            for product_data in category_data.values():
                total_components += len(product_data)
        
        print(f"\n[*] COMPONENTS ANALYZED: {total_components}")
        
        # Show top component winners
        print(f"\n[*] TOP COMPONENT PERFORMERS:")
        for category, winners in results['component_winners'].items():
            print(f"   {category}:")
            for component, winner in list(winners.items())[:3]:
                print(f"      {component}: {winner['winner'].split()[0]} ({winner['rating']:.1f}/5.0)")
        
        print(f"\n[*] OUTPUT FILES:")
        if os.path.exists('component_comparison_results.json'):
            size = os.path.getsize('component_comparison_results.json')
            print(f"   [+] component_comparison_results.json ({size:,} bytes)")
        
        print(f"\n[+] COMPARISON STATUS: COMPLETED")
        print("="*80)
        
        print(f"\n[+] Component-based product comparison completed!")
        print(f"[*] Products compared based on actual component performance")

def main():
    """Main function to run component comparison."""
    try:
        pipeline = ComponentComparisonPipeline()
        results = pipeline.run_component_comparison()
        return results
    except Exception as e:
        print(f"\n[!] Component comparison failed: {e}")
        return None

if __name__ == "__main__":
    results = main()
