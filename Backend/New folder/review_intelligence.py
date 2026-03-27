import json
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReviewIntelligence:
    """
    Identify and analyze most common product complaints from negative reviews.
    Extract actionable insights for product improvement and competitive intelligence.
    """
    
    def __init__(self):
        self.component_data = {}
        self.sentiment_scores = {}
        self.negative_reviews = {}
        self.complaint_analysis = {}
        
        # Common complaint patterns and keywords
        self.complaint_patterns = {
            'battery': [
                'battery drain', 'battery dies', 'poor battery', 'battery life', 'battery backup',
                'fast draining', 'battery not lasting', 'short battery', 'weak battery',
                'battery overheating', 'battery swelling', 'battery dead', 'no battery',
                'battery charging', 'slow charging', 'quick drain', 'battery issues'
            ],
            'sound': [
                'poor sound', 'bad sound', 'sound quality', 'audio quality', 'low volume',
                'no sound', 'muffled sound', 'distorted sound', 'crackling sound',
                'sound cuts', 'audio issues', 'bass poor', 'treble poor', 'sound problems',
                'earpiece sound', 'speaker sound', 'headphone sound', 'sound distortion'
            ],
            'camera': [
                'camera poor', 'bad camera', 'camera quality', 'photo quality', 'blurry photos',
                'camera focus', 'camera slow', 'dark photos', 'camera flash', 'camera lag',
                'camera crashes', 'front camera', 'rear camera', 'camera not working',
                'low resolution', 'grainy photos', 'camera issues', 'picture quality'
            ],
            'display': [
                'screen issues', 'display problems', 'screen cracked', 'screen flicker',
                'dead pixels', 'screen burn', 'display dim', 'screen resolution',
                'touch screen', 'screen unresponsive', 'screen freeze', 'display quality',
                'screen brightness', 'color issues', 'screen ghosting', 'lcd problems'
            ],
            'performance': [
                'slow performance', 'lag', 'freezing', 'crashes', 'performance issues',
                'slow response', 'system lag', 'app crashes', 'phone hangs', 'slow startup',
                'memory issues', 'ram problems', 'cpu performance', 'overheating',
                'thermal throttling', 'performance slow', 'system freeze'
            ],
            'build_quality': [
                'build quality', 'cheap material', 'plastic feel', 'poor build',
                'easily broken', 'fragile', 'weak construction', 'build issues',
                'material quality', 'durability issues', 'poor craftsmanship',
                'loose parts', 'creaking', 'bending', 'structural issues'
            ],
            'comfort': [
                'uncomfortable', 'tight fit', 'heavy', 'painful', 'ear pressure',
                'head pressure', 'uncomfortable wear', 'hurts ears', 'too tight',
                'weight issues', 'fit problems', 'size issues', 'comfort problems'
            ],
            'connectivity': [
                'bluetooth issues', 'wifi problems', 'connection drops', 'poor connection',
                'network issues', 'signal weak', 'bluetooth disconnect', 'wifi slow',
                'connection lost', 'pairing issues', 'connectivity problems',
                'signal strength', 'network drops', 'bluetooth pairing'
            ],
            'software': [
                'software issues', 'bugs', 'glitches', 'software crash', 'app problems',
                'system bugs', 'software update', 'os issues', 'firmware problems',
                'software lag', 'app compatibility', 'system errors', 'software bugs'
            ],
            'price': [
                'overpriced', 'too expensive', 'not worth', 'poor value', 'expensive',
                'price too high', 'cost issues', 'not affordable', 'waste of money',
                'poor value for money', 'overpriced for', 'price performance'
            ]
        }
        
        # Negative sentiment indicators
        self.negative_indicators = [
            'terrible', 'awful', 'horrible', 'worst', 'bad', 'poor', 'disappointing',
            'useless', 'waste', 'regret', 'hate', 'dislike', 'frustrated', 'annoyed',
            'angry', 'upset', 'unhappy', 'dissatisfied', 'problem', 'issue', 'defect',
            'broken', 'doesn\'t work', 'failed', 'failure', 'defective', 'faulty',
            'returned', 'refund', 'complaint', 'concern', 'trouble', 'difficult'
        ]
    
    def load_component_data(self, component_file: str = 'component_reviews.json') -> None:
        """
        Load component reviews data.
        
        Args:
            component_file: Path to the component reviews JSON file
        """
        try:
            with open(component_file, 'r', encoding='utf-8') as f:
                self.component_data = json.load(f)
            logger.info(f"Successfully loaded component data from {component_file}")
            
            total_products = len(self.component_data)
            total_components = sum(len(components) for components in self.component_data.values())
            total_reviews = sum(len(reviews) for components in self.component_data.values() for reviews in components.values())
            
            logger.info(f"Loaded {total_products} products with {total_components} components and {total_reviews} total reviews")
            
        except FileNotFoundError:
            logger.error(f"File not found: {component_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading component data: {e}")
            raise
    
    def load_sentiment_scores(self, sentiment_file: str = 'component_sentiment_scores.json') -> None:
        """
        Load sentiment scores data for reference.
        
        Args:
            sentiment_file: Path to the sentiment scores JSON file
        """
        try:
            with open(sentiment_file, 'r', encoding='utf-8') as f:
                self.sentiment_scores = json.load(f)
            logger.info(f"Successfully loaded sentiment scores from {sentiment_file}")
        except FileNotFoundError:
            logger.warning(f"Sentiment scores file not found: {sentiment_file}")
            self.sentiment_scores = {}
        except Exception as e:
            logger.warning(f"Error loading sentiment scores: {e}")
            self.sentiment_scores = {}
    
    def is_negative_review(self, review_text: str, sentiment_threshold: float = -0.1) -> bool:
        """
        Determine if a review is negative based on sentiment indicators.
        
        Args:
            review_text: The review text to analyze
            sentiment_threshold: Threshold for negative sentiment
            
        Returns:
            True if the review is negative
        """
        review_lower = review_text.lower()
        
        # Check for negative indicators
        negative_count = sum(1 for indicator in self.negative_indicators if indicator in review_lower)
        
        # Simple heuristic: if multiple negative indicators, mark as negative
        if negative_count >= 2:
            return True
        
        # Check for strong negative words
        strong_negatives = ['terrible', 'awful', 'horrible', 'worst', 'hate', 'useless', 'waste']
        if any(neg in review_lower for neg in strong_negatives):
            return True
        
        # Check for problem/issue patterns
        problem_patterns = ['doesn\'t work', 'not working', 'stopped working', 'broken', 'failed']
        if any(pattern in review_lower for pattern in problem_patterns):
            return True
        
        return False
    
    def extract_negative_reviews(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Extract negative reviews from component data.
        
        Returns:
            Dictionary with negative reviews by product and component
        """
        logger.info("Extracting negative reviews...")
        
        negative_reviews = defaultdict(lambda: defaultdict(list))
        total_reviews = 0
        negative_count = 0
        
        for product_name, components in self.component_data.items():
            for component, reviews in components.items():
                for review_text in reviews:
                    total_reviews += 1
                    
                    if self.is_negative_review(review_text):
                        negative_reviews[product_name][component].append(review_text.strip())
                        negative_count += 1
        
        self.negative_reviews = dict(negative_reviews)
        
        logger.info(f"Extracted {negative_count} negative reviews out of {total_reviews} total reviews")
        logger.info(f"Negative review rate: {(negative_count/total_reviews)*100:.1f}%")
        
        return self.negative_reviews
    
    def normalize_complaint_text(self, text: str) -> str:
        """
        Normalize complaint text for better clustering.
        
        Args:
            text: The complaint text to normalize
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common filler words
        filler_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        for word in filler_words:
            text = text.replace(f' {word} ', ' ')
        
        # Remove punctuation except for meaningful ones
        text = re.sub(r'[^\w\s\.\!\?]', '', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def identify_complaint_component(self, review_text: str) -> Optional[str]:
        """
        Identify which component the complaint is about.
        
        Args:
            review_text: The review text to analyze
            
        Returns:
            Component name if identified, None otherwise
        """
        normalized_text = review_text.lower()
        
        # Check each component's complaint patterns
        for component, patterns in self.complaint_patterns.items():
            for pattern in patterns:
                if pattern in normalized_text:
                    return component
        
        return None
    
    def extract_complaint_phrases(self, review_text: str, component: str) -> List[str]:
        """
        Extract specific complaint phrases from review text.
        
        Args:
            review_text: The review text
            component: The component category
            
        Returns:
            List of complaint phrases
        """
        phrases = []
        normalized_text = review_text.lower()
        
        # Extract phrases based on component patterns
        if component in self.complaint_patterns:
            patterns = self.complaint_patterns[component]
            
            for pattern in patterns:
                if pattern in normalized_text:
                    # Extract a window around the pattern for context
                    pattern_index = normalized_text.find(pattern)
                    start = max(0, pattern_index - 20)
                    end = min(len(normalized_text), pattern_index + len(pattern) + 20)
                    
                    phrase = normalized_text[start:end].strip()
                    if len(phrase) > 10:  # Filter out very short phrases
                        phrases.append(phrase)
        
        # Also look for general complaint phrases
        complaint_starters = [
            'the problem is', 'issue with', 'problem with', 'complaint about',
            'disappointed with', 'frustrated with', 'unhappy with', 'issue is'
        ]
        
        for starter in complaint_starters:
            if starter in normalized_text:
                starter_index = normalized_text.find(starter)
                start = starter_index
                end = min(len(normalized_text), starter_index + 100)  # Get reasonable length
                
                phrase = normalized_text[start:end].strip()
                if len(phrase) > 15:
                    phrases.append(phrase)
        
        return phrases
    
    def cluster_complaints_by_component(self) -> Dict[str, Dict[str, Any]]:
        """
        Cluster negative reviews by component and extract common complaints.
        
        Returns:
            Dictionary with clustered complaints by component
        """
        logger.info("Clustering complaints by component...")
        
        clustered_complaints = defaultdict(lambda: {
            'complaints': [],
            'phrases': [],
            'products': set(),
            'review_count': 0
        })
        
        for product_name, components in self.negative_reviews.items():
            for component, reviews in components.items():
                for review_text in reviews:
                    # Identify which component this complaint is about
                    complaint_component = self.identify_complaint_component(review_text)
                    
                    if complaint_component:
                        cluster = clustered_complaints[complaint_component]
                        cluster['complaints'].append(review_text)
                        cluster['products'].add(product_name)
                        cluster['review_count'] += 1
                        
                        # Extract complaint phrases
                        phrases = self.extract_complaint_phrases(review_text, complaint_component)
                        cluster['phrases'].extend(phrases)
        
        # Convert sets to lists for JSON serialization
        for component, data in clustered_complaints.items():
            data['products'] = list(data['products'])
        
        logger.info(f"Clustered complaints into {len(clustered_complaints)} component categories")
        
        return dict(clustered_complaints)
    
    def rank_complaint_frequencies(self, clustered_complaints: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank complaints by frequency and importance.
        
        Args:
            clustered_complaints: Clustered complaint data
            
        Returns:
            Ranked list of complaints
        """
        logger.info("Ranking complaint frequencies...")
        
        complaint_rankings = []
        
        for component, data in clustered_complaints.items():
            # Count phrase frequencies
            phrase_counter = Counter(data['phrases'])
            
            # Get top phrases
            top_phrases = phrase_counter.most_common(10)
            
            # Calculate importance score (frequency + severity indicators)
            importance_score = data['review_count']
            
            # Add weight for severe complaint words
            severe_words = ['terrible', 'awful', 'horrible', 'worst', 'broken', 'failed', 'useless']
            for complaint in data['complaints']:
                if any(severe in complaint.lower() for severe in severe_words):
                    importance_score += 1
            
            complaint_rankings.append({
                'component': component,
                'review_count': data['review_count'],
                'product_count': len(data['products']),
                'importance_score': importance_score,
                'top_phrases': top_phrases,
                'affected_products': data['products'],
                'sample_complaints': data['complaints'][:5]  # Top 5 sample complaints
            })
        
        # Sort by importance score
        complaint_rankings.sort(key=lambda x: x['importance_score'], reverse=True)
        
        logger.info(f"Ranked {len(complaint_rankings)} complaint categories")
        
        return complaint_rankings
    
    def generate_complaint_summary(self, ranked_complaints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a comprehensive complaint summary.
        
        Args:
            ranked_complaints: List of ranked complaint data
            
        Returns:
            Complaint summary dictionary
        """
        total_negative_reviews = sum(complaint['review_count'] for complaint in ranked_complaints)
        
        # Generate top customer issues list
        top_issues = []
        for i, complaint in enumerate(ranked_complaints[:10], 1):
            if complaint['top_phrases']:
                top_issue = complaint['top_phrases'][0][0]  # Most frequent phrase
                top_issues.append({
                    'rank': i,
                    'issue': top_issue,
                    'component': complaint['component'],
                    'frequency': complaint['review_count'],
                    'products_affected': complaint['product_count']
                })
        
        # Component-wise breakdown
        component_breakdown = {}
        for complaint in ranked_complaints:
            component_breakdown[complaint['component']] = {
                'review_count': complaint['review_count'],
                'product_count': complaint['product_count'],
                'top_phrases': complaint['top_phrases'][:5],
                'severity_score': complaint['importance_score']
            }
        
        return {
            'total_negative_reviews': total_negative_reviews,
            'total_complaint_categories': len(ranked_complaints),
            'top_customer_issues': top_issues,
            'component_breakdown': component_breakdown,
            'detailed_rankings': ranked_complaints
        }
    
    def save_complaint_analysis(self, output_file: str = 'review_intelligence.json') -> None:
        """
        Save complaint analysis as JSON file.
        
        Args:
            output_file: Output file name
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.complaint_analysis, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved complaint analysis to {output_file}")
        except Exception as e:
            logger.error(f"Error saving complaint analysis: {e}")
            raise
    
    def process_review_intelligence(self, component_file: str = 'component_reviews.json',
                                  sentiment_file: str = 'component_sentiment_scores.json',
                                  output_file: str = 'review_intelligence.json',
                                  sentiment_threshold: float = -0.1) -> Dict[str, Any]:
        """
        Complete pipeline to process review intelligence.
        
        Args:
            component_file: Input component reviews JSON file
            sentiment_file: Input sentiment scores JSON file
            output_file: Output review intelligence JSON file
            sentiment_threshold: Threshold for negative sentiment
            
        Returns:
            Complete review intelligence analysis
        """
        try:
            # Load data
            self.load_component_data(component_file)
            self.load_sentiment_scores(sentiment_file)
            
            # Extract negative reviews
            self.extract_negative_reviews()
            
            # Cluster complaints by component
            clustered_complaints = self.cluster_complaints_by_component()
            
            # Rank complaint frequencies
            ranked_complaints = self.rank_complaint_frequencies(clustered_complaints)
            
            # Generate summary
            self.complaint_analysis = self.generate_complaint_summary(ranked_complaints)
            
            # Save analysis
            self.save_complaint_analysis(output_file)
            
            # Print summary
            self._print_summary()
            
            logger.info("Review intelligence analysis completed successfully!")
            return self.complaint_analysis
            
        except Exception as e:
            logger.error(f"Error in review intelligence pipeline: {e}")
            raise
    
    def _print_summary(self) -> None:
        """Print summary of review intelligence results."""
        print("\n" + "="*60)
        print("🚨 REVIEW INTELLIGENCE SUMMARY")
        print("="*60)
        
        print(f"\n🔍 TOP CUSTOMER ISSUES:")
        top_issues = self.complaint_analysis.get('top_customer_issues', [])
        
        for issue in top_issues[:10]:
            print(f"   {issue['rank']:2d}. {issue['issue'].title()} ({issue['component']})")
            print(f"       Frequency: {issue['frequency']} reviews | Products: {issue['products_affected']}")
        
        print(f"\n📊 COMPLAINT BREAKDOWN:")
        component_breakdown = self.complaint_analysis.get('component_breakdown', {})
        
        for component, data in component_breakdown.items():
            print(f"   📁 {component.title()}:")
            print(f"      Reviews: {data['review_count']} | Products: {data['product_count']}")
            print(f"      Severity Score: {data['severity_score']}")
            
            if data['top_phrases']:
                print(f"      Top Complaints:")
                for phrase, count in data['top_phrases'][:3]:
                    print(f"        - {phrase.title()} ({count} mentions)")
        
        print(f"\n📈 OVERALL STATISTICS:")
        print(f"   Total Negative Reviews: {self.complaint_analysis.get('total_negative_reviews', 0)}")
        print(f"   Complaint Categories: {self.complaint_analysis.get('total_complaint_categories', 0)}")
        print(f"   Components Affected: {len(component_breakdown)}")
        
        print("="*60)
    
    def get_complaint_trends(self) -> Dict[str, Any]:
        """
        Analyze complaint trends and patterns.
        
        Returns:
            Dictionary with trend analysis
        """
        component_breakdown = self.complaint_analysis.get('component_breakdown', {})
        
        # Find most problematic components
        most_problematic = max(component_breakdown.items(), 
                              key=lambda x: x[1]['severity_score']) if component_breakdown else None
        
        # Find most frequently mentioned issues
        all_phrases = []
        for data in component_breakdown.values():
            all_phrases.extend([(phrase, count) for phrase, count in data['top_phrases']])
        
        phrase_counter = Counter(all_phrases)
        top_phrases = phrase_counter.most_common(10)
        
        return {
            'most_problematic_component': most_problematic,
            'top_complaint_phrases': top_phrases,
            'total_components_analyzed': len(component_breakdown)
        }
    
    def get_product_specific_complaints(self, product_name: str) -> Dict[str, Any]:
        """
        Get complaints specific to a particular product.
        
        Args:
            product_name: Name of the product to analyze
            
        Returns:
            Dictionary with product-specific complaints
        """
        product_complaints = defaultdict(list)
        
        for component, reviews in self.negative_reviews.get(product_name, {}).items():
            for review in reviews:
                complaint_component = self.identify_complaint_component(review)
                if complaint_component:
                    product_complaints[complaint_component].append(review)
        
        return dict(product_complaints)

# Example usage
if __name__ == "__main__":
    # Initialize and process review intelligence
    intelligence = ReviewIntelligence()
    complaint_analysis = intelligence.process_review_intelligence(
        component_file='component_reviews.json',
        sentiment_file='component_sentiment_scores.json',
        output_file='review_intelligence.json'
    )
    
    print(f"\n✅ Review intelligence analysis complete! Results saved to review_intelligence.json")
    
    # Show complaint trends
    trends = intelligence.get_complaint_trends()
    print(f"\n📈 COMPLAINT TRENDS:")
    if trends['most_problematic_component']:
        component, data = trends['most_problematic_component']
        print(f"   Most Problematic: {component} (Severity: {data['severity_score']})")
    
    print(f"\n🔝 Top Complaint Phrases:")
    for phrase, count in trends['top_complaint_phrases'][:5]:
        print(f"   {phrase.title()}: {count} mentions")
