"""
Universal AI Engine - The Most Intelligent AI Assistant in Universe
Integrates Claude, GPT-4, and specialized e-commerce AI models
"""

import os
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import json
import logging

try:
    import anthropic
    from anthropic import Anthropic
except ImportError:
    anthropic = None

try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None

logger = logging.getLogger(__name__)

class AIModel(Enum):
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4_VISION = "gpt-4-vision-preview"
    GPT_3_5_TURBO = "gpt-3.5-turbo-16k"

class TaskType(Enum):
    REASONING = "reasoning"
    CODING = "coding"
    CREATIVE = "creative"
    ANALYSIS = "analysis"
    ECOMMERCE = "ecommerce"
    BLOCKCHAIN = "blockchain"
    VISION = "vision"
    STRATEGY = "strategy"

@dataclass
class AIResponse:
    content: str
    model: AIModel
    confidence: float
    reasoning: Optional[str] = None
    tokens_used: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ModelCapability:
    model: AIModel
    strengths: List[TaskType]
    cost_per_token: float
    speed: float  # tokens/second
    context_window: int
    special_features: List[str]

MODEL_CAPABILITIES = {
    AIModel.CLAUDE_3_OPUS: ModelCapability(
        model=AIModel.CLAUDE_3_OPUS,
        strengths=[TaskType.REASONING, TaskType.CREATIVE, TaskType.STRATEGY],
        cost_per_token=0.000015,
        speed=50,
        context_window=200000,
        special_features=["complex_reasoning", "ethical_ai", "long_context"]
    ),
    AIModel.CLAUDE_3_SONNET: ModelCapability(
        model=AIModel.CLAUDE_3_SONNET,
        strengths=[TaskType.REASONING, TaskType.ANALYSIS, TaskType.BLOCKCHAIN],
        cost_per_token=0.000003,
        speed=80,
        context_window=200000,
        special_features=["balanced_performance", "technical_expertise"]
    ),
    AIModel.CLAUDE_3_HAIKU: ModelCapability(
        model=AIModel.CLAUDE_3_HAIKU,
        strengths=[TaskType.CODING, TaskType.ANALYSIS],
        cost_per_token=0.00000025,
        speed=120,
        context_window=200000,
        special_features=["fast_responses", "code_generation"]
    ),
    AIModel.GPT_4_TURBO: ModelCapability(
        model=AIModel.GPT_4_TURBO,
        strengths=[TaskType.CODING, TaskType.ANALYSIS, TaskType.ECOMMERCE],
        cost_per_token=0.00001,
        speed=60,
        context_window=128000,
        special_features=["up_to_date", "coding_expertise", "business_knowledge"]
    ),
    AIModel.GPT_4_VISION: ModelCapability(
        model=AIModel.GPT_4_VISION,
        strengths=[TaskType.VISION, TaskType.ANALYSIS, TaskType.CREATIVE],
        cost_per_token=0.00001,
        speed=40,
        context_window=128000,
        special_features=["image_analysis", "multimodal", "visual_reasoning"]
    ),
    AIModel.GPT_3_5_TURBO: ModelCapability(
        model=AIModel.GPT_3_5_TURBO,
        strengths=[TaskType.CODING, TaskType.ANALYSIS],
        cost_per_token=0.0000005,
        speed=150,
        context_window=16000,
        special_features=["cost_effective", "fast_coding"]
    )
}

