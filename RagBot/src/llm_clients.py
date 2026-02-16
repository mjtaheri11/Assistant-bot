from __future__ import annotations

import os
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml
from openai import AsyncOpenAI

from src.config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ReasoningEffort = Literal["none", "minimal", "low", "medium", "high", "xhigh"]
# Added "responses" to supported API types
ApiType = Literal["chat", "completions", "responses"]

FALLBACK_MODEL = "oss"


@dataclass
class ModelConfig:
    """Configuration for a specific LLM model."""
    
    name: str
    provider: str
    model_id: str
    context_window: int
    max_output_tokens: int
    api_type: ApiType = "chat"
    supports_reasoning: bool = False
    default_reasoning_effort: ReasoningEffort | None = None
    temperature: float = 0.7
    max_tokens: int = 16000

    def get_params(
        self,
        *,
        reasoning_effort: ReasoningEffort | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **extra: Any,
    ) -> dict[str, Any]:
        """
        Build API parameters.
        For 'responses' API, we filter out incompatible legacy/chat params if needed.
        """
        params: dict[str, Any] = {
            "model": self.model_id,
        }
        
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        # --- LOGIC FOR RESPONSES API ---
        if self.api_type == "responses":
            if self.supports_reasoning:
                pass 
            
            params.update(extra)
            return params

        # --- LOGIC FOR CHAT / LEGACY ---
        if self.supports_reasoning:
            params["max_completion_tokens"] = tokens
            effort = reasoning_effort or self.default_reasoning_effort
            if effort:
                params["reasoning_effort"] = effort
            extra.pop("max_tokens", None)
            extra.pop("temperature", None)
        else:
            params["max_tokens"] = tokens
            params["temperature"] = temperature if temperature is not None else self.temperature
        
        params.update(extra)
        return params


def messages_to_prompt(messages: list[dict[str, str]]) -> str:
    """Convert chat messages to a single prompt string for legacy completions API."""
    parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        parts.append(f"{role.capitalize()}: {content}")
    parts.append("Assistant:")
    return "\n\n".join(parts)


class LLMClientManager:
    """Manages LLM clients and model configurations."""
    
    def __init__(self):
        self._clients: dict[str, AsyncOpenAI] = {}
        self._models: dict[str, ModelConfig] = {}
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return
        
        self._clients["gpt"] = AsyncOpenAI(
            base_url=os.getenv("GPT_API_BASE"),
            api_key=os.getenv("GPT_API_KEY")
        )
        self._clients["oss"] = AsyncOpenAI(
            base_url=os.getenv("OSS_API_BASE"),
            api_key=os.getenv("OSS_API_KEY")
        )
        self._clients["openrouter"] = AsyncOpenAI(
            base_url=os.getenv("OPENROUTER_API_BASE"),
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        
        self._load_models()
        self._initialized = True
        print("LLM clients initialized.")

    def _load_models(self) -> None:
        defaults = config.get("api_defaults", {})
        
        for name, model_cfg in config.get("api_models", {}).items():
            merged = {**defaults, **model_cfg}
            self._models[name] = ModelConfig(
                name=name,
                provider=merged["provider"],
                model_id=merged["model_id"],
                context_window=merged.get("context_window", 128000),
                max_output_tokens=merged.get("max_output_tokens", 16000),
                api_type=merged.get("api_type", "chat"),
                supports_reasoning=merged.get("supports_reasoning", False),
                default_reasoning_effort=merged.get("default_reasoning_effort"),
                temperature=merged.get("temperature", 0.7),
                max_tokens=merged.get("max_tokens", 16000),
            )

    def get_model(self, model_name: str) -> tuple[AsyncOpenAI, ModelConfig]:
        if model_name not in self._models:
            raise ValueError(f"Model '{model_name}' not found.")
        config = self._models[model_name]
        return self._clients[config.provider], config

    async def _execute_call(
        self,
        client: AsyncOpenAI,
        config: ModelConfig,
        messages: list[dict[str, str]],
        params: dict[str, Any],
    ) -> Any:
        """Execute a single API call based on config.api_type."""
        if config.api_type == "responses":
            return await client.responses.create(
                input=messages,
                **params
            )
        elif config.api_type == "completions":
            prompt = messages_to_prompt(messages)
            params.pop("messages", None)
            return await client.completions.create(prompt=prompt, **params)
        else:
            return await client.chat.completions.create(messages=messages, **params)

    async def complete(
        self,
        model_name: str,
        messages: list[dict[str, str]],
        *,
        reasoning_effort: ReasoningEffort | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **extra: Any,
    ) -> Any:
        """
        Execute completion with strict API routing and fallback to OSS on failure.
        1. Chat -> client.chat.completions.create
        2. Responses -> client.responses.create
        3. Legacy -> client.completions.create

        On failure, if the model is not already the fallback, retry once with the
        fallback (OSS) model and log the event.
        """
        client, model_config = self.get_model(model_name)

        params = model_config.get_params(
            reasoning_effort=reasoning_effort,
            temperature=temperature,
            max_tokens=max_tokens,
            **extra,
        )

        try:
            return await self._execute_call(client, model_config, messages, params)
        except Exception as exc:
            if model_name == FALLBACK_MODEL:
                # Already on the fallback model — nothing left to try
                logger.error(
                    "Fallback model '%s' itself failed: %s", FALLBACK_MODEL, exc
                )
                raise

            logger.warning(
                "Model '%s' failed (%s: %s). Retrying with fallback model '%s'...",
                model_name,
                type(exc).__name__,
                exc,
                FALLBACK_MODEL,
            )

            # Build params for the fallback model
            fallback_client, fallback_config = self.get_model(FALLBACK_MODEL)
            fallback_params = fallback_config.get_params(
                reasoning_effort=reasoning_effort,
                temperature=temperature,
                max_tokens=max_tokens,
                **extra,
            )

            try:
                return await self._execute_call(
                    fallback_client, fallback_config, messages, fallback_params
                )
            except Exception as fallback_exc:
                logger.error(
                    "Fallback model '%s' also failed: %s", FALLBACK_MODEL, fallback_exc
                )
                raise

    def extract_text(self, response: Any, model_name: str) -> str:
        """
        Extract text from response, handling both Objects and String Representations.
        """
        import re
        
        s_response = str(response)

        # --- STRATEGY 1: Parse the String Representation ---
        match = re.search(r"text=\\?['\"](.*?)\\?['\"], type=", s_response, re.DOTALL)
        
        if match:
            extracted_text = match.group(1)
            clean_text = extracted_text.replace(r"\'", "'").replace(r'\"', '"')
            clean_text = clean_text.replace(r"\\", "\\")
            return clean_text

        # --- STRATEGY 2: Standard Object Access ---
        # Responses API (v1/responses)
        if hasattr(response, "output") and isinstance(response.output, list):
            text_parts = []
            for item in response.output:
                if hasattr(item, "text") and item.text:
                    text_parts.append(item.text)
                elif hasattr(item, "content") and item.content:
                    text_parts.append(str(item.content))
            if text_parts:
                return "".join(text_parts)

        # Legacy / Chat Fallbacks
        if hasattr(response, "choices"):
            if hasattr(response.choices[0], "text") and response.choices[0].text:
                return response.choices[0].text.strip()
            if hasattr(response.choices[0], "message"):
                return response.choices[0].message.content or ""
            
        # --- STRATEGY 3: Last Resort JSON Extraction ---
        json_match = re.search(r'(\{.*"SQL":.*\})', s_response, re.DOTALL)
        if json_match:
            return json_match.group(1)

        return ""

llm_manager = LLMClientManager()