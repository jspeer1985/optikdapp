# ============================================
# OPTIK PLATFORM - BACKEND SERVICES
# ============================================
# 
# Core backend services for the automated dApp factory:
# - AI Agent Pipeline
# - Automated dApp Factory
# - Client Onboarding System
# ============================================

from .ai_agent_pipeline import AIAgentPipeline
from .automated_dapp_factory import AutomatedDAppFactory
from .automated_client_onboarding import AutomatedClientOnboarding

__all__ = [
    'AIAgentPipeline',
    'AutomatedDAppFactory', 
    'AutomatedClientOnboarding'
]

__version__ = "1.0.0"
__description__ = "Optik Platform Backend Services"
