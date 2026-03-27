import requests
import json
import logging
import time
import random
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urljoin, quote
from datetime import datetime, timedelta
import re

# Try to import BeautifulSoup
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
    logger = logging.getLogger(__name__)
except ImportError:
    BS4_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("BeautifulSoup not available. Web scraping functionality will be limited.")

# Try to import Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Selenium not available. Dynamic content scraping will be limited.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    """
    Web scraper for fetching latest reviews and pricing from Amazon.
    Supports both requests+BeautifulSoup and Selenium for dynamic content.
    """
    
    def __init__(self, use_selenium: bool = False, headless: bool = True):
        """
        Initialize the web scraper.
        
        Args:
            use_selenium: Whether to use Selenium for dynamic content
            headless: Whether to run browser in headless mode (Selenium only)
        """
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.headless = headless
        self.session = requests.Session()
        self.driver = None
        self.scraped_data = {}
        
        # Amazon-specific configurations
        self.amazon_base_url = "https://www.amazon.com"
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        
        # Set up session headers
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Initialize Selenium if requested
        if self.use_selenium:
            self._initialize_selenium()
        
        logger.info(f"Web scraper initialized (Selenium: {self.use_selenium})")
    
    def _initialize_selenium(self) -> None:
        """Initialize Selenium WebDriver."""
        try:
            options = Options()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument(f'--user-agent={self.user_agent}')
            
            # Disable images for faster scraping
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
            
            self.driver = webdriver.Chrome(options=options)
            logger.info("Selenium WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Selenium: {e}")
            self.use_selenium = False
            logger.info("Falling back to requests + BeautifulSoup")
    
    def search_amazon_product(self, search_query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for products on Amazon.
        
        Args:
            search_query: Product search query
            max_results: Maximum number of results to return
            
        Returns:
            List of product search results
        """
        logger.info(f"Searching Amazon for: {search_query}")
        
        # Construct search URL
        search_url = f"{self.amazon_base_url}/s"
        params = {
            'k': search_query,
            'ref': 'nb_sb_noss',
            'page': 1
        }
        
        try:
            if self.use_selenium:
                products = self._search_with_selenium(search_url, params, max_results)
            else:
                products = self._search_with_requests(search_url, params, max_results)
            
            logger.info(f"Found {len(products)} products for '{search_query}'")
            return products
            
        except Exception as e:
            logger.error(f"Error searching Amazon: {e}")
            return []
    
    def _search_with_selenium(self, search_url: str, params: Dict[str, Any], 
                           max_results: int) -> List[Dict[str, Any]]:
        """Search using Selenium WebDriver."""
        products = []
        
        try:
            # Navigate to search page
            full_url = f"{search_url}?" + "&".join([f"{k}={quote(str(v))}" for k, v in params.items()])
            self.driver.get(full_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-component-type='s-search-result']"))
            )
            
            # Scroll to load more results
            self._scroll_page()
            
            # Extract product information
            product_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-component-type='s-search-result']")
            
            for element in product_elements[:max_results]:
                try:
                    product_info = self._extract_product_info_selenium(element)
                    if product_info:
                        products.append(product_info)
                except Exception as e:
                    logger.warning(f"Error extracting product info: {e}")
                    continue
            
        except TimeoutException:
            logger.error("Timeout waiting for search results to load")
        except Exception as e:
            logger.error(f"Error in Selenium search: {e}")
        
        return products
    
    def _search_with_requests(self, search_url: str, params: Dict[str, Any], 
                           max_results: int) -> List[Dict[str, Any]]:
        """Search using requests + BeautifulSoup."""
        products = []
        
        try:
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product information
            product_elements = soup.find_all(['div'], {'data-component-type': 's-search-result'})
            
            for element in product_elements[:max_results]:
                try:
                    product_info = self._extract_product_info_bs4(element)
                    if product_info:
                        products.append(product_info)
                except Exception as e:
                    logger.warning(f"Error extracting product info: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in requests search: {e}")
        
        return products
    
    def _extract_product_info_selenium(self, element) -> Optional[Dict[str, Any]]:
        """Extract product information using Selenium."""
        try:
            # Product title
            title_elem = element.find_element(By.CSS_SELECTOR, "h2 a span")
            title = title_elem.text.strip()
            
            # Product URL
            url_elem = element.find_element(By.CSS_SELECTOR, "h2 a")
            url = url_elem.get_attribute('href')
            if url:
                url = urljoin(self.amazon_base_url, url)
            
            # Price
            price = self._extract_price_selenium(element)
            
            # Rating
            rating = self._extract_rating_selenium(element)
            
            # Number of reviews
            num_reviews = self._extract_num_reviews_selenium(element)
            
            # Product image
            image = self._extract_image_selenium(element)
            
            return {
                'title': title,
                'url': url,
                'price': price,
                'rating': rating,
                'num_reviews': num_reviews,
                'image': image,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Error extracting product info with Selenium: {e}")
            return None
    
    def _extract_product_info_bs4(self, element) -> Optional[Dict[str, Any]]:
        """Extract product information using BeautifulSoup."""
        try:
            # Product title
            title_elem = element.find('h2')
            if title_elem:
                title_link = title_elem.find('a')
                if title_link:
                    title_span = title_link.find('span')
                    title = title_span.text.strip() if title_span else title_link.text.strip()
                    url = title_link.get('href')
                    if url:
                        url = urljoin(self.amazon_base_url, url)
                else:
                    title = title_elem.text.strip()
                    url = None
            else:
                return None
            
            # Price
            price = self._extract_price_bs4(element)
            
            # Rating
            rating = self._extract_rating_bs4(element)
            
            # Number of reviews
            num_reviews = self._extract_num_reviews_bs4(element)
            
            # Product image
            image = self._extract_image_bs4(element)
            
            return {
                'title': title,
                'url': url,
                'price': price,
                'rating': rating,
                'num_reviews': num_reviews,
                'image': image,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Error extracting product info with BeautifulSoup: {e}")
            return None
    
    def _extract_price_selenium(self, element) -> Optional[float]:
        """Extract price using Selenium."""
        try:
            price_elem = element.find_element(By.CSS_SELECTOR, ".a-price-whole")
            price_text = price_elem.text.strip()
            
            # Remove currency symbols and convert to float
            price_clean = re.sub(r'[^\d.]', '', price_text)
            return float(price_clean) if price_clean else None
            
        except:
            try:
                # Alternative price selector
                price_elem = element.find_element(By.CSS_SELECTOR, ".a-price")
                price_text = price_elem.text.strip()
                price_clean = re.sub(r'[^\d.]', '', price_text)
                return float(price_clean) if price_clean else None
            except:
                return None
    
    def _extract_price_bs4(self, element) -> Optional[float]:
        """Extract price using BeautifulSoup."""
        try:
            price_elem = element.find('span', class_='a-price-whole')
            if price_elem:
                price_text = price_elem.text.strip()
                price_clean = re.sub(r'[^\d.]', '', price_text)
                return float(price_clean) if price_clean else None
            
            # Alternative price selector
            price_elem = element.find('span', class_='a-price')
            if price_elem:
                price_text = price_elem.text.strip()
                price_clean = re.sub(r'[^\d.]', '', price_text)
                return float(price_clean) if price_clean else None
            
            return None
            
        except:
            return None
    
    def _extract_rating_selenium(self, element) -> Optional[float]:
        """Extract rating using Selenium."""
        try:
            rating_elem = element.find_element(By.CSS_SELECTOR, "[aria-label*='stars']")
            rating_text = rating_elem.get_attribute('aria-label')
            
            # Extract rating from text like "4.5 out of 5 stars"
            rating_match = re.search(r'(\d+\.?\d*)\s*out of', rating_text)
            return float(rating_match.group(1)) if rating_match else None
            
        except:
            return None
    
    def _extract_rating_bs4(self, element) -> Optional[float]:
        """Extract rating using BeautifulSoup."""
        try:
            rating_elem = element.find('span', attrs={'aria-label': True})
            if rating_elem:
                rating_text = rating_elem.get('aria-label', '')
                rating_match = re.search(r'(\d+\.?\d*)\s*out of', rating_text)
                return float(rating_match.group(1)) if rating_match else None
            
            return None
            
        except:
            return None
    
    def _extract_num_reviews_selenium(self, element) -> Optional[int]:
        """Extract number of reviews using Selenium."""
        try:
            reviews_elem = element.find_element(By.CSS_SELECTOR, "[aria-label*='reviews']")
            reviews_text = reviews_elem.get_attribute('aria-label')
            
            # Extract number from text like "1,234 reviews"
            reviews_match = re.search(r'([\d,]+)\s*reviews?', reviews_text)
            if reviews_match:
                reviews_clean = reviews_match.group(1).replace(',', '')
                return int(reviews_clean)
            
            return None
            
        except:
            return None
    
    def _extract_num_reviews_bs4(self, element) -> Optional[int]:
        """Extract number of reviews using BeautifulSoup."""
        try:
            reviews_elem = element.find('a', attrs={'aria-label': True})
            if reviews_elem:
                reviews_text = reviews_elem.get('aria-label', '')
                reviews_match = re.search(r'([\d,]+)\s*reviews?', reviews_text)
                if reviews_match:
                    reviews_clean = reviews_match.group(1).replace(',', '')
                    return int(reviews_clean)
            
            return None
            
        except:
            return None
    
    def _extract_image_selenium(self, element) -> Optional[str]:
        """Extract product image using Selenium."""
        try:
            img_elem = element.find_element(By.CSS_SELECTOR, "img")
            return img_elem.get_attribute('src')
        except:
            return None
    
    def _extract_image_bs4(self, element) -> Optional[str]:
        """Extract product image using BeautifulSoup."""
        try:
            img_elem = element.find('img')
            return img_elem.get('src') if img_elem else None
        except:
            return None
    
    def get_product_reviews(self, product_url: str, max_reviews: int = 50) -> List[Dict[str, Any]]:
        """
        Get reviews for a specific product.
        
        Args:
            product_url: Amazon product page URL
            max_reviews: Maximum number of reviews to fetch
            
        Returns:
            List of review data
        """
        logger.info(f"Fetching reviews for product: {product_url}")
        
        reviews = []
        
        try:
            if self.use_selenium:
                reviews = self._get_reviews_selenium(product_url, max_reviews)
            else:
                reviews = self._get_reviews_requests(product_url, max_reviews)
            
            logger.info(f"Successfully fetched {len(reviews)} reviews")
            return reviews
            
        except Exception as e:
            logger.error(f"Error fetching reviews: {e}")
            return []
    
    def _get_reviews_selenium(self, product_url: str, max_reviews: int) -> List[Dict[str, Any]]:
        """Get reviews using Selenium."""
        reviews = []
        
        try:
            self.driver.get(product_url)
            
            # Click on "See all reviews" if present
            try:
                see_all_reviews = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-hook='see-all-reviews-link-foot'] a"))
                )
                see_all_reviews.click()
                time.sleep(2)
            except TimeoutException:
                # Already on reviews page or no reviews link
                pass
            
            # Extract reviews from multiple pages
            page = 1
            while len(reviews) < max_reviews:
                try:
                    # Wait for reviews to load
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-hook='review']"))
                    )
                    
                    # Extract reviews from current page
                    review_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-hook='review']")
                    
                    for element in review_elements:
                        if len(reviews) >= max_reviews:
                            break
                        
                        review_data = self._extract_review_data_selenium(element)
                        if review_data:
                            reviews.append(review_data)
                    
                    # Check if there's a next page
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, "li.a-last a")
                        if 'aria-disabled' in next_button.get_attribute('class'):
                            break  # No more pages
                        
                        next_button.click()
                        time.sleep(random.uniform(2, 4))  # Random delay
                        page += 1
                        
                        if page > 10:  # Safety limit
                            break
                            
                    except:
                        break  # No next page found
                        
                except TimeoutException:
                    logger.warning(f"Timeout on page {page}")
                    break
            
        except Exception as e:
            logger.error(f"Error getting reviews with Selenium: {e}")
        
        return reviews
    
    def _get_reviews_requests(self, product_url: str, max_reviews: int) -> List[Dict[str, Any]]:
        """Get reviews using requests + BeautifulSoup."""
        reviews = []
        
        try:
            # Navigate to reviews page
            reviews_url = product_url.replace('/dp/', '/product-reviews/') + "/ref=cm_cr_dp_d_show_all_btm"
            
            page = 1
            while len(reviews) < max_reviews:
                try:
                    params = {'pageNumber': page, 'reviewerType': 'all_reviews'}
                    response = self.session.get(reviews_url, params=params)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract reviews
                    review_elements = soup.find_all(['div'], {'data-hook': 'review'})
                    
                    if not review_elements:
                        break  # No more reviews found
                    
                    for element in review_elements:
                        if len(reviews) >= max_reviews:
                            break
                        
                        review_data = self._extract_review_data_bs4(element)
                        if review_data:
                            reviews.append(review_data)
                    
                    # Check if there's a next page
                    next_page = soup.find('li', class_='a-last')
                    if not next_page or 'a-disabled' in next_page.get('class', []):
                        break
                    
                    page += 1
                    time.sleep(random.uniform(1, 3))  # Random delay
                    
                    if page > 10:  # Safety limit
                        break
                        
                except Exception as e:
                    logger.error(f"Error on page {page}: {e}")
                    break
            
        except Exception as e:
            logger.error(f"Error getting reviews with requests: {e}")
        
        return reviews
    
    def _extract_review_data_selenium(self, element) -> Optional[Dict[str, Any]]:
        """Extract review data using Selenium."""
        try:
            # Rating
            rating_elem = element.find_element(By.CSS_SELECTOR, "[data-hook='review-star-rating']")
            rating_text = rating_elem.text.strip()
            rating_match = re.search(r'(\d+\.?\d*)\s*out of', rating_text)
            rating = float(rating_match.group(1)) if rating_match else None
            
            # Title
            try:
                title_elem = element.find_element(By.CSS_SELECTOR, "[data-hook='review-title'] span")
                title = title_elem.text.strip()
            except:
                title = ""
            
            # Review text
            try:
                review_text_elem = element.find_element(By.CSS_SELECTOR, "[data-hook='review-body'] span")
                review_text = review_text_elem.text.strip()
            except:
                review_text = ""
            
            # Date
            try:
                date_elem = element.find_element(By.CSS_SELECTOR, "[data-hook='review-date']")
                date_text = date_elem.text.strip()
                date = self._parse_review_date(date_text)
            except:
                date = None
            
            # Reviewer
            try:
                reviewer_elem = element.find_element(By.CSS_SELECTOR, "[data-hook='review-author']")
                reviewer = reviewer_elem.text.strip()
            except:
                reviewer = "Anonymous"
            
            # Verified purchase
            try:
                verified_elem = element.find_element(By.CSS_SELECTOR, "[data-hook='avp-badge']")
                verified = len(verified_elem.text.strip()) > 0
            except:
                verified = False
            
            return {
                'rating': rating,
                'title': title,
                'review_text': review_text,
                'date': date,
                'reviewer': reviewer,
                'verified_purchase': verified,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Error extracting review data with Selenium: {e}")
            return None
    
    def _extract_review_data_bs4(self, element) -> Optional[Dict[str, Any]]:
        """Extract review data using BeautifulSoup."""
        try:
            # Rating
            rating_elem = element.find('i', {'data-hook': 'review-star-rating'})
            rating_text = rating_elem.text.strip() if rating_elem else ""
            rating_match = re.search(r'(\d+\.?\d*)\s*out of', rating_text)
            rating = float(rating_match.group(1)) if rating_match else None
            
            # Title
            title_elem = element.find('a', {'data-hook': 'review-title'})
            title = title_elem.text.strip() if title_elem else ""
            
            # Review text
            review_text_elem = element.find('span', {'data-hook': 'review-body'})
            review_text = review_text_elem.text.strip() if review_text_elem else ""
            
            # Date
            date_elem = element.find('span', {'data-hook': 'review-date'})
            date_text = date_elem.text.strip() if date_elem else ""
            date = self._parse_review_date(date_text)
            
            # Reviewer
            reviewer_elem = element.find('div', {'data-hook': 'review-author'})
            reviewer = reviewer_elem.text.strip() if reviewer_elem else "Anonymous"
            
            # Verified purchase
            verified_elem = element.find('span', {'data-hook': 'avp-badge'})
            verified = len(verified_elem.text.strip()) > 0 if verified_elem else False
            
            return {
                'rating': rating,
                'title': title,
                'review_text': review_text,
                'date': date,
                'reviewer': reviewer,
                'verified_purchase': verified,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Error extracting review data with BeautifulSoup: {e}")
            return None
    
    def _parse_review_date(self, date_text: str) -> Optional[str]:
        """Parse review date string to ISO format."""
        try:
            # Handle various Amazon date formats
            # Example: "Reviewed in the United States on October 25, 2023"
            # Example: "Reviewed in India on March 15, 2023"
            
            date_match = re.search(r'on (\w+)\s+(\d+),\s+(\d{4})', date_text)
            if date_match:
                month, day, year = date_match.groups()
                month_num = datetime.strptime(month, '%B').month
                date_obj = datetime(int(year), month_num, int(day))
                return date_obj.isoformat()
            
            return date_text  # Return original if parsing fails
            
        except:
            return date_text
    
    def _scroll_page(self):
        """Scroll page to load dynamic content."""
        if self.use_selenium:
            try:
                # Scroll down to bottom of page
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Scroll back up
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
            except:
                pass
    
    def append_to_dataset(self, scraped_data: Dict[str, Any], 
                         existing_file: str = 'scraped_reviews.json') -> None:
        """
        Append scraped data to existing dataset.
        
        Args:
            scraped_data: New scraped data
            existing_file: Path to existing dataset file
        """
        try:
            # Load existing data
            existing_data = []
            try:
                with open(existing_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = []
            except FileNotFoundError:
                logger.info(f"Creating new dataset file: {existing_file}")
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in {existing_file}, creating new file")
                existing_data = []
            
            # Append new data
            if isinstance(scraped_data, list):
                existing_data.extend(scraped_data)
            else:
                existing_data.append(scraped_data)
            
            # Save updated data
            with open(existing_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Appended {len(scraped_data) if isinstance(scraped_data, list) else 1} items to dataset")
            
        except Exception as e:
            logger.error(f"Error appending to dataset: {e}")
            raise
    
    def save_scraped_data(self, data: Dict[str, Any], 
                         filename: str = 'scraped_reviews.json') -> None:
        """
        Save scraped data to JSON file.
        
        Args:
            data: Scraped data to save
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Scraped data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving scraped data: {e}")
            raise
    
    def scrape_product_data(self, search_query: str, max_products: int = 5, 
                           max_reviews_per_product: int = 20) -> Dict[str, Any]:
        """
        Complete scraping pipeline for product data and reviews.
        
        Args:
            search_query: Product search query
            max_products: Maximum number of products to scrape
            max_reviews_per_product: Maximum reviews per product
            
        Returns:
            Complete scraped data
        """
        logger.info(f"Starting complete scraping for: {search_query}")
        
        scraped_data = {
            'search_query': search_query,
            'scraped_at': datetime.now().isoformat(),
            'products': [],
            'total_reviews': 0
        }
        
        try:
            # Search for products
            products = self.search_amazon_product(search_query, max_products)
            
            for i, product in enumerate(products[:max_products], 1):
                logger.info(f"Scraping product {i}/{len(products)}: {product['title'][:50]}...")
                
                # Get reviews for this product
                if product.get('url'):
                    reviews = self.get_product_reviews(product['url'], max_reviews_per_product)
                    product['reviews'] = reviews
                    scraped_data['total_reviews'] += len(reviews)
                else:
                    product['reviews'] = []
                
                scraped_data['products'].append(product)
                
                # Random delay between products
                time.sleep(random.uniform(2, 5))
            
            # Save scraped data
            self.save_scraped_data(scraped_data)
            
            # Also append to existing dataset
            self.append_to_dataset(scraped_data)
            
            logger.info(f"Scraping completed: {len(scraped_data['products'])} products, {scraped_data['total_reviews']} reviews")
            
            return scraped_data
            
        except Exception as e:
            logger.error(f"Error in scraping pipeline: {e}")
            raise
    
    def close(self):
        """Clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        if self.session:
            try:
                self.session.close()
            except:
                pass
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

# Example usage
if __name__ == "__main__":
    # Example usage
    with WebScraper(use_selenium=False) as scraper:
        # Scrape product data
        data = scraper.scrape_product_data(
            search_query="Sony WH-1000XM4 headphones",
            max_products=3,
            max_reviews_per_product=10
        )
        
        print(f"Scraped {len(data['products'])} products")
        print(f"Total reviews: {data['total_reviews']}")
        
        # Display sample data
        for product in data['products']:
            print(f"\nProduct: {product['title']}")
            print(f"Price: ${product.get('price', 'N/A')}")
            print(f"Rating: {product.get('rating', 'N/A')}")
            print(f"Reviews: {len(product.get('reviews', []))}")
