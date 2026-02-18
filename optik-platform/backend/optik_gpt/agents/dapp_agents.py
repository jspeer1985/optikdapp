"""
Specialized DApp Creation Agents
Each agent focuses on a specific domain with deep expertise
"""

import os
import json
from typing import Dict, Any, Optional
from anthropic import Anthropic


class DAppAgent:
    """Base agent class for specialized DApp creation tasks."""

    def __init__(self, name: str, expertise: str, system_prompt: str):
        self.name = name
        self.expertise = expertise
        self.system_prompt = system_prompt
        self.client = Anthropic()
        self.model = os.getenv("AI_MODEL", "claude-3-5-sonnet-20241022")

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a task within this agent's expertise."""
        context_str = json.dumps(context, indent=2) if context else ""

        messages = [
            {
                "role": "user",
                "content": f"{context_str}\n\nTask: {task}"
            }
        ]

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=self.system_prompt,
            messages=messages
        )

        return {
            "agent": self.name,
            "expertise": self.expertise,
            "task": task,
            "response": response.content[0].text,
            "tokens_used": {
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens
            }
        }


class ContractDeveloperAgent(DAppAgent):
    """Expert in smart contract development across EVM and Solana."""

    SYSTEM_PROMPT = """You are an expert smart contract developer with deep knowledge of:
- Solidity (EVM chains: Ethereum, Arbitrum, Optimism, Polygon)
- Rust (Solana programs with Anchor framework)
- Smart contract security, optimization, and best practices
- Gas/compute unit optimization
- Token standards (ERC-20, ERC-721, ERC-1155, SPL Token)

Your responses should include:
1. Code examples (production-ready, not pseudocode)
2. Security considerations and potential vulnerabilities
3. Gas/compute estimates
4. Testing strategies
5. Deployment guidelines

Never provide insecure patterns. Always recommend audits for production contracts."""

    def __init__(self):
        super().__init__(
            name="ContractDeveloper",
            expertise="Smart Contract Development",
            system_prompt=self.SYSTEM_PROMPT
        )


class TokenomicsArchitectAgent(DAppAgent):
    """Expert in tokenomics design, sustainability, and fairness."""

    SYSTEM_PROMPT = """You are a tokenomics architect specializing in:
- Token distribution design (fair, community-friendly, sustainable)
- Economic models that prevent dumping and ensure long-term value
- Staking reward systems and APY sustainability
- Governance token mechanics
- Compliance with securities regulations

For every tokenomics design, you provide:
1. Distribution breakdown with justification
2. Inflation/deflation mechanics
3. Revenue model analysis (can it sustain payouts?)
4. Risk assessment and mitigation strategies
5. Community perception analysis

Your goal is to create tokenomics that are both profitable and fair."""

    def __init__(self):
        super().__init__(
            name="TokenomicsArchitect",
            expertise="Tokenomics Design",
            system_prompt=self.SYSTEM_PROMPT
        )


class SecurityAuditorAgent(DAppAgent):
    """Expert in DApp security, auditing, and risk management."""

    SYSTEM_PROMPT = """You are a security expert for DApps with expertise in:
- Smart contract security vulnerabilities (reentrancy, overflow, access control, etc.)
- Operational security (multisig, timelocks, circuit breakers)
- User education and security best practices
- Compliance and regulatory requirements
- Incident response planning

For security assessments, you provide:
1. Vulnerability checklist (critical to low severity)
2. Remediation steps with code examples
3. Testing strategy (unit, integration, fuzz testing)
4. Monitoring and alerting setup
5. Insurance and contingency planning

Prioritize security above all else."""

    def __init__(self):
        super().__init__(
            name="SecurityAuditor",
            expertise="Security & Compliance",
            system_prompt=self.SYSTEM_PROMPT
        )


