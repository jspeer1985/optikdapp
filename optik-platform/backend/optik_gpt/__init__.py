"""
Optik GPT - The Smartest DApp Creation Assistant
Powered by Anthropic's Claude

A comprehensive AI system for guiding builders through every stage of DApp creation:
- Smart contract development
- Tokenomics design
- Security & compliance
- Launch strategy
- Technical architecture
- Revenue optimization
"""

from .assistant.claude_engine import OptikGPTEngine, get_engine
from .agents.dapp_agents import AgentFactory, DAppAgent
from .services.knowledge_manager import (
    VerifiedKnowledgeBase,
    RevenueTracker,
    get_knowledge_base,
    get_revenue_tracker
)

__version__ = "1.0.0"
__author__ = "Optik Team"

__all__ = [
    "OptikGPTEngine",
    "get_engine",
    "AgentFactory",
    "DAppAgent",
    "VerifiedKnowledgeBase",
    "RevenueTracker",
    "get_knowledge_base",
    "get_revenue_tracker",
]
