"""
Optik GPT Usage Examples
Demonstrates how to use Optik GPT in your applications
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .assistant.claude_engine import get_engine
from .agents.dapp_agents import AgentFactory
from .services.knowledge_manager import get_knowledge_base, get_revenue_tracker


def example_basic_chat():
    """Example 1: Basic conversation with Optik GPT."""
    print("=" * 80)
    print("EXAMPLE 1: Basic Chat")
    print("=" * 80)

    engine = get_engine()

    # First message
    response = engine.chat(
        merchant_id="demo_merchant_001",
        user_message="I want to create a DEX. Where should I start?",
        update_metadata={
            "dapp_type": "DEX (Decentralized Exchange)",
            "stage": "Ideation",
            "team_size": "3-5 people"
        }
    )

    print(f"\n🤖 Optik GPT Response:\n{response['message']}")
    print(f"\n💡 Revenue Opportunity: {response.get('revenue_opportunity')}")
    print(f"\n📊 Metadata: {response['metadata']}")


def example_multi_turn_conversation():
    """Example 2: Multi-turn conversation with context."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Multi-Turn Conversation")
    print("=" * 80)

    engine = get_engine()
    merchant_id = "demo_merchant_002"

    # Turn 1: Ask about tokenomics
    print("\n👤 User: How should I structure my token?")
    response1 = engine.chat(
        merchant_id=merchant_id,
        user_message="How should I structure my token?",
        update_metadata={
            "dapp_type": "Yield Farming",
            "stage": "Development"
        }
    )
    print(f"🤖 Assistant: {response1['message'][:500]}...")

    # Turn 2: Follow-up question (uses conversation history)
    print("\n👤 User: What APY should I offer for staking?")
    response2 = engine.chat(
        merchant_id=merchant_id,
        user_message="What APY should I offer for staking?"
    )
    print(f"🤖 Assistant: {response2['message'][:500]}...")

    # Get session summary
    summary = engine.get_session_summary(merchant_id)
    print(f"\n📋 Session Summary:")
    print(f"   Total messages: {summary['message_count']}")
    print(f"   Topics discussed: {', '.join(summary['conversation_topics'])}")
    print(f"   Recommendations: {summary['recommendations'][:2]}")


def example_specialized_agents():
    """Example 3: Use specialized agents for specific tasks."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Specialized Agents")
    print("=" * 80)

    factory = AgentFactory()

    # Example 1: Contract Developer Agent
    print("\n🔧 Contract Developer Agent:")
    contract_agent = factory.create_agent("contract")
    result = contract_agent.execute(
        task="Write a secure ERC-20 token contract with minting controls",
        context={"framework": "OpenZeppelin", "solidity_version": "0.8.20"}
    )
    print(f"Response: {result['response'][:400]}...")
    print(f"Tokens used: {result['tokens_used']}")

    # Example 2: Tokenomics Agent
    print("\n💰 Tokenomics Architect Agent:")
    tokenomics_agent = factory.create_agent("tokenomics")
    result = tokenomics_agent.execute(
        task="Design sustainable tokenomics for a DEX with 10M supply",
        context={"target_tvl": "$100M", "initial_apys": "5-10%"}
    )
    print(f"Response: {result['response'][:400]}...")

    # Example 3: Auto-select best agent
    print("\n🎯 Auto-selected Agent (for security audit task):")
    best_agent = factory.get_agent_for_task(
        "What are the most critical security vulnerabilities to check?"
    )
    result = best_agent.execute("Check for reentrancy vulnerabilities")
    print(f"Selected agent: {result['agent']}")
    print(f"Response: {result['response'][:400]}...")

    # List all available agents
    print("\n📚 Available Agents:")
    agents = factory.list_agents()
    for agent_type, expertise in agents.items():
        print(f"   - {agent_type}: {expertise}")


def example_knowledge_base():
    """Example 4: Access verified knowledge base."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Verified Knowledge Base")
    print("=" * 80)

    kb = get_knowledge_base()

    # Get specific knowledge
    erc20_info = kb.get_verified_fact("blockchain_standards", "ethereum")
    print(f"\n🔍 ERC-20 Standard Info:")
    print(f"   Name: {erc20_info['erc20']['name']}")
    print(f"   Spec: {erc20_info['erc20']['spec']}")
    print(f"   Functions: {', '.join(erc20_info['erc20']['functions'])}")

    # Verify claims
    print(f"\n✅ Claim Verification:")

    claim1 = "ERC-20 is the standard for fungible tokens on Ethereum"
    verified1, explanation1 = kb.verify_claim(claim1)
    print(f"   Claim: {claim1}")
    print(f"   Verified: {verified1}")
    print(f"   Explanation: {explanation1}")

    claim2 = "Solana transactions cost less than a cent"
    verified2, explanation2 = kb.verify_claim(claim2)
    print(f"\n   Claim: {claim2}")
    print(f"   Verified: {verified2}")
    print(f"   Explanation: {explanation2}")


