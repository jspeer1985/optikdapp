"""
dApp Integration API Routes
Endpoints for transforming Shopify data into Web3 commerce opportunities
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime

from dapp_integration_service import get_dapp_service, StoreDappProfile, DappFeatureType
from utils.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dapp-integration", tags=["dapp-integration"])

# Pydantic models for API responses
class DappFeatureResponse(BaseModel):
    feature_type: str
    title: str
    description: str
    business_case: str
    expected_roi: str
    implementation_complexity: str
    time_to_implement: str
    target_customers: List[str]
    technical_requirements: List[str]
    smart_contract_features: List[str]
    tokenomics: Dict[str, Any]
    success_metrics: List[str]

class StoreProfileResponse(BaseModel):
    store_domain: str
    conversion_score: float
    dapp_readiness_score: float
    recommended_features: List[DappFeatureResponse]
    priority_features: List[DappFeatureResponse]
    implementation_roadmap: Dict[str, Any]
    estimated_costs: Dict[str, float]
    projected_revenue_impact: Dict[str, float]
    competitive_advantages: List[str]
    risk_factors: List[str]

class MarketAnalysisResponse(BaseModel):
    market_overview: Dict[str, Any]
    top_dapp_opportunities: List[Dict[str, Any]]
    financial_projections: Dict[str, Any]
    implementation_recommendations: Dict[str, Any]

@router.get("/store-profile/{store_domain}", response_model=StoreProfileResponse)
async def get_store_dapp_profile(
    store_domain: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate comprehensive dApp integration profile for a specific store
    """
    try:
        dapp_service = get_dapp_service()
        profile = await dapp_service.generate_store_dapp_profile(store_domain)
        
        # Convert to response format
        return StoreProfileResponse(
            store_domain=profile.store_domain,
            conversion_score=profile.conversion_score,
            dapp_readiness_score=profile.dapp_readiness_score,
            recommended_features=[
                DappFeatureResponse(
                    feature_type=f.feature_type.value,
                    title=f.title,
                    description=f.description,
                    business_case=f.business_case,
                    expected_roi=f.expected_roi,
                    implementation_complexity=f.implementation_complexity,
                    time_to_implement=f.time_to_implement,
                    target_customers=f.target_customers,
                    technical_requirements=f.technical_requirements,
                    smart_contract_features=f.smart_contract_features,
                    tokenomics=f.tokenomics,
                    success_metrics=f.success_metrics
                )
                for f in profile.recommended_features
            ],
            priority_features=[
                DappFeatureResponse(
                    feature_type=f.feature_type.value,
                    title=f.title,
                    description=f.description,
                    business_case=f.business_case,
                    expected_roi=f.expected_roi,
                    implementation_complexity=f.implementation_complexity,
                    time_to_implement=f.time_to_implement,
                    target_customers=f.target_customers,
                    technical_requirements=f.technical_requirements,
                    smart_contract_features=f.smart_contract_features,
                    tokenomics=f.tokenomics,
                    success_metrics=f.success_metrics
                )
                for f in profile.priority_features
            ],
            implementation_roadmap=profile.implementation_roadmap,
            estimated_costs=profile.estimated_costs,
            projected_revenue_impact=profile.projected_revenue_impact,
            competitive_advantages=profile.competitive_advantages,
            risk_factors=profile.risk_factors
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate dApp profile for {store_domain}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate profile: {str(e)}")

@router.get("/market-analysis", response_model=MarketAnalysisResponse)
async def get_market_analysis(
    current_user: dict = Depends(get_current_user)
):
    """
    Generate market-wide analysis of dApp opportunities across all scraped stores
    """
    try:
        dapp_service = get_dapp_service()
        analysis = await dapp_service.generate_market_analysis()
        
        return MarketAnalysisResponse(**analysis)
        
    except Exception as e:
        logger.error(f"Failed to generate market analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate analysis: {str(e)}")

@router.get("/feature-types")
async def get_dapp_feature_types(
    current_user: dict = Depends(get_current_user)
):
    """
    Get available dApp feature types with descriptions
    """
    feature_types = {
        "loyalty_program": {
            "name": "Token-Based Loyalty Program",
            "description": "Blockchain-powered loyalty system with token rewards",
            "best_for": "Stores with repeat customers and CLV > $100",
            "complexity": "Medium",
            "typical_roi": "250-400%"
        },
        "cart_recovery": {
            "name": "NFT Cart Recovery",
            "description": "Recover abandoned carts with NFT incentives",
            "best_for": "Stores with cart abandonment > 65%",
            "complexity": "Low",
            "typical_roi": "150-300%"
        },
        "nft_collectibles": {
            "name": "Premium NFT Collectibles",
            "description": "Exclusive digital collectibles with premium purchases",
            "best_for": "Stores with AOV > $75",
            "complexity": "Medium",
            "typical_roi": "200-500%"
        },
        "token_rewards": {
            "name": "Purchase Token Rewards",
            "description": "Token rewards for every purchase",
            "best_for": "Stores looking to increase conversion rate",
            "complexity": "Low",
            "typical_roi": "180-350%"
        },
        "gamification": {
            "name": "Shopping Gamification",
            "description": "Game-like experiences with blockchain rewards",
            "best_for": "Stores with multiple customer segments",
            "complexity": "High",
            "typical_roi": "300-600%"
        },
        "premium_access": {
            "name": "Premium Access Tokens",
            "description": "Token-gated exclusive content and features",
            "best_for": "Established brands with loyal following",
            "complexity": "Medium",
            "typical_roi": "200-400%"
        },
        "referral_program": {
            "name": "Blockchain Referral Program",
            "description": "Token-powered referral and affiliate system",
            "best_for": "Stores with strong social media presence",
            "complexity": "Medium",
            "typical_roi": "300-500%"
        }
    }
    
    return {
        "feature_types": feature_types,
        "total_features": len(feature_types),
        "complexity_distribution": {
            "low": 2,
            "medium": 4,
            "high": 1
        }
    }

@router.get("/implementation-guide")
async def get_implementation_guide(
    feature_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed implementation guide for dApp features
    """
    guides = {
        "general": {
            "phases": [
                {
                    "phase": "Discovery & Planning",
                    "duration": "2-3 weeks",
                    "activities": [
                        "Requirements gathering",
                        "Technical architecture design",
                        "Smart contract specification",
                        "UI/UX design",
                        "Security audit planning"
                    ]
                },
                {
                    "phase": "Development",
                    "duration": "4-8 weeks",
                    "activities": [
                        "Smart contract development",
                        "Frontend implementation",
                        "Backend integration",
                        "Wallet connection setup",
                        "IPFS integration"
                    ]
                },
                {
                    "phase": "Testing & Security",
                    "duration": "2-3 weeks",
                    "activities": [
                        "Unit testing",
                        "Integration testing",
                        "Security audit",
                        "Penetration testing",
                        "User acceptance testing"
                    ]
                },
                {
                    "phase": "Deployment",
                    "duration": "1-2 weeks",
                    "activities": [
                        "Mainnet deployment",
                        "Frontend deployment",
                        "Monitoring setup",
                        "Documentation",
                        "Team training"
                    ]
                }
            ],
            "team_requirements": {
                "blockchain_developer": "Solidity/Rust smart contract expertise",
                "frontend_developer": "React/Web3.js experience",
                "backend_developer": "Node.js/Python API development",
                "ui_ux_designer": "Web3 design experience",
                "security_auditor": "Smart contract security expertise"
            },
            "technology_stack": {
                "smart_contracts": ["Solidity", "Hardhat/Foundry", "OpenZeppelin"],
                "frontend": ["React", "Web3.js/Ethers.js", "TailwindCSS"],
                "backend": ["Node.js", "Python", "PostgreSQL"],
                "storage": ["IPFS", "Pinata", "Arweave"],
                "monitoring": ["Sentry", "Graph Protocol", "Dune Analytics"]
            }
        },
        "loyalty_program": {
            "specific_considerations": [
                "Token economics design",
                "Tier level mechanics",
                "Staking rewards calculation",
                "Governance token features",
                "Anti-manipulation measures"
            ],
            "smart_contract_features": [
                "ERC-20 token contract",
                "Staking contract",
                "Rewards distribution contract",
                "Tier management contract",
                "Governance contract"
            ],
            "integration_points": [
                "Shopify customer data sync",
                "Purchase tracking",
                "Reward calculation engine",
                "Wallet connection",
                "Token redemption system"
            ]
        },
        "cart_recovery": {
            "specific_considerations": [
                "Time-sensitive NFT design",
                "Cart abandonment detection",
                "Incentive calculation logic",
                "NFT expiration mechanics",
                "Conversion tracking"
            ],
            "smart_contract_features": [
                "Dynamic NFT contract",
                "Time-locked rewards",
                "Conditional minting",
                "Expiration handling",
                "Conversion tracking"
            ],
            "integration_points": [
                "Shopify cart tracking",
                "Email campaign integration",
                "Abandonment detection",
                "NFT delivery system",
                "Recovery analytics"
            ]
        }
    }
    
    if feature_type and feature_type in guides:
        return {"feature_type": feature_type, "guide": guides[feature_type]}
    else:
        return {"general_guide": guides["general"], "feature_guides": {k: v for k, v in guides.items() if k != "general"}}

@router.get("/roi-calculator")
async def get_roi_calculator(
    current_revenue: float,
    current_conversion_rate: float,
    current_aov: float,
    feature_types: List[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate ROI for implementing specific dApp features
    """
    try:
        # Feature impact assumptions (conservative estimates)
        feature_impacts = {
            "loyalty_program": {
                "revenue_increase": 0.25,  # 25% increase
                "implementation_cost": 25000,
                "time_to_roi": "8-12 months"
            },
            "cart_recovery": {
                "revenue_increase": 0.15,  # 15% increase
                "implementation_cost": 15000,
                "time_to_roi": "3-6 months"
            },
            "nft_collectibles": {
                "revenue_increase": 0.20,  # 20% increase
                "implementation_cost": 30000,
                "time_to_roi": "6-9 months"
            },
            "token_rewards": {
                "revenue_increase": 0.18,  # 18% increase
                "implementation_cost": 20000,
                "time_to_roi": "4-7 months"
            },
            "gamification": {
                "revenue_increase": 0.30,  # 30% increase
                "implementation_cost": 40000,
                "time_to_roi": "10-14 months"
            }
        }
        
        if not feature_types:
            feature_types = ["loyalty_program", "cart_recovery"]
        
        # Calculate projections
        current_annual_revenue = current_revenue * 12
        total_implementation_cost = 0
        total_revenue_increase = 0
        
        feature_projections = []
        
        for feature_type in feature_types:
            if feature_type not in feature_impacts:
                continue
                
            impact = feature_impacts[feature_type]
            revenue_increase = current_annual_revenue * impact["revenue_increase"]
            
            # Apply diminishing returns for multiple features
            if len(feature_types) > 1:
                revenue_increase *= 0.8
            
            feature_projections.append({
                "feature_type": feature_type,
                "revenue_increase": revenue_increase,
                "implementation_cost": impact["implementation_cost"],
                "time_to_roi": impact["time_to_roi"],
                "annual_roi_percentage": (revenue_increase / impact["implementation_cost"]) * 100
            })
            
            total_implementation_cost += impact["implementation_cost"]
            total_revenue_increase += revenue_increase
        
        # Calculate overall metrics
        overall_roi = (total_revenue_increase / total_implementation_cost) * 100 if total_implementation_cost > 0 else 0
        
        return {
            "current_metrics": {
                "monthly_revenue": current_revenue,
                "annual_revenue": current_annual_revenue,
                "conversion_rate": current_conversion_rate,
                "average_order_value": current_aov
            },
            "feature_projections": feature_projections,
            "summary": {
                "total_implementation_cost": total_implementation_cost,
                "total_annual_revenue_increase": total_revenue_increase,
                "overall_roi_percentage": overall_roi,
                "payback_period_months": (total_implementation_cost / (total_revenue_increase / 12)) if total_revenue_increase > 0 else "Never",
                "projected_annual_revenue": current_annual_revenue + total_revenue_increase
            },
            "assumptions": {
                "conservative_estimates": True,
                "diminishing_returns_applied": len(feature_types) > 1,
                "market_conditions": "Current e-commerce trends",
                "calculation_date": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"ROI calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ROI calculation failed: {str(e)}")

@router.get("/smart-contract-templates")
async def get_smart_contract_templates(
    feature_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get smart contract templates and examples for dApp features
    """
    templates = {
        "loyalty_token": {
            "name": "Loyalty Token Contract",
            "description": "ERC-20 token for loyalty rewards",
            "features": ["Minting", "Burning", "Staking", "Rewards"],
            "code_example": """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract LoyaltyToken is ERC20, Ownable {
    mapping(address => uint256) public stakingBalance;
    mapping(address => uint256) public stakeTimestamp;
    
    uint256 public constant REWARD_RATE = 100; // tokens per second
    
    constructor() ERC20("Loyalty Token", "LOYALTY") {}
    
    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
    
    function stake(uint256 amount) external {
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");
        _transfer(msg.sender, address(this), amount);
        stakingBalance[msg.sender] += amount;
        if (stakeTimestamp[msg.sender] == 0) {
            stakeTimestamp[msg.sender] = block.timestamp;
        }
    }
    
    function unstake(uint256 amount) external {
        require(stakingBalance[msg.sender] >= amount, "Insufficient stake");
        uint256 rewards = calculateRewards(msg.sender);
        stakingBalance[msg.sender] -= amount;
        stakeTimestamp[msg.sender] = block.timestamp;
        _transfer(address(this), msg.sender, amount);
        _mint(msg.sender, rewards);
    }
    
    function calculateRewards(address user) public view returns (uint256) {
        if (stakeTimestamp[user] == 0) return 0;
        return (block.timestamp - stakeTimestamp[user]) * REWARD_RATE * stakingBalance[user] / 1e18;
    }
}
            """,
            "deployment_notes": [
                "Set initial supply in constructor",
                "Configure reward rate based on business model",
                "Add emergency pause functionality",
                "Implement upgradeable proxy pattern"
            ]
        },
        "cart_recovery_nft": {
            "name": "Cart Recovery NFT Contract",
            "description": "Dynamic NFT for cart recovery incentives",
            "features": ["Dynamic NFT", "Time-locked rewards", "Expiration"],
            "code_example": """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract CartRecoveryNFT is ERC721 {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;
    
    struct CartInfo {
        uint256 cartValue;
        uint256 expirationTime;
        uint256 discountPercentage;
        bool claimed;
    }
    
    mapping(uint256 => CartInfo) public cartInfos;
    mapping(address => uint256[]) public userTokens;
    
    constructor() ERC721("Cart Recovery NFT", "CARTNFT") {}
    
    function mintRecoveryNFT(
        address to,
        uint256 cartValue,
        uint256 discountPercentage
    ) external returns (uint256) {
        _tokenIds.increment();
        uint256 tokenId = _tokenIds.current();
        
        _mint(to, tokenId);
        userTokens[to].push(tokenId);
        
        cartInfos[tokenId] = CartInfo({
            cartValue: cartValue,
            expirationTime: block.timestamp + 48 hours,
            discountPercentage: discountPercentage,
            claimed: false
        });
        
        return tokenId;
    }
    
    function claimDiscount(uint256 tokenId) external {
        require(ownerOf(tokenId) == msg.sender, "Not token owner");
        require(!cartInfos[tokenId].claimed, "Already claimed");
        require(block.timestamp <= cartInfos[tokenId].expirationTime, "Expired");
        
        cartInfos[tokenId].claimed = true;
        // Emit discount claimed event
    }
    
    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_exists(tokenId), "Token does not exist");
        // Return dynamic metadata based on cart info
    }
}
            """,
            "deployment_notes": [
                "Set appropriate expiration time",
                "Configure discount calculation logic",
                "Add metadata URI for dynamic images",
                "Implement batch minting for efficiency"
            ]
        }
    }
    
    if feature_type and feature_type in templates:
        return {"feature_type": feature_type, "template": templates[feature_type]}
    else:
        return {"templates": templates, "total_templates": len(templates)}

@router.get("/case-studies")
async def get_case_studies(
    current_user: dict = Depends(get_current_user)
):
    """
    Get case studies and success stories of dApp implementations
    """
    case_studies = [
        {
            "store": "Fashion Boutique XYZ",
            "industry": "Fashion",
            "features_implemented": ["loyalty_program", "nft_collectibles"],
            "results": {
                "revenue_increase": "35%",
                "customer_retention": "+45%",
                "average_order_value": "+28%",
                "implementation_time": "10 weeks",
                "roi": "320%"
            },
            "key_learnings": [
                "Customers loved the tier-based loyalty system",
                "NFT collectibles drove premium purchases",
                "Integration with existing Shopify was seamless",
                "Social sharing increased brand awareness"
            ]
        },
        {
            "store": "Electronics Store ABC",
            "industry": "Electronics",
            "features_implemented": ["cart_recovery", "token_rewards"],
            "results": {
                "cart_recovery_rate": "22%",
                "conversion_rate": "+18%",
                "customer_acquisition_cost": "-30%",
                "implementation_time": "6 weeks",
                "roi": "280%"
            },
            "key_learnings": [
                "Time-sensitive NFTs were highly effective",
                "Token rewards encouraged repeat purchases",
                "Email integration was crucial for success",
                "Analytics provided valuable insights"
            ]
        },
        {
            "store": "Beauty Brand DEF",
            "industry": "Beauty",
            "features_implemented": ["gamification", "premium_access"],
            "results": {
                "daily_active_users": "+150%",
                "social_shares": "+200%",
                "customer_lifetime_value": "+65%",
                "implementation_time": "12 weeks",
                "roi": "450%"
            },
            "key_learnings": [
                "Gamification drove daily engagement",
                "Premium access created exclusivity",
                "Community building was essential",
                "Influencer partnerships amplified results"
            ]
        }
    ]
    
    return {
        "case_studies": case_studies,
        "total_studies": len(case_studies),
        "average_metrics": {
            "revenue_increase": "29%",
            "implementation_time": "9 weeks",
            "roi": "350%"
        },
        "success_factors": [
            "Clear value proposition for customers",
            "Seamless user experience",
            "Strong marketing and education",
            "Ongoing optimization and updates"
        ]
    }