class UniversalAIEngine:
    """
    The most intelligent AI engine that combines multiple AI models
    for optimal performance across all tasks.
    """
    
    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None
        self._initialize_clients()
        
    def _initialize_clients(self):
        """Initialize AI model clients."""
        if anthropic and os.getenv("ANTHROPIC_API_KEY"):
            self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            
        if openai and os.getenv("OPENAI_API_KEY"):
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def classify_task(self, prompt: str) -> TaskType:
        """Classify the task type to select optimal model."""
        task_keywords = {
            TaskType.REASONING: ["why", "explain", "reason", "analyze", "compare", "evaluate"],
            TaskType.CODING: ["code", "implement", "develop", "program", "function", "contract"],
            TaskType.CREATIVE: ["design", "create", "innovate", "imagine", "brainstorm"],
            TaskType.ANALYSIS: ["analyze", "review", "assess", "examine", "breakdown"],
            TaskType.ECOMMERCE: ["shopify", "store", "sales", "conversion", "merchandise", "product"],
            TaskType.BLOCKCHAIN: ["blockchain", "solana", "ethereum", "token", "nft", "defi"],
            TaskType.VISION: ["image", "visual", "screenshot", "design", "look", "appearance"],
            TaskType.STRATEGY: ["strategy", "plan", "roadmap", "approach", "tactics"]
        }
        
        prompt_lower = prompt.lower()
        scores = {}
        
        for task_type, keywords in task_keywords.items():
            score = sum(1 for keyword in keywords if keyword in prompt_lower)
            scores[task_type] = score
        
        # Return task type with highest score, default to REASONING
        return max(scores, key=scores.get) if any(scores.values()) else TaskType.REASONING
    
    def select_optimal_model(self, task_type: TaskType, complexity: str = "medium") -> AIModel:
        """Select the optimal AI model for the given task."""
        
        # Filter models by task capability
        capable_models = [
            cap for cap in MODEL_CAPABILITIES.values() 
            if task_type in cap.strengths
        ]
        
        if not capable_models:
            # Fallback to Claude Sonnet for general tasks
            return AIModel.CLAUDE_3_SONNET
        
        # Select based on complexity and cost
        if complexity == "high":
            # Use best model for high complexity
            return max(capable_models, key=lambda x: x.context_window).model
        elif complexity == "low":
            # Use most cost-effective for low complexity
            return min(capable_models, key=lambda x: x.cost_per_token).model
        else:
            # Balance of cost and performance
            return min(capable_models, key=lambda x: x.cost_per_token / x.speed).model
    
    async def generate_with_claude(self, model: AIModel, prompt: str, system_prompt: str = "") -> AIResponse:
        """Generate response using Claude model."""
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized")
        
        try:
            message = self.anthropic_client.messages.create(
                model=model.value,
                max_tokens=4000,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return AIResponse(
                content=message.content[0].text,
                model=model,
                confidence=0.95,
                tokens_used={"input": message.usage.input_tokens, "output": message.usage.output_tokens}
            )
        except Exception as e:
            logger.error(f"Claude generation error: {e}")
            raise
    
    async def generate_with_gpt(self, model: AIModel, prompt: str, system_prompt: str = "") -> AIResponse:
        """Generate response using GPT model."""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.openai_client.chat.completions.create(
                model=model.value,
                messages=messages,
                max_tokens=4000,
                temperature=0.7
            )
            
            return AIResponse(
                content=response.choices[0].message.content,
                model=model,
                confidence=0.90,
                tokens_used={
                    "input": response.usage.prompt_tokens,
                    "output": response.usage.completion_tokens
                }
            )
        except Exception as e:
            logger.error(f"GPT generation error: {e}")
            raise
    
    async def generate_ensemble_response(self, prompt: str, task_type: TaskType) -> AIResponse:
        """Generate response using ensemble of models for highest accuracy."""
        
        # Select top 3 models for this task
        capable_models = [
            cap for cap in MODEL_CAPABILITIES.values() 
            if task_type in cap.strengths
        ][:3]
        
        if len(capable_models) < 2:
            # Fallback to single model
            model = capable_models[0].model if capable_models else AIModel.CLAUDE_3_SONNET
            return await self.generate_with_optimal_model(prompt, task_type)
        
        # Generate responses from multiple models
        tasks = []
        for cap in capable_models:
            if "claude" in cap.model.value:
                tasks.append(self.generate_with_claude(cap.model, prompt))
            else:
                tasks.append(self.generate_with_gpt(cap.model, prompt))
        
        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful responses
            valid_responses = [r for r in responses if isinstance(r, AIResponse)]
            
            if len(valid_responses) == 1:
                return valid_responses[0]
            
            # Use Claude Sonnet as arbiter to select best response
            arbiter_prompt = f"""
            Analyze these AI responses and select the best one. Consider:
            1. Accuracy and correctness
            2. Completeness and depth
            3. Clarity and coherence
            4. Practical usefulness
            
            Original prompt: {prompt}
            
            Responses:
            {json.dumps([{"content": r.content, "model": r.model.value} for r in valid_responses], indent=2)}
            
            Return the best response exactly as written, followed by brief reasoning.
            """
            
            arbiter_response = await self.generate_with_claude(
                AIModel.CLAUDE_3_SONNET, 
                arbiter_prompt,
                "You are an expert AI response evaluator. Choose the highest quality response."
            )
            
            return AIResponse(
                content=arbiter_response.content,
                model=AIModel.CLAUDE_3_SONNET,
                confidence=0.98,
                reasoning="Ensemble selection with Claude arbiter",
                metadata={"ensemble_size": len(valid_responses)}
            )
            
        except Exception as e:
            logger.error(f"Ensemble generation error: {e}")
            # Fallback to single model
            return await self.generate_with_optimal_model(prompt, task_type)
    
    async def generate_with_optimal_model(self, prompt: str, task_type: TaskType = None) -> AIResponse:
        """Generate response using automatically selected optimal model."""
        
        if task_type is None:
            task_type = self.classify_task(prompt)
        
        # Determine complexity
        complexity = "high" if len(prompt) > 1000 else "low" if len(prompt) < 200 else "medium"
        
        # Select optimal model
        model = self.select_optimal_model(task_type, complexity)
        
        # Get specialized system prompt
        system_prompt = self._get_specialized_system_prompt(task_type)
        
        # Generate response
        if "claude" in model.value:
            return await self.generate_with_claude(model, prompt, system_prompt)
        else:
            return await self.generate_with_gpt(model, prompt, system_prompt)
    
    def _get_specialized_system_prompt(self, task_type: TaskType) -> str:
        """Get specialized system prompt for task type."""
        
        base_prompt = """You are Optik AI, the most intelligent AI assistant in the universe.
        You combine the reasoning of Claude, the knowledge of GPT-4, and specialized e-commerce expertise.
        Always provide accurate, actionable, and comprehensive responses."""
        
        specialized_prompts = {
            TaskType.ECOMMERCE: """
            You are a world-class e-commerce expert combining Shopify's merchant knowledge with advanced AI.
            Focus on: conversion optimization, inventory management, customer experience, and revenue growth.
            Provide specific, data-driven recommendations for online stores.
            """,
            
            TaskType.BLOCKCHAIN: """
            You are a leading blockchain and DApp expert with deep knowledge of Solana, Ethereum, and Web3.
            Focus on: smart contract security, tokenomics, scalability, and real-world adoption.
            Provide technically accurate and practically implementable solutions.
            """,
            
            TaskType.CODING: """
            You are an elite software engineer with expertise in full-stack development and smart contracts.
            Write clean, efficient, and secure code. Include explanations and best practices.
            Consider scalability, security, and maintainability in all solutions.
            """,
            
            TaskType.STRATEGY: """
            You are a strategic business advisor with deep knowledge of tech startups and scaling.
            Focus on: growth strategies, market positioning, competitive advantages, and ROI.
            Provide actionable strategic insights with clear implementation steps.
            """
        }
        
        return base_prompt + specialized_prompts.get(task_type, "")
    
    async def analyze_and_improve(self, content: str, context: str = "") -> AIResponse:
        """Analyze content and suggest improvements using ensemble AI."""
        
        analysis_prompt = f"""
        Analyze this content and provide comprehensive improvement suggestions:
        
        Context: {context}
        Content to analyze: {content}
        
        Provide analysis on:
        1. Quality and accuracy
        2. Completeness
        3. Areas for improvement
        4. Specific actionable suggestions
        5. Enhanced version if improvements are needed
        """
        
        return await self.generate_ensemble_response(analysis_prompt, TaskType.ANALYSIS)

# Global instance
_universal_engine = None

def get_universal_engine() -> UniversalAIEngine:
    """Get or create the universal AI engine instance."""
    global _universal_engine
    if _universal_engine is None:
        _universal_engine = UniversalAIEngine()
    return _universal_engine