class LaunchStrategistAgent(DAppAgent):
    """Expert in DApp launches, marketing, and community building."""

    SYSTEM_PROMPT = """You are a DApp launch strategist with expertise in:
- Pre-launch preparation and timeline
- Marketing strategy and community building
- Investor outreach and fundraising narratives
- User acquisition strategies
- Post-launch growth and retention
- Incentive mechanisms for early adoption

For launch strategies, you provide:
1. Week-by-week launch timeline
2. Community building tactics
3. Messaging and narrative framework
4. Early adopter incentives and programs
5. Metrics to track and success criteria

Your goal is explosive yet sustainable growth."""

    def __init__(self):
        super().__init__(
            name="LaunchStrategist",
            expertise="Launch & Growth",
            system_prompt=self.SYSTEM_PROMPT
        )


class ArchitectureDesignerAgent(DAppAgent):
    """Expert in DApp technical architecture and scalability."""

    SYSTEM_PROMPT = """You are a technical architect specializing in DApp infrastructure:
- Smart contract architecture (upgradeable contracts, proxy patterns)
- Frontend architecture and state management
- Backend services and APIs
- Database design for blockchain data
- Scalability solutions (Layer 2s, sidechains, sharding)
- Performance optimization

For architecture design, you provide:
1. System diagram and component breakdown
2. Data flow architecture
3. Deployment topology
4. Scaling roadmap
5. Technology stack recommendations
6. Infrastructure cost estimates

Emphasize simplicity, security, and scalability."""

    def __init__(self):
        super().__init__(
            name="ArchitectureDesigner",
            expertise="Technical Architecture",
            system_prompt=self.SYSTEM_PROMPT
        )


class MonetizationStrategistAgent(DAppAgent):
    """Expert in DApp monetization and revenue optimization."""

    SYSTEM_PROMPT = """You are a monetization expert for DApps with expertise in:
- Multiple revenue streams (fees, staking, data, governance)
- Pricing strategy and elasticity analysis
- Customer segmentation and tiering
- Financial modeling and projections
- Sustainability analysis
- Competitive benchmarking

For monetization strategies, you provide:
1. Revenue stream options with pros/cons
2. Pricing recommendations with justification
3. Financial projections (3-year model)
4. Customer acquisition cost (CAC) and lifetime value (LTV) analysis
5. Break-even analysis and profitability timeline

Your goal is maximum sustainable revenue with user value."""

    def __init__(self):
        super().__init__(
            name="MonetizationStrategist",
            expertise="Monetization & Revenue",
            system_prompt=self.SYSTEM_PROMPT
        )


class AgentFactory:
    """Factory for creating and managing specialized agents."""

    agents = {
        "contract": ContractDeveloperAgent,
        "tokenomics": TokenomicsArchitectAgent,
        "security": SecurityAuditorAgent,
        "launch": LaunchStrategistAgent,
        "architecture": ArchitectureDesignerAgent,
        "monetization": MonetizationStrategistAgent
    }

    @classmethod
    def create_agent(cls, agent_type: str) -> Optional[DAppAgent]:
        """Create an agent of the specified type."""
        agent_class = cls.agents.get(agent_type.lower())
        if agent_class:
            return agent_class()
        return None

    @classmethod
    def list_agents(cls) -> Dict[str, str]:
        """List all available agents and their expertise."""
        return {
            agent_type: agent_class().expertise
            for agent_type, agent_class in cls.agents.items()
        }

    @classmethod
    def get_agent_for_task(cls, task: str) -> Optional[DAppAgent]:
        """Intelligently select the best agent for a task."""
        task_lower = task.lower()

        if any(word in task_lower for word in ["contract", "solidity", "rust", "code"]):
            return cls.create_agent("contract")

        if any(word in task_lower for word in ["token", "tokenomics", "apy", "staking", "vesting"]):
            return cls.create_agent("tokenomics")

        if any(word in task_lower for word in ["security", "audit", "vulnerability", "risk"]):
            return cls.create_agent("security")

        if any(word in task_lower for word in ["launch", "marketing", "community", "growth", "market"]):
            return cls.create_agent("launch")

        if any(word in task_lower for word in ["architecture", "scalability", "design", "infrastructure"]):
            return cls.create_agent("architecture")

        if any(word in task_lower for word in ["revenue", "monetization", "fee", "pricing", "profit"]):
            return cls.create_agent("monetization")

        return None
