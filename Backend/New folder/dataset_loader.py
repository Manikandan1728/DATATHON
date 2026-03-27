import pandas as pd
import json
import re
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatasetLoader:
    """
    A comprehensive dataset loader for AI competitive intelligence system.
    Loads, processes, and merges Amazon electronics datasets.
    """
    
    def __init__(self):
        self.required_columns = {
            'product_name', 'brand', 'category', 'review_text', 'rating', 'review_date'
        }
        self.product_categories = [
            'Headphones', 'Smartphones', 'Laptops', 'Speakers', 'Smartwatches'
        ]
        self.datasets = {}
        self.processed_data = {}
        
    def load_datasets(self, file_paths: Dict[str, str]) -> None:
        """
        Load the three datasets using pandas.
        
        Args:
            file_paths: Dictionary with dataset names as keys and file paths as values
        """
        dataset_names = [
            'amazon_electronics_master_dataset',
            'amazon_electronics_reviews_cleaned', 
            'amazon_reviews_cleaned_4M'
        ]
        
        for dataset_name in dataset_names:
            if dataset_name in file_paths:
                try:
                    logger.info(f"Loading {dataset_name}...")
                    df = pd.read_csv(file_paths[dataset_name])
                    self.datasets[dataset_name] = df
                    logger.info(f"Successfully loaded {dataset_name}: {len(df)} rows")
                except Exception as e:
                    logger.error(f"Error loading {dataset_name}: {str(e)}")
                    raise
            else:
                logger.warning(f"File path not provided for {dataset_name}")
    
    def inspect_columns(self) -> Dict[str, List[str]]:
        """
        Inspect columns in all datasets and detect required columns.
        
        Returns:
            Dictionary with dataset names as keys and column lists as values
        """
        column_info = {}
        
        for dataset_name, df in self.datasets.items():
            columns = df.columns.tolist()
            column_info[dataset_name] = columns
            
            # Check for required columns (case-insensitive)
            found_columns = set()
            for req_col in self.required_columns:
                for col in columns:
                    if req_col.lower() in col.lower():
                        found_columns.add(req_col)
                        break
            
            missing = self.required_columns - found_columns
            if missing:
                logger.warning(f"{dataset_name} missing columns: {missing}")
            else:
                logger.info(f"{dataset_name} has all required columns")
        
        return column_info
    
    def detect_and_rename_columns(self) -> None:
        """
        Detect and rename columns to standard names.
        """
        column_mappings = {
            'product_name': ['product_name', 'product', 'title', 'product_title', 'item_name'],
            'brand': ['brand', 'manufacturer', 'company', 'make'],
            'category': ['category', 'product_category', 'type', 'subcategory'],
            'review_text': ['review_text', 'review', 'review_body', 'content', 'text'],
            'rating': ['rating', 'star_rating', 'stars', 'score'],
            'review_date': ['review_date', 'date', 'timestamp', 'review_time']
        }
        
        for dataset_name, df in self.datasets.items():
            rename_dict = {}
            columns = df.columns.tolist()
            
            for standard_name, possible_names in column_mappings.items():
                for col in columns:
                    if col.lower() in [name.lower() for name in possible_names]:
                        rename_dict[col] = standard_name
                        break
            
            if rename_dict:
                self.datasets[dataset_name] = df.rename(columns=rename_dict)
                logger.info(f"Renamed columns in {dataset_name}: {rename_dict}")
    
    def clean_data(self) -> None:
        """
        Remove invalid or empty reviews and perform basic data cleaning.
        """
        for dataset_name, df in self.datasets.items():
            original_count = len(df)
            
            # Remove rows with empty review_text
            if 'review_text' in df.columns:
                df = df.dropna(subset=['review_text'])
                df = df[df['review_text'].str.strip() != '']
            
            # Remove rows with invalid ratings
            if 'rating' in df.columns:
                df = df.dropna(subset=['rating'])
                df = df[df['rating'].between(1, 5)]
            
            # Remove rows with missing essential fields
            essential_fields = ['product_name', 'brand']
            for field in essential_fields:
                if field in df.columns:
                    df = df.dropna(subset=[field])
                    df = df[df[field].str.strip() != '']
            
            cleaned_count = len(df)
            logger.info(f"Cleaned {dataset_name}: removed {original_count - cleaned_count} rows")
            
            self.datasets[dataset_name] = df
    
    def normalize_brand_names(self) -> None:
        """
        Normalize brand names (e.g., Sony, SONY → Sony).
        """
        for dataset_name, df in self.datasets.items():
            if 'brand' in df.columns:
                # Convert to title case and handle common variations
                df['brand'] = df['brand'].astype(str).str.title().str.strip()
                
                # Handle specific brand variations
                brand_corrections = {
                    'Sony': 'Sony',
                    'Apple': 'Apple', 
                    'Samsung': 'Samsung',
                    'Bose': 'Bose',
                    'Jbl': 'JBL',
                    'Jbl': 'JBL',
                    'Hp': 'HP',
                    'Dell': 'Dell',
                    'Lenovo': 'Lenovo',
                    'LG': 'LG',
                    'Panasonic': 'Panasonic'
                }
                
                for incorrect, correct in brand_corrections.items():
                    df['brand'] = df['brand'].replace([incorrect, incorrect.upper(), incorrect.lower()], correct)
                
                logger.info(f"Normalized brand names in {dataset_name}")
    
    def extract_product_categories(self) -> None:
        """
        Extract product categories based on product names and categories.
        """
        category_keywords = {
            'Headphones': ['headphone', 'earphone', 'earbud', 'in-ear', 'over-ear', 'on-ear', 'audio'],
            'Smartphones': ['phone', 'smartphone', 'mobile', 'cell phone', 'iphone', 'android'],
            'Laptops': ['laptop', 'notebook', 'computer', 'pc', 'macbook', 'ultrabook'],
            'Speakers': ['speaker', 'bluetooth speaker', 'sound system', 'audio speaker', 'portable speaker'],
            'Smartwatches': ['watch', 'smartwatch', 'fitness tracker', 'wearable', 'apple watch']
        }
        
        for dataset_name, df in self.datasets.items():
            if 'category' in df.columns:
                df['extracted_category'] = df['category'].astype(str).str.lower()
            else:
                df['extracted_category'] = ''
            
            if 'product_name' in df.columns:
                product_names = df['product_name'].astype(str).str.lower()
                
                for category, keywords in category_keywords.items():
                    # Check if any keywords match in product name or category
                    mask = (df['extracted_category'].str.contains('|'.join(keywords), case=False, na=False) | 
                           product_names.str.contains('|'.join(keywords), case=False, na=False))
                    df.loc[mask, 'extracted_category'] = category
            
            # Set default category for unmatched items
            df.loc[df['extracted_category'] == '', 'extracted_category'] = 'Other'
            
            logger.info(f"Extracted categories in {dataset_name}")
    
    def merge_product_reviews(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Merge product metadata with reviews and structure the output.
        
        Returns:
            Nested dictionary structure: {category: {product_name: {brand: "", reviews: []}}}
        """
        # Combine all datasets
        all_data = pd.concat(self.datasets.values(), ignore_index=True)
        
        # Group by category, product_name, and brand
        result = {}
        
        for category in all_data['extracted_category'].unique():
            category_data = all_data[all_data['extracted_category'] == category]
            result[category] = {}
            
            for product_name in category_data['product_name'].unique():
                product_data = category_data[category_data['product_name'] == product_name]
                
                # Get brand for this product
                brand = product_data['brand'].iloc[0] if not product_data['brand'].empty else 'Unknown'
                
                # Collect reviews
                reviews = []
                for _, review in product_data.iterrows():
                    review_dict = {
                        'review_text': review.get('review_text', ''),
                        'rating': review.get('rating', 0),
                        'review_date': review.get('review_date', '')
                    }
                    reviews.append(review_dict)
                
                result[category][product_name] = {
                    'brand': brand,
                    'reviews': reviews
                }
        
        self.processed_data = result
        logger.info(f"Merged data into {len(result)} categories")
        return result
    
    def save_processed_data(self, output_file: str = 'processed_product_reviews.json') -> None:
        """
        Save processed data as JSON file.
        
        Args:
            output_file: Output file name
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.processed_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved processed data to {output_file}")
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
            raise
    
    def process_all_datasets(self, file_paths: Dict[str, str], output_file: str = 'processed_product_reviews.json') -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Complete pipeline to process all datasets.
        
        Args:
            file_paths: Dictionary with dataset names as keys and file paths as values
            output_file: Output file name
            
        Returns:
            Processed data structure
        """
        try:
            # Load datasets
            self.load_datasets(file_paths)
            
            # Inspect and rename columns
            self.inspect_columns()
            self.detect_and_rename_columns()
            
            # Clean data
            self.clean_data()
            
            # Normalize brands
            self.normalize_brand_names()
            
            # Extract categories
            self.extract_product_categories()
            
            # Merge and structure data
            result = self.merge_product_reviews()
            
            # Save to file
            self.save_processed_data(output_file)
            
            logger.info("Dataset processing completed successfully!")
            return result
            
        except Exception as e:
            logger.error(f"Error in processing pipeline: {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    # Example file paths - replace with actual paths
    file_paths = {
        'amazon_electronics_master_dataset': 'path/to/amazon_electronics_master_dataset.csv',
        'amazon_electronics_reviews_cleaned': 'path/to/amazon_electronics_reviews_cleaned.csv',
        'amazon_reviews_cleaned_4M': 'path/to/amazon_reviews_cleaned_4M.csv'
    }
    
    # Initialize and process
    loader = DatasetLoader()
    processed_data = loader.process_all_datasets(file_paths)
    
    print(f"Processed data structure created with {len(processed_data)} categories")
    for category, products in processed_data.items():
        print(f"  {category}: {len(products)} products")
