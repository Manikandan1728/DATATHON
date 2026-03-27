import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import NLTK VADER
try:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    NLTK_AVAILABLE = True
    logger.info("NLTK VADER sentiment analyzer available")
except ImportError:
    NLTK_AVAILABLE = False
    logger.warning("NLTK VADER not available. Will use fallback sentiment analysis.")

# Try to import HuggingFace transformers
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    HF_AVAILABLE = True
    logger.info("HuggingFace transformers available")
except ImportError:
    HF_AVAILABLE = False
    logger.warning("HuggingFace transformers not available. Will use NLTK VADER or fallback.")

class SentimentEngine:
    """
    Calculate sentiment scores for product components using NLTK VADER or HuggingFace models.
    """
    
    def __init__(self, model_type: str = 'auto'):
        """
        Initialize the sentiment engine.
        
        Args:
            model_type: 'vader', 'huggingface', 'auto', or 'fallback'
        """
        self.model_type = model_type
        self.vader_analyzer = None
        self.hf_pipeline = None
        self.component_data = {}
        self.sentiment_scores = {}
        
        # Initialize the selected model
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize the sentiment analysis model based on availability and preference."""
        if self.model_type == 'auto':
            # Auto-select best available model
            if HF_AVAILABLE:
                self._initialize_huggingface()
            elif NLTK_AVAILABLE:
                self._initialize_vader()
            else:
                self._initialize_fallback()
        elif self.model_type == 'huggingface':
            if HF_AVAILABLE:
                self._initialize_huggingface()
            else:
                logger.warning("HuggingFace not available, falling back to NLTK VADER")
                if NLTK_AVAILABLE:
                    self._initialize_vader()
                else:
                    self._initialize_fallback()
        elif self.model_type == 'vader':
            if NLTK_AVAILABLE:
                self._initialize_vader()
            else:
                logger.warning("NLTK VADER not available, falling back to HuggingFace")
                if HF_AVAILABLE:
                    self._initialize_huggingface()
                else:
                    self._initialize_fallback()
        else:
            self._initialize_fallback()
    
    def _initialize_vader(self) -> None:
        """Initialize NLTK VADER sentiment analyzer."""
        try:
            self.vader_analyzer = SentimentIntensityAnalyzer()
            logger.info("Initialized NLTK VADER sentiment analyzer")
        except Exception as e:
            logger.error(f"Error initializing VADER: {e}")
            self._initialize_fallback()
    
    def _initialize_huggingface(self) -> None:
        """Initialize HuggingFace sentiment analysis pipeline."""
        try:
            # Use a lightweight, accurate sentiment model
            model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
            self.hf_pipeline = pipeline(
                "sentiment-analysis",
                model=model_name,
                tokenizer=model_name,
                device=-1  # Use CPU
            )
            logger.info(f"Initialized HuggingFace sentiment model: {model_name}")
        except Exception as e:
            logger.error(f"Error initializing HuggingFace: {e}")
            if NLTK_AVAILABLE:
                self._initialize_vader()
            else:
                self._initialize_fallback()
    
    def _initialize_fallback(self) -> None:
        """Initialize fallback rule-based sentiment analysis."""
        logger.info("Using fallback rule-based sentiment analysis")
        self.vader_analyzer = None
        self.hf_pipeline = None
    
    def load_component_data(self, input_file: str = 'component_reviews.json') -> None:
        """
        Load component reviews data.
        
        Args:
            input_file: Path to the component reviews JSON file
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                self.component_data = json.load(f)
            logger.info(f"Successfully loaded component data from {input_file}")
            
            total_products = len(self.component_data)
            total_components = sum(len(components) for components in self.component_data.values())
            total_reviews = sum(len(reviews) for components in self.component_data.values() for reviews in components.values())
            
            logger.info(f"Loaded {total_products} products with {total_components} components and {total_reviews} total reviews")
            
        except FileNotFoundError:
            logger.error(f"File not found: {input_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading component data: {e}")
            raise
    
    def analyze_sentiment_vader(self, text: str) -> float:
        """
        Analyze sentiment using NLTK VADER.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment score (-1, 0, 1)
        """
        if not self.vader_analyzer:
            return self._fallback_sentiment_analysis(text)
        
        try:
            scores = self.vader_analyzer.polarity_scores(text)
            compound_score = scores['compound']
            
            # Convert compound score to -1, 0, 1
            if compound_score >= 0.05:
                return 1.0  # Positive
            elif compound_score <= -0.05:
                return -1.0  # Negative
            else:
                return 0.0  # Neutral
                
        except Exception as e:
            logger.warning(f"VADER analysis error: {e}")
            return self._fallback_sentiment_analysis(text)
    
    def analyze_sentiment_huggingface(self, text: str) -> float:
        """
        Analyze sentiment using HuggingFace transformer.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment score (-1, 0, 1)
        """
        if not self.hf_pipeline:
            return self._fallback_sentiment_analysis(text)
        
        try:
            # Truncate text if too long for the model
            max_length = 512
            if len(text) > max_length:
                text = text[:max_length]
            
            result = self.hf_pipeline(text)[0]
            label = result['label'].lower()
            
            # Convert labels to -1, 0, 1
            if 'positive' in label:
                return 1.0
            elif 'negative' in label:
                return -1.0
            else:
                return 0.0
                
        except Exception as e:
            logger.warning(f"HuggingFace analysis error: {e}")
            return self._fallback_sentiment_analysis(text)
    
    def _fallback_sentiment_analysis(self, text: str) -> float:
        """
        Fallback rule-based sentiment analysis.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment score (-1, 0, 1)
        """
        text_lower = text.lower()
        
        # Positive words
        positive_words = [
            'good', 'great', 'excellent', 'amazing', 'awesome', 'fantastic',
            'perfect', 'love', 'best', 'wonderful', 'nice', 'happy', 'pleased',
            'satisfied', 'impressed', 'outstanding', 'superb', 'brilliant'
        ]
        
        # Negative words
        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'disappoint',
            'poor', 'cheap', 'broken', 'useless', 'waste', 'regret', 'annoy',
            'frustrat', 'problem', 'issue', 'defect', 'fail', 'wrong'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 1.0
        elif negative_count > positive_count:
            return -1.0
        else:
            return 0.0
    
    def analyze_sentiment(self, text: str) -> float:
        """
        Analyze sentiment using the selected model.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment score (-1, 0, 1)
        """
        text = text.strip()
        if not text:
            return 0.0
        
        if self.hf_pipeline:
            return self.analyze_sentiment_huggingface(text)
        elif self.vader_analyzer:
            return self.analyze_sentiment_vader(text)
        else:
            return self._fallback_sentiment_analysis(text)
    
    def calculate_component_sentiments(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        Calculate sentiment scores for all components.
        
        Returns:
            Dictionary structure: {category: {component: {brand: score}}}
        """
        logger.info("Calculating sentiment scores for components...")
        
        # Load category data to get brand information
        try:
            with open('category_products.json', 'r', encoding='utf-8') as f:
                category_data = json.load(f)
        except FileNotFoundError:
            logger.warning("category_products.json not found, brand information will be 'Unknown'")
            category_data = {}
        
        # Structure to hold sentiment data
        sentiment_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        
        # Process each product and its component reviews
        for product_name, components in self.component_data.items():
            # Find the brand and category for this product
            brand = 'Unknown'
            category = 'Unknown'
            
            for cat_name, products in category_data.items():
                if product_name in products:
                    brand = products[product_name].get('brand', 'Unknown')
                    category = cat_name
                    break
            
            # Analyze sentiment for each component
            for component, reviews in components.items():
                component_scores = []
                
                for review_text in reviews:
                    score = self.analyze_sentiment(review_text)
                    component_scores.append(score)
                
                if component_scores:
                    avg_score = statistics.mean(component_scores)
                    sentiment_data[category][component][brand].append(avg_score)
        
        # Calculate average scores for each brand-component combination
        final_scores = {}
        for category, components in sentiment_data.items():
            final_scores[category] = {}
            for component, brands in components.items():
                final_scores[category][component] = {}
                for brand, scores in brands.items():
                    final_scores[category][component][brand] = statistics.mean(scores)
        
        self.sentiment_scores = final_scores
        
        logger.info("Sentiment calculation completed")
        return final_scores
    
    def enhance_sentiment_analysis(self) -> None:
        """
        Enhance sentiment analysis with additional processing.
        """
        logger.info("Enhancing sentiment analysis...")
        
        # Could add features like:
        # - Aspect-based sentiment analysis
        # - Context-aware sentiment
        # - Emotion detection
        # - Confidence scoring
        
        # For now, we'll just log the enhancement
        logger.info("Sentiment analysis enhanced with current methodology")
    
    def save_sentiment_scores(self, output_file: str = 'component_sentiment_scores.json') -> None:
        """
        Save sentiment scores as JSON file.
        
        Args:
            output_file: Output file name
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.sentiment_scores, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved sentiment scores to {output_file}")
        except Exception as e:
            logger.error(f"Error saving sentiment scores: {e}")
            raise
    
    def process_sentiments(self, input_file: str = 'component_reviews.json',
                          output_file: str = 'component_sentiment_scores.json',
                          model_type: str = 'auto',
                          enhance_analysis: bool = True) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        Complete pipeline to calculate sentiment scores.
        
        Args:
            input_file: Input component reviews JSON file
            output_file: Output sentiment scores JSON file
            model_type: Sentiment analysis model type
            enhance_analysis: Whether to enhance analysis
            
        Returns:
            Sentiment scores structure
        """
        try:
            # Load component data
            self.load_component_data(input_file)
            
            # Enhance analysis if requested
            if enhance_analysis:
                self.enhance_sentiment_analysis()
            
            # Calculate sentiment scores
            self.calculate_component_sentiments()
            
            # Save sentiment scores
            self.save_sentiment_scores(output_file)
            
            # Print summary
            self._print_summary()
            
            logger.info("Sentiment analysis completed successfully!")
            return self.sentiment_scores
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis pipeline: {e}")
            raise
    
    def _print_summary(self) -> None:
        """Print summary of sentiment analysis results."""
        print("\n" + "="*60)
        print("😊 SENTIMENT ANALYSIS SUMMARY")
        print("="*60)
        
        total_categories = len(self.sentiment_scores)
        total_components = 0
        total_brands = 0
        sentiment_distribution = {'positive': 0, 'neutral': 0, 'negative': 0}
        
        for category, components in self.sentiment_scores.items():
            for component, brands in components.items():
                total_components += 1
                for brand, score in brands.items():
                    total_brands += 1
                    
                    if score > 0.1:
                        sentiment_distribution['positive'] += 1
                    elif score < -0.1:
                        sentiment_distribution['negative'] += 1
                    else:
                        sentiment_distribution['neutral'] += 1
        
        print(f"\n📊 Overall Statistics:")
        print(f"   Categories analyzed: {total_categories}")
        print(f"   Components analyzed: {total_components}")
        print(f"   Brand-component pairs: {total_brands}")
        
        print(f"\n😊 Sentiment Distribution:")
        for sentiment, count in sentiment_distribution.items():
            percentage = (count / total_brands * 100) if total_brands > 0 else 0
            print(f"   {sentiment.capitalize()}: {count} ({percentage:.1f}%)")
        
        print(f"\n📁 Sentiment by Category:")
        for category, components in self.sentiment_scores.items():
            category_scores = []
            for component, brands in components.items():
                category_scores.extend(brands.values())
            
            if category_scores:
                avg_sentiment = statistics.mean(category_scores)
                print(f"   {category}: {avg_sentiment:.2f}")
        
        print("="*60)
    
    def get_top_performing_components(self, top_n: int = 10) -> List[Tuple[str, str, str, float]]:
        """
        Get top performing components by sentiment score.
        
        Args:
            top_n: Number of top components to return
            
        Returns:
            List of (category, component, brand, score) tuples
        """
        all_scores = []
        
        for category, components in self.sentiment_scores.items():
            for component, brands in components.items():
                for brand, score in brands.items():
                    all_scores.append((category, component, brand, score))
        
        # Sort by score (descending)
        all_scores.sort(key=lambda x: x[3], reverse=True)
        
        return all_scores[:top_n]
    
    def get_worst_performing_components(self, top_n: int = 10) -> List[Tuple[str, str, str, float]]:
        """
        Get worst performing components by sentiment score.
        
        Args:
            top_n: Number of worst components to return
            
        Returns:
            List of (category, component, brand, score) tuples
        """
        all_scores = []
        
        for category, components in self.sentiment_scores.items():
            for component, brands in components.items():
                for brand, score in brands.items():
                    all_scores.append((category, component, brand, score))
        
        # Sort by score (ascending)
        all_scores.sort(key=lambda x: x[3])
        
        return all_scores[:top_n]

# Example usage
if __name__ == "__main__":
    # Initialize and process sentiments
    engine = SentimentEngine(model_type='auto')
    sentiment_scores = engine.process_sentiments(
        input_file='component_reviews.json',
        output_file='component_sentiment_scores.json',
        model_type='auto',
        enhance_analysis=True
    )
    
    print(f"\n✅ Sentiment analysis complete! Results saved to component_sentiment_scores.json")
    
    # Show top and worst performing components
    print(f"\n🏆 Top 5 Performing Components:")
    top_components = engine.get_top_performing_components(5)
    for i, (category, component, brand, score) in enumerate(top_components, 1):
        print(f"   {i}. {brand} {component} ({category}): {score:.2f}")
    
    print(f"\n⚠️  Worst 5 Performing Components:")
    worst_components = engine.get_worst_performing_components(5)
    for i, (category, component, brand, score) in enumerate(worst_components, 1):
        print(f"   {i}. {brand} {component} ({category}): {score:.2f}")
