import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompetitorIntelligence:
    """
    Compare brands within each category based on component sentiment scores.
    Generate competitive intelligence reports and performance tables.
    """
    
    def __init__(self):
        self.sentiment_scores = {}
        self.competitor_analysis = {}
        self.performance_tables = {}
        self.summaries = {}
    
    def load_sentiment_scores(self, input_file: str = 'component_sentiment_scores.json') -> None:
        """
        Load component sentiment scores data.
        
        Args:
            input_file: Path to the sentiment scores JSON file
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                self.sentiment_scores = json.load(f)
            logger.info(f"Successfully loaded sentiment scores from {input_file}")
            
            total_categories = len(self.sentiment_scores)
            total_components = sum(len(components) for components in self.sentiment_scores.values())
            total_brand_components = sum(len(brands) for components in self.sentiment_scores.values() for brands in components.values())
            
            logger.info(f"Loaded {total_categories} categories with {total_components} components and {total_brand_components} brand-component pairs")
            
        except FileNotFoundError:
            logger.error(f"File not found: {input_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading sentiment scores: {e}")
            raise
    
    def compare_component_scores(self, category: str, component: str) -> Dict[str, Any]:
        """
        Compare sentiment scores for a specific component within a category.
        
        Args:
            category: Product category
            component: Component name
            
        Returns:
            Dictionary with comparison results
        """
        if category not in self.sentiment_scores:
            return {}
        
        if component not in self.sentiment_scores[category]:
            return {}
        
        brand_scores = self.sentiment_scores[category][component]
        
        if not brand_scores:
            return {}
        
        # Find winning brand
        winning_brand = max(brand_scores.items(), key=lambda x: x[1])
        losing_brand = min(brand_scores.items(), key=lambda x: x[1])
        
        # Calculate statistics
        scores = list(brand_scores.values())
        avg_score = statistics.mean(scores)
        score_range = max(scores) - min(scores)
        
        # Rank brands
        ranked_brands = sorted(brand_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'component': component,
            'category': category,
            'brand_scores': brand_scores,
            'ranked_brands': ranked_brands,
            'winning_brand': winning_brand[0],
            'winning_score': winning_brand[1],
            'losing_brand': losing_brand[0],
            'losing_score': losing_brand[1],
            'average_score': avg_score,
            'score_range': score_range,
            'total_brands': len(brand_scores)
        }
    
    def generate_performance_table(self, category: str) -> Dict[str, Any]:
        """
        Generate performance table for a category.
        
        Args:
            category: Product category
            
        Returns:
            Dictionary with performance table data
        """
        if category not in self.sentiment_scores:
            return {}
        
        components = self.sentiment_scores[category]
        performance_data = {}
        brand_wins = defaultdict(int)
        
        for component in components.keys():
            comparison = self.compare_component_scores(category, component)
            if comparison:
                performance_data[component] = comparison
                brand_wins[comparison['winning_brand']] += 1
        
        # Generate table string
        table_lines = [f"{category.upper()} PERFORMANCE TABLE"]
        table_lines.append("=" * 50)
        
        for component, data in performance_data.items():
            # Create brand score line
            brand_scores_str = " | ".join([f"{brand}: {score:.2f}" for brand, score in data['ranked_brands']])
            winner_str = f"Winner: {data['winning_brand']}"
            
            line = f"{component:<15} {brand_scores_str} | {winner_str}"
            table_lines.append(line)
        
        table_str = "\n".join(table_lines)
        
        # Generate summary
        summary_lines = [f"\n{category.upper()} SUMMARY:"]
        sorted_wins = sorted(brand_wins.items(), key=lambda x: x[1], reverse=True)
        
        for brand, wins in sorted_wins:
            summary_lines.append(f"{brand}: {wins} component wins")
        
        summary_str = "\n".join(summary_lines)
        
        return {
            'category': category,
            'performance_table': table_str,
            'performance_data': performance_data,
            'brand_wins': dict(brand_wins),
            'summary': summary_str,
            'total_components': len(performance_data)
        }
    
    def analyze_all_categories(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze all categories and generate performance tables.
        
        Returns:
            Dictionary with analysis results for all categories
        """
        logger.info("Analyzing all categories...")
        
        analysis_results = {}
        
        for category in self.sentiment_scores.keys():
            logger.info(f"Analyzing {category}...")
            category_analysis = self.generate_performance_table(category)
            if category_analysis:
                analysis_results[category] = category_analysis
        
        self.competitor_analysis = analysis_results
        logger.info(f"Completed analysis for {len(analysis_results)} categories")
        
        return analysis_results
    
    def generate_cross_category_analysis(self) -> Dict[str, Any]:
        """
        Generate cross-category competitive analysis.
        
        Returns:
            Dictionary with cross-category insights
        """
        logger.info("Generating cross-category analysis...")
        
        # Collect all brand performance data
        brand_performance = defaultdict(lambda: defaultdict(list))
        brand_wins_total = defaultdict(int)
        brand_categories = defaultdict(set)
        
        for category, analysis in self.competitor_analysis.items():
            for component, data in analysis['performance_data'].items():
                for brand, score in data['brand_scores'].items():
                    brand_performance[brand][category].append(score)
                    brand_categories[brand].add(category)
            
            for brand, wins in analysis['brand_wins'].items():
                brand_wins_total[brand] += wins
        
        # Calculate brand statistics
        brand_stats = {}
        for brand in brand_performance.keys():
            all_scores = []
            for category_scores in brand_performance[brand].values():
                all_scores.extend(category_scores)
            
            if all_scores:
                brand_stats[brand] = {
                    'total_wins': brand_wins_total[brand],
                    'categories': list(brand_categories[brand]),
                    'category_count': len(brand_categories[brand]),
                    'average_score': statistics.mean(all_scores),
                    'score_count': len(all_scores),
                    'best_category': None,
                    'worst_category': None
                }
                
                # Find best and worst categories
                category_averages = {}
                for category, scores in brand_performance[brand].items():
                    if scores:
                        category_averages[category] = statistics.mean(scores)
                
                if category_averages:
                    best_cat = max(category_averages.items(), key=lambda x: x[1])
                    worst_cat = min(category_averages.items(), key=lambda x: x[1])
                    brand_stats[brand]['best_category'] = {'name': best_cat[0], 'score': best_cat[1]}
                    brand_stats[brand]['worst_category'] = {'name': worst_cat[0], 'score': worst_cat[1]}
        
        # Generate overall rankings
        overall_ranking = sorted(brand_stats.items(), key=lambda x: x[1]['total_wins'], reverse=True)
        
        return {
            'brand_statistics': brand_stats,
            'overall_ranking': overall_ranking,
            'total_brands': len(brand_stats),
            'total_categories': len(self.competitor_analysis)
        }
    
    def identify_market_leaders(self) -> Dict[str, Any]:
        """
        Identify market leaders and trends.
        
        Returns:
            Dictionary with market leader insights
        """
        cross_analysis = self.generate_cross_category_analysis()
        brand_stats = cross_analysis['brand_statistics']
        
        # Market leaders by different metrics
        leaders = {
            'overall_winner': cross_analysis['overall_ranking'][0] if cross_analysis['overall_ranking'] else None,
            'highest_average_score': max(brand_stats.items(), key=lambda x: x[1]['average_score']) if brand_stats else None,
            'most_categories': max(brand_stats.items(), key=lambda x: x[1]['category_count']) if brand_stats else None,
            'most_consistent': None,  # Lowest score variance
            'dominant_categories': {}
        }
        
        # Find most consistent brand (lowest score variance)
        if brand_stats:
            consistency_scores = {}
            for brand, stats in brand_stats.items():
                all_scores = []
                for category_scores in self.competitor_analysis.values():
                    for component_data in category_scores['performance_data'].values():
                        if brand in component_data['brand_scores']:
                            all_scores.append(component_data['brand_scores'][brand])
                
                if len(all_scores) > 1:
                    consistency_scores[brand] = statistics.stdev(all_scores)
            
            if consistency_scores:
                leaders['most_consistent'] = min(consistency_scores.items(), key=lambda x: x[1])
        
        # Find dominant brands per category
        for category, analysis in self.competitor_analysis.items():
            if analysis['brand_wins']:
                dominant_brand = max(analysis['brand_wins'].items(), key=lambda x: x[1])
                leaders['dominant_categories'][category] = {
                    'brand': dominant_brand[0],
                    'wins': dominant_brand[1],
                    'total_components': analysis['total_components']
                }
        
        return leaders
    
    def save_competitor_analysis(self, output_file: str = 'competitor_analysis.json') -> None:
        """
        Save competitor analysis as JSON file.
        
        Args:
            output_file: Output file name
        """
        try:
            # Prepare complete analysis data
            complete_analysis = {
                'category_analysis': self.competitor_analysis,
                'cross_category_analysis': self.generate_cross_category_analysis(),
                'market_leaders': self.identify_market_leaders(),
                'metadata': {
                    'total_categories': len(self.competitor_analysis),
                    'analysis_timestamp': None  # Could add timestamp if needed
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(complete_analysis, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved competitor analysis to {output_file}")
        except Exception as e:
            logger.error(f"Error saving competitor analysis: {e}")
            raise
    
    def process_competitor_intelligence(self, input_file: str = 'component_sentiment_scores.json',
                                       output_file: str = 'competitor_analysis.json') -> Dict[str, Any]:
        """
        Complete pipeline to process competitor intelligence.
        
        Args:
            input_file: Input sentiment scores JSON file
            output_file: Output competitor analysis JSON file
            
        Returns:
            Complete competitor analysis results
        """
        try:
            # Load sentiment scores
            self.load_sentiment_scores(input_file)
            
            # Analyze all categories
            self.analyze_all_categories()
            
            # Save analysis
            self.save_competitor_analysis(output_file)
            
            # Print summary
            self._print_summary()
            
            logger.info("Competitor intelligence analysis completed successfully!")
            return self.competitor_analysis
            
        except Exception as e:
            logger.error(f"Error in competitor intelligence pipeline: {e}")
            raise
    
    def _print_summary(self) -> None:
        """Print summary of competitor intelligence results."""
        print("\n" + "="*60)
        print("🏆 COMPETITOR INTELLIGENCE SUMMARY")
        print("="*60)
        
        # Print performance tables for each category
        for category, analysis in self.competitor_analysis.items():
            print(f"\n{analysis['performance_table']}")
            print(analysis['summary'])
        
        # Print cross-category analysis
        cross_analysis = self.generate_cross_category_analysis()
        market_leaders = self.identify_market_leaders()
        
        print(f"\n" + "="*60)
        print("🌍 CROSS-CATEGORY ANALYSIS")
        print("="*60)
        
        print(f"\n🏆 OVERALL RANKINGS:")
        for i, (brand, stats) in enumerate(cross_analysis['overall_ranking'][:10], 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            print(f"   {emoji} {i:2d}. {brand}: {stats['total_wins']} wins, {stats['category_count']} categories")
        
        if market_leaders['overall_winner']:
            winner = market_leaders['overall_winner']
            print(f"\n👑 OVERALL MARKET LEADER: {winner[0]} with {winner[1]['total_wins']} component wins")
        
        if market_leaders['highest_average_score']:
            best_avg = market_leaders['highest_average_score']
            print(f"⭐ HIGHEST AVERAGE SCORE: {best_avg[0]} ({best_avg[1]['average_score']:.3f})")
        
        print(f"\n📁 DOMINANT BRANDS BY CATEGORY:")
        for category, dominant in market_leaders['dominant_categories'].items():
            dominance_pct = (dominant['wins'] / dominant['total_components']) * 100
            print(f"   {category}: {dominant['brand']} ({dominant['wins']}/{dominant['total_components']} = {dominance_pct:.1f}%)")
        
        print("="*60)
    
    def get_brand_comparison(self, brand1: str, brand2: str) -> Dict[str, Any]:
        """
        Get detailed comparison between two specific brands.
        
        Args:
            brand1: First brand name
            brand2: Second brand name
            
        Returns:
            Dictionary with brand comparison data
        """
        comparison_data = {
            'brand1': brand1,
            'brand2': brand2,
            'head_to_head': {},
            'brand1_stats': {},
            'brand2_stats': {},
            'overall_winner': None
        }
        
        brand1_wins = 0
        brand2_wins = 0
        
        for category, analysis in self.competitor_analysis.items():
            category_comparison = {'components': {}, 'winner': None}
            
            for component, data in analysis['performance_data'].items():
                brand_scores = data['brand_scores']
                
                if brand1 in brand_scores and brand2 in brand_scores:
                    score1 = brand_scores[brand1]
                    score2 = brand_scores[brand2]
                    
                    component_winner = brand1 if score1 > score2 else brand2 if score2 > score1 else 'Tie'
                    
                    category_comparison['components'][component] = {
                        brand1: score1,
                        brand2: score2,
                        'winner': component_winner
                    }
                    
                    if component_winner == brand1:
                        brand1_wins += 1
                    elif component_winner == brand2:
                        brand2_wins += 1
            
            if category_comparison['components']:
                category_winner = brand1 if brand1_wins > brand2_wins else brand2 if brand2_wins > brand1 else 'Tie'
                category_comparison['winner'] = category_winner
                comparison_data['head_to_head'][category] = category_comparison
        
        # Get overall brand statistics
        cross_analysis = self.generate_cross_category_analysis()
        brand_stats = cross_analysis['brand_statistics']
        
        comparison_data['brand1_stats'] = brand_stats.get(brand1, {})
        comparison_data['brand2_stats'] = brand_stats.get(brand2, {})
        comparison_data['overall_winner'] = brand1 if brand1_wins > brand2_wins else brand2 if brand2_wins > brand1 else 'Tie'
        
        return comparison_data

# Example usage
if __name__ == "__main__":
    # Initialize and process competitor intelligence
    intelligence = CompetitorIntelligence()
    analysis_results = intelligence.process_competitor_intelligence(
        input_file='component_sentiment_scores.json',
        output_file='competitor_analysis.json'
    )
    
    print(f"\n✅ Competitor intelligence analysis complete! Results saved to competitor_analysis.json")
    
    # Example brand comparison
    if len(analysis_results) > 0:
        # Get top two brands for comparison
        cross_analysis = intelligence.generate_cross_category_analysis()
        if cross_analysis['overall_ranking'] and len(cross_analysis['overall_ranking']) >= 2:
            brand1 = cross_analysis['overall_ranking'][0][0]
            brand2 = cross_analysis['overall_ranking'][1][0]
            
            print(f"\n🥊 HEAD-TO-HEAD COMPARISON: {brand1} vs {brand2}")
            comparison = intelligence.get_brand_comparison(brand1, brand2)
            print(f"Overall Winner: {comparison['overall_winner']}")
