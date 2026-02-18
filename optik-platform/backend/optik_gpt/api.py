"""
Optik GPT API Endpoints
Provides REST interface to the smartest DApp creation assistant
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from .assistant.claude_engine import get_engine as get_claude_engine
from .agents.dapp_agents import AgentFactory
from .services.knowledge_manager import get_knowledge_base, get_revenue_tracker

logger = logging.getLogger(__name__)

# API Router
router = APIRouter(prefix="/api/optik-gpt", tags=["Optik GPT"])


# ============================================
# Request/Response Models
# ============================================

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    merchant_id: str
    dapp_type: Optional[str] = None
    stage: Optional[str] = None
    team_size: Optional[str] = None
    revenue_model: Optional[str] = None
    challenges: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    status: str
    message: str
    metadata: Dict[str, Any]
    revenue_opportunity: Optional[Dict[str, Any]]
    session_length: int


class AgentTaskRequest(BaseModel):
    """Request model for specialized agent endpoint."""
    task: str
    agent_type: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class AgentTaskResponse(BaseModel):
    """Response model for specialized agent endpoint."""
    agent: str
    expertise: str
    task: str
    response: str
    tokens_used: Dict[str, int]


class SessionSummaryResponse(BaseModel):
    """Response model for session summary endpoint."""
    merchant_id: str
    message_count: int
    user_messages: int
    assistant_responses: int
    metadata: Dict[str, Any]
    conversation_topics: list
    recommendations: list


class VerificationRequest(BaseModel):
    """Request model for fact-checking endpoint."""
    claim: str


class VerificationResponse(BaseModel):
    """Response model for fact-checking endpoint."""
    claim: str
    verified: bool
    explanation: str


# ============================================
# Core Endpoints
# ============================================

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint - Talk to Optik GPT about DApp creation.

    Features:
    - Claude-powered responses with DApp expertise
    - Automatic revenue opportunity detection
    - Conversation memory and context management
    - Personalized guidance based on DApp stage and type
    """
    try:
        engine = get_claude_engine()

        # Prepare metadata update
        metadata_update = {}
        if request.dapp_type:
            metadata_update["dapp_type"] = request.dapp_type
        if request.stage:
            metadata_update["stage"] = request.stage
        if request.team_size:
            metadata_update["team_size"] = request.team_size
        if request.revenue_model:
            metadata_update["revenue_model"] = request.revenue_model
        if request.challenges:
            metadata_update["challenges"] = request.challenges

        # Get response from Claude engine
        response = engine.chat(
            merchant_id=request.merchant_id,
            user_message=request.message,
            update_metadata=metadata_update if metadata_update else None
        )

        # Track revenue opportunity
        if response.get("revenue_opportunity"):
            revenue_tracker = get_revenue_tracker()
            revenue_tracker.identify_revenue_opportunity(
                request.merchant_id,
                request.message,
                response["message"]
            )

        return ChatResponse(**response)

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.post("/agent/execute", response_model=AgentTaskResponse)
async def execute_agent_task(request: AgentTaskRequest) -> AgentTaskResponse:
    """
    Execute a specialized agent task.

    Available agent types:
    - `contract` - Smart contract development expertise
    - `tokenomics` - Token design and economics
    - `security` - Security auditing and compliance
    - `launch` - Launch strategy and growth
    - `architecture` - Technical architecture design
    - `monetization` - Revenue and business model

    If agent_type is not specified, the system automatically selects the best agent.
    """
    try:
        factory = AgentFactory()

        # Select agent
        if request.agent_type:
            agent = factory.create_agent(request.agent_type)
            if not agent:
                available = list(factory.list_agents().keys())
                raise HTTPException(
                    status_code=400,
                    detail=f"Unknown agent type. Available: {available}"
                )
        else:
            agent = factory.get_agent_for_task(request.task)
            if not agent:
                agent = factory.create_agent("tokenomics")  # Default fallback

        # Execute task
        result = agent.execute(request.task, request.context)

        return AgentTaskResponse(**result)

    except Exception as e:
        logger.error(f"Agent execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")


@router.get("/agents", response_model=Dict[str, str])
async def list_agents() -> Dict[str, str]:
    """List all available specialized agents and their expertise areas."""
    factory = AgentFactory()
    return factory.list_agents()


