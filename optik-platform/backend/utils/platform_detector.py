"""
Platform Detection Utilities
Automatically detects e-commerce platforms from URLs and HTML content
"""

import logging
import re
from typing import Dict, Any, Optional, List
import httpx
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class PlatformDetector:
    """
    Detects e-commerce platforms from URLs and page content
    """
    
    def __init__(self):
        self.platform_signatures = {
            "shopify": {
                "url_patterns": [
                    r'\.myshopify\.com',
                    r'shopify\.com',
                ],
                "html_patterns": [
                    r'Shopify\.shop',
                    r'Shopify\.theme',
                    r'cdn\.shopify\.com',
                    r'meta name="shopify-checkout-api-token"',
                    r'window\.Shopify',
                    r'SHOPIFY',
                ],
                "headers": [
                    r'X-Shopify.*',
                ],
                "scripts": [
                    r'cdn\.shopify\.com',
                    r'shopify\.cloud',
                ]
            },
            "woocommerce": {
                "url_patterns": [
                    r'/wp-json/wc/',
                    r'/wp-content/plugins/woocommerce/',
                ],
                "html_patterns": [
                    r'WooCommerce',
                    r'wc-',
                    r'woocommerce',
                    r'add-to-cart',
                    r'product-type-',
                    r'woocommerce-product-gallery',
                ],
                "headers": [
                    r'wp-json',
                ],
                "scripts": [
                    r'/wp-content/plugins/woocommerce/',
                    r'wc-add-to-cart',
                ]
            },
            "magento": {
                "url_patterns": [
                    r'magento',
                    r'/checkout/cart/',
                ],
                "html_patterns": [
                    r'Magento',
                    r'mage/',
                    r'Mage\.',
                    r'catalog/product/view',
                ],
                "headers": [
                    r'Magento',
                ],
                "scripts": [
                    r'mage/',
                    r'skin/frontend/',
                ]
            },
            "bigcommerce": {
                "url_patterns": [
                    r'bigcommerce\.com',
                    r'/cart\.php',
                ],
                "html_patterns": [
                    r'BigCommerce',
                    r'bc-',
                    r'bigcommerce',
                ],
                "headers": [
                    r'BigCommerce',
                ],
                "scripts": [
                    r'cdn\.bigcommerce\.com',
                ]
            },
            "shopware": {
                "url_patterns": [
                    r'shopware',
                    r'/checkout/',
                ],
                "html_patterns": [
                    r'Shopware',
                    r'sw-',
                    r'shopware',
                ],
                "headers": [
                    r'Shopware',
                ],
                "scripts": [
                    r'/bundles/',
                    r'/themes/',
                ]
            }
        }
    
    async def detect_platform(self, url: str, timeout: int = 10) -> Dict[str, Any]:
        """
        Detect the e-commerce platform for a given URL
        
        Args:
            url: URL to analyze
            timeout: Request timeout in seconds
            
        Returns:
            Dict with platform detection results
        """
        try:
            # Parse URL
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Initial URL-based detection
            url_detection = self._detect_from_url(url, domain)
            if url_detection["confidence"] > 0.8:
                return url_detection
            
            # HTTP-based detection
            http_detection = await self._detect_from_http(url, timeout)
            
            # Combine results
            return self._combine_detections(url_detection, http_detection)
            
        except Exception as e:
            logger.error(f"Platform detection failed for {url}: {e}")
            return {
                "platform": "unknown",
                "confidence": 0.0,
                "method": "error",
                "error": str(e),
                "url": url
            }
    
    def _detect_from_url(self, url: str, domain: str) -> Dict[str, Any]:
        """Detect platform from URL patterns"""
        scores = {}
        
        for platform, signatures in self.platform_signatures.items():
            score = 0.0
            
            # Check URL patterns
            for pattern in signatures["url_patterns"]:
                if re.search(pattern, url, re.IGNORECASE):
                    score += 0.5
            
            # Check domain patterns
            for pattern in signatures["url_patterns"]:
                if re.search(pattern, domain, re.IGNORECASE):
                    score += 0.3
            
            if score > 0:
                scores[platform] = score
        
        if scores:
            best_platform = max(scores, key=scores.get)
            return {
                "platform": best_platform,
                "confidence": min(1.0, scores[best_platform]),
                "method": "url_pattern",
                "all_scores": scores,
                "url": url
            }
        
        return {
            "platform": "unknown",
            "confidence": 0.0,
            "method": "url_pattern",
            "url": url
        }
    
    async def _detect_from_http(self, url: str, timeout: int) -> Dict[str, Any]:
        """Detect platform from HTTP response and content"""
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            ) as client:
                response = await client.get(url)
                
                # Analyze headers
                header_scores = self._analyze_headers(response.headers)
                
                # Analyze HTML content
                content_scores = self._analyze_content(response.text)
                
                # Analyze scripts
                script_scores = self._analyze_scripts(response.text)
                
                # Combine all scores
                combined_scores = self._combine_scores([header_scores, content_scores, script_scores])
                
                if combined_scores:
                    best_platform = max(combined_scores, key=combined_scores.get)
                    return {
                        "platform": best_platform,
                        "confidence": min(1.0, combined_scores[best_platform]),
                        "method": "http_analysis",
                        "all_scores": combined_scores,
                        "url": url,
                        "status_code": response.status_code
                    }
                
        except Exception as e:
            logger.warning(f"HTTP analysis failed for {url}: {e}")
        
        return {
            "platform": "unknown",
            "confidence": 0.0,
            "method": "http_analysis",
            "url": url
        }
    
    def _analyze_headers(self, headers: Dict[str, str]) -> Dict[str, float]:
        """Analyze HTTP headers for platform signatures"""
        scores = {}
        
        for platform, signatures in self.platform_signatures.items():
            score = 0.0
            
            for header_name, header_value in headers.items():
                header_text = f"{header_name}: {header_value}".lower()
                
                for pattern in signatures["headers"]:
                    if re.search(pattern, header_text, re.IGNORECASE):
                        score += 0.3
            
            if score > 0:
                scores[platform] = score
        
        return scores
    
    def _analyze_content(self, html: str) -> Dict[str, float]:
        """Analyze HTML content for platform signatures"""
        scores = {}
        
        for platform, signatures in self.platform_signatures.items():
            score = 0.0
            
            for pattern in signatures["html_patterns"]:
                matches = len(re.findall(pattern, html, re.IGNORECASE))
                score += matches * 0.2
            
            if score > 0:
                scores[platform] = score
        
        return scores
    
    def _analyze_scripts(self, html: str) -> Dict[str, float]:
        """Analyze script tags for platform signatures"""
        scores = {}
        
        # Extract script src attributes
        script_pattern = r'<script[^>]*src=["\']([^"\']+)["\'][^>]*>'
        scripts = re.findall(script_pattern, html, re.IGNORECASE)
        
        for platform, signatures in self.platform_signatures.items():
            score = 0.0
            
            for script in scripts:
                for pattern in signatures["scripts"]:
                    if re.search(pattern, script, re.IGNORECASE):
                        score += 0.4
            
            if score > 0:
                scores[platform] = score
        
        return scores
    
    def _combine_scores(self, score_lists: List[Dict[str, float]]) -> Dict[str, float]:
        """Combine multiple score dictionaries"""
        combined = {}
        
        for scores in score_lists:
            for platform, score in scores.items():
                combined[platform] = combined.get(platform, 0) + score
        
        return combined
    
    def _combine_detections(self, url_detection: Dict[str, Any], http_detection: Dict[str, Any]) -> Dict[str, Any]:
        """Combine URL and HTTP detection results"""
        url_platform = url_detection.get("platform")
        http_platform = http_detection.get("platform")
        url_confidence = url_detection.get("confidence", 0)
        http_confidence = http_detection.get("confidence", 0)
        
        # If both agree, increase confidence
        if url_platform == http_platform and url_platform != "unknown":
            return {
                "platform": url_platform,
                "confidence": min(1.0, (url_confidence + http_confidence) / 2 + 0.2),
                "method": "combined",
                "url_detection": url_detection,
                "http_detection": http_detection,
                "url": url_detection.get("url")
            }
        
        # Choose the higher confidence detection
        if url_confidence > http_confidence:
            return {
                "platform": url_platform,
                "confidence": url_confidence,
                "method": "url_primary",
                "url_detection": url_detection,
                "http_detection": http_detection,
                "url": url_detection.get("url")
            }
        else:
            return {
                "platform": http_platform,
                "confidence": http_confidence,
                "method": "http_primary",
                "url_detection": url_detection,
                "http_detection": http_detection,
                "url": http_detection.get("url")
            }
    
    def batch_detect(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Detect platforms for multiple URLs"""
        import asyncio
        
        async def detect_all():
            tasks = [self.detect_platform(url) for url in urls]
            return await asyncio.gather(*tasks, return_exceptions=True)
        
        return asyncio.run(detect_all())
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms"""
        return list(self.platform_signatures.keys())
    
    def add_platform_signature(self, platform: str, signatures: Dict[str, List[str]]):
        """Add custom platform signature"""
        self.platform_signatures[platform] = signatures
    
    def update_platform_signature(self, platform: str, signatures: Dict[str, List[str]]):
        """Update existing platform signature"""
        if platform in self.platform_signatures:
            self.platform_signatures[platform].update(signatures)
        else:
            self.platform_signatures[platform] = signatures

# Global instance
platform_detector = PlatformDetector()
