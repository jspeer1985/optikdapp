from typing import Dict, Any, List, Optional
import os
import logging

try:
    from anthropic import Anthropic
except Exception:
    Anthropic = None

# Import the intent router
try:
    from .intent_router import route_intent
except ImportError:
    # Handle relative import when running as standalone script for testing
    from intent_router import route_intent

logger = logging.getLogger(__name__)

class OptikAssistant:
    def __init__(self):
        self.sessions = {}
        self.provider = os.getenv("OPTIK_ASSISTANT_PROVIDER", "anthropic")
        self.model_fast = os.getenv("OPTIK_ASSISTANT_MODEL_FAST", "claude-3-haiku-20240307")
        self.model_accurate = os.getenv("OPTIK_ASSISTANT_MODEL_ACCURATE", "claude-3-sonnet-20240229")
        self.mode = os.getenv("OPTIK_ASSISTANT_MODE", "balanced")
        self.client = None
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if self.provider == "anthropic" and api_key and Anthropic:
            self.client = Anthropic(api_key=api_key)

    def _select_model(self, preference: Optional[str]) -> str:
        pref = (preference or self.mode or "balanced").lower()
        if pref == "fast":
            return self.model_fast
        if pref == "accurate":
            return self.model_accurate
        return self.model_accurate

    async def handle_message(self, merchant_id: str, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        session = self.sessions.get(merchant_id, {"history": []})
        session["history"].append({"role": "user", "content": message})

        if self.client:
            model = self._select_model((context or {}).get("model_preference"))
            system_prompt = (
                "You are Optik GPT, an enterprise commerce copilot for DApp creation. "
                "Be concise, accurate, and execution-focused. Provide verified next actions."
            )
            if context:
                profile = context.get("prompt_profile")
                if profile:
                    system_prompt += f" Prompt profile: {profile}."
                assistant_mode = context.get("assistant_mode")
                if assistant_mode:
                    system_prompt += f" Mode: {assistant_mode}."
            try:
                response = self.client.messages.create(
                    model=model,
                    max_tokens=300,
                    temperature=0.2,
                    system=system_prompt,
                    messages=[{"role": "user", "content": message}],
                )
                content = response.content[0].text if response.content else "I could not generate a response."
                session["history"].append({"role": "assistant", "content": content})
                self.sessions[merchant_id] = session
                return {"status": "success", "message": content, "actions": []}
            except Exception as exc:
                logger.error(f"Optik GPT error: {exc}")

        intent = route_intent(message)
        response = self._route_intent(intent)
        session["history"].append({"role": "assistant", "content": response["message"]})
        self.sessions[merchant_id] = session
        return response

    def _route_intent(self, intent: str) -> Dict[str, Any]:
        if intent == "CREATE_PRODUCT":
            return {
                "status": "success",
                "message": "Open Products to add a new item. I can guide pricing and metadata if needed.",
                "actions": ["open:/dashboard/products", "open:/dashboard/nft-creator"]
            }
        if intent == "DEPLOY_STORE":
            return {
                "status": "success",
                "message": "Start deployment from the Create Dapp flow once conversion is complete.",
                "actions": ["open:/create-dapp", "open:/orchestrator"]
            }
        if intent == "CHECK_SALES":
            return {
                "status": "success",
                "message": "Review sales performance in Analytics or Billing history.",
                "actions": ["open:/dashboard/analytics", "open:/dashboard/billing/history"]
            }
        if intent == "WITHDRAW_FUNDS":
            return {
                "status": "success",
                "message": "Manage Stripe payouts from Billing once your Stripe Connect account is active.",
                "actions": ["open:/dashboard/billing", "open:/dashboard/merchant"]
            }
        if intent == "SETUP_STAKING":
            return {
                "status": "success",
                "message": "Configure staking in Marketing or Optik coin settings.",
                "actions": ["open:/dashboard/marketing", "open:/optik-coin"]
            }
        if intent == "GENERAL_HELP":
            return {
                "status": "success",
                "message": "I can help with conversion, deployment, analytics, or NFT setup. Tell me what you want to do next.",
                "actions": ["open:/create-dapp", "open:/dashboard/analytics"]
            }
        return {
            "status": "success",
            "message": "I need more detail to help. Tell me the task or the page you want to work on.",
            "actions": []
        }
