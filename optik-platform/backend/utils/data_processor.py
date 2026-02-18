"""
Data Processing Utilities
Handles product data normalization, validation, and transformation for the Optik pipeline
"""

import logging
import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from urllib.parse import urlparse
import hashlib

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Universal data processor for normalizing product data across different platforms
    """
    
    def __init__(self):
        self.required_fields = ["external_id", "title", "price"]
        self.optional_fields = [
            "description", "images", "sku", "currency", "variants", 
            "categories", "tags", "vendor", "product_type"
        ]
    
    def normalize_product(self, product: Dict[str, Any], source_platform: str = "unknown") -> Dict[str, Any]:
        """
        Normalize product data to Optik standard format
        
        Args:
            product: Raw product data from any platform
            source_platform: Platform identifier (shopify, woocommerce, etc.)
            
        Returns:
            Normalized product data
        """
        try:
            normalized = {
                "external_id": self._extract_external_id(product),
                "title": self._clean_text(product.get("title") or product.get("name")),
                "description": self._clean_html(product.get("description") or ""),
                "price": self._normalize_price(product.get("price")),
                "currency": product.get("currency", "USD"),
                "images": self._normalize_images(product.get("images", [])),
                "sku": product.get("sku"),
                "variants": self._normalize_variants(product.get("variants", [])),
                "categories": self._normalize_categories(product.get("categories", [])),
                "tags": self._normalize_tags(product.get("tags", [])),
                "vendor": product.get("vendor"),
                "product_type": product.get("product_type"),
                "source_platform": source_platform,
                "processed_at": datetime.utcnow().isoformat(),
                "data_hash": self._generate_data_hash(product)
            }
            
            # Validate required fields
            missing_fields = [field for field in self.required_fields if not normalized.get(field)]
            if missing_fields:
                logger.warning(f"Product missing required fields: {missing_fields}")
                normalized["validation_errors"] = missing_fields
            
            # Add metadata
            normalized["validation_score"] = self._calculate_validation_score(normalized)
            normalized["completeness_score"] = self._calculate_completeness_score(normalized)
            
            return normalized
            
        except Exception as e:
            logger.error(f"Failed to normalize product: {e}")
            return {
                "error": str(e),
                "raw_data": product,
                "source_platform": source_platform
            }
    
    def _extract_external_id(self, product: Dict[str, Any]) -> str:
        """Extract or generate external ID"""
        # Try common ID fields
        for field in ["id", "external_id", "product_id", "sku"]:
            if product.get(field):
                return str(product[field])
        
        # Fallback to hash of title and price
        title = product.get("title") or product.get("name", "")
        price = product.get("price", "")
        return hashlib.md5(f"{title}_{price}".encode()).hexdigest()
    
    def _clean_text(self, text: Union[str, None]) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-.,!?()[\]{}:;\'"/\\]', '', text)
        
        return text
    
    def _clean_html(self, html: Union[str, None]) -> str:
        """Clean HTML content while preserving basic formatting"""
        if not html:
            return ""
        
        # Convert to text but preserve line breaks
        html = re.sub(r'<br[^>]*>', '\n', html)
        html = re.sub(r'<p[^>]*>', '\n', html)
        html = re.sub(r'</p>', '\n', html)
        html = re.sub(r'<[^>]+>', '', html)
        
        # Clean up whitespace
        return re.sub(r'\n\s*\n', '\n\n', html).strip()
    
    def _normalize_price(self, price: Union[str, float, int, None]) -> float:
        """Normalize price to float"""
        if price is None:
            return 0.0
        
        if isinstance(price, (int, float)):
            return float(price)
        
        if isinstance(price, str):
            # Remove currency symbols and formatting
            price = re.sub(r'[^\d.]', '', price)
            try:
                return float(price)
            except ValueError:
                return 0.0
        
        return 0.0
    
    def _normalize_images(self, images: List) -> List[str]:
        """Normalize image URLs"""
        normalized_images = []
        
        for img in images:
            if isinstance(img, str):
                normalized_images.append(img)
            elif isinstance(img, dict):
                # Try common image URL fields
                for field in ["src", "url", "image"]:
                    if img.get(field):
                        normalized_images.append(img[field])
                        break
        
        # Filter and validate URLs
        return [self._validate_url(url) for url in normalized_images if url and self._is_valid_url(url)]
    
    def _normalize_variants(self, variants: List) -> List[Dict[str, Any]]:
        """Normalize product variants"""
        normalized_variants = []
        
        for variant in variants:
            if isinstance(variant, dict):
                normalized_variants.append({
                    "id": variant.get("id"),
                    "title": variant.get("title"),
                    "price": self._normalize_price(variant.get("price")),
                    "sku": variant.get("sku"),
                    "available": variant.get("available", True),
                    "inventory_quantity": variant.get("inventory_quantity"),
                    "image": variant.get("image"),
                    "attributes": variant.get("attributes", {})
                })
        
        return normalized_variants
    
    def _normalize_categories(self, categories: List) -> List[str]:
        """Normalize categories to string list"""
        normalized = []
        
        for cat in categories:
            if isinstance(cat, str):
                normalized.append(cat)
            elif isinstance(cat, dict):
                # Try common category name fields
                for field in ["name", "title", "category"]:
                    if cat.get(field):
                        normalized.append(cat[field])
                        break
        
        return list(set(normalized))  # Remove duplicates
    
    def _normalize_tags(self, tags: List) -> List[str]:
        """Normalize tags to string list"""
        if isinstance(tags, str):
            # Handle comma-separated tags
            return [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        normalized = []
        for tag in tags:
            if isinstance(tag, str):
                normalized.append(tag)
            elif isinstance(tag, dict):
                for field in ["name", "tag"]:
                    if tag.get(field):
                        normalized.append(tag[field])
                        break
        
        return list(set(normalized))  # Remove duplicates
    
    def _validate_url(self, url: str) -> str:
        """Validate and normalize URL"""
        if not url:
            return ""
        
        # Ensure URL has protocol
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        return url
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _generate_data_hash(self, data: Dict[str, Any]) -> str:
        """Generate hash of product data for change detection"""
        # Use only stable fields for hashing
        stable_fields = {
            "title": data.get("title"),
            "price": data.get("price"),
            "sku": data.get("sku"),
            "external_id": data.get("external_id")
        }
        
        content = str(sorted(stable_fields.items()))
        return hashlib.md5(content.encode()).hexdigest()
    
    def _calculate_validation_score(self, product: Dict[str, Any]) -> float:
        """Calculate validation score (0.0 - 1.0)"""
        score = 0.0
        total_checks = len(self.required_fields)
        
        for field in self.required_fields:
            if product.get(field):
                score += 1.0
        
        # Bonus points for optional fields
        bonus = 0.0
        for field in self.optional_fields:
            if product.get(field):
                bonus += 0.1
        
        return min(1.0, (score + bonus) / total_checks)
    
    def _calculate_completeness_score(self, product: Dict[str, Any]) -> float:
        """Calculate data completeness score (0.0 - 1.0)"""
        all_fields = self.required_fields + self.optional_fields
        filled_fields = sum(1 for field in all_fields if product.get(field))
        
        return filled_fields / len(all_fields)
    
    def batch_normalize(self, products: List[Dict[str, Any]], source_platform: str = "unknown") -> List[Dict[str, Any]]:
        """Normalize a batch of products"""
        normalized_products = []
        
        for i, product in enumerate(products):
            try:
                normalized = self.normalize_product(product, source_platform)
                normalized["batch_index"] = i
                normalized_products.append(normalized)
            except Exception as e:
                logger.error(f"Failed to normalize product at index {i}: {e}")
                normalized_products.append({
                    "error": str(e),
                    "raw_data": product,
                    "batch_index": i,
                    "source_platform": source_platform
                })
        
        return normalized_products
    
    def validate_batch(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a batch of normalized products"""
        total = len(products)
        valid = 0
        invalid = 0
        errors = []
        
        for product in products:
            if product.get("error"):
                invalid += 1
                errors.append(product.get("error"))
            else:
                validation_errors = product.get("validation_errors", [])
                if validation_errors:
                    invalid += 1
                    errors.extend(validation_errors)
                else:
                    valid += 1
        
        return {
            "total_products": total,
            "valid_products": valid,
            "invalid_products": invalid,
            "validation_rate": valid / total if total > 0 else 0,
            "common_errors": self._analyze_errors(errors)
        }
    
    def _analyze_errors(self, errors: List[str]) -> Dict[str, int]:
        """Analyze common validation errors"""
        error_counts = {}
        for error in errors:
            error_counts[error] = error_counts.get(error, 0) + 1
        
        # Sort by frequency
        return dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True))

# Global instance
data_processor = DataProcessor()
