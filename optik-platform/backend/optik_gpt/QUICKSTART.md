# 🚀 Optik GPT Quick Start Guide

Get started with the smartest DApp creation assistant in minutes.

## Installation

### 1. Ensure Dependencies
```bash
cd /home/kali/Dapp_Optik/optik-platform/backend

# Verify requirements.txt includes:
# anthropic>=0.25.0
# langchain-anthropic>=0.1.15
# fastapi==0.111.0
# uvicorn==0.30.1
# pydantic>=2.7.2

pip install -r requirements.txt
```

### 2. Set Environment Variable
```bash
export ANTHROPIC_API_KEY="sk-ant-YOUR_API_KEY_HERE"
```

## Usage

### Option A: Use the REST API

**Start the server:**
```bash
cd /home/kali/Dapp_Optik/optik-platform/backend
uvicorn optik_gpt.main:app --reload --port 8000
```

**Access the API:**
- Interactive Docs: http://localhost:8000/docs
- API Root: http://localhost:8000/api/optik-gpt

**Example cURL request:**
```bash
curl -X POST "http://localhost:8000/api/optik-gpt/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_id": "merchant_001",
    "message": "How do I design my token?",
    "dapp_type": "DEX",
    "stage": "Development"
  }'
```

### Option B: Use Python Directly

```python
from optik_gpt.assistant.claude_engine import get_engine

# Get the engine
engine = get_engine()

# Chat with Optik GPT
response = engine.chat(
    merchant_id="my_dapp_123",
    user_message="How do I design sustainable tokenomics?",
    update_metadata={
        "dapp_type": "DEX",
        "stage": "Development",
        "team_size": "5 people"
    }
)

print(response["message"])
print(f"Revenue opportunity: {response['revenue_opportunity']}")
```

### Option C: Use Specialized Agents

```python
from optik_gpt.agents.dapp_agents import AgentFactory

factory = AgentFactory()

# Auto-select best agent
agent = factory.get_agent_for_task("Write a secure token contract")
result = agent.execute("Create an ERC-20 contract with minting controls")

print(result["response"])
```

## Key Features

### 1. **Never False Responses**
- All claims verified against knowledge base
- Unknown facts explicitly marked
- Fallback to official specifications

### 2. **Revenue Generation Focus**
- Automatic opportunity detection
- Monetization strategy recommendations
- Financial model analysis

### 3. **Specialized Agents**

| Agent | Use for |
|-------|---------|
| **contract** | Writing smart contracts |
| **tokenomics** | Token design and economics |
| **security** | Security auditing |
| **launch** | Launch strategy |
| **architecture** | Technical design |
| **monetization** | Revenue optimization |

### 4. **Conversation Memory**
- Maintains context across messages
- Provides session summaries
- Tracks topics discussed

## Common Questions

### Q: "How do I design my token distribution?"

```python
engine = get_engine()
response = engine.chat(
    merchant_id="my_merchant",
    user_message="What's a fair token distribution for my DApp?"
)
print(response["message"])
```

**Expected response includes:**
- Fair distribution breakdown (team, advisors, treasury, community)
- Justification for each allocation
- Vesting schedules
- Revenue model implications

### Q: "How do I create a smart contract?"

```python
from optik_gpt.agents.dapp_agents import AgentFactory

agent = AgentFactory.create_agent("contract")
result = agent.execute(
    "Write a secure ERC-20 token contract",
    context={"framework": "OpenZeppelin"}
)
print(result["response"])
```

### Q: "What's my sustainable APY?"

```python
engine = get_engine()
response = engine.chat(
    merchant_id="my_merchant",
    user_message="I have $10M TVL and generate $50k daily revenue. What APY can I sustain?"
)
# Returns: APY = (50k / 10M) × 365 = 18.25%
```

### Q: "How do I monetize my protocol?"

```python
agent = AgentFactory.create_agent("monetization")
result = agent.execute("Design 3 revenue streams for my DEX")
print(result["response"])
```

## API Endpoints Overview

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/optik-gpt/chat` | Main conversation endpoint |
| POST | `/api/optik-gpt/agent/execute` | Execute specialized agent |
| GET | `/api/optik-gpt/agents` | List available agents |
| GET | `/api/optik-gpt/session/{merchant_id}/summary` | Get conversation summary |
| POST | `/api/optik-gpt/verify` | Verify a claim |
| GET | `/api/optik-gpt/knowledge` | Export knowledge base |
| GET | `/api/optik-gpt/revenue/opportunities` | Get revenue opportunities |
| GET | `/api/optik-gpt/health` | Health check |

## Running Examples

```bash
cd /home/kali/Dapp_Optik/optik-platform/backend
python -m optik_gpt.examples
```

This runs all example scenarios:
1. Basic chat
2. Multi-turn conversation
3. Specialized agents
4. Knowledge base access
5. Revenue tracking
6. Complete workflow

## Tips & Best Practices

### 1. Provide Context
Always include merchant metadata for better responses:
```python
engine.chat(
    merchant_id="my_merchant",
    user_message="Help me launch!",
    update_metadata={
        "dapp_type": "DEX",
        "stage": "Ready for launch",
        "team_size": "10+ people",
        "challenges": "User acquisition"
    }
)
```

### 2. Use Specialized Agents
Let the right expert handle the task:
```python
# Instead of asking in general chat:
# "Write me a smart contract"

# Use the expert:
agent = factory.create_agent("contract")
agent.execute("Write ERC-20 token with minting controls")
```

### 3. Follow Up Naturally
Maintain conversations for deeper insights:
```python
# First: High-level design
engine.chat(merchant_id, "Design my token distribution")

# Then: Specific follow-up
engine.chat(merchant_id, "What about vesting schedules?")

# Then: Implementation
engine.chat(merchant_id, "How do I implement this in code?")
```

### 4. Verify Critical Claims
For important decisions, verify claims:
```python
kb = get_knowledge_base()
verified, explanation = kb.verify_claim("ERC-20 is the token standard")
# verified: True
# explanation: "ERC-20 is the standard interface for fungible tokens..."
```

### 5. Track Revenue Opportunities
Monitor monetization potential:
```python
tracker = get_revenue_tracker()
profile = tracker.get_merchant_revenue_profile("my_merchant")
print(f"Identified opportunities: {profile['identified_opportunities']}")
print(f"Revenue streams: {profile['primary_revenue_streams']}")
```

## Troubleshooting

### Error: "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY="sk-ant-YOUR_KEY"
# Or add to .env file in backend directory
```

### Error: "Connection refused"
Make sure the API server is running:
```bash
uvicorn optik_gpt.main:app --reload --port 8000
```

### Error: "Module not found"
Install dependencies:
```bash
pip install -r requirements.txt
```

### Slow responses
Claude responses take 2-5 seconds. This is normal. For API, use async calls for multiple concurrent requests.

## Next Steps

1. **Read the full documentation:** `OPTIK_GPT.md`
2. **Explore the examples:** `python -m optik_gpt.examples`
3. **Integrate into your app:** Use REST API or Python SDK
4. **Build your DApp:** Use Optik GPT to guide every decision

---

**Questions?** Check `OPTIK_GPT.md` for detailed documentation.

**Ready to build?** 🚀 Let Optik GPT guide you to success!