def example_revenue_tracking():
    """Example 5: Revenue opportunity tracking."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Revenue Opportunity Tracking")
    print("=" * 80)

    engine = get_engine()
    tracker = get_revenue_tracker()

    merchant_id = "demo_merchant_003"

    # Have conversations about different revenue opportunities
    messages = [
        "How do I implement transaction fees?",
        "What about staking rewards?",
        "Can I monetize my data?",
    ]

    for msg in messages:
        response = engine.chat(merchant_id=merchant_id, user_message=msg)
        opportunity = response.get("revenue_opportunity")
        if opportunity:
            print(f"\n💡 Identified: {opportunity['opportunity_type']}")
            print(f"   Suggestion: {opportunity['suggestion']}")

    # Get merchant revenue profile
    profile = tracker.get_merchant_revenue_profile(merchant_id)
    print(f"\n📊 Merchant Revenue Profile:")
    print(f"   Opportunities identified: {profile['identified_opportunities']}")
    print(f"   Primary streams: {profile['primary_revenue_streams']}")
    print(f"   Secondary streams: {profile['secondary_revenue_streams']}")


def example_complete_workflow():
    """Example 6: Complete DApp creation workflow."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Complete DApp Creation Workflow")
    print("=" * 80)

    engine = get_engine()
    factory = AgentFactory()
    merchant_id = "complete_dapp_merchant"

    workflow_steps = [
        {
            "step": 1,
            "title": "Ideation",
            "message": "I want to build a lending protocol. What should my architecture look like?",
            "metadata": {"stage": "Ideation", "dapp_type": "Lending"}
        },
        {
            "step": 2,
            "title": "Design",
            "message": "Help me design the token distribution and staking model",
            "agent_type": "tokenomics"
        },
        {
            "step": 3,
            "title": "Security",
            "message": "What security measures do I need?",
            "agent_type": "security"
        },
        {
            "step": 4,
            "title": "Monetization",
            "message": "How can I generate revenue sustainably?",
            "agent_type": "monetization"
        },
        {
            "step": 5,
            "title": "Launch",
            "message": "What's my launch strategy?",
            "agent_type": "launch"
        }
    ]

    for step_data in workflow_steps:
        step = step_data["step"]
        title = step_data["title"]

        print(f"\n📍 Step {step}: {title}")
        print(f"   Message: {step_data['message']}")

        if step_data.get("agent_type"):
            # Use specialized agent
            agent = factory.create_agent(step_data["agent_type"])
            result = agent.execute(step_data["message"])
            print(f"   Agent: {result['agent']}")
            print(f"   Response: {result['response'][:300]}...")
        else:
            # Use general chat
            metadata = step_data.get("metadata", {})
            response = engine.chat(
                merchant_id=merchant_id,
                user_message=step_data["message"],
                update_metadata=metadata
            )
            print(f"   Response: {response['message'][:300]}...")


if __name__ == "__main__":
    """Run all examples"""
    print("\n" + "🌟" * 40)
    print("OPTIK GPT - USAGE EXAMPLES")
    print("🌟" * 40)

    try:
        example_basic_chat()
        example_multi_turn_conversation()
        example_specialized_agents()
        example_knowledge_base()
        example_revenue_tracking()
        example_complete_workflow()

        print("\n" + "=" * 80)
        print("✅ All examples completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        print("Make sure ANTHROPIC_API_KEY is set in your environment")
        raise
