"""
ai_component_generator.py
AI-based component generation using LLM knowledge.
Generates real product components without extracting from reviews.
"""
import re
import logging
import json
from typing import Dict, List, Any, Optional
from product_aspect_analyzer import ProductAspectAnalyzer

logger = logging.getLogger(__name__)

class AIComponentGenerator:
    """Generate product components using AI/LLM knowledge."""
    
    def __init__(self, llm_client=None):
        """
        Initialize the AI component generator.
        
        Args:
            llm_client: Optional LLM client (OpenAI, Anthropic, etc.)
        """
        self.llm_client = llm_client
        self.aspect_analyzer = ProductAspectAnalyzer()
        
        # Fallback component knowledge base for common categories
        self.component_knowledge = {
            "laptop": [
                "CPU", "RAM", "Storage", "Display", "Graphics Card", 
                "Battery", "Keyboard", "Trackpad", "Webcam", "Speakers",
                "Ports", "Cooling System", "Chassis", "Power Adapter"
            ],
            "smartphone": [
                "Processor", "RAM", "Storage", "Display", "Camera",
                "Battery", "Speakers", "Microphone", "Ports", "Sensors",
                "Glass", "Frame", "Charging Port", "Buttons"
            ],
            "headphones": [
                "Drivers", "Cable", "Ear Pads", "Headband", "Microphone",
                "Controls", "Battery", "Charging Port", "Connectivity Module"
            ],
            "tablet": [
                "Processor", "RAM", "Storage", "Display", "Battery",
                "Cameras", "Speakers", "Microphones", "Ports", "Sensors",
                "Glass", "Frame", "Connectivity"
            ],
            "tv": [
                "Display Panel", "Processor", "RAM", "Storage", "Speakers",
                "Ports", "Stand", "Remote", "Power Supply", "Tuner",
                "Smart TV Module", "Connectivity"
            ],
            "camera": [
                "Sensor", "Lens", "Processor", "Viewfinder", "Display",
                "Battery", "Memory Card Slot", "Ports", "Body", "Dial",
                "Buttons", "Flash", "Image Stabilization"
            ],
            "smartwatch": [
                "Processor", "RAM", "Storage", "Display", "Sensors",
                "Battery", "Band", "Crown", "Buttons", "Connectivity",
                "Charging Port", "Glass", "Frame"
            ],
            "desktop": [
                "CPU", "Motherboard", "RAM", "Storage", "Graphics Card",
                "Power Supply", "Case", "Cooling System", "Ports",
                "Optical Drive", "Fans", "Cables"
            ],
            "monitor": [
                "Display Panel", "Stand", "Ports", "Power Supply",
                "Controls", "Speakers", "Bezel", "Panel Technology"
            ],
            "speaker": [
                "Drivers", "Cabinet", "Crossover", "Ports", "Grille",
                "Amplifier", "Power Supply", "Controls", "Connectivity"
            ]
        }
    
    def _infer_product_category(self, search_query: str) -> str:
        """Infer product category from search query."""
        query = search_query.lower().strip()
        
        # Category mapping
        category_keywords = {
            "laptop": ["laptop", "notebook", "macbook", "chromebook"],
            "smartphone": ["smartphone", "phone", "iphone", "android", "galaxy"],
            "headphones": ["headphone", "earphone", "earbud", "airpod", "beats"],
            "tablet": ["tablet", "ipad", "kindle", "galaxy tab"],
            "tv": ["tv", "television", "monitor", "display"],
            "camera": ["camera", "dslr", "mirrorless", "gopro", "webcam"],
            "smartwatch": ["smartwatch", "fitness tracker", "fitbit", "garmin", "apple watch"],
            "desktop": ["desktop", "pc", "computer", "tower"],
            "monitor": ["monitor", "display", "screen"],
            "speaker": ["speaker", "audio", "sound system", "bluetooth speaker"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in query for keyword in keywords):
                return category
        
        return "general"
    
    def _generate_components_with_llm(self, search_query: str) -> List[str]:
        """
        Generate components using LLM.
        
        Args:
            search_query: Product search query
            
        Returns:
            List of component names
        """
        if not self.llm_client:
            logger.warning("No LLM client provided, using fallback knowledge base")
            return self._get_fallback_components(search_query)
        
        try:
            # Create prompt for LLM
            prompt = f"""List the main physical components of a {search_query}.
Return only component names as a list.
Focus on hardware parts and physical elements.
Do not include software, features, or abstract concepts.
Keep it concise and technical."""
            
            # Call LLM (implementation depends on the specific LLM client)
            response = self._call_llm(prompt)
            
            # Parse response into list
            components = self._parse_llm_response(response)
            
            logger.info(f"Generated {len(components)} components using LLM for: {search_query}")
            return components
            
        except Exception as e:
            logger.error(f"LLM component generation failed: {e}")
            return self._get_fallback_components(search_query)
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call the LLM with the given prompt.
        This method should be implemented based on the specific LLM client.
        
        Args:
            prompt: The prompt to send to LLM
            
        Returns:
            LLM response text
        """
        if hasattr(self.llm_client, 'chat'):
            # OpenAI-like API
            response = self.llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0
            )
            return response.choices[0].message.content
        
        elif hasattr(self.llm_client, 'generate'):
            # Generic generate method
            response = self.llm_client.generate(
                prompt=prompt,
                max_tokens=150,
                temperature=0
            )
            return response.text
        
        else:
            raise ValueError("Unsupported LLM client interface")
    
    def _parse_llm_response(self, response: str) -> List[str]:
        """
        Parse LLM response into a clean list of components.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Clean list of component names
        """
        # Remove common formatting
        response = response.strip()
        
        # Try to extract list items
        components = []
        
        # Look for numbered lists
        numbered_items = re.findall(r'^\d+\.\s*(.+)$', response, re.MULTILINE)
        if numbered_items:
            components = [item.strip() for item in numbered_items]
        
        # Look for bullet points
        elif re.search(r'^[-*•]\s*', response, re.MULTILINE):
            bullet_items = re.findall(r'^[-*•]\s*(.+)$', response, re.MULTILINE)
            components = [item.strip() for item in bullet_items]
        
        # Look for comma-separated values
        elif ',' in response:
            components = [item.strip() for item in response.split(',')]
        
        # Split by newlines
        elif '\n' in response:
            components = [line.strip() for line in response.split('\n') if line.strip()]
        
        # Single line - try to split by common separators
        else:
            components = [response.strip()]
        
        # Clean up components
        cleaned_components = []
        for component in components:
            # Remove quotes and extra punctuation
            component = component.strip('\'".,;:()[]{}')
            # Remove numbering if still present
            component = re.sub(r'^\d+\.\s*', '', component)
            # Remove bullet points if still present
            component = re.sub(r'^[-*•]\s*', '', component)
            
            if component and len(component) > 2:
                cleaned_components.append(component)
        
        return cleaned_components
    
    def _get_fallback_components(self, search_query: str) -> List[str]:
        """
        Get components from fallback knowledge base.
        
        Args:
            search_query: Product search query
            
        Returns:
            List of component names
        """
        category = self._infer_product_category(search_query)
        components = self.component_knowledge.get(category, [])
        
        if not components:
            # Default general components
            components = [
                "Processor", "Memory", "Storage", "Display", "Battery",
                "Connectivity", "Controls", "Casing", "Power Supply"
            ]
        
        logger.info(f"Used fallback components for category '{category}': {len(components)} components")
        return components
    
    def generate_components(self, search_query: str, use_llm: bool = True) -> List[str]:
        """
        Generate components for a product.
        
        Args:
            search_query: Product search query (e.g., "laptop")
            use_llm: Whether to use LLM or fallback knowledge base
            
        Returns:
            List of component names
        """
        search_query = search_query.strip()
        if not search_query:
            return ["Processor", "Memory", "Storage", "Display", "Battery"]
        
        if use_llm and self.llm_client:
            return self._generate_components_with_llm(search_query)
        else:
            return self._get_fallback_components(search_query)
    
    def generate_aspects_from_reviews(self, reviews: List[str]) -> List[str]:
        """
        Generate aspects from reviews using the existing aspect analyzer.
        
        Args:
            reviews: List of review texts
            
        Returns:
            List of aspect names
        """
        return self.aspect_analyzer.extract_aspects(reviews)
    
    def analyze_product(
        self,
        search_query: str,
        reviews: List[str] = None,
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        Complete product analysis: AI components + review aspects.
        
        Args:
            search_query: Product search query
            reviews: List of review texts
            use_llm: Whether to use LLM for component generation
            
        Returns:
            Dictionary with components and aspects
        """
        if reviews is None:
            reviews = []
        
        # Generate components using AI knowledge
        components = self.generate_components(search_query, use_llm)
        
        # Generate aspects from reviews
        aspects = self.generate_aspects_from_reviews(reviews)
        
        result = {
            "search_query": search_query,
            "components": components,
            "aspects": aspects,
            "component_count": len(components),
            "aspect_count": len(aspects),
            "review_count": len(reviews),
            "generation_method": "llm" if use_llm and self.llm_client else "fallback"
        }
        
        logger.info(f"Generated {len(components)} components and {len(aspects)} aspects for: {search_query}")
        
        return result

# Convenience function for quick usage
def generate_ai_components(
    search_query: str,
    reviews: List[str] = None,
    llm_client=None,
    use_llm: bool = True
) -> Dict[str, List[str]]:
    """
    Quick function to generate AI components and review aspects.
    
    Args:
        search_query: Product search query
        reviews: List of review texts
        llm_client: Optional LLM client
        use_llm: Whether to use LLM
        
    Returns:
        Dictionary with components and aspects
    """
    generator = AIComponentGenerator(llm_client)
    result = generator.analyze_product(search_query, reviews, use_llm)
    
    return {
        "components": result["components"],
        "aspects": result["aspects"]
    }
