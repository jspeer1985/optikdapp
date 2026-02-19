from typing import Literal

# --- Constants ---

StoreCategory = Literal["Apparel", "Luxury", "Digital Goods", "Electronics"]

VALID_CATEGORIES = ["Apparel", "Luxury", "Digital Goods", "Electronics"]
TOKEN_REWARD_RANGE = (0.5, 5.0)


# --- Prompts ---

PRODUCT_OPTIMIZATION_PROMPT = """
You are a Web3 product strategist. Transform the product below into a Web3-native asset listing.

## Input
- **Title:** {title}
- **Description:** {description}

## Output Requirements
Return a single JSON object with exactly these keys:
```json
{{
  "optimized_title": "A concise, premium, Web3-native product title",
  "optimized_description": "2–3 sentences emphasizing provenance, digital scarcity, and NFT utility. Use a tech-forward, premium tone.",
  "traits": [
    {{"trait_type": "<category>", "value": "<value>"}},
    {{"trait_type": "<category>", "value": "<value>"}},
    {{"trait_type": "<category>", "value": "<value>"}}
  ]
}}
```

### Trait Rules
- Include **exactly 3 traits**.
- Each trait must represent rarity, material, or provenance.
- Use standard NFT metadata format: `trait_type` + `value`.

### Tone Guidelines
- Emphasize **ownership**, **scarcity**, and **on-chain utility**.
- Avoid generic buzzwords (e.g., "revolutionary", "disruptive").
- Write for a crypto-native audience.

Return only the JSON — no explanation or markdown wrapper.
"""


STRATEGY_ANALYSIS_PROMPT = """
You are a Web3 commerce strategist. Analyze the store data below and return a structured migration plan.

## Store Data
{scrape_data}

## Output Requirements
Return a single JSON object with exactly these keys:
```json
{{
  "category": "<one of: Apparel | Luxury | Digital Goods | Electronics>",
  "token_reward_percentage": <float between {min_reward} and {max_reward}>,
  "reward_rationale": "1–2 sentences justifying the reward percentage based on margin and customer LTV.",
  "roadmap": [
    {{"month": 1, "milestone": "..."}},
    {{"month": 2, "milestone": "..."}},
    {{"month": 3, "milestone": "..."}},
    {{"month": 4, "milestone": "..."}},
    {{"month": 5, "milestone": "..."}},
    {{"month": 6, "milestone": "..."}}
  ]
}}
```

### Roadmap Guidelines
- Month 1–2: Focus on wallet integration and onboarding.
- Month 3–4: Token reward activation and community seeding.
- Month 5–6: Loyalty lock-in mechanisms and retention analytics.
- Each milestone should be specific and actionable, not generic.

Return only the JSON — no explanation or markdown wrapper.
"""


# --- Prompt Builder Utilities ---

def build_product_prompt(title: str, description: str) -> str:
    """Render the product optimization prompt with validation."""
    if not title or not title.strip():
        raise ValueError("Product title must not be empty.")
    if not description or not description.strip():
        raise ValueError("Product description must not be empty.")
    return PRODUCT_OPTIMIZATION_PROMPT.format(
        title=title.strip(),
        description=description.strip(),
    )


def build_strategy_prompt(scrape_data: str) -> str:
    """Render the strategy analysis prompt with reward range injected."""
    if not scrape_data or not scrape_data.strip():
        raise ValueError("Store scrape data must not be empty.")
    return STRATEGY_ANALYSIS_PROMPT.format(
        scrape_data=scrape_data.strip(),
        min_reward=TOKEN_REWARD_RANGE[0],
        max_reward=TOKEN_REWARD_RANGE[1],
    )