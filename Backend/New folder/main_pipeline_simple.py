import json
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import locale
    try:
        # Try to set UTF-8 encoding
        os.system('chcp 65001 >nul 2>&1')
    except:
        pass

# Import all pipeline modules
from dataset_loader import DatasetLoader
from category_filter import CategoryFilter
from component_extractor import ComponentExtractor
from sentiment_engine import SentimentEngine
from competitor_intelligence import CompetitorIntelligence
from review_intelligence import ReviewIntelligence
from strategy_engine import StrategyEngine
from executive_report import ExecutiveReport

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MainPipeline:
    """
    Main pipeline orchestrator for the complete competitive intelligence system.
    Runs all analysis steps and produces formatted terminal output.
    """
    
    def __init__(self, config_file: str = 'pipeline_config.json'):
        """
        Initialize the main pipeline.
        
        Args:
            config_file: Configuration file path
        """
        self.config = self._load_config(config_file)
        self.results = {}
        self.pipeline_start_time = datetime.now()
        
        # Initialize all modules
        self.dataset_loader = DatasetLoader()
        self.category_filter = CategoryFilter()
        self.component_extractor = ComponentExtractor()
        self.sentiment_engine = SentimentEngine()
        self.competitor_intelligence = CompetitorIntelligence()
        self.review_intelligence = ReviewIntelligence()
        self.strategy_engine = StrategyEngine()
        self.executive_report = ExecutiveReport()
        
        logger.info("Main pipeline initialized")
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load pipeline configuration."""
        default_config = {
            "input_files": {
                "amazon_electronics_master_dataset": "amazon_electronics_master_dataset.csv",
                "amazon_electronics_reviews_cleaned": "amazon_electronics_reviews_cleaned.csv",
                "amazon_reviews_cleaned_4M": "amazon_reviews_cleaned_4M.csv"
            },
            "output_files": {
                "processed_data": "processed_product_reviews.json",
                "category_products": "category_products.json",
                "component_reviews": "component_reviews.json",
                "sentiment_scores": "component_sentiment_scores.json",
                "competitor_analysis": "competitor_analysis.json",
                "review_intelligence": "review_intelligence.json",
                "strategic_recommendations": "strategic_recommendations.json",
                "executive_reports": "executive_reports.json"
            },
            "parameters": {
                "min_brands": 2,
                "max_brands": 5,
                "max_products_per_brand": 3,
                "min_reviews_per_component": 5,
                "sentiment_model": "auto",
                "max_reviews_per_product": 20
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # Merge with defaults
                for key, value in user_config.items():
                    if key in default_config:
                        if isinstance(value, dict) and isinstance(default_config[key], dict):
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
            return default_config
        except Exception as e:
            logger.warning(f"Could not load config file {config_file}: {e}")
            return default_config
    
    def run_complete_pipeline(self) -> Dict[str, Any]:
        """
        Run the complete competitive intelligence pipeline.
        
        Returns:
            Complete pipeline results
        """
        print("\n" + "="*80)
        print("MULTI CATEGORY PRODUCT INTELLIGENCE PLATFORM")
        print("="*80)
        
        try:
            # Step 1: Load datasets
            self._step_1_load_datasets()
            
            # Step 2: Filter categories
            self._step_2_filter_categories()
            
            # Step 3: Extract components
            self._step_3_extract_components()
            
            # Step 4: Run sentiment analysis
            self._step_4_sentiment_analysis()
            
            # Step 5: Generate competitor comparison
            self._step_5_competitor_analysis()
            
            # Step 6: Identify review issues
            self._step_6_review_intelligence()
            
            # Step 7: Generate strategy suggestions
            self._step_7_strategy_engine()
            
            # Step 8: Produce executive report
            self._step_8_executive_report()
            
            # Generate multi-category summary
            self._generate_multi_category_summary()
            
            # Display final summary
            self._display_final_summary()
            
            return self.results
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            print(f"\n[X] Pipeline failed: {e}")
            raise
    
    def _step_1_load_datasets(self):
        """Step 1: Load and process datasets."""
        print(f"\n[STEP 1] LOADING DATASETS")
        print("-" * 50)
        
        try:
            # Check if input files exist
            input_files = self.config["input_files"]
            missing_files = []
            
            for file_key, file_path in input_files.items():
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            if missing_files:
                print(f"[!] Warning: Missing input files: {missing_files}")
                print("   Using existing processed data if available...")
                
                # Try to load existing processed data
                processed_file = self.config["output_files"]["processed_data"]
                if os.path.exists(processed_file):
                    print(f"[+] Using existing processed data: {processed_file}")
                    with open(processed_file, 'r', encoding='utf-8') as f:
                        self.results["processed_data"] = json.load(f)
                else:
                    print(f"[!] No processed data found. Please provide input files.")
                    return
            else:
                print(f"[*] Loading datasets...")
                processed_data = self.dataset_loader.process_all_datasets(input_files)
                self.results["processed_data"] = processed_data
                print(f"[+] Datasets loaded successfully")
        
        except Exception as e:
            logger.error(f"Error loading datasets: {e}")
            print(f"[!] Error loading datasets: {e}")
            raise
    
    def _step_2_filter_categories(self):
        """Step 2: Filter categories."""
        print(f"\n[STEP 2] FILTERING CATEGORIES")
        print("-" * 50)
        
        try:
            params = self.config["parameters"]
            output_file = self.config["output_files"]["category_products"]
            
            print(f"[*] Filtering categories...")
            print(f"   Min brands per category: {params['min_brands']}")
            print(f"   Max brands per category: {params['max_brands']}")
            print(f"   Max products per brand: {params['max_products_per_brand']}")
            
            category_data = self.category_filter.process_categories(
                input_file=self.config["output_files"]["processed_data"],
                output_file=output_file,
                min_brands=params["min_brands"],
                max_brands=params["max_brands"],
                max_products_per_brand=params["max_products_per_brand"]
            )
            
            self.results["category_data"] = category_data
            
            # Display category summary
            categories = list(category_data.keys())
            print(f"[+] Categories filtered: {len(categories)}")
            print(f"   Categories found: {', '.join(categories)}")
            
        except Exception as e:
            logger.error(f"Error filtering categories: {e}")
            print(f"[!] Error filtering categories: {e}")
            raise
    
    def _step_3_extract_components(self):
        """Step 3: Extract components."""
        print(f"\n[STEP 3] EXTRACTING COMPONENTS")
        print("-" * 50)
        
        try:
            params = self.config["parameters"]
            output_file = self.config["output_files"]["component_reviews"]
            
            print(f"[*] Extracting components from reviews...")
            print(f"   Min reviews per component: {params['min_reviews_per_component']}")
            
            component_data = self.component_extractor.process_components(
                input_file=self.config["output_files"]["category_products"],
                output_file=output_file,
                min_reviews_per_component=params["min_reviews_per_component"],
                enhance_detection=True
            )
            
            self.results["component_data"] = component_data
            
            # Display component summary
            total_components = 0
            for category, data in component_data.items():
                components = list(data.keys())
                total_components += len(components)
                print(f"   {category}: {len(components)} components")
            
            print(f"[+] Components extracted: {total_components} total")
            
        except Exception as e:
            logger.error(f"Error extracting components: {e}")
            print(f"[!] Error extracting components: {e}")
            raise
    
    def _step_4_sentiment_analysis(self):
        """Step 4: Run sentiment analysis."""
        print(f"\n[STEP 4] SENTIMENT ANALYSIS")
        print("-" * 50)
        
        try:
            params = self.config["parameters"]
            output_file = self.config["output_files"]["sentiment_scores"]
            
            print(f"[*] Analyzing sentiment for components...")
            print(f"   Model: {params['sentiment_model']}")
            
            sentiment_data = self.sentiment_engine.process_sentiments(
                input_file=self.config["output_files"]["component_reviews"],
                output_file=output_file,
                model_type=params["sentiment_model"],
                enhance_analysis=True
            )
            
            self.results["sentiment_data"] = sentiment_data
            
            # Display sentiment summary
            total_analyses = 0
            for category, data in sentiment_data.items():
                analyses = len(data)
                total_analyses += analyses
                print(f"   {category}: {analyses} component analyses")
            
            print(f"[+] Sentiment analysis completed: {total_analyses} total")
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            print(f"[!] Error in sentiment analysis: {e}")
            raise
    
    def _step_5_competitor_analysis(self):
        """Step 5: Generate competitor comparison."""
        print(f"\n[STEP 5] COMPETITOR ANALYSIS")
        print("-" * 50)
        
        try:
            output_file = self.config["output_files"]["competitor_analysis"]
            
            print(f"[*] Generating competitor intelligence...")
            
            competitor_data = self.competitor_intelligence.process_competitor_intelligence(
                input_file=self.config["output_files"]["sentiment_scores"],
                output_file=output_file
            )
            
            self.results["competitor_data"] = competitor_data
            
            # Display performance tables for each category
            category_analysis = competitor_data.get("category_analysis", {})
            
            for category, analysis in category_analysis.items():
                print(f"\n[*] ANALYZING CATEGORY: {category.upper()}")
                
                # Get performance table
                performance_table = self.competitor_intelligence.get_performance_table(category)
                if performance_table:
                    print(f"\n{category.upper()} PERFORMANCE TABLE")
                    print(performance_table)
                
                # Show top competitors
                brand_wins = analysis.get("brand_wins", {})
                if brand_wins:
                    sorted_brands = sorted(brand_wins.items(), key=lambda x: x[1], reverse=True)
                    top_2_brands = sorted_brands[:2]
                    
                    if len(top_2_brands) >= 2:
                        brand1, wins1 = top_2_brands[0]
                        brand2, wins2 = top_2_brands[1]
                        print(f"\n{brand1} vs {brand2}")
            
            print(f"\n[+] Competitor analysis completed")
            
        except Exception as e:
            logger.error(f"Error in competitor analysis: {e}")
            print(f"[!] Error in competitor analysis: {e}")
            raise
    
    def _step_6_review_intelligence(self):
        """Step 6: Identify review issues."""
        print(f"\n[STEP 6] REVIEW INTELLIGENCE")
        print("-" * 50)
        
        try:
            output_file = self.config["output_files"]["review_intelligence"]
            
            print(f"[*] Analyzing customer complaints and issues...")
            
            review_data = self.review_intelligence.process_review_intelligence(
                component_file=self.config["output_files"]["component_reviews"],
                sentiment_file=self.config["output_files"]["sentiment_scores"],
                output_file=output_file
            )
            
            self.results["review_data"] = review_data
            
            # Display top issues
            top_issues = review_data.get("top_customer_issues", [])
            if top_issues:
                print(f"\n[!] TOP CUSTOMER ISSUES:")
                for i, issue in enumerate(top_issues[:5], 1):
                    print(f"   {i}. {issue['issue']} ({issue['component']})")
                    print(f"      Frequency: {issue['frequency']} | Products: {issue['products_affected']}")
            
            # Display component breakdown
            component_breakdown = review_data.get("component_breakdown", {})
            if component_breakdown:
                print(f"\n[*] COMPONENT ISSUE BREAKDOWN:")
                for component, data in list(component_breakdown.items())[:3]:
                    severity = data.get("severity_score", 0)
                    review_count = data.get("review_count", 0)
                    print(f"   {component.title()}: Severity {severity:.1f} | {review_count} reviews")
            
            print(f"\n[+] Review intelligence completed")
            
        except Exception as e:
            logger.error(f"Error in review intelligence: {e}")
            print(f"[!] Error in review intelligence: {e}")
            raise
    
    def _step_7_strategy_engine(self):
        """Step 7: Generate strategy suggestions."""
        print(f"\n[STEP 7] STRATEGY ENGINE")
        print("-" * 50)
        
        try:
            output_file = self.config["output_files"]["strategic_recommendations"]
            
            print(f"[*] Generating strategic recommendations...")
            
            strategy_data = self.strategy_engine.process_strategy_engine(
                competitor_file=self.config["output_files"]["competitor_analysis"],
                review_file=self.config["output_files"]["review_intelligence"],
                output_file=output_file
            )
            
            self.results["strategy_data"] = strategy_data
            
            # Display top recommendations
            summary = strategy_data.get("strategic_summary", {})
            top_recommendations = summary.get("top_recommendations", [])
            
            if top_recommendations:
                print(f"\n[+] TOP STRATEGIC RECOMMENDATIONS:")
                for i, rec in enumerate(top_recommendations[:5], 1):
                    print(f"   {i}. {rec['key_recommendation']}")
                    print(f"      Component: {rec['component']} | Priority: {rec['priority']}")
                    print(f"      Impact Score: {rec['impact_score']} | Products: {rec['affected_products']}")
            
            # Display priority breakdown
            priority_breakdown = summary.get("priority_breakdown", {})
            if priority_breakdown:
                print(f"\n[*] PRIORITY BREAKDOWN:")
                for priority, count in priority_breakdown.items():
                    print(f"   {priority.title()}: {count} recommendations")
            
            print(f"\n[+] Strategy engine completed")
            
        except Exception as e:
            logger.error(f"Error in strategy engine: {e}")
            print(f"[!] Error in strategy engine: {e}")
            raise
    
    def _step_8_executive_report(self):
        """Step 8: Produce executive report."""
        print(f"\n[STEP 8] EXECUTIVE REPORT")
        print("-" * 50)
        
        try:
            output_file = self.config["output_files"]["executive_reports"]
            
            print(f"[*] Generating executive-level reports...")
            
            executive_data = self.executive_report.process_executive_reports(
                competitor_file=self.config["output_files"]["competitor_analysis"],
                review_file=self.config["output_files"]["review_intelligence"],
                strategy_file=self.config["output_files"]["strategic_recommendations"],
                output_file=output_file
            )
            
            self.results["executive_data"] = executive_data
            
            # Display sample executive reports
            print(f"\n[*] EXECUTIVE INTELLIGENCE REPORT")
            
            # Overall market report
            overall_report = self.executive_report.get_overall_market_report()
            if overall_report:
                # Show first few lines
                lines = overall_report.split('\n')
                for line in lines[:10]:
                    if line.strip():
                        print(f"   {line}")
                print("   ...")
            
            # Brand-specific reports
            brand_reports = {k: v for k, v in executive_data.items() if k != 'overall_market'}
            
            for i, (report_key, report_content) in enumerate(list(brand_reports.items())[:2], 1):
                parts = report_key.split('_')
                brand = parts[0].title()
                category = ' '.join(parts[1:]).title()
                
                print(f"\n[*] {brand} {category} Executive Summary:")
                lines = report_content.split('\n')
                for line in lines:
                    if line.startswith('Market Position:') or line.startswith('Top Priority:'):
                        print(f"   {line}")
                        if line.startswith('Top Priority:'):
                            break
            
            print(f"\n[+] Executive reports completed")
            
        except Exception as e:
            logger.error(f"Error generating executive reports: {e}")
            print(f"[!] Error generating executive reports: {e}")
            raise
    
    def _generate_multi_category_summary(self):
        """Generate multi-category summary."""
        print(f"\n" + "="*80)
        print("MULTI CATEGORY SUMMARY")
        print("="*80)
        
        try:
            # Get all categories analyzed
            category_data = self.results.get("category_data", {})
            categories = list(category_data.keys())
            
            print(f"\n[*] CATEGORIES ANALYZED: {len(categories)}")
            for category in categories:
                brands = list(category_data[category].keys())
                print(f"   {category.title()}: {len(brands)} brands ({', '.join(brands)})")
            
            # Overall sentiment trends
            sentiment_data = self.results.get("sentiment_data", {})
            if sentiment_data:
                print(f"\n[*] SENTIMENT OVERVIEW:")
                for category, data in sentiment_data.items():
                    if data:
                        # Calculate average sentiment across all components
                        all_scores = []
                        for component, comp_data in data.items():
                            if isinstance(comp_data, dict) and 'average_sentiment' in comp_data:
                                all_scores.append(comp_data['average_sentiment'])
                        
                        if all_scores:
                            avg_sentiment = sum(all_scores) / len(all_scores)
                            print(f"   {category.title()}: {avg_sentiment:.3f} avg sentiment")
            
            # Top competitors across all categories
            competitor_data = self.results.get("competitor_data", {})
            cross_analysis = competitor_data.get("cross_category_analysis", {})
            overall_ranking = cross_analysis.get("overall_ranking", [])
            
            if overall_ranking:
                print(f"\n[*] OVERALL MARKET LEADERS:")
                for i, (brand, stats) in enumerate(overall_ranking[:5], 1):
                    categories = stats.get("categories", [])
                    print(f"   {i}. {brand}: {stats['total_wins']} component wins")
                    print(f"      Categories: {', '.join(categories[:2])}")
            
            # Critical issues across market
            review_data = self.results.get("review_data", {})
            top_issues = review_data.get("top_customer_issues", [])
            
            if top_issues:
                print(f"\n[!] MARKET-WIDE CRITICAL ISSUES:")
                for i, issue in enumerate(top_issues[:3], 1):
                    print(f"   {i}. {issue['issue']} ({issue['component']})")
                    print(f"      Affects {issue['products_affected']} products")
            
            # Strategic priorities
            strategy_data = self.results.get("strategy_data", {})
            summary = strategy_data.get("strategic_summary", {})
            priority_breakdown = summary.get("priority_breakdown", {})
            
            if priority_breakdown:
                print(f"\n[*] STRATEGIC PRIORITIES:")
                total_recs = sum(priority_breakdown.values())
                for priority, count in priority_breakdown.items():
                    percentage = (count / total_recs) * 100 if total_recs > 0 else 0
                    print(f"   {priority.title()}: {count} recommendations ({percentage:.1f}%)")
            
        except Exception as e:
            logger.error(f"Error generating multi-category summary: {e}")
            print(f"[!] Error generating summary: {e}")
    
    def _display_final_summary(self):
        """Display final pipeline summary."""
        pipeline_end_time = datetime.now()
        duration = pipeline_end_time - self.pipeline_start_time
        
        print(f"\n" + "="*80)
        print("PIPELINE EXECUTION SUMMARY")
        print("="*80)
        
        print(f"\n[*] Execution Time: {duration.total_seconds():.2f} seconds")
        print(f"[*] Started: {self.pipeline_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[*] Completed: {pipeline_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n[*] OUTPUT FILES GENERATED:")
        output_files = self.config["output_files"]
        for file_key, file_path in output_files.items():
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"   [+] {file_key}: {file_path} ({size:,} bytes)")
            else:
                print(f"   [-] {file_key}: {file_path} (not found)")
        
        print(f"\n[+] PIPELINE STATUS: COMPLETED SUCCESSFULLY")
        print("="*80)
    
    def get_results(self) -> Dict[str, Any]:
        """Get complete pipeline results."""
        return self.results

# Main execution function
def main():
    """Main function to run the complete pipeline."""
    try:
        # Initialize and run pipeline
        pipeline = MainPipeline()
        results = pipeline.run_complete_pipeline()
        
        print(f"\n[+] Competitive intelligence pipeline completed successfully!")
        print(f"[*] Results available in pipeline.results dictionary")
        
        return results
        
    except KeyboardInterrupt:
        print(f"\n[!] Pipeline interrupted by user")
        return None
    except Exception as e:
        print(f"\n[!] Pipeline failed: {e}")
        logger.error(f"Pipeline failed: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Run the complete pipeline
    results = main()
    
    if results:
        print(f"\n[*] Next steps:")
        print(f"   • Review executive reports for strategic insights")
        print(f"   • Analyze competitor performance tables")
        print(f"   • Review strategic recommendations")
        print(f"   • Consider web scraping for fresh data")
    else:
        print(f"\n[*] Troubleshooting:")
        print(f"   • Check input files exist and are properly formatted")
        print(f"   • Verify all dependencies are installed")
        print(f"   • Review error logs for specific issues")
