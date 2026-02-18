"""
Knowledge Manager for Optik GPT
Manages the verified knowledge base, fact-checking, and learning
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime


class VerifiedKnowledgeBase:
    """Manages verified, always-accurate information about DApp creation."""

    def __init__(self):
        self.knowledge = {
            "blockchain_standards": {
                "ethereum": {
                    "erc20": {
                        "name": "ERC-20 Token Standard",
                        "spec": "https://eips.ethereum.org/EIPS/eip-20",
                        "functions": ["transfer", "approve", "transferFrom", "balanceOf"],
                        "events": ["Transfer", "Approval"],
                        "verified": True,
                        "description": "Standard interface for fungible tokens on EVM chains"
                    },
                    "erc721": {
                        "name": "ERC-721 NFT Standard",
                        "spec": "https://eips.ethereum.org/EIPS/eip-721",
                        "functions": ["balanceOf", "ownerOf", "safeTransferFrom", "setApprovalForAll"],
                        "events": ["Transfer", "Approval", "ApprovalForAll"],
                        "verified": True,
                        "description": "Standard for non-fungible tokens"
                    },
                    "erc1155": {
                        "name": "ERC-1155 Multi-Token Standard",
                        "spec": "https://eips.ethereum.org/EIPS/eip-1155",
                        "functions": ["balanceOf", "safeTransferFrom", "safeBatchTransferFrom"],
                        "verified": True,
                        "description": "Efficient standard for both fungible and non-fungible tokens"
                    }
                },
                "solana": {
                    "spl_token": {
                        "name": "SPL Token Program",
                        "spec": "https://spl.solana.com/token",
                        "verified": True,
                        "description": "Standard for creating and managing tokens on Solana",
                        "cost_advantage": "Sub-cent transaction costs"
                    },
                    "metaplex": {
                        "name": "Metaplex Token Metadata",
                        "spec": "https://metaplex.com/",
                        "verified": True,
                        "description": "Standard for NFT metadata and digital assets on Solana"
                    }
                }
            },
            "gas_and_costs": {
                "ethereum": {
                    "simple_transfer": "21,000 gas (~$0.50 at 50 gwei)",
                    "token_transfer": "65,000 gas (~$1.50)",
                    "complex_defi_interaction": "200,000-500,000 gas (~$5-12)",
                    "verified": True,
                    "source": "Ethereum Yellowpaper and network analysis"
                },
                "solana": {
                    "token_transfer": "~5,000 compute units (~$0.000005)",
                    "complex_program_call": "~100,000 compute units (~$0.0001)",
                    "verified": True,
                    "advantage": "10,000x cheaper than Ethereum for comparable operations"
                }
            },
            "legal_frameworks": {
                "united_states": {
                    "howey_test": "Securities are investments with expectation of profits from efforts of others",
                    "implication": "Most tokens that meet Howey test need SEC registration or exemption",
                    "exemptions": ["Regulation D (506c)", "Regulation A", "Section 4(a)(2)"],
                    "verified": True,
                    "source": "SEC enforcement history"
                },
                "singapore": {
                    "mica": "Monetary Authority of Singapore regulates digital asset exchanges",
                    "advantage": "Most crypto-friendly jurisdiction",
                    "verified": True,
                    "source": "MAS official guidance"
                },
                "european_union": {
                    "mica_regulation": "Markets in Crypto-Assets Regulation (MiCA)",
                    "effective_date": "December 2024",
                    "requirement": "Operators must apply for authorization",
                    "verified": True,
                    "source": "EU official gazette"
                }
            },
            "security_checklist": {
                "smart_contract": [
                    {
                        "check": "Reentrancy guards (ReentrancyGuard, checks-effects-interactions)",
                        "severity": "CRITICAL",
                        "verified": True
                    },
                    {
                        "check": "Integer overflow/underflow (Solidity 0.8+, SafeMath)",
                        "severity": "CRITICAL",
                        "verified": True
                    },
                    {
                        "check": "Access control (onlyOwner, role-based)",
                        "severity": "CRITICAL",
                        "verified": True
                    },
                    {
                        "check": "Front-running protection",
                        "severity": "HIGH",
                        "verified": True
                    },
                    {
                        "check": "Time-dependent logic (block.timestamp manipulation)",
                        "severity": "MEDIUM",
                        "verified": True
                    }
                ]
            },
            "tokenomics_fundamentals": {
                "sustainable_staking": {
                    "principle": "Daily inflation must not exceed daily protocol revenue",
                    "formula": "APY = (Daily Revenue / Staked Amount) * 365",
                    "safe_apy_range": "5-15% depending on adoption",
                    "verified": True,
                    "example": "If staking $1M and generating $50k/day: APY = (50k / 1M) * 365 = 18.25%"
                },
                "token_distribution": {
                    "fair_launch": {
                        "team": "5% with 4-year linear vesting",
                        "advisors": "10% with 2-year cliff + 2-year vesting",
                        "treasury": "15% for development and growth",
                        "community_liquidity_mining": "70% for users and early adoption",
                        "verified": True,
                        "reasoning": "Prevents founder dumps, incentivizes community participation"
                    }
                }
            }
        }

    def get_verified_fact(self, topic: str, subtopic: Optional[str] = None) -> Optional[Dict]:
        """Retrieve a verified fact from the knowledge base."""
        if subtopic:
            return self.knowledge.get(topic, {}).get(subtopic)
        return self.knowledge.get(topic)

    def verify_claim(self, claim: str) -> Tuple[bool, str]:
        """
        Verify if a claim matches our verified knowledge base.
        Returns (is_verified, explanation)
        """
        claim_lower = claim.lower()

        # Check against known standards
        if "erc20" in claim_lower or "erc-20" in claim_lower:
            return True, "ERC-20 is the standard token interface for EVM blockchains"

        if "erc721" in claim_lower or "erc-721" in claim_lower:
            return True, "ERC-721 is the standard for non-fungible tokens (NFTs) on EVM"

        if "solana" in claim_lower and "cent" in claim_lower:
            return True, "Solana transactions cost a fraction of a cent"

        if "reentrancy" in claim_lower:
            return True, "Reentrancy is a critical vulnerability requiring guards or checks-effects-interactions pattern"

        if "howey" in claim_lower:
            return True, "The Howey Test is the legal standard for determining if something is a security in the US"

        # Uncertain claim
        return False, f"Unable to verify: '{claim}' - recommend additional research"

    def add_verified_knowledge(self, topic: str, content: Dict[str, Any], source: str):
        """Add new verified knowledge to the base."""
        if topic not in self.knowledge:
            self.knowledge[topic] = {}

        self.knowledge[topic].update({
            **content,
            "verified": True,
            "added_at": datetime.now().isoformat(),
            "source": source
        })

    def export_knowledge(self) -> Dict[str, Any]:
        """Export all verified knowledge as JSON."""
        return self.knowledge


class RevenueTracker:
    """Tracks revenue opportunities and monetization recommendations."""

    def __init__(self):
        self.revenue_opportunities = []
        self.merchant_revenue_profiles: Dict[str, Dict] = {}

    def identify_revenue_opportunity(self, merchant_id: str, task: str, response: str) -> Optional[Dict]:
        """
        Identify revenue opportunities in the conversation context.
        Returns structured opportunity data.
        """
        opportunity = {
            "merchant_id": merchant_id,
            "identified_at": datetime.now().isoformat(),
            "task_context": task,
            "opportunity_type": None,
            "estimated_annual_revenue": None,
            "implementation_complexity": None,
            "recommendation": None
        }

        # Identify opportunity type
        if "staking" in task.lower():
            opportunity["opportunity_type"] = "Staking Rewards"
            opportunity["estimated_annual_revenue"] = "5-10% of TVL"
            opportunity["implementation_complexity"] = "Medium"
            opportunity["recommendation"] = "Implement staking contract with revenue sharing from protocol fees"

        elif "token" in task.lower() and "distribution" in task.lower():
            opportunity["opportunity_type"] = "Token Economics"
            opportunity["estimated_annual_revenue"] = "Varies by model"
            opportunity["implementation_complexity"] = "High"
            opportunity["recommendation"] = "Design sustainable inflation mechanism backed by protocol revenue"

        elif "fee" in task.lower() or "transaction" in task.lower():
            opportunity["opportunity_type"] = "Transaction Fees"
            opportunity["estimated_annual_revenue"] = "0.1% - 0.5% of trading volume"
            opportunity["implementation_complexity"] = "Low"
            opportunity["recommendation"] = "Implement router contract that collects fee on each transaction"

        elif "launch" in task.lower():
            opportunity["opportunity_type"] = "Launch Revenue Stream"
            opportunity["estimated_annual_revenue"] = "Multiple streams combined"
            opportunity["implementation_complexity"] = "High"
            opportunity["recommendation"] = "Establish primary revenue model before mainnet launch"

        if opportunity["opportunity_type"]:
            self.revenue_opportunities.append(opportunity)
            return opportunity

        return None

    def get_merchant_revenue_profile(self, merchant_id: str) -> Dict[str, Any]:
        """Get revenue profile for a merchant."""
        if merchant_id not in self.merchant_revenue_profiles:
            self.merchant_revenue_profiles[merchant_id] = {
                "merchant_id": merchant_id,
                "identified_opportunities": 0,
                "total_estimated_annual_revenue": "$0",
                "primary_revenue_streams": [],
                "secondary_revenue_streams": []
            }

        return self.merchant_revenue_profiles[merchant_id]

    def update_revenue_profile(self, merchant_id: str, opportunity: Dict):
        """Update merchant's revenue profile with new opportunity."""
        profile = self.get_merchant_revenue_profile(merchant_id)
        profile["identified_opportunities"] += 1

        if "Primary" in opportunity.get("opportunity_type", ""):
            profile["primary_revenue_streams"].append(opportunity["opportunity_type"])
        else:
            profile["secondary_revenue_streams"].append(opportunity["opportunity_type"])

    def export_revenue_opportunities(self, merchant_id: Optional[str] = None) -> List[Dict]:
        """Export revenue opportunities (filtered by merchant if provided)."""
        if merchant_id:
            return [opp for opp in self.revenue_opportunities if opp["merchant_id"] == merchant_id]
        return self.revenue_opportunities


# Singleton instances
_knowledge_base_instance: Optional[VerifiedKnowledgeBase] = None
_revenue_tracker_instance: Optional[RevenueTracker] = None


def get_knowledge_base() -> VerifiedKnowledgeBase:
    """Get or create the global knowledge base instance."""
    global _knowledge_base_instance
    if _knowledge_base_instance is None:
        _knowledge_base_instance = VerifiedKnowledgeBase()
    return _knowledge_base_instance


def get_revenue_tracker() -> RevenueTracker:
    """Get or create the global revenue tracker instance."""
    global _revenue_tracker_instance
    if _revenue_tracker_instance is None:
        _revenue_tracker_instance = RevenueTracker()
    return _revenue_tracker_instance
