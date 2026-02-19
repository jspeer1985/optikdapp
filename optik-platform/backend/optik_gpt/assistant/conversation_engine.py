from typing import Dict, Any, List, Optional
import os
import logging
import ast

try:
    from anthropic import Anthropic
except Exception:
    Anthropic = None

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

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
        self.provider = os.getenv("OPTIK_ASSISTANT_PROVIDER", "auto").lower()
        self.model_fast = os.getenv("OPTIK_ASSISTANT_MODEL_FAST", "claude-3-haiku-20240307")
        self.model_accurate = os.getenv("OPTIK_ASSISTANT_MODEL_ACCURATE", "claude-3-sonnet-20240229")
        self.openai_model_fast = os.getenv("OPTIK_ASSISTANT_OPENAI_MODEL_FAST", "gpt-4o-mini")
        self.openai_model_accurate = os.getenv("OPTIK_ASSISTANT_OPENAI_MODEL_ACCURATE", "gpt-4o")
        self.mode = os.getenv("OPTIK_ASSISTANT_MODE", "balanced")
        self.anthropic_client = None
        self.openai_client = None

        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if anthropic_key and Anthropic:
            self.anthropic_client = Anthropic(api_key=anthropic_key)

        if openai_key and OpenAI:
            self.openai_client = OpenAI(api_key=openai_key)

    def _provider_order(self) -> List[str]:
        available: List[str] = []
        if self.anthropic_client:
            available.append("anthropic")
        if self.openai_client:
            available.append("openai")

        if not available:
            return []

        configured = self.provider
        if configured in available:
            return [configured] + [provider for provider in available if provider != configured]

        if configured == "auto":
            return available

        # If a specific provider was configured but unavailable, transparently fail over.
        return available

    def _select_model(self, preference: Optional[str], provider: str) -> str:
        pref = (preference or self.mode or "balanced").lower()
        use_fast = pref == "fast"

        if provider == "openai":
            return self.openai_model_fast if use_fast else self.openai_model_accurate

        return self.model_fast if use_fast else self.model_accurate

    def _build_system_prompt(self, context: Optional[Dict[str, Any]]) -> str:
        system_prompt = (
            "You are Optik GPT, a practical AI assistant that can answer questions on any topic. "
            "When a question is about commerce, product, or DApp execution, provide concrete steps. "
            "Be clear, direct, and avoid hallucinations. If uncertain, say what is uncertain."
        )

        if context:
            profile = context.get("prompt_profile")
            if profile:
                system_prompt += f" Prompt profile: {profile}."
            assistant_mode = context.get("assistant_mode")
            if assistant_mode:
                system_prompt += f" Mode: {assistant_mode}."
            page_context = context.get("page_context")
            if page_context:
                system_prompt += f" Page context: {page_context}."

        return system_prompt

    def _build_messages(self, session: Dict[str, Any], message: str) -> List[Dict[str, str]]:
        history = session.get("history", [])[-8:]
        messages: List[Dict[str, str]] = []

        for turn in history:
            role = turn.get("role")
            content = turn.get("content")
            if role in {"user", "assistant"} and isinstance(content, str):
                messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": message})
        return messages

    def _generate_with_anthropic(self, model: str, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized")

        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=500,
            temperature=0.2,
            system=system_prompt,
            messages=messages,
        )

        parts = []
        for block in response.content or []:
            text = getattr(block, "text", "")
            if text:
                parts.append(text)
        return "".join(parts).strip()

    def _generate_with_openai(self, model: str, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")

        response = self.openai_client.chat.completions.create(
            model=model,
            max_tokens=500,
            temperature=0.2,
            messages=[{"role": "system", "content": system_prompt}, *messages],
        )

        content = response.choices[0].message.content if response.choices else None
        return (content or "").strip()

    def _try_llm_response(
        self,
        session: Dict[str, Any],
        message: str,
        context: Optional[Dict[str, Any]],
    ) -> Optional[str]:
        providers = self._provider_order()
        if not providers:
            return None

        system_prompt = self._build_system_prompt(context)
        messages = self._build_messages(session, message)
        preference = (context or {}).get("model_preference")

        for provider in providers:
            model = self._select_model(preference, provider)
            try:
                if provider == "anthropic":
                    content = self._generate_with_anthropic(model, system_prompt, messages)
                else:
                    content = self._generate_with_openai(model, system_prompt, messages)

                if content:
                    return content
            except Exception as exc:
                logger.error(f"Optik GPT {provider} error: {exc}")

        return None

    def _safe_eval_expression(self, expression: str) -> Optional[float]:
        try:
            parsed = ast.parse(expression, mode="eval")
        except Exception:
            return None

        allowed_nodes = (
            ast.Expression,
            ast.BinOp,
            ast.UnaryOp,
            ast.Constant,
            ast.Add,
            ast.Sub,
            ast.Mult,
            ast.Div,
            ast.Pow,
            ast.Mod,
            ast.FloorDiv,
            ast.USub,
            ast.UAdd,
        )

        for node in ast.walk(parsed):
            if not isinstance(node, allowed_nodes):
                return None
            if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float)):
                return None

        try:
            result = eval(compile(parsed, "<optik_math>", "eval"), {"__builtins__": {}}, {})
        except Exception:
            return None

        if not isinstance(result, (int, float)):
            return None

        return float(result)

    def _offline_general_response(self, message: str) -> Dict[str, Any]:
        text = " ".join(message.strip().split())
        if not text:
            return {
                "status": "success",
                "message": "Ask me any question and include context or constraints for a better answer.",
                "actions": [],
            }

        normalized = text.lower()
        expression = text
        for prefix in ("what is ", "calculate ", "solve "):
            if normalized.startswith(prefix):
                expression = text[len(prefix):]
                break
        expression = expression.rstrip("?").strip()

        calculated = self._safe_eval_expression(expression)
        if calculated is not None:
            rendered = int(calculated) if calculated.is_integer() else round(calculated, 8)
            return {
                "status": "success",
                "message": f"The answer is {rendered}.",
                "actions": [],
            }

        return {
            "status": "success",
            "message": (
                "I can help with that. The live AI provider is unavailable right now, "
                "so my response depth is limited. Ask with specific context, desired output, "
                "and constraints, and I will give a structured step-by-step answer."
            ),
            "actions": [],
        }

    async def handle_message(self, merchant_id: str, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        session = self.sessions.get(merchant_id, {"history": []})
        content = self._try_llm_response(session, message, context)

        session["history"].append({"role": "user", "content": message})
        if content:
            session["history"].append({"role": "assistant", "content": content})
            self.sessions[merchant_id] = session
            return {"status": "success", "message": content, "actions": []}

        intent = route_intent(message)
        response = self._route_intent(intent) if intent != "UNKNOWN_INTENT" else self._offline_general_response(message)
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
