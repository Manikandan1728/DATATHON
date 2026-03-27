import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StrategyEngine:
    """
    Generate product improvement suggestions based on competitive analysis and customer feedback.
    Combine competitor intelligence and review intelligence to create actionable strategic recommendations.
    """
    
    def __init__(self):
        self.competitor_analysis = {}
        self.review_intelligence = {}
        self.strategic_recommendations = {}
        
        # Component-specific improvement strategies
        self.improvement_strategies = {
            'battery': {
                'high_priority': [
                    "Implement advanced battery optimization algorithms",
                    "Upgrade to higher capacity battery cells",
                    "Integrate fast charging technology",
                    "Develop power-saving modes for intensive usage"
                ],
                'medium_priority': [
                    "Improve battery health monitoring and reporting",
                    "Optimize background app management",
                    "Enhance wireless charging efficiency",
                    "Implement adaptive battery usage patterns"
                ],
                'low_priority': [
                    "Add battery usage analytics dashboard",
                    "Provide battery care tips in user interface",
                    "Optimize charging cable design",
                    "Improve battery indicator accuracy"
                ]
            },
            'sound': {
                'high_priority': [
                    "Upgrade audio drivers and sound processing chips",
                    "Implement advanced noise cancellation technology",
                    "Enhance speaker and microphone hardware quality",
                    "Develop AI-powered audio optimization"
                ],
                'medium_priority': [
                    "Improve audio equalization and customization options",
                    "Enhance bluetooth audio codec support",
                    "Optimize audio for different use cases",
                    "Improve audio latency and synchronization"
                ],
                'low_priority': [
                    "Add audio presets for different genres",
                    "Improve audio recording quality",
                    "Enhance audio accessibility features",
                    "Optimize audio compression algorithms"
                ]
            },
            'camera': {
                'high_priority': [
                    "Upgrade camera sensor and lens quality",
                    "Implement advanced image processing algorithms",
                    "Enhance low-light photography capabilities",
                    "Improve optical image stabilization"
                ],
                'medium_priority': [
                    "Develop AI-powered scene recognition",
                    "Improve camera autofocus speed and accuracy",
                    "Enhance video recording capabilities",
                    "Optimize camera software interface"
                ],
                'low_priority': [
                    "Add more camera modes and filters",
                    "Improve camera app user experience",
                    "Enhance photo editing capabilities",
                    "Optimize camera startup speed"
                ]
            },
            'display': {
                'high_priority': [
                    "Upgrade to higher resolution and brightness panels",
                    "Implement advanced display calibration",
                    "Enhance touch responsiveness and accuracy",
                    "Improve display durability and protection"
                ],
                'medium_priority': [
                    "Optimize display power efficiency",
                    "Enhance color accuracy and gamut",
                    "Improve display refresh rate technology",
                    "Reduce display bezels and improve design"
                ],
                'low_priority': [
                    "Add more display customization options",
                    "Improve display accessibility features",
                    "Enhance always-on display functionality",
                    "Optimize display for outdoor visibility"
                ]
            },
            'performance': {
                'high_priority': [
                    "Upgrade processor and memory configuration",
                    "Implement advanced thermal management system",
                    "Optimize operating system performance",
                    "Enhance memory management and multitasking"
                ],
                'medium_priority': [
                    "Improve software optimization and bug fixes",
                    "Enhance app compatibility and performance",
                    "Optimize startup and shutdown times",
                    "Implement performance monitoring tools"
                ],
                'low_priority': [
                    "Add performance customization options",
                    "Improve system maintenance features",
                    "Enhance storage management tools",
                    "Optimize background processing"
                ]
            },
            'build_quality': {
                'high_priority': [
                    "Use premium materials for construction",
                    "Improve manufacturing quality control",
                    "Enhance structural integrity and durability",
                    "Implement better water and dust resistance"
                ],
                'medium_priority': [
                    "Improve ergonomics and user comfort",
                    "Enhance finish and surface treatment",
                    "Optimize weight distribution and balance",
                    "Improve button and port durability"
                ],
                'low_priority': [
                    "Add more color and finish options",
                    "Improve packaging and unboxing experience",
                    "Enhance accessory quality",
                    "Optimize assembly and repairability"
                ]
            },
            'comfort': {
                'high_priority': [
                    "Redesign ergonomics for extended use comfort",
                    "Use lightweight and comfortable materials",
                    "Improve weight distribution and balance",
                    "Enhance adjustability and fit options"
                ],
                'medium_priority': [
                    "Improve padding and cushioning materials",
                    "Enhance ventilation and heat dissipation",
                    "Optimize size and proportions",
                    "Improve grip and handling"
                ],
                'low_priority': [
                    "Add more size and fit options",
                    "Improve accessory comfort",
                    "Enhance cleaning and maintenance",
                    "Optimize for different user types"
                ]
            },
            'connectivity': {
                'high_priority': [
                    "Upgrade to latest wireless standards",
                    "Improve antenna design and signal strength",
                    "Enhance connection stability and reliability",
                    "Implement advanced pairing and connection management"
                ],
                'medium_priority': [
                    "Improve connection range and speed",
                    "Enhance multi-device connectivity",
                    "Optimize connection management software",
                    "Improve connection troubleshooting tools"
                ],
                'low_priority': [
                    "Add more connectivity options",
                    "Improve connection customization",
                    "Enhance connection monitoring",
                    "Optimize connection power usage"
                ]
            },
            'software': {
                'high_priority': [
                    "Fix critical bugs and stability issues",
                    "Improve user interface and experience",
                    "Enhance app compatibility and performance",
                    "Implement regular security updates"
                ],
                'medium_priority': [
                    "Add new features and functionality",
                    "Improve system optimization and speed",
                    "Enhance customization options",
                    "Improve documentation and help resources"
                ],
                'low_priority': [
                    "Enhance accessibility features",
                    "Improve backup and restore functionality",
                    "Add more customization themes",
                    "Optimize system maintenance tools"
                ]
            },
            'price': {
                'high_priority': [
                    "Reassess pricing strategy and market positioning",
                    "Improve value proposition through features",
                    "Consider competitive pricing adjustments",
                    "Enhance perceived value through quality"
                ],
                'medium_priority': [
                    "Develop tiered product offerings",
                    "Improve cost efficiency in production",
                    "Enhance marketing and value communication",
                    "Consider promotional and bundling strategies"
                ],
                'low_priority': [
                    "Optimize distribution channels",
                    "Improve after-sales service value",
                    "Enhance customer support experience",
                    "Develop loyalty and retention programs"
                ]
            }
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
            
            # Validate structure
            if 'category_analysis' not in self.competitor_analysis:
                logger.warning("Category analysis not found in competitor data")
            
        except FileNotFoundError:
            logger.error(f"File not found: {competitor_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise
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
            
            # Validate structure
            if 'component_breakdown' not in self.review_intelligence:
                logger.warning("Component breakdown not found in review intelligence data")
            
        except FileNotFoundError:
            logger.error(f"File not found: {review_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading review intelligence: {e}")
            raise
    
    def analyze_competitive_gaps(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze competitive gaps and opportunities.
        
        Returns:
            Dictionary with competitive gap analysis
        """
        logger.info("Analyzing competitive gaps...")
        
        gap_analysis = {}
        category_analysis = self.competitor_analysis.get('category_analysis', {})
        market_leaders = self.competitor_analysis.get('market_leaders', {})
        
        for category, analysis in category_analysis.items():
            brand_wins = analysis.get('brand_wins', {})
            
            if not brand_wins:
                continue
            
            # Identify market leader in this category
            dominant_brand = max(brand_wins.items(), key=lambda x: x[1])
            
            # Find components where leader is weak
            component_performance = analysis.get('performance_data', {})
            weak_components = []
            
            for component, data in component_performance.items():
                brand_scores = data.get('brand_scores', {})
                
                if dominant_brand[0] in brand_scores:
                    leader_score = brand_scores[dominant_brand[0]]
                    
                    # Check if leader's score is below threshold
                    if leader_score < 0.3:  # Low performance threshold
                        weak_components.append({
                            'component': component,
                            'leader_score': leader_score,
                            'leader_brand': dominant_brand[0],
                            'opportunity': True
                        })
            
            gap_analysis[category] = {
                'dominant_brand': dominant_brand[0],
                'brand_wins': brand_wins,
                'weak_components': weak_components,
                'total_components': len(component_performance),
                'improvement_opportunities': len(weak_components)
            }
        
        logger.info(f"Analyzed competitive gaps for {len(gap_analysis)} categories")
        return gap_analysis
    
    def analyze_customer_pain_points(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze customer pain points from review intelligence.
        
        Returns:
            Dictionary with customer pain point analysis
        """
        logger.info("Analyzing customer pain points...")
        
        component_breakdown = self.review_intelligence.get('component_breakdown', {})
        pain_point_analysis = {}
        
        for component, data in component_breakdown.items():
            review_count = data.get('review_count', 0)
            severity_score = data.get('severity_score', 0)
            product_count = data.get('product_count', 0)
            top_phrases = data.get('top_phrases', [])
            
            # Calculate pain point intensity
            intensity_score = review_count * (severity_score / 10)  # Weighted by severity
            
            # Determine priority level
            if intensity_score > 100:
                priority = 'high'
            elif intensity_score > 50:
                priority = 'medium'
            else:
                priority = 'low'
            
            pain_point_analysis[component] = {
                'review_count': review_count,
                'severity_score': severity_score,
                'product_count': product_count,
                'intensity_score': intensity_score,
                'priority': priority,
                'top_complaints': top_phrases[:5],  # Top 5 complaints
                'affected_products': product_count
            }
        
        logger.info(f"Analyzed pain points for {len(pain_point_analysis)} components")
        return pain_point_analysis
    
    def generate_component_recommendations(self, component: str, 
                                        competitive_gap: Dict[str, Any],
                                        pain_point: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate specific recommendations for a component.
        
        Args:
            component: Component name
            competitive_gap: Competitive gap analysis for this component
            pain_point: Customer pain point analysis for this component
            
        Returns:
            Dictionary with component recommendations
        """
        priority = pain_point.get('priority', 'medium')
        intensity = pain_point.get('intensity_score', 0)
        
        # Get base recommendations
        base_recommendations = self.improvement_strategies.get(component, {
            'high_priority': ["Improve overall component quality and performance"],
            'medium_priority': ["Enhance component features and user experience"],
            'low_priority': ["Optimize component for specific use cases"]
        })
        
        # Select recommendations based on priority
        if priority == 'high':
            selected_recommendations = base_recommendations['high_priority']
        elif priority == 'medium':
            selected_recommendations = base_recommendations['medium_priority']
        else:
            selected_recommendations = base_recommendations['low_priority']
        
        # Add context-specific recommendations
        contextual_recommendations = []
        
        # Based on competitive gaps
        if competitive_gap.get('opportunity'):
            contextual_recommendations.append(
                f"Focus on {component} excellence to gain competitive advantage"
            )
        
        # Based on customer complaints
        top_complaints = pain_point.get('top_complaints', [])
        if top_complaints:
            main_complaint = top_complaints[0][0] if top_complaints[0] else "general issues"
            contextual_recommendations.append(
                f"Address customer complaints about {main_complaint}"
            )
        
        # Based on intensity
        if intensity > 200:
            contextual_recommendations.append(
                "Urgent attention required - high customer dissatisfaction"
            )
        
        return {
            'component': component,
            'priority': priority,
            'intensity_score': intensity,
            'base_recommendations': selected_recommendations,
            'contextual_recommendations': contextual_recommendations,
            'customer_complaints': [complaint[0] for complaint in top_complaints[:3]],
            'affected_products': pain_point.get('product_count', 0),
            'competitive_opportunity': competitive_gap.get('opportunity', False)
        }
    
    def generate_strategic_recommendations(self) -> Dict[str, Any]:
        """
        Generate comprehensive strategic recommendations.
        
        Returns:
            Dictionary with strategic recommendations
        """
        logger.info("Generating strategic recommendations...")
        
        # Analyze competitive gaps and customer pain points
        competitive_gaps = self.analyze_competitive_gaps()
        pain_points = self.analyze_customer_pain_points()
        
        # Generate recommendations for each component
        component_recommendations = {}
        
        # Get all unique components from both analyses
        all_components = set(pain_points.keys())
        all_components.update(competitive_gaps.keys())
        
        for component in all_components:
            pain_point = pain_points.get(component, {
                'priority': 'low',
                'intensity_score': 0,
                'top_complaints': [],
                'product_count': 0
            })
            
            competitive_gap = competitive_gaps.get(component, {
                'opportunity': False
            })
            
            recommendation = self.generate_component_recommendations(
                component, competitive_gap, pain_point
            )
            
            component_recommendations[component] = recommendation
        
        # Prioritize recommendations
        prioritized_recommendations = self._prioritize_recommendations(component_recommendations)
        
        # Generate strategic summary
        strategic_summary = self._generate_strategic_summary(prioritized_recommendations, pain_points)
        
        self.strategic_recommendations = {
            'strategic_summary': strategic_summary,
            'component_recommendations': component_recommendations,
            'prioritized_recommendations': prioritized_recommendations,
            'competitive_gaps': competitive_gaps,
            'customer_pain_points': pain_points,
            'implementation_timeline': self._generate_implementation_timeline(prioritized_recommendations)
        }
        
        logger.info("Strategic recommendations generated successfully")
        return self.strategic_recommendations
    
    def _prioritize_recommendations(self, component_recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Prioritize recommendations based on multiple factors.
        
        Args:
            component_recommendations: Component recommendations
            
        Returns:
            Prioritized list of recommendations
        """
        recommendations = []
        
        for component, data in component_recommendations.items():
            priority_score = 0
            
            # Priority weighting
            if data['priority'] == 'high':
                priority_score += 30
            elif data['priority'] == 'medium':
                priority_score += 20
            else:
                priority_score += 10
            
            # Intensity weighting
            intensity = data['intensity_score']
            if intensity > 200:
                priority_score += 25
            elif intensity > 100:
                priority_score += 15
            elif intensity > 50:
                priority_score += 10
            
            # Competitive opportunity weighting
            if data['competitive_opportunity']:
                priority_score += 15
            
            # Product impact weighting
            product_count = data['affected_products']
            if product_count > 10:
                priority_score += 10
            elif product_count > 5:
                priority_score += 5
            
            recommendations.append({
                'component': component,
                'priority': data['priority'],
                'priority_score': priority_score,
                'intensity_score': intensity,
                'recommendations': data['base_recommendations'] + data['contextual_recommendations'],
                'customer_complaints': data['customer_complaints'],
                'affected_products': product_count,
                'competitive_opportunity': data['competitive_opportunity']
            })
        
        # Sort by priority score
        recommendations.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return recommendations
    
    def _generate_strategic_summary(self, prioritized_recommendations: List[Dict[str, Any]], 
                                 pain_points: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate strategic summary of recommendations.
        
        Args:
            prioritized_recommendations: Prioritized recommendations list
            pain_points: Customer pain points analysis
            
        Returns:
            Strategic summary dictionary
        """
        # Count priorities
        high_priority_count = sum(1 for rec in prioritized_recommendations if rec['priority'] == 'high')
        medium_priority_count = sum(1 for rec in prioritized_recommendations if rec['priority'] == 'medium')
        low_priority_count = sum(1 for rec in prioritized_recommendations if rec['priority'] == 'low')
        
        # Top strategic recommendations
        top_recommendations = []
        for i, rec in enumerate(prioritized_recommendations[:10], 1):
            top_recommendations.append({
                'rank': i,
                'component': rec['component'],
                'priority': rec['priority'],
                'key_recommendation': rec['recommendations'][0] if rec['recommendations'] else "Improve component quality",
                'impact_score': rec['priority_score'],
                'affected_products': rec['affected_products']
            })
        
        # Strategic focus areas
        focus_areas = []
        for rec in prioritized_recommendations[:5]:
            focus_areas.append({
                'area': rec['component'],
                'rationale': f"High customer dissatisfaction ({rec['intensity_score']:.1f} intensity)",
                'expected_impact': "Significant improvement in customer satisfaction"
            })
        
        return {
            'total_recommendations': len(prioritized_recommendations),
            'priority_breakdown': {
                'high': high_priority_count,
                'medium': medium_priority_count,
                'low': low_priority_count
            },
            'top_recommendations': top_recommendations,
            'strategic_focus_areas': focus_areas,
            'overall_strategy': "Focus on high-priority components with significant customer impact and competitive opportunities"
        }
    
    def _generate_implementation_timeline(self, prioritized_recommendations: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Generate implementation timeline for recommendations.
        
        Args:
            prioritized_recommendations: Prioritized recommendations list
            
        Returns:
            Implementation timeline dictionary
        """
        timeline = {
            'immediate': [],  # 0-3 months
            'short_term': [],  # 3-6 months
            'medium_term': [],  # 6-12 months
            'long_term': []   # 12+ months
        }
        
        for rec in prioritized_recommendations:
            component = rec['component']
            priority = rec['priority']
            
            if priority == 'high':
                timeline['immediate'].append(component)
                timeline['short_term'].append(component)
            elif priority == 'medium':
                timeline['short_term'].append(component)
                timeline['medium_term'].append(component)
            else:
                timeline['medium_term'].append(component)
                timeline['long_term'].append(component)
        
        return timeline
    
    def save_strategic_recommendations(self, output_file: str = 'strategic_recommendations.json') -> None:
        """
        Save strategic recommendations as JSON file.
        
        Args:
            output_file: Output file name
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.strategic_recommendations, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved strategic recommendations to {output_file}")
        except Exception as e:
            logger.error(f"Error saving strategic recommendations: {e}")
            raise
    
    def process_strategy_engine(self, competitor_file: str = 'competitor_analysis.json',
                              review_file: str = 'review_intelligence.json',
                              output_file: str = 'strategic_recommendations.json') -> Dict[str, Any]:
        """
        Complete pipeline to process strategic recommendations.
        
        Args:
            competitor_file: Input competitor analysis JSON file
            review_file: Input review intelligence JSON file
            output_file: Output strategic recommendations JSON file
            
        Returns:
            Complete strategic recommendations
        """
        try:
            # Load input data
            self.load_competitor_analysis(competitor_file)
            self.load_review_intelligence(review_file)
            
            # Generate strategic recommendations
            self.generate_strategic_recommendations()
            
            # Save recommendations
            self.save_strategic_recommendations(output_file)
            
            # Print summary
            self._print_summary()
            
            logger.info("Strategy engine processing completed successfully!")
            return self.strategic_recommendations
            
        except Exception as e:
            logger.error(f"Error in strategy engine pipeline: {e}")
            raise
    
    def _print_summary(self) -> None:
        """Print summary of strategic recommendations."""
        print("\n" + "="*60)
        print("🎯 STRATEGIC RECOMMENDATIONS SUMMARY")
        print("="*60)
        
        summary = self.strategic_recommendations.get('strategic_summary', {})
        top_recommendations = summary.get('top_recommendations', [])
        
        print(f"\n🚨 STRATEGIC RECOMMENDATIONS:")
        for rec in top_recommendations:
            print(f"   {rec['rank']:2d}. {rec['key_recommendation']}")
            print(f"       Component: {rec['component']} | Priority: {rec['priority']}")
            print(f"       Impact Score: {rec['impact_score']} | Products: {rec['affected_products']}")
        
        print(f"\n📊 PRIORITY BREAKDOWN:")
        priority_breakdown = summary.get('priority_breakdown', {})
        total = sum(priority_breakdown.values())
        
        for priority, count in priority_breakdown.items():
            percentage = (count / total) * 100 if total > 0 else 0
            print(f"   {priority.title()}: {count} recommendations ({percentage:.1f}%)")
        
        print(f"\n🎯 STRATEGIC FOCUS AREAS:")
        focus_areas = summary.get('strategic_focus_areas', [])
        for area in focus_areas:
            print(f"   • {area['area'].title()}: {area['rationale']}")
        
        print(f"\n⏰ IMPLEMENTATION TIMELINE:")
        timeline = self.strategic_recommendations.get('implementation_timeline', {})
        
        for phase, components in timeline.items():
            phase_name = phase.replace('_', ' ').title()
            print(f"   {phase_name}: {', '.join(components)}")
        
        print("="*60)
    
    def get_component_strategy(self, component: str) -> Dict[str, Any]:
        """
        Get detailed strategy for a specific component.
        
        Args:
            component: Component name
            
        Returns:
            Component strategy details
        """
        component_recommendations = self.strategic_recommendations.get('component_recommendations', {})
        return component_recommendations.get(component, {})
    
    def get_quick_wins(self) -> List[Dict[str, Any]]:
        """
        Get quick win opportunities (high impact, low effort).
        
        Returns:
            List of quick win recommendations
        """
        prioritized = self.strategic_recommendations.get('prioritized_recommendations', [])
        
        # Filter for high priority with moderate complexity
        quick_wins = []
        for rec in prioritized:
            if rec['priority'] == 'high' and rec['priority_score'] >= 40:
                quick_wins.append(rec)
        
        return quick_wins[:5]  # Top 5 quick wins

# Example usage
if __name__ == "__main__":
    # Initialize and process strategy engine
    engine = StrategyEngine()
    strategic_recommendations = engine.process_strategy_engine(
        competitor_file='competitor_analysis.json',
        review_file='review_intelligence.json',
        output_file='strategic_recommendations.json'
    )
    
    print(f"\n✅ Strategic recommendations complete! Results saved to strategic_recommendations.json")
    
    # Show quick wins
    quick_wins = engine.get_quick_wins()
    print(f"\n🚀 QUICK WINS:")
    for i, win in enumerate(quick_wins, 1):
        print(f"   {i}. {win['recommendations'][0]}")
        print(f"      Component: {win['component']} | Impact: {win['priority_score']}")
