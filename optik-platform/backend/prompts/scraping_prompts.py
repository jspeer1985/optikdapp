# AI Prompts for Web Scraping and Analysis

PLATFORM_DETECTION_PROMPT = """
Analyze the provided HTML snippet or URL to determine the e-commerce platform being used.
Possible Platforms: [Shopify, WooCommerce, Magento, BigCommerce, Squarespace, Wix, Other]

HTML Content:
{html_content}

Return a single word identify the platform.
"""

PRODUCT_EXTRACTION_PROMPT = """
You are a expert at parsing unstructured e-commerce data. 
Given the following raw text or HTML, extract all product details.

Required Fields for each product:
- title
- price
- description
- main_image_url
- variants (if any)

Raw Data:
{raw_data}

Return a valid JSON list of products.
"""

CATEGORY_IDENTIFICATION_PROMPT = """
Identify the primary product category for this store based on the product list.
Categories: [Electronics, Apparel, Home & Garden, Beauty, Services, NFT/Digital]

Product List:
{product_list}

Return the best fitting category and a 1-sentence explanation why.
"""
