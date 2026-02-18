# AI Prompts for Web3 Conversion

PRODUCT_OPTIMIZATION_PROMPT = """
Transform this traditional product into a Web3-native asset.

Original Title: {title}
Original Description: {description}

Requirements:
- Emphasize provenance and digital scarcity.
- Highlight the utility of the associated NFT.
- Use a tech-forward, premium tone.
- Add exactly 3 'Metadata Traits' representing rarity or material.

Return a JSON with keys: "optimized_title", "optimized_description", "traits".
"""

STRATEGY_ANALYSIS_PROMPT = """
Given the following store data:
{scrape_data}

Categorize this store into one of: [Apparel, Luxury, Digital Goods, Electronics].
Suggest an $OPTIK token reward percentage (0.5% - 5%).
Outline a 6-month migration roadmap focusing on community lock-in.
"""
