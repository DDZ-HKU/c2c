from __future__ import annotations

import os
from typing import Any

from litellm.integrations.custom_logger import CustomLogger
from litellm.proxy.proxy_server import DualCache, UserAPIKeyAuth
from litellm.types.utils import CallTypesLiteral

TARGET_MODEL = os.getenv("TARGET_MODEL", "gpt-5.4")
ANTHROPIC_MODEL_ALIASES = {
    "sonnet",
    "opus",
    "haiku",
    "claude",
    "claude-3",
    "claude-3.5",
    "claude-3.7",
    "claude-4",
    "claude-4.1",
    "claude-sonnet",
    "claude-opus",
    "claude-haiku",
}


def _is_anthropic_target(model_name: str) -> bool:
    lowered = model_name.lower()
    return lowered.startswith("claude") or lowered.startswith("anthropic/")


def _should_remap_to_target(model_name: str) -> bool:
    lowered = model_name.lower().strip()
    if lowered in ANTHROPIC_MODEL_ALIASES:
        return True
    if lowered.startswith("claude") or lowered.startswith("anthropic/"):
        return True
    if lowered.startswith("sonnet") or lowered.startswith("opus") or lowered.startswith("haiku"):
        return True
    return False


class AnthropicCompatLogger(CustomLogger):
    async def async_pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        cache: DualCache,
        data: dict[str, Any],
        call_type: CallTypesLiteral,
    ) -> dict[str, Any]:
        model_name = str(data.get("model") or "")
        if _should_remap_to_target(model_name):
            data["model"] = TARGET_MODEL
            model_name = TARGET_MODEL

        if not model_name or _is_anthropic_target(model_name):
            return data

        data.pop("context_management", None)

        thinking = data.pop("thinking", None)
        if isinstance(thinking, dict):
            budget_tokens = thinking.get("budget_tokens")
            if isinstance(budget_tokens, int) and budget_tokens > 0:
                metadata = data.setdefault("metadata", {})
                if isinstance(metadata, dict):
                    metadata["anthropic_thinking_budget_tokens"] = budget_tokens

        return data

    async def async_post_call_success_hook(
        self,
        data: dict[str, Any],
        user_api_key_dict: UserAPIKeyAuth,
        response: Any,
    ) -> None:
        if hasattr(response, "model"):
            response.model = TARGET_MODEL
        elif isinstance(response, dict):
            response["model"] = TARGET_MODEL


proxy_handler_instance = AnthropicCompatLogger()
