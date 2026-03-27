import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import statistics
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExecutiveReport:
    """
    Generate executive-level competitive intelligence reports.
    Transform complex analysis data into clear, actionable insights for business leaders.
    """
    
    def __init__(self):
        self.competitor_analysis = {}
        self.review_intelligence = {}
        self.strategic_recommendations = {}
        self.executive_reports = {}
        
        # Executive summary templates
        self.report_templates = {
            'brand_category': """
============================================================
EXECUTIVE INTELLIGENCE ANALYSIS - {brand} {category}
============================================================

Market Position:
{market_position}

Products Analyzed: {products_analyzed}
Categories: {categories}

Top Priority:
{top_priority}

Critical Weaknesses:
{critical_weaknesses}

Competitive Advantages:
{competitive_advantages}

Strategic Recommendations:
{strategic_recommendations}

Market Share Opportunity:
{market_opportunity}

Risk Assessment:
{risk_assessment}

Investment Priority:
{investment_priority}

============================================================
""",
            'overall_market': """
============================================================
EXECUTIVE MARKET INTELLIGENCE SUMMARY
============================================================

Market Overview:
{market_overview}

Top Performing Brands:
{top_brands}

Key Market Trends:
{market_trends}

Critical Issues Across Market:
{critical_issues}

Strategic Market Opportunities:
{market_opportunities}

Investment Recommendations:
{investment_recommendations}

============================================================
"""
        }
    
    def load_competitor_analysis(self, competitor_file: str = 'competitor_analysis.json') -> None:
        """
        Load competitor analysis data.
        
        Args:
            competitor_file: Path to the competitor analysis JSON file
        """
        try:
            with open(competitor_file, 'r', encoding='utf-8') as f:
                self.competitor_analysis = json.load(f)
            logger.info(f"Successfully loaded competitor analysis from {competitor_file}")
        except Exception as e:
            logger.error(f"Error loading competitor analysis: {e}")
            raise
    
    def load_review_intelligence(self, review_file: str = 'review_intelligence.json') -> None:
        """
        Load review intelligence data.
        
        Args:
            review_file: Path to the review intelligence JSON file
        """
        try:
            with open(review_file, 'r', encoding='utf-8') as f:
                self.review_intelligence = json.load(f)
            logger.info(f"Successfully loaded review intelligence from {review_file}")
        except Exception as e:
            logger.error(f"Error loading review intelligence: {e}")
            raise
    
    def load_strategic_recommendations(self, strategy_file: str = 'strategic_recommendations.json') -> None:
        """
        Load strategic recommendations data.
        
        Args:
            strategy_file: Path to the strategic recommendations JSON file
        """
        try:
            with open(strategy_file, 'r', encoding='utf-8') as f:
                self.strategic_recommendations = json.load(f)
            logger.info(f"Successfully loaded strategic recommendations from {strategy_file}")
        except Exception as e:
            logger.error(f"Error loading strategic recommendations: {e}")
            raise
    
    def analyze_brand_market_position(self, brand: str, category: str) -> Dict[str, Any]:
        """
        Analyze market position for a specific brand in a category.
        
        Args:
            brand: Brand name
            category: Product category
            
        Returns:
            Market position analysis
        """
        category_analysis = self.competitor_analysis.get('category_analysis', {}).get(category, {})
        cross_analysis = self.competitor_analysis.get('cross_category_analysis', {})
        
        # Find brand ranking in category
        brand_wins = category_analysis.get('brand_wins', {})
        brand_rank = None
        total_brands = len(brand_wins)
        
        sorted_brands = sorted(brand_wins.items(), key=lambda x: x[1], reverse=True)
        for i, (brand_name, wins) in enumerate(sorted_brands, 1):
            if brand_name == brand:
                brand_rank = i
                break
        
        # Analyze component performance
        performance_data = category_analysis.get('performance_data', {})
        component_performance = {}
        
        for component, data in performance_data.items():
            brand_scores = data.get('brand_scores', {})
            if brand in brand_scores:
                component_performance[component] = {
                    'score': brand_scores[brand],
                    'rank': len([b for b in brand_scores.values() if b > brand_scores[brand]]) + 1,
                    'total_brands': len(brand_scores)
                }
        
        # Calculate competitive gaps
        competitive_gaps = {}
        for component, perf in component_performance.items():
            if perf['rank'] > 1:  # Not the leader
                top_score = max(brand_scores.values())
                gap_percentage = ((top_score - perf['score']) / top_score) * 100
                competitive_gaps[component] = gap_percentage
        
        # Calculate competitive advantages
        competitive_advantages = {}
        for component, perf in component_performance.items():
            if perf['rank'] == 1:  # Leader
                second_score = sorted(brand_scores.values(), reverse=True)[1] if len(brand_scores) > 1 else 0
                advantage_percentage = ((perf['score'] - second_score) / perf['score']) * 100 if perf['score'] > 0 else 0
                competitive_advantages[component] = advantage_percentage
        
        return {
            'brand': brand,
            'category': category,
            'overall_rank': brand_rank,
            'total_brands': total_brands,
            'component_performance': component_performance,
            'competitive_gaps': competitive_gaps,
            'competitive_advantages': competitive_advantages,
            'brand_wins': brand_wins.get(brand, 0)
        }
    
    def identify_critical_weaknesses(self, market_position: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify critical weaknesses for a brand.
        
        Args:
            market_position: Market position analysis
            
        Returns:
            List of critical weaknesses
        """
        weaknesses = []
        competitive_gaps = market_position.get('competitive_gaps', {})
        
        # Sort gaps by severity (largest gap first)
        sorted_gaps = sorted(competitive_gaps.items(), key=lambda x: x[1], reverse=True)
        
        for component, gap_percentage in sorted_gaps[:5]:  # Top 5 weaknesses
            weakness_level = "Critical" if gap_percentage > 50 else "Severe" if gap_percentage > 25 else "Moderate"
            
            weaknesses.append({
                'component': component,
                'gap_percentage': gap_percentage,
                'weakness_level': weakness_level,
                'impact': "High" if gap_percentage > 40 else "Medium" if gap_percentage > 20 else "Low"
            })
        
        return weaknesses
    
    def identify_competitive_advantages(self, market_position: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify competitive advantages for a brand.
        
        Args:
            market_position: Market position analysis
            
        Returns:
            List of competitive advantages
        """
        advantages = []
        competitive_adv = market_position.get('competitive_advantages', {})
        
        # Sort advantages by magnitude (largest advantage first)
        sorted_adv = sorted(competitive_adv.items(), key=lambda x: x[1], reverse=True)
        
        for component, advantage_percentage in sorted_adv[:5]:  # Top 5 advantages
            advantage_level = "Dominant" if advantage_percentage > 30 else "Strong" if advantage_percentage > 15 else "Moderate"
            
            advantages.append({
                'component': component,
                'advantage_percentage': advantage_percentage,
                'advantage_level': advantage_level,
                'strategic_value': "High" if advantage_percentage > 25 else "Medium" if advantage_percentage > 10 else "Low"
            })
        
        return advantages
    
    def generate_brand_priority_recommendations(self, brand: str, category: str, 
                                             market_position: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate priority recommendations for a brand.
        
        Args:
            brand: Brand name
            category: Product category
            market_position: Market position analysis
            
        Returns:
            Priority recommendations
        """
        weaknesses = self.identify_critical_weaknesses(market_position)
        advantages = self.identify_competitive_advantages(market_position)
        
        # Determine top priority
        if weaknesses:
            top_weakness = weaknesses[0]
            top_priority = f"Address {top_weakness['component']} performance gap ({top_weakness['gap_percentage']:.0f}% deficit vs competitors)"
        else:
            top_priority = f"Maintain {category} market leadership through continuous innovation"
        
        # Strategic recommendations
        strategic_recs = []
        
        # Address critical weaknesses
        for weakness in weaknesses[:3]:
            rec = f"Urgent: Improve {weakness['component']} performance to close {weakness['gap_percentage']:.0f}% competitive gap"
            strategic_recs.append(rec)
        
        # Leverage competitive advantages
        for advantage in advantages[:2]:
            rec = f"Strengthen {advantage['component']} advantage in marketing and product development"
            strategic_recs.append(rec)
        
        # Market opportunity assessment
        market_opportunity = "Moderate" if market_position.get('overall_rank', 5) <= 3 else "High" if market_position.get('overall_rank', 5) <= 5 else "Limited"
        
        # Risk assessment
        risk_factors = []
        if weaknesses:
            risk_factors.append(f"Market share loss due to {weaknesses[0]['component']} underperformance")
        if market_position.get('overall_rank', 5) > 3:
            risk_factors.append("Competitive pressure from top-performing brands")
        
        risk_level = "High" if len(risk_factors) > 1 else "Medium" if risk_factors else "Low"
        
        # Investment priority
        investment_priority = "Immediate" if weaknesses and weaknesses[0]['gap_percentage'] > 40 else "High" if weaknesses else "Medium"
        
        return {
            'top_priority': top_priority,
            'strategic_recommendations': strategic_recs,
            'market_opportunity': market_opportunity,
            'risk_assessment': {
                'level': risk_level,
                'factors': risk_factors
            },
            'investment_priority': investment_priority
        }
    
    def generate_brand_executive_report(self, brand: str, category: str) -> str:
        """
        Generate executive report for a specific brand and category.
        
        Args:
            brand: Brand name
            category: Product category
            
        Returns:
            Formatted executive report string
        """
        # Analyze market position
        market_position = self.analyze_brand_market_position(brand, category)
        
        # Generate recommendations
        recommendations = self.generate_brand_priority_recommendations(brand, category, market_position)
        
        # Format market position text
        overall_rank = market_position.get('overall_rank', 'Unknown')
        total_brands = market_position.get('total_brands', 'Unknown')
        brand_wins = market_position.get('brand_wins', 0)
        
        market_position_text = f"Ranked #{overall_rank} overall, "
        
        # Add strengths and weaknesses
        advantages = self.identify_competitive_advantages(market_position)
        weaknesses = self.identify_critical_weaknesses(market_position)
        
        if advantages and weaknesses:
            top_adv = advantages[0]['component']
            top_weak = weaknesses[0]['component']
            market_position_text += f"strong in {top_adv} but weak in {top_weak}."
        elif advantages:
            market_position_text += f"strong in {advantages[0]['component']}."
        elif weaknesses:
            market_position_text += f"weak in {weaknesses[0]['component']}."
        else:
            market_position_text += "balanced performance across components."
        
        # Format critical weaknesses
        critical_weaknesses_text = ""
        for weakness in weaknesses[:3]:
            component = weakness['component'].replace('_', ' ').title()
            gap = weakness['gap_percentage']
            
            # Find competitor to compare against
            performance_data = market_position.get('component_performance', {}).get(component, {})
            competitor_info = ""
            
            critical_weaknesses_text += f"{component}: {gap:.0f}% deficit vs competitors\n"
        
        # Format competitive advantages
        competitive_advantages_text = ""
        for advantage in advantages[:3]:
            component = advantage['component'].replace('_', ' ').title()
            advantage_pct = advantage['advantage_percentage']
            competitive_advantages_text += f"{component}: {advantage_pct:.0f}% superiority over competitors\n"
        
        # Format strategic recommendations
        strategic_recs_text = ""
        for i, rec in enumerate(recommendations['strategic_recommendations'][:3], 1):
            strategic_recs_text += f"{i}. {rec}\n"
        
        # Get products analyzed count
        category_analysis = self.competitor_analysis.get('category_analysis', {}).get(category, {})
        products_analyzed = len(category_analysis.get('performance_data', {}))
        
        # Format report using template
        report = self.report_templates['brand_category'].format(
            brand=brand.upper(),
            category=category.upper(),
            market_position=market_position_text,
            products_analyzed=products_analyzed,
            categories=category,
            top_priority=recommendations['top_priority'],
            critical_weaknesses=critical_weaknesses_text.strip(),
            competitive_advantages=competitive_advantages_text.strip(),
            strategic_recommendations=strategic_recs_text.strip(),
            market_opportunity=recommendations['market_opportunity'],
            risk_assessment=f"{recommendations['risk_assessment']['level']} risk - {', '.join(recommendations['risk_assessment']['factors'])}" if recommendations['risk_assessment']['factors'] else f"{recommendations['risk_assessment']['level']} risk",
            investment_priority=recommendations['investment_priority']
        )
        
        return report
    
    def generate_overall_market_report(self) -> str:
        """
        Generate overall market intelligence report.
        
        Returns:
            Formatted overall market report string
        """
        cross_analysis = self.competitor_analysis.get('cross_category_analysis', {})
        overall_ranking = cross_analysis.get('overall_ranking', [])
        
        # Market overview
        total_brands = len(overall_ranking)
        total_categories = len(self.competitor_analysis.get('category_analysis', {}))
        
        market_overview = f"Analyzed {total_brands} brands across {total_categories} product categories. "
        
        # Identify market leaders
        if overall_ranking:
            top_brand = overall_ranking[0]
            market_overview += f"{top_brand[0]} leads with {top_brand[1]['total_wins']} component wins. "
        
        # Market concentration
        if len(overall_ranking) >= 3:
            top_3_wins = sum(brand[1]['total_wins'] for brand in overall_ranking[:3])
            total_wins = sum(brand[1]['total_wins'] for brand in overall_ranking)
            concentration = (top_3_wins / total_wins) * 100
            market_overview += f"Top 3 brands control {concentration:.0f}% of component wins. "
        
        # Top performing brands
        top_brands_text = ""
        for i, (brand, stats) in enumerate(overall_ranking[:5], 1):
            categories = ', '.join(stats.get('categories', [])[:2])
            top_brands_text += f"{i}. {brand}: {stats['total_wins']} wins in {categories}\n"
        
        # Key market trends
        market_trends = []
        
        # Analyze component performance across market
        component_performance = defaultdict(list)
        category_analysis = self.competitor_analysis.get('category_analysis', {})
        
        for category, analysis in category_analysis.items():
            performance_data = analysis.get('performance_data', {})
            for component, data in performance_data.items():
                brand_scores = data.get('brand_scores', {})
                if brand_scores:
                    avg_score = statistics.mean(brand_scores.values())
                    component_performance[component].append(avg_score)
        
        # Find best and worst performing components
        component_averages = {}
        for component, scores in component_performance.items():
            if scores:
                component_averages[component] = statistics.mean(scores)
        
        if component_averages:
            best_component = max(component_averages.items(), key=lambda x: x[1])
            worst_component = min(component_averages.items(), key=lambda x: x[1])
            
            market_trends.append(f"Strongest market component: {best_component[0]} ({best_component[1]:.2f} avg score)")
            market_trends.append(f"Weakest market component: {worst_component[0]} ({worst_component[1]:.2f} avg score)")
        
        # Critical issues across market
        critical_issues = []
        review_intel = self.review_intelligence.get('component_breakdown', {})
        
        # Find most complained about components
        if review_intel:
            sorted_issues = sorted(review_intel.items(), 
                                key=lambda x: x[1].get('severity_score', 0), 
                                reverse=True)
            
            for component, data in sorted_issues[:3]:
                severity = data.get('severity_score', 0)
                review_count = data.get('review_count', 0)
                critical_issues.append(f"{component.title()}: {review_count} complaints, {severity:.1f} severity")
        
        critical_issues_text = '\n'.join(f"• {issue}" for issue in critical_issues)
        
        # Strategic market opportunities
        market_opportunities = []
        
        # Find components with high complaint rates but low competitive scores
        for component, data in review_intel.items():
            if component in component_averages:
                complaint_level = data.get('severity_score', 0)
                market_score = component_averages[component]
                
                if complaint_level > 30 and market_score < 0.3:
                    market_opportunities.append(f"Improve {component} - high customer dissatisfaction, low market performance")
        
        market_opportunities_text = '\n'.join(f"• {opp}" for opp in market_opportunities[:3])
        
        # Investment recommendations
        investment_recs = []
        
        # Based on strategic recommendations
        strategy_data = self.strategic_recommendations.get('strategic_summary', {})
        top_recs = strategy_data.get('top_recommendations', [])
        
        for rec in top_recs[:3]:
            component = rec.get('component', 'unknown')
            impact = rec.get('impact_score', 0)
            investment_recs.append(f"Priority investment in {component} (impact score: {impact})")
        
        investment_recs_text = '\n'.join(f"• {rec}" for rec in investment_recs)
        
        # Format report using template
        report = self.report_templates['overall_market'].format(
            market_overview=market_overview,
            top_brands=top_brands_text.strip(),
            market_trends='\n'.join(f"• {trend}" for trend in market_trends),
            critical_issues=critical_issues_text,
            market_opportunities=market_opportunities_text,
            investment_recommendations=investment_recs_text
        )
        
        return report
    
    def save_executive_reports(self, output_file: str = 'executive_reports.json') -> None:
        """
        Save executive reports as JSON file.
        
        Args:
            output_file: Output file name
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.executive_reports, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved executive reports to {output_file}")
        except Exception as e:
            logger.error(f"Error saving executive reports: {e}")
            raise
    
    def process_executive_reports(self, competitor_file: str = 'competitor_analysis.json',
                                review_file: str = 'review_intelligence.json',
                                strategy_file: str = 'strategic_recommendations.json',
                                output_file: str = 'executive_reports.json') -> Dict[str, Any]:
        """
        Complete pipeline to process executive reports.
        
        Args:
            competitor_file: Input competitor analysis JSON file
            review_file: Input review intelligence JSON file
            strategy_file: Input strategic recommendations JSON file
            output_file: Output executive reports JSON file
            
        Returns:
            Complete executive reports
        """
        try:
            # Load input data
            self.load_competitor_analysis(competitor_file)
            self.load_review_intelligence(review_file)
            self.load_strategic_recommendations(strategy_file)
            
            # Generate reports
            reports = {}
            
            # Generate overall market report
            reports['overall_market'] = self.generate_overall_market_report()
            
            # Generate brand-specific reports for top brands
            cross_analysis = self.competitor_analysis.get('cross_category_analysis', {})
            overall_ranking = cross_analysis.get('overall_ranking', [])
            
            # Generate reports for top 5 brands in their best categories
            for brand, brand_stats in overall_ranking[:5]:
                categories = brand_stats.get('categories', [])
                if categories:
                    # Find brand's best performing category
                    best_category = None
                    best_wins = 0
                    
                    category_analysis = self.competitor_analysis.get('category_analysis', {})
                    for category in categories:
                        if category in category_analysis:
                            brand_wins = category_analysis[category].get('brand_wins', {}).get(brand, 0)
                            if brand_wins > best_wins:
                                best_wins = brand_wins
                                best_category = category
                    
                    if best_category:
                        report_key = f"{brand.lower()}_{best_category.lower()}"
                        reports[report_key] = self.generate_brand_executive_report(brand, best_category)
            
            self.executive_reports = reports
            
            # Save reports
            self.save_executive_reports(output_file)
            
            # Print summary
            self._print_summary()
            
            logger.info("Executive reports processing completed successfully!")
            return self.executive_reports
            
        except Exception as e:
            logger.error(f"Error in executive reports pipeline: {e}")
            raise
    
    def _print_summary(self) -> None:
        """Print summary of executive reports."""
        print("\n" + "="*60)
        print("📊 EXECUTIVE REPORTS SUMMARY")
        print("="*60)
        
        total_reports = len(self.executive_reports)
        print(f"\n📈 Generated Reports: {total_reports}")
        
        # Show overall market summary
        if 'overall_market' in self.executive_reports:
            print(f"\n🌍 Overall Market Report Available")
        
        # Show brand-specific reports
        brand_reports = {k: v for k, v in self.executive_reports.items() if k != 'overall_market'}
        
        print(f"\n🏢 Brand-Specific Reports:")
        for report_key, report_content in brand_reports.items():
            # Extract brand and category from key
            parts = report_key.split('_')
            brand = parts[0].title()
            category = ' '.join(parts[1:]).title()
            
            print(f"   📋 {brand} {category}")
        
        print(f"\n💾 Reports saved to: executive_reports.json")
        print("="*60)
    
    def get_brand_report(self, brand: str, category: str) -> Optional[str]:
        """
        Get executive report for a specific brand and category.
        
        Args:
            brand: Brand name
            category: Product category
            
        Returns:
            Executive report string or None if not found
        """
        report_key = f"{brand.lower()}_{category.lower()}"
        return self.executive_reports.get(report_key)
    
    def get_overall_market_report(self) -> Optional[str]:
        """
        Get overall market executive report.
        
        Returns:
            Overall market report string or None if not found
        """
        return self.executive_reports.get('overall_market')

# Example usage
if __name__ == "__main__":
    # Initialize and process executive reports
    executive = ExecutiveReport()
    reports = executive.process_executive_reports(
        competitor_file='competitor_analysis.json',
        review_file='review_intelligence.json',
        strategy_file='strategic_recommendations.json',
        output_file='executive_reports.json'
    )
    
    print(f"\n✅ Executive reports complete! Results saved to executive_reports.json")
    
    # Show sample reports
    print(f"\n📊 SAMPLE EXECUTIVE REPORTS:")
    
    # Overall market report
    overall_report = executive.get_overall_market_report()
    if overall_report:
        print(f"\n{overall_report}")
    
    # Brand-specific report (example)
    sony_report = executive.get_brand_report('Sony', 'Headphones')
    if sony_report:
        print(f"\n{sony_report}")
