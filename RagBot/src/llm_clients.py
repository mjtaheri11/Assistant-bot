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
    max_tokens: int = 4096

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
            # The Responses API usually handles params differently.
            # Based on your snippet, it takes 'input', 'tools', etc.
            # We assume it might accept max_completion_tokens if it's a reasoning model,
            # but we must be careful not to send 'messages' as a param (it uses 'input').
            
            # If it supports reasoning/effort, we add them:
            if self.supports_reasoning:
                # Use max_completion_tokens? (Assumption based on model type)
                # If the API rejects this, we might need to remove it, but 
                # generally newer endpoints prefer max_completion_tokens.
                # However, strictly adhering to your snippet, we focus on model/input.
                pass 
            
            # Pass extra params (tools, etc.)
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
                max_output_tokens=merged.get("max_output_tokens", 4096),
                api_type=merged.get("api_type", "chat"), # Defaults to chat
                supports_reasoning=merged.get("supports_reasoning", False),
                default_reasoning_effort=merged.get("default_reasoning_effort"),
                temperature=merged.get("temperature", 0.7),
                max_tokens=merged.get("max_tokens", 4096),
            )

    def get_model(self, model_name: str) -> tuple[AsyncOpenAI, ModelConfig]:
        if model_name not in self._models:
            raise ValueError(f"Model '{model_name}' not found.")
        config = self._models[model_name]
        return self._clients[config.provider], config

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
        Execute completion with strict API routing:
        1. Chat -> client.chat.completions.create
        2. Responses -> client.responses.create
        3. Legacy -> client.completions.create
        """
        client, config = self.get_model(model_name)
        
        params = config.get_params(
            reasoning_effort=reasoning_effort,
            temperature=temperature,
            max_tokens=max_tokens,
            **extra,
        )
        
        # --- ROUTING LOGIC ---
        
        if config.api_type == "responses":
            # The Responses API takes 'input' instead of 'messages'
            # The structure of 'messages' ([{"role": "user", ...}]) is compatible 
            # with 'ResponseInputParam' for text messages.
            return await client.responses.create(
                input=messages, 
                **params
            )
            
        elif config.api_type == "completions":
            prompt = messages_to_prompt(messages)
            params.pop("messages", None) 
            return await client.completions.create(prompt=prompt, **params)
            
        else:
            # Default: Chat API
            return await client.chat.completions.create(messages=messages, **params)

    def extract_text(self, response: Any, model_name: str) -> str:
        """
        Extract text from response, handling both Objects and String Representations.
        """
        import re
        
        # Convert to string to handle the case where response is a list/object 
        # but behaves like the string repr you are seeing.
        s_response = str(response)

        # --- STRATEGY 1: Parse the String Representation (Specific to your error) ---
        # Target format: text=\'{"SQL": ...}\', type=
        # We look for: text=  --> optional backslash --> quote --> (CONTENT) --> optional backslash --> quote --> , type=
        match = re.search(r"text=\\?['\"](.*?)\\?['\"], type=", s_response, re.DOTALL)
        
        if match:
            extracted_text = match.group(1)
            # The content inside repr() is often escaped (e.g., \" instead of "). 
            # We must unescape it to get valid JSON.
            # 1. Unescape literal backslash-quote sequences
            clean_text = extracted_text.replace(r"\'", "'").replace(r'\"', '"')
            # 2. Unescape double backslashes
            clean_text = clean_text.replace(r"\\", "\\")
            return clean_text

        # --- STRATEGY 2: Standard Object Access (If strictly an object) ---
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
        # If all else fails, look for the first JSON-like block starting with "SQL"
        # This is specific to your use case (generating SQL)
        json_match = re.search(r'(\{.*"SQL":.*\})', s_response, re.DOTALL)
        if json_match:
            return json_match.group(1)

        return ""

llm_manager = LLMClientManager()