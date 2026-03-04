"""
dApp Integration Service - Shopify Data for Web3 Commerce
Transforms scraped Shopify conversion data into actionable dApp features and opportunities
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

from shopify_data_scraper import get_shopify_scraper, ConversionData
from optik_gpt.assistant.shopify_ai import get_shopify_ai
from config.settings import get_settings

logger = logging.getLogger(__name__)

class DappFeatureType(Enum):
    LOYALTY_PROGRAM = "loyalty_program"
    CART_RECOVERY = "cart_recovery"
    NFT_COLLECTIBLES = "nft_collectibles"
    TOKEN_REWARDS = "token_rewards"
    GAMIFICATION = "gamification"
    PREMIUM_ACCESS = "premium_access"
    REFERRAL_PROGRAM = "referral_program"

@dataclass
class DappFeature:
    """A dApp feature recommendation based on Shopify data."""
    feature_type: DappFeatureType
    title: str
    description: str
    business_case: str
    expected_roi: str
    implementation_complexity: str  # low, medium, high
    time_to_implement: str
    target_customers: List[str]
    technical_requirements: List[str]
    smart_contract_features: List[str]
    tokenomics: Dict[str, Any]
    success_metrics: List[str]

@dataclass
class StoreDappProfile:
    """Complete dApp integration profile for a Shopify store."""
    store_domain: str
    conversion_score: float  # 0-100
    dapp_readiness_score: float  # 0-100
    recommended_features: List[DappFeature]
    priority_features: List[DappFeature]  # Top 3 immediate features
    implementation_roadmap: Dict[str, Any]
    estimated_costs: Dict[str, float]
    projected_revenue_impact: Dict[str, float]
    competitive_advantages: List[str]
    risk_factors: List[str]

class DappIntegrationService:
    """
    Service for integrating Shopify data with dApp features
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.shopify_scraper = get_shopify_scraper()
        self.shopify_ai = get_shopify_ai()
        
    async def generate_store_dapp_profile(self, store_domain: str) -> StoreDappProfile:
        """
        Generate comprehensive dApp integration profile for a store
        """
        logger.info(f"Generating dApp profile for {store_domain}")
        
        # Get scraped data
        cached_data = self.shopify_scraper.get_cached_data(store_domain)
        if not cached_data:
            raise ValueError(f"No scraped data found for {store_domain}")
        
        conversion_data = cached_data['data']
        insights = cached_data['insights']
        
        # Calculate scores
        conversion_score = self._calculate_conversion_score(conversion_data)
        dapp_readiness_score = self._calculate_dapp_readiness(conversion_data)
        
        # Generate feature recommendations
        all_features = await self._generate_dapp_features(conversion_data, insights)
        priority_features = self._select_priority_features(all_features, conversion_data)
        
        # Create implementation roadmap
        roadmap = self._create_implementation_roadmap(priority_features, conversion_data)
        
        # Estimate costs and revenue impact
        costs = self._estimate_implementation_costs(all_features)
        revenue_impact = self._project_revenue_impact(all_features, conversion_data)
        
        # Identify competitive advantages and risks
        advantages = self._identify_competitive_advantages(conversion_data, all_features)
        risks = self._identify_risk_factors(conversion_data)
        
        return StoreDappProfile(
            store_domain=store_domain,
            conversion_score=conversion_score,
            dapp_readiness_score=dapp_readiness_score,
            recommended_features=all_features,
            priority_features=priority_features,
            implementation_roadmap=roadmap,
            estimated_costs=costs,
            projected_revenue_impact=revenue_impact,
            competitive_advantages=advantages,
            risk_factors=risks
        )
    
    def _calculate_conversion_score(self, data: ConversionData) -> float:
        """Calculate conversion performance score (0-100)."""
        score = 0
        
        # Conversion rate scoring (40% weight)
        if data.conversion_rate >= 3.0:
            score += 40
        elif data.conversion_rate >= 2.0:
            score += 30
        elif data.conversion_rate >= 1.0:
            score += 20
        else:
            score += 10
        
        # AOV scoring (25% weight)
        if data.average_order_value >= 150:
            score += 25
        elif data.average_order_value >= 100:
            score += 20
        elif data.average_order_value >= 75:
            score += 15
        else:
            score += 10
        
        # Cart abandonment scoring (20% weight) - lower is better
        if data.cart_abandonment_rate <= 60:
            score += 20
        elif data.cart_abandonment_rate <= 70:
            score += 15
        elif data.cart_abandonment_rate <= 80:
            score += 10
        else:
            score += 5
        
        # CLV scoring (15% weight)
        if data.customer_lifetime_value >= 500:
            score += 15
        elif data.customer_lifetime_value >= 250:
            score += 12
        elif data.customer_lifetime_value >= 100:
            score += 8
        else:
            score += 4
        
        return min(score, 100)
    
    def _calculate_dapp_readiness(self, data: ConversionData) -> float:
        """Calculate dApp readiness score (0-100)."""
        score = 0
        
        # Revenue scale (30% weight)
        if data.total_revenue >= 100000:
            score += 30
        elif data.total_revenue >= 50000:
            score += 25
        elif data.total_revenue >= 25000:
            score += 20
        elif data.total_revenue >= 10000:
            score += 15
        else:
            score += 10
        
        # Customer base (25% weight)
        if data.total_orders >= 1000:
            score += 25
        elif data.total_orders >= 500:
            score += 20
        elif data.total_orders >= 250:
            score += 15
        elif data.total_orders >= 100:
            score += 10
        else:
            score += 5
        
        # Product variety (20% weight)
        if len(data.top_products) >= 10:
            score += 20
        elif len(data.top_products) >= 7:
            score += 15
        elif len(data.top_products) >= 5:
            score += 10
        else:
            score += 5
        
        # Market position (25% weight)
        if data.conversion_rate >= 3.0 and data.average_order_value >= 100:
            score += 25
        elif data.conversion_rate >= 2.0 or data.average_order_value >= 75:
            score += 20
        elif data.conversion_rate >= 1.5 or data.average_order_value >= 50:
            score += 15
        else:
            score += 10
        
        return min(score, 100)
    
    async def _generate_dapp_features(self, conversion_data: ConversionData, 
                                    insights: Dict[str, Any]) -> List[DappFeature]:
        """Generate dApp feature recommendations based on store data."""
        features = []
        
        # Loyalty Program Feature
        if conversion_data.customer_lifetime_value > 100:
            features.append(DappFeature(
                feature_type=DappFeatureType.LOYALTY_PROGRAM,
                title="Token-Based Loyalty Program",
                description="Create a blockchain-based loyalty system where customers earn tokens for purchases, reviews, and referrals",
                business_case=f"Increase repeat purchases from {conversion_data.customer_lifetime_value:.2f} CLV customers",
                expected_roi="250-400% over 12 months",
                implementation_complexity="medium",
                time_to_implement="6-8 weeks",
                target_customers=["Repeat customers", "High-value shoppers"],
                technical_requirements=["Smart contracts", "Token minting", "Wallet integration"],
                smart_contract_features=["ERC-20 tokens", "Staking rewards", "Tier levels"],
                tokenomics={
                    "token_supply": "1,000,000 tokens",
                    "distribution": "60% customers, 20% treasury, 20% team",
                    "utility": "Discounts, exclusive access, voting rights"
                },
                success_metrics=["Repeat purchase rate", "Token holder retention", "Program ROI"]
            ))
        
        # Cart Recovery Feature
        if conversion_data.cart_abandonment_rate > 65:
            features.append(DappFeature(
                feature_type=DappFeatureType.CART_RECOVERY,
                title="NFT Cart Recovery System",
                description="Recover abandoned carts with NFT incentives and time-sensitive token rewards",
                business_case=f"Recover {conversion_data.cart_abandonment_rate:.1f}% of abandoned carts worth potential ${conversion_data.average_order_value * conversion_data.total_orders * conversion_data.cart_abandonment_rate / 100:.2f}",
                expected_roi="150-300% in first 3 months",
                implementation_complexity="low",
                time_to_implement="3-4 weeks",
                target_customers=["Cart abandoners", "Price-sensitive shoppers"],
                technical_requirements=["Cart tracking", "NFT minting", "Email integration"],
                smart_contract_features=["Dynamic NFTs", "Time-locked rewards", "Conditional minting"],
                tokenomics={
                    "recovery_tokens": "Limited supply based on abandonment rate",
                    "incentive_value": "5-15% of cart value",
                    "expiry": "24-48 hours"
                },
                success_metrics=["Cart recovery rate", "Conversion from recovery", "Cost per recovery"]
            ))
        
        # NFT Collectibles Feature
        if conversion_data.average_order_value > 75:
            features.append(DappFeature(
                feature_type=DappFeatureType.NFT_COLLECTIBLES,
                title="Premium NFT Collectibles",
                description="Offer exclusive NFTs with high-value purchases that provide ongoing benefits",
                business_case=f"Leverage ${conversion_data.average_order_value:.2f} AOV to create premium digital collectibles",
                expected_roi="200-500% through secondary market royalties",
                implementation_complexity="medium",
                time_to_implement="4-6 weeks",
                target_customers=["High-value customers", "Collectors", "Brand advocates"],
                technical_requirements=["NFT marketplace", "Royalty system", "IPFS storage"],
                smart_contract_features=["ERC-721/1155", "Royalty splits", "Upgrade mechanics"],
                tokenomics={
                    "collectible_supply": "Limited editions (100-1000 per design)",
                    "royalty_rate": "5-10% on secondary sales",
                    "utility": "Exclusive access, discounts, special editions"
                },
                success_metrics=["NFT sales volume", "Secondary market activity", "Holder engagement"]
            ))
        
        # Token Rewards Feature
        if conversion_data.conversion_rate < 2.5:
            features.append(DappFeature(
                feature_type=DappFeatureType.TOKEN_REWARDS,
                title="Purchase Token Rewards",
                description="Reward customers with tokens for every purchase that can be redeemed for discounts or exclusive products",
                business_case=f"Increase conversion rate from {conversion_data.conversion_rate:.1f}% through immediate value incentives",
                expected_roi="180-350% through increased conversion frequency",
                implementation_complexity="low",
                time_to_implement="2-3 weeks",
                target_customers=["Price-conscious shoppers", "New customers"],
                technical_requirements=["Token distribution", "Redemption system", "POS integration"],
                smart_contract_features=["Automatic distribution", "Redemption burning", "Value locking"],
                tokenomics={
                    "reward_rate": "2-5% of purchase value in tokens",
                    "token_value": "1 token = $0.10 - $1.00",
                    "redemption_options": "Discounts, free shipping, exclusive items"
                },
                success_metrics=["Conversion rate increase", "Token redemption rate", "Customer acquisition cost"]
            ))
        
        # Gamification Feature
        if len(conversion_data.customer_segments) > 2:
            features.append(DappFeature(
                feature_type=DappFeatureType.GAMIFICATION,
                title="Shopping Gamification System",
                description="Turn shopping into a game with achievements, leaderboards, and blockchain-based rewards",
                business_case="Engage multiple customer segments with competitive and collaborative elements",
                expected_roi="300-600% through increased engagement and social sharing",
                implementation_complexity="high",
                time_to_implement="8-10 weeks",
                target_customers=["All customer segments", "Social media users"],
                technical_requirements=["Achievement system", "Leaderboard", "Social sharing"],
                smart_contract_features=["Achievement NFTs", "Tournament prizes", "Seasonal rewards"],
                tokenomics={
                    "achievement_rewards": "Rare NFTs for milestones",
                    "tournament_prizes": "Token pools and exclusive items",
                    "social_rewards": "Referral bonuses and sharing incentives"
                },
                success_metrics=["Daily active users", "Social shares", "Achievement completion rate"]
            ))
        
        return features
    
    def _select_priority_features(self, all_features: List[DappFeature], 
                                conversion_data: ConversionData) -> List[DappFeature]:
        """Select top 3 priority features based on store data."""
        scored_features = []
        
        for feature in all_features:
            score = 0
            
            # Score based on implementation complexity (prefer easier first)
            if feature.implementation_complexity == "low":
                score += 30
            elif feature.implementation_complexity == "medium":
                score += 20
            else:
                score += 10
            
            # Score based on expected ROI
            if "300%" in feature.expected_roi or "400%" in feature.expected_roi:
                score += 25
            elif "200%" in feature.expected_roi or "250%" in feature.expected_roi:
                score += 20
            else:
                score += 15
            
            # Score based on store fit
            if feature.feature_type == DappFeatureType.CART_RECOVERY and conversion_data.cart_abandonment_rate > 70:
                score += 20
            elif feature.feature_type == DappFeatureType.LOYALTY_PROGRAM and conversion_data.customer_lifetime_value > 200:
                score += 20
            elif feature.feature_type == DappFeatureType.NFT_COLLECTIBLES and conversion_data.average_order_value > 100:
                score += 20
            
            scored_features.append((score, feature))
        
        # Sort by score and return top 3
        scored_features.sort(key=lambda x: x[0], reverse=True)
        return [feature for _, feature in scored_features[:3]]
    
    def _create_implementation_roadmap(self, priority_features: List[DappFeature],
                                     conversion_data: ConversionData) -> Dict[str, Any]:
        """Create implementation roadmap for priority features."""
        roadmap = {
            "phase_1": {
                "duration": "4-6 weeks",
                "features": [],
                "milestones": [],
                "resources_needed": []
            },
            "phase_2": {
                "duration": "6-8 weeks",
                "features": [],
                "milestones": [],
                "resources_needed": []
            },
            "phase_3": {
                "duration": "8-12 weeks",
                "features": [],
                "milestones": [],
                "resources_needed": []
            }
        }
        
        # Assign features to phases based on complexity
        for i, feature in enumerate(priority_features):
            if i == 0:
                phase = "phase_1"
            elif i == 1:
                phase = "phase_2"
            else:
                phase = "phase_3"
            
            roadmap[phase]["features"].append(feature.title)
            
            # Add milestones
            roadmap[phase]["milestones"].extend([
                f"{feature.title} - Smart contract development",
                f"{feature.title} - Frontend integration",
                f"{feature.title} - Testing and deployment"
            ])
            
            # Add resources
            roadmap[phase]["resources_needed"].extend(feature.technical_requirements)
        
        # Remove duplicates
        for phase in roadmap.values():
            phase["resources_needed"] = list(set(phase["resources_needed"]))
        
        return roadmap
    
    def _estimate_implementation_costs(self, features: List[DappFeature]) -> Dict[str, float]:
        """Estimate implementation costs for all features."""
        costs = {
            "smart_contracts": 0,
            "frontend_development": 0,
            "backend_integration": 0,
            "testing_security": 0,
            "deployment": 0,
            "total": 0
        }
        
        for feature in features:
            base_cost = 15000 if feature.implementation_complexity == "low" else \
                       25000 if feature.implementation_complexity == "medium" else 40000
            
            costs["smart_contracts"] += base_cost * 0.3
            costs["frontend_development"] += base_cost * 0.25
            costs["backend_integration"] += base_cost * 0.25
            costs["testing_security"] += base_cost * 0.15
            costs["deployment"] += base_cost * 0.05
        
        costs["total"] = sum(costs.values())
        return costs
    
    def _project_revenue_impact(self, features: List[DappFeature], 
                              conversion_data: ConversionData) -> Dict[str, float]:
        """Project revenue impact from implementing features."""
        impacts = {
            "year_1": 0,
            "year_2": 0,
            "year_3": 0,
            "total_3_year": 0
        }
        
        current_annual_revenue = conversion_data.total_revenue * 12  # Assuming monthly data
        
        for feature in features:
            # Extract ROI percentage from expected_roi
            roi_percentage = 0
            if "300%" in feature.expected_roi:
                roi_percentage = 3.0
            elif "250%" in feature.expected_roi:
                roi_percentage = 2.5
            elif "200%" in feature.expected_roi:
                roi_percentage = 2.0
            elif "150%" in feature.expected_roi:
                roi_percentage = 1.5
            elif "400%" in feature.expected_roi:
                roi_percentage = 4.0
            elif "500%" in feature.expected_roi:
                roi_percentage = 5.0
            elif "600%" in feature.expected_roi:
                roi_percentage = 6.0
            
            # Calculate impact (ROI is on investment, not revenue increase)
            # Assume conservative 10-30% revenue increase based on feature type
            if feature.feature_type == DappFeatureType.LOYALTY_PROGRAM:
                revenue_increase = 0.25  # 25% increase
            elif feature.feature_type == DappFeatureType.CART_RECOVERY:
                revenue_increase = 0.15  # 15% increase
            elif feature.feature_type == DappFeatureType.NFT_COLLECTIBLES:
                revenue_increase = 0.20  # 20% increase
            elif feature.feature_type == DappFeatureType.TOKEN_REWARDS:
                revenue_increase = 0.18  # 18% increase
            else:
                revenue_increase = 0.12  # 12% increase
            
            # Apply diminishing returns for multiple features
            if len(features) > 1:
                revenue_increase *= 0.7  # 30% less effective with multiple features
            if len(features) > 2:
                revenue_increase *= 0.8  # Additional reduction
            
            annual_impact = current_annual_revenue * revenue_increase
            
            # Phase in the impact over time
            impacts["year_1"] += annual_impact * 0.6  # 60% in first year
            impacts["year_2"] += annual_impact * 0.8  # 80% in second year
            impacts["year_3"] += annual_impact  # Full impact in third year
        
        impacts["total_3_year"] = impacts["year_1"] + impacts["year_2"] + impacts["year_3"]
        
        return impacts
    
    def _identify_competitive_advantages(self, conversion_data: ConversionData,
                                       features: List[DappFeature]) -> List[str]:
        """Identify competitive advantages from dApp integration."""
        advantages = []
        
        if conversion_data.conversion_rate > 2.5:
            advantages.append("High conversion rate provides strong foundation for dApp success")
        
        if conversion_data.average_order_value > 100:
            advantages.append("High AOV customers more likely to engage with premium NFT features")
        
        if conversion_data.customer_lifetime_value > 200:
            advantages.append("Strong CLV indicates loyal customer base for token rewards")
        
        if len(conversion_data.top_products) >= 5:
            advantages.append("Diverse product catalog supports multiple dApp features")
        
        if any(f.feature_type == DappFeatureType.LOYALTY_PROGRAM for f in features):
            advantages.append("First-mover advantage in blockchain loyalty programs")
        
        if any(f.feature_type == DappFeatureType.NFT_COLLECTIBLES for f in features):
            advantages.append("Unique digital collectibles create brand differentiation")
        
        return advantages
    
    def _identify_risk_factors(self, conversion_data: ConversionData) -> List[str]:
        """Identify potential risk factors."""
        risks = []
        
        if conversion_data.conversion_rate < 1.0:
            risks.append("Low conversion rate may indicate customer resistance to new features")
        
        if conversion_data.cart_abandonment_rate > 80:
            risks.append("Very high cart abandonment suggests checkout friction issues")
        
        if conversion_data.total_revenue < 10000:
            risks.append("Low revenue may limit resources for dApp development")
        
        if conversion_data.total_orders < 100:
            risks.append("Limited order history reduces data for personalization")
        
        if len(conversion_data.customer_segments) < 2:
            risks.append("Limited customer segmentation reduces targeting options")
        
        return risks
    
    async def generate_market_analysis(self) -> Dict[str, Any]:
        """Generate market-wide analysis from all scraped stores."""
        dapp_data = self.shopify_scraper.export_data_for_dapp()
        
        if not dapp_data["stores"]:
            return {"message": "No store data available for analysis"}
        
        # Analyze all stores for dApp readiness
        store_profiles = []
        for domain in dapp_data["stores"]:
            try:
                profile = await self.generate_store_dapp_profile(domain)
                store_profiles.append(profile)
            except Exception as e:
                logger.error(f"Failed to generate profile for {domain}: {str(e)}")
        
        if not store_profiles:
            return {"message": "No valid store profiles generated"}
        
        # Calculate market insights
        total_stores = len(store_profiles)
        high_readiness = len([p for p in store_profiles if p.dapp_readiness_score >= 70])
        medium_readiness = len([p for p in store_profiles if 50 <= p.dapp_readiness_score < 70])
        low_readiness = len([p for p in store_profiles if p.dapp_readiness_score < 50])
        
        # Most recommended features
        feature_counts = {}
        for profile in store_profiles:
            for feature in profile.priority_features:
                feature_type = feature.feature_type.value
                feature_counts[feature_type] = feature_counts.get(feature_type, 0) + 1
        
        # Market opportunities
        top_opportunities = sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Revenue potential
        total_revenue_impact = sum(profile.projected_revenue_impact["total_3_year"] for profile in store_profiles)
        total_implementation_cost = sum(profile.estimated_costs["total"] for profile in store_profiles)
        
        return {
            "market_overview": {
                "total_stores_analyzed": total_stores,
                "dapp_readiness_distribution": {
                    "high": high_readiness,
                    "medium": medium_readiness,
                    "low": low_readiness
                },
                "average_dapp_readiness": sum(p.dapp_readiness_score for p in store_profiles) / total_stores
            },
            "top_dapp_opportunities": [
                {"feature": feature, "store_count": count, "percentage": (count / total_stores) * 100}
                for feature, count in top_opportunities[:5]
            ],
            "financial_projections": {
                "total_3_year_revenue_impact": total_revenue_impact,
                "total_implementation_cost": total_implementation_cost,
                "average_roi_per_store": (total_revenue_impact / total_implementation_cost - 1) * 100 if total_implementation_cost > 0 else 0
            },
            "implementation_recommendations": {
                "priority_markets": [p.store_domain for p in sorted(store_profiles, key=lambda x: x.dapp_readiness_score, reverse=True)[:5]],
                "recommended_rollout_strategy": "Start with high-readiness stores featuring loyalty and cart recovery programs",
                "key_success_factors": [
                    "Focus on stores with >$50k annual revenue",
                    "Prioritize easy-to-implement features first",
                    "Target stores with existing customer loyalty"
                ]
            }
        }

# Global instance
_dapp_service = None

def get_dapp_service() -> DappIntegrationService:
    """Get or create the dApp integration service instance."""
    global _dapp_service
    if _dapp_service is None:
        _dapp_service = DappIntegrationService()
    return _dapp_service