@router.get("/session/{merchant_id}/summary", response_model=SessionSummaryResponse)
async def get_session_summary(merchant_id: str) -> SessionSummaryResponse:
    """
    Get a summary of the conversation session for a merchant.

    Includes:
    - Message count and topic analysis
    - Conversation topics discussed
    - Personalized recommendations
    - Metadata about the DApp being built
    """
    try:
        engine = get_claude_engine()
        summary = engine.get_session_summary(merchant_id)

        return SessionSummaryResponse(**summary)

    except Exception as e:
        logger.error(f"Session summary error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session summary: {str(e)}")


# ============================================
# Verification & Knowledge Endpoints
# ============================================

@router.post("/verify", response_model=VerificationResponse)
async def verify_claim(request: VerificationRequest) -> VerificationResponse:
    """
    Verify if a claim is accurate according to our verified knowledge base.

    This ensures Optik GPT responses are never false - all claims are checked
    against blockchain standards, legal frameworks, and security principles.
    """
    try:
        kb = get_knowledge_base()
        is_verified, explanation = kb.verify_claim(request.claim)

        return VerificationResponse(
            claim=request.claim,
            verified=is_verified,
            explanation=explanation
        )

    except Exception as e:
        logger.error(f"Verification error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.get("/knowledge", response_model=Dict[str, Any])
async def get_knowledge_base_export() -> Dict[str, Any]:
    """
    Export the verified knowledge base used by Optik GPT.

    This includes:
    - Blockchain standards and specifications
    - Gas costs and performance metrics
    - Legal frameworks by jurisdiction
    - Security checklists
    - Tokenomics fundamentals
    """
    try:
        kb = get_knowledge_base()
        return kb.export_knowledge()

    except Exception as e:
        logger.error(f"Knowledge export error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export knowledge: {str(e)}")


# ============================================
# Revenue & Analytics Endpoints
# ============================================

@router.get("/revenue/opportunities")
async def get_revenue_opportunities(merchant_id: Optional[str] = Query(None)):
    """
    Get identified revenue opportunities for a merchant or all merchants.

    Returns structured opportunities with:
    - Opportunity type
    - Estimated annual revenue potential
    - Implementation complexity
    - Specific recommendations
    """
    try:
        tracker = get_revenue_tracker()
        opportunities = tracker.export_revenue_opportunities(merchant_id)

        return {
            "status": "success",
            "merchant_id": merchant_id,
            "opportunities_count": len(opportunities),
            "opportunities": opportunities
        }

    except Exception as e:
        logger.error(f"Revenue opportunities error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get revenue opportunities: {str(e)}")


@router.get("/revenue/profile/{merchant_id}")
async def get_revenue_profile(merchant_id: str):
    """
    Get monetization profile for a specific merchant.

    Includes:
    - Number of revenue opportunities identified
    - Total estimated annual revenue potential
    - Primary and secondary revenue streams
    """
    try:
        tracker = get_revenue_tracker()
        profile = tracker.get_merchant_revenue_profile(merchant_id)

        return {
            "status": "success",
            "profile": profile
        }

    except Exception as e:
        logger.error(f"Revenue profile error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get revenue profile: {str(e)}")


# ============================================
# Health & Status Endpoints
# ============================================

@router.get("/health")
async def health_check():
    """Health check endpoint for Optik GPT service."""
    return {
        "status": "healthy",
        "service": "Optik GPT",
        "version": "1.0.0",
        "features": [
            "Claude-powered conversations",
            "Specialized DApp agents",
            "Verified knowledge base",
            "Revenue opportunity detection",
            "Session management",
            "Fact verification"
        ]
    }


@router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Optik GPT - The Smartest DApp Creation Assistant",
        "description": "Powered by Anthropic's Claude",
        "version": "1.0.0",
        "features": {
            "chat": "Intelligent conversations about DApp creation",
            "agents": "Specialized experts for contracts, tokenomics, security, launch, architecture, monetization",
            "knowledge": "Verified knowledge base for accurate information",
            "revenue": "Automatic revenue opportunity detection and analysis"
        },
        "docs": "/docs",
        "redoc": "/redoc"
    }
