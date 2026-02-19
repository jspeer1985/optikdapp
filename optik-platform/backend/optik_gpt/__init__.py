"""
Optik GPT - The Smartest DApp Creation Assistant.

This package may run in environments where some optional AI providers are not
installed. Keep imports defensive so lightweight modules can still be loaded.
"""

OptikGPTEngine = None
get_engine = None
AgentFactory = None
DAppAgent = None
VerifiedKnowledgeBase = None
RevenueTracker = None
get_knowledge_base = None
get_revenue_tracker = None

try:
    from .assistant.claude_engine import OptikGPTEngine, get_engine
except Exception:
    pass

try:
    from .agents.dapp_agents import AgentFactory, DAppAgent
except Exception:
    pass

try:
    from .services.knowledge_manager import (
        VerifiedKnowledgeBase,
        RevenueTracker,
        get_knowledge_base,
        get_revenue_tracker,
    )
except Exception:
    pass

__version__ = "1.0.0"
__author__ = "Optik Team"

__all__ = [
    name
    for name in [
        "OptikGPTEngine",
        "get_engine",
        "AgentFactory",
        "DAppAgent",
        "VerifiedKnowledgeBase",
        "RevenueTracker",
        "get_knowledge_base",
        "get_revenue_tracker",
    ]
    if globals().get(name) is not None
]
