from __future__ import annotations

import json
import re
import os
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml
from openai import AsyncOpenAI

from src.config import config

import tiktoken

# Mirror logic.py's encoder + safety buffer so budgets stay consistent.
_FALLBACK_ENCODING = tiktoken.encoding_for_model("gpt-4o-mini")
_PROMPT_SAFETY_BUFFER = 2000

import httpx
import dns.asyncresolver

_GOOGLE_DNS = ["8.8.8.8", "1.1.1.1"]
ABRAMAD_DEFAULT_BASE = os.getenv("ABRAMAD_DEFAULT_BASE", "https://api.ml.abramad.com/v1")


class GoogleDNSTransport(httpx.AsyncHTTPTransport):
    """httpx transport that resolves hostnames with Google's public DNS
    instead of the system resolver, then connects to the resolved IP."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._resolver = dns.asyncresolver.Resolver(configure=False)
        self._resolver.nameservers = _GOOGLE_DNS
        self._cache: dict[str, str] = {}

    async def _resolve(self, host: str) -> str:
        # Leave IPv4 literals untouched.
        if host.replace(".", "").isdigit():
            return host
        if host not in self._cache:
            answer = await self._resolver.resolve(host, "A")
            self._cache[host] = answer[0].address
        return self._cache[host]

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        original_host = request.url.host
        ip = await self._resolve(original_host)

        # Dial the IP, but keep the real hostname for TLS SNI + cert validation
        # and for the Host header (vhost routing on OpenRouter's side).
        request.url = request.url.copy_with(host=ip)
        request.headers["Host"] = original_host
        request.extensions["sni_hostname"] = original_host

        return await super().handle_async_request(request)

async def _strip_authorization_header(request: httpx.Request) -> None:
    """Abramad authenticates via `x-api-key`, not `Authorization`. The OpenAI
    SDK always adds `Authorization: Bearer …`, so we drop it to mirror the curl."""
    request.headers.pop("Authorization", None)

def _count_tokens(text: str) -> int:
    return len(_FALLBACK_ENCODING.encode(text or ""))

OutputFormat = Literal["json", "text", "auto"]

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ReasoningEffort = Literal["none", "minimal", "low", "medium", "high", "xhigh"]
# Added "responses" to supported API types
ApiType = Literal["chat", "completions", "responses"]

FALLBACK_MODEL = "qwen36-35b"
VLLM_CLUSTER_BASE_TEMPLATE = "http://{host}.admin.svc.cluster.local/v1"
_FALLBACK_ENCODING = tiktoken.encoding_for_model("gpt-4o-mini")
_PROMPT_SAFETY_BUFFER = 2000  # keep in sync with the prompt budgeter in the main module



@dataclass
class ModelConfig:
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
    reasoning_param_style: str = "openai"
    supports_response_format: bool = True
    # --- NEW: needed to build per-model vLLM clients on demand ---
    base_url: str | None = None
    api_key: str = "EMPTY"
    timeout: float | None = None
    max_retries: int = 0
    # --- NEW: how to render the prompt for api_type == "completions" ---
    prompt_format: str = "generic"   # "generic" | "qwen3"

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
        if not self.supports_response_format:
            extra.pop("response_format", None)
            extra.pop("text", None)
        
        
        # --- LOGIC FOR RESPONSES API ---

        # --- LOGIC FOR RESPONSES API ---
        if self.api_type == "responses":
            # Responses API doesn't accept Chat-style response_format
            extra.pop("response_format", None)
            params.update(extra)
            return params

        # Chat / legacy path — strip Responses-API-only kwargs that may have
        # leaked through from a caller that didn't know which surface it was hitting.
        extra.pop("text", None)

        # --- LOGIC FOR CHAT / LEGACY ---
        if self.supports_reasoning:
            if self.reasoning_param_style == "openrouter":
                params["max_tokens"] = tokens
                params["temperature"] = temperature if temperature is not None else self.temperature
                effort = reasoning_effort or self.default_reasoning_effort
                existing_extra_body = extra.pop("extra_body", {}) or {}
                reasoning_cfg = {"enabled": True}
                if effort and effort != "none":
                    reasoning_cfg["effort"] = effort
                existing_extra_body["reasoning"] = reasoning_cfg
                params["extra_body"] = existing_extra_body
            elif self.reasoning_param_style == "vllm_thinking":
                # vLLM chat-template toggle (Gemma/Qwen-style): thinking is
                # switched on via chat_template_kwargs, NOT a top-level field.
                params["max_tokens"] = tokens
                params["temperature"] = temperature if temperature is not None else self.temperature
                effort = reasoning_effort or self.default_reasoning_effort
                enable = bool(effort) and effort != "none"
                existing_extra_body = extra.pop("extra_body", {}) or {}
                ctk = existing_extra_body.get("chat_template_kwargs", {}) or {}
                ctk["enable_thinking"] = enable
                existing_extra_body["chat_template_kwargs"] = ctk
                params["extra_body"] = existing_extra_body
            else:
                # OpenAI-native style (unchanged)
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

_IM_START = "<|im_start|>"
_IM_END = "<|im_end|>"
_VALID_ROLES = ("system", "user", "assistant", "tool")


def qwen3_messages_to_prompt(
    messages: list[dict[str, str]],
    *,
    thinking: str = "optional",     # "optional" | "always" | "never"
    enable_thinking: bool = True,   # used when thinking == "optional"
) -> str:
    """Render Qwen3 ChatML for /v1/completions (vLLM doesn't run the chat
    template here, so we emit ChatML ourselves).

    Verified behavior of this checkpoint:
      * bare assistant cue           -> empty <think></think>, no reasoning
      * cue + prefilled '<think>\\n'  -> model reasons, then closes </think>
    So we prefill '<think>' to engage reasoning; a closed empty block is the
    deterministic non-thinking path.
    """
    parts: list[str] = []
    for msg in messages:
        role = msg.get("role", "user")
        if role not in _VALID_ROLES:
            role = "user"
        content = msg.get("content", "") or ""
        parts.append(f"{_IM_START}{role}\n{content}{_IM_END}\n")

    parts.append(f"{_IM_START}assistant\n")

    want_think = thinking == "always" or (thinking == "optional" and enable_thinking)
    if want_think:
        parts.append("<think>\n")               # force the reasoning channel
    else:
        parts.append("<think>\n\n</think>\n\n")  # deterministic non-thinking
    return "".join(parts)
    

def render_completion_prompt(
    messages: list[dict[str, str]],
    cfg: "ModelConfig",
    *,
    enable_thinking: bool = True,
) -> str:
    """Pick the raw-prompt renderer for an api_type == 'completions' model."""
    if getattr(cfg, "prompt_format", "generic") == "qwen3":
        return qwen3_messages_to_prompt(
            messages,
            thinking=getattr(cfg, "qwen_thinking", "optional"),
            enable_thinking=enable_thinking,
        )
    return messages_to_prompt(messages)

class LLMClientManager:
    """Manages LLM clients and model configurations."""
    _REASONING_TAGS = ("think", "thinking", "reasoning", "analysis")
    def __init__(self):
        self._clients: dict[str, AsyncOpenAI] = {}
        self._models: dict[str, ModelConfig] = {}
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return

        # Single-endpoint providers: one client serves many model_ids.
        self._clients["gpt"] = AsyncOpenAI(
            base_url=os.getenv("GPT_API_BASE"),
            api_key=os.getenv("GPT_API_KEY"),
        )
        self._clients["openrouter"] = AsyncOpenAI(
            base_url=os.getenv("OPENROUTER_API_BASE"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            http_client=httpx.AsyncClient(transport=GoogleDNSTransport()),
        )
        self._clients["hooshyar"] = AsyncOpenAI(
            base_url=os.getenv("HOOSHYAR_API_BASE"),
            api_key=os.getenv("HOOSHYAR_API_KEY"),
            timeout=config["api_models"]["deepseek-v4-flash"]["timeout"],
            max_retries=0,
        )
        # Locally-served (vLLM) models no longer get a hand-written client here.
        # Their clients are built lazily from each model's own base_url and
        # cached by URL, so adding a new local model is config-only.

        self._load_models()
        self._initialized = True
        print("LLM clients initialized.")

    def _resolve_base_url(self, merged: dict) -> str | None:
        # 1. explicit full URL wins
        if merged.get("base_url"):
            return merged["base_url"]
        # 2. back-compat: dedicated env var (e.g. OSS_API_BASE) if present
        env_key = merged.get("base_url_env")
        if env_key and os.getenv(env_key):
            return os.getenv(env_key)
        # 2.5 abramad: single shared endpoint, overridable via ABRAMAD_API_BASE
        if merged.get("provider") == "abramad":
            return os.getenv("ABRAMAD_API_BASE", ABRAMAD_DEFAULT_BASE)
        # 3. construct from the shared cluster template + per-model host
        host = merged.get("cluster_host")
        if host:
            template = config.get("api_default", {}).get(
                "vllm_base_url_template", VLLM_CLUSTER_BASE_TEMPLATE
            )
            return template.format(host=host)
        return None

    @staticmethod
    def _resolve_api_key(merged: dict) -> str:
        key_env = merged.get("api_key_env")
        if key_env and os.getenv(key_env):
            return os.getenv(key_env)
        # abramad: default to the customer key unless a model overrides api_key_env
        if merged.get("provider") == "abramad":
            return os.getenv("ABRAMAD_DEV_API_KEY", merged.get("api_key", "EMPTY"))
        return merged.get("api_key", "EMPTY")
    
    @staticmethod
    def _take_thinking_flag(params: dict[str, Any], *, default: bool = True) -> bool:
        """Completions path only: pull `enable_thinking` out of the chat-only
        extra_body.chat_template_kwargs (set by reasoning_param_style ==
        'vllm_thinking') and remove it, since /v1/completions never runs the
        chat template and would ignore — or reject — those kwargs."""
        enable = default
        extra_body = params.get("extra_body")
        if isinstance(extra_body, dict):
            ctk = extra_body.pop("chat_template_kwargs", None)
            if isinstance(ctk, dict) and "enable_thinking" in ctk:
                enable = bool(ctk["enable_thinking"])
            if not extra_body:
                params.pop("extra_body", None)
        return enable

    def _load_models(self) -> None:
        defaults = config.get("api_default", {})
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
                reasoning_param_style=merged.get("reasoning_param_style", "openai"),
                supports_response_format=merged.get("supports_response_format", True),
                # NEW
                base_url=self._resolve_base_url(merged),
                api_key=self._resolve_api_key(merged),
                timeout=merged.get("timeout"),
                max_retries=merged.get("max_retries", 0),
                prompt_format=merged.get("prompt_format", "generic"),
            )

    def _client_for_model(self, cfg: ModelConfig) -> AsyncOpenAI:
        # Abramad: OpenRouter-compatible proxy. Auth via `x-api-key` header
        # (not Authorization: Bearer) and two keys (customer / dev). One cached
        # client per (base_url, key).
        if cfg.provider == "abramad":
            api_key = cfg.api_key or os.getenv("ABRAMAD_CUSTOMER_API_KEY") or "EMPTY"
            base_url = cfg.base_url or ABRAMAD_DEFAULT_BASE
            cache_key = f"abramad::{base_url}::{api_key}"
            client = self._clients.get(cache_key)
            if client is None:
                http_client = httpx.AsyncClient(
                    event_hooks={"request": [_strip_authorization_header]},
                    timeout=cfg.timeout if cfg.timeout is not None else 30,
                )
                client = AsyncOpenAI(
                    base_url=base_url,
                    api_key="EMPTY",  # Authorization is stripped; auth is x-api-key
                    default_headers={"x-api-key": api_key},
                    http_client=http_client,
                    max_retries=cfg.max_retries,
                )
                self._clients[cache_key] = client
            return client

        # Pre-built single-endpoint providers (gpt / openrouter / hooshyar).
        if cfg.provider != "vllm":
            try:
                return self._clients[cfg.provider]
            except KeyError:
                raise ValueError(
                    f"No client for provider '{cfg.provider}' (model '{cfg.name}')."
                )
        # vLLM: one client per base_url, built on first use and cached.
        if not cfg.base_url:
            raise ValueError(
                f"vLLM model '{cfg.name}' has no base_url. Set 'base_url', "
                f"'cluster_host', or 'base_url_env' in its config."
            )
        client = self._clients.get(cfg.base_url)
        if client is None:
            client = AsyncOpenAI(
                base_url=cfg.base_url,
                api_key=cfg.api_key or "EMPTY",
                timeout=cfg.timeout if cfg.timeout is not None else 30,
                max_retries=cfg.max_retries,
            )
            self._clients[cfg.base_url] = client
        return client

    def get_model(self, model_name: str) -> tuple[AsyncOpenAI, ModelConfig]:
        if model_name not in self._models:
            raise ValueError(f"Model '{model_name}' not found.")
        cfg = self._models[model_name]
        return self._client_for_model(cfg), cfg

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
            # vLLM /v1/completions feeds raw text (no chat template), so we
            # render ChatML ourselves — this is what makes a system-only
            # prompt valid for Qwen3.
            enable_thinking = self._take_thinking_flag(params)
            prompt = render_completion_prompt(
                messages, config, enable_thinking=enable_thinking
            )
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

            fallback_client, fallback_config = self.get_model(FALLBACK_MODEL)
            fallback_extra = {k: v for k, v in extra.items()
                            if k not in {"response_format", "text"}}
            fallback_params = fallback_config.get_params(
                reasoning_effort=reasoning_effort, temperature=temperature,
                max_tokens=max_tokens, **fallback_extra,
            )

            # Prompt was budgeted for the large-context primary model; re-fit it
            # to the fallback window, keeping instructions (head) and the
            # highest-priority chunks + question (tail).
            fallback_messages = self._fit_messages_to_model(messages, fallback_config)
            fallback_params = self._clamp_output_tokens(
                fallback_params, fallback_config, fallback_messages
            )

            try:
                return await self._execute_call(
                    fallback_client, fallback_config, fallback_messages, fallback_params
                )
            except Exception as fallback_exc:
                logger.error(
                    "Fallback model '%s' also failed: %s", FALLBACK_MODEL, fallback_exc
                )
                raise                
    @staticmethod
    def _model_input_budget(cfg: ModelConfig) -> int:
        """context_window - max_output_tokens - safety_buffer (== logic.get_max_input_tokens)."""
        return max(256, cfg.context_window - cfg.max_output_tokens - _PROMPT_SAFETY_BUFFER)

    def _fit_messages_to_model(
        self,
        messages: list[dict[str, str]],
        cfg: ModelConfig,
        head_reserve: int = 1200,
    ) -> list[dict[str, str]]:
        """
        Shrink the prompt to fit `cfg`'s window. Only used on the fallback path;
        the primary model still gets the full prompt.

        The biggest message (the RAG system prompt) is trimmed with
        head+tail preservation:
          - head_reserve tokens from the TOP  -> task / output-format instructions
          - remaining budget from the BOTTOM  -> the most-relevant retrieved
            chunks + the user question, which the pipeline deliberately places
            at the END of the prompt (highest priority).
        """
        budget = self._model_input_budget(cfg)
        sizes = [_count_tokens(m.get("content", "") or "") for m in messages]
        if sum(sizes) <= budget:
            return messages

        big = max(range(len(messages)), key=lambda i: sizes[i])
        other = sum(s for i, s in enumerate(sizes) if i != big)
        allowance = max(256, budget - other)

        toks = _FALLBACK_ENCODING.encode(messages[big].get("content", "") or "")
        if len(toks) <= allowance:
            return messages

        hr = min(head_reserve, max(0, allowance // 3))
        marker = _FALLBACK_ENCODING.encode(
            "\n\n[... context truncated to fit fallback model ...]\n\n"
        )
        tail_reserve = max(1, allowance - hr - len(marker))

        new_content = _FALLBACK_ENCODING.decode(
            toks[:hr] + marker + toks[-tail_reserve:]
        )
        new_messages = list(messages)
        new_messages[big] = {**messages[big], "content": new_content}
        logger.warning(
            "Fallback prompt trimmed for '%s': %d -> ~%d tokens (budget=%d).",
            cfg.model_id, len(toks), hr + tail_reserve, budget,
        )
        return new_messages

    @staticmethod
    def _clamp_output_tokens(
        params: dict[str, Any],
        cfg: ModelConfig,
        messages: list[dict[str, str]],
    ) -> dict[str, Any]:
        """Guarantee a positive generation length that fits remaining context."""
        prompt_toks = sum(_count_tokens(m.get("content", "") or "") for m in messages)
        room = max(1, min(cfg.context_window - prompt_toks - 64, cfg.max_output_tokens))
        for key in ("max_completion_tokens", "max_tokens"):
            if key in params:
                params[key] = max(1, min(params[key] or room, room))
        return params

    @staticmethod
    def _strip_reasoning(text: str) -> str:
        if not text:
            return text
        out = text
        for tag in LLMClientManager._REASONING_TAGS:
            out = re.sub(rf"<{tag}\b[^>]*>.*?</{tag}>", "", out,
                        flags=re.DOTALL | re.IGNORECASE)
        # completions-prefill / truncated opener leaves a dangling closer
        out = re.sub(r"^.*?</(?:think|thinking|reasoning|analysis)>", "", out,
                    flags=re.DOTALL | re.IGNORECASE)
        return out

    def extract_text(
        self,
        response: Any,
        model_name: str | None = None,
        output_format: OutputFormat = "auto",
    ) -> str:
        """
        Extract content from an LLM response.

        Reasoning models often emit chain-of-thought before/after the final
        answer. This method:
          1. Pulls raw text out of the response object (skipping reasoning items).
          2. If output_format == "json", isolates the best JSON object inside that text.
          3. If output_format == "text", returns the cleaned text as-is.
          4. If "auto", returns JSON when one is detected, otherwise text.

        Args:
            response: API response (Responses API or Chat Completions).
            model_name: Kept for signature stability; not required.
            output_format:
                "json" — return a JSON-shaped string (best-effort, even if malformed).
                "text" — return plain text (no JSON extraction).
                "auto" — JSON if detected, otherwise text.
        """
        raw = self._get_raw_response_text(response)
        if not raw:
            return ""

        raw = self._strip_reasoning(raw)      # NEW — applies to text AND json
        if output_format == "text":
            return raw.strip()

        json_str = self._extract_best_json(raw)
        if output_format == "json":
            # JSON callers always get *something* — caller's json_cleaning can repair further.
            return json_str if json_str else raw.strip()

        # auto
        return json_str if json_str else raw.strip()

    # ──────────────────────────────────────────────────────────────────────
    # Raw response → text
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def _get_raw_response_text(response: Any) -> str:
        """
        Pull text from a response object without regex tricks.
        Handles:
          - Responses API:  response.output[i].content[j].text  (skips type=='reasoning')
          - Chat API:       response.choices[0].message.content
          - Legacy:         response.choices[0].text
        """
        if response is None:
            return ""

        # ---- Responses API ----
        output = getattr(response, "output", None)
        if isinstance(output, list):
            parts: list[str] = []
            for item in output:
                # Skip reasoning blocks — they contain CoT, not the user-facing answer.
                if getattr(item, "type", None) == "reasoning":
                    continue

                content = getattr(item, "content", None)
                if isinstance(content, list):
                    for block in content:
                        t = getattr(block, "text", None)
                        if isinstance(t, str) and t:
                            parts.append(t)
                elif isinstance(content, str) and content:
                    parts.append(content)
                else:
                    t = getattr(item, "text", None)
                    if isinstance(t, str) and t:
                        parts.append(t)
            if parts:
                return "".join(parts)

        # ---- Chat Completions ----
        choices = getattr(response, "choices", None)
        if choices:
            choice = choices[0]
            msg = getattr(choice, "message", None)
            if msg is not None:
                c = getattr(msg, "content", None)
                if isinstance(c, str):
                    return c
            legacy = getattr(choice, "text", None)
            if isinstance(legacy, str):
                return legacy

        return ""

    # ──────────────────────────────────────────────────────────────────────
    # JSON isolation
    # ──────────────────────────────────────────────────────────────────────

    # Keys we expect to see in valid model outputs across the pipeline.
    _EXPECTED_JSON_KEYS = frozenset({
        "response", "parameters", "response_template",
        "SQL", "sql",
        "title", "description", "form", "system",
    })

    def _extract_best_json(self, text: str) -> str:
        """
        Find the most plausible JSON object in `text`.

        Order of preference:
          1. Last parseable block containing an expected pipeline key.
          2. Last *non-empty* parseable block (a bare {} is never an answer).
          3. Regex-salvaged "response" field, re-emitted as a minimal valid
             object (handles unescaped quotes / raw newlines in the value).
          4. Longest raw block, as a last-resort handoff to the caller's
             json_cleaning() repair step.
        """
        # Reasoning models emit chain-of-thought that frequently contains a
        # stray "{}" or an illustrative "{...}". json_cleaning() strips
        # <think> later, but that is AFTER block selection — too late. Drop
        # it here so it cannot out-compete the real answer.
        cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        cleaned_text = re.sub(
            r"<reasoning>.*?</reasoning>", "", cleaned_text, flags=re.DOTALL
        )

        blocks = self._find_json_blocks(cleaned_text)

        parsed_blocks: list[tuple[str, dict]] = []
        for block in blocks:
            parsed = self._try_parse_json(block)
            if isinstance(parsed, dict):
                parsed_blocks.append((block, parsed))

        # 1. Last block matching the schema we expect anywhere in the
        #    pipeline. Reasoning models put the final answer last.
        for _block, parsed in reversed(parsed_blocks):
            if any(k in parsed for k in self._EXPECTED_JSON_KEYS):
                return json.dumps(parsed, ensure_ascii=False)

        # 2. Last *non-empty* parseable block. A bare {} (or any empty dict)
        #    carries no answer; previously step 2 re-serialised it and the
        #    user received the literal string "{}". Skip empties entirely.
        for _block, parsed in reversed(parsed_blocks):
            if parsed:
                return json.dumps(parsed, ensure_ascii=False)

        # 3. Nothing parsed cleanly. The real answer is probably present but
        #    malformed (unescaped inner quote or raw newline in a Persian
        #    string value). Salvage the "response" field and re-emit a
        #    minimal well-formed object so the caller's json.loads() +
        #    .get("response") still yields the real text instead of "{}".
        salvaged = self._salvage_response_field(cleaned_text)
        if salvaged is not None:
            conf = "DOUBTFUL" if re.search(r'"confidence"\s*:\s*"DOUBTFUL"',
                                        cleaned_text, re.IGNORECASE) else "ACCURATE"
            return json.dumps(
                {"response": salvaged, "parameters": {}, "confidence": conf},
                ensure_ascii=False,
            )

        # 4. Last resort.
        if blocks:
            return max(blocks, key=len)
        return cleaned_text.strip()

    @staticmethod
    def _salvage_response_field(text: str) -> str | None:
        """
        Best-effort extraction of the "response" string value from a
        malformed JSON-ish blob. Tolerates unescaped inner quotes, raw
        newlines, and a truncated tail. Returns the unescaped string, or
        None if there is no "response" key at all.
        """
        m = re.search(
            r'"response"\s*:\s*"(.*)"\s*'
            r'(?:,\s*"(?:confidence|parameters)"|}\s*$|})',
            text,
            re.DOTALL,
        )
        if not m:
            # No clean terminator found — take everything after the key.
            m = re.search(r'"response"\s*:\s*"(.*)$', text, re.DOTALL)
            if not m:
                return None

        value = m.group(1)
        # Strip a dangling closing quote/brace the greedy capture may keep.
        value = re.sub(r'"\s*}?\s*$', "", value).rstrip()
        value = value.replace('\\"', '"').replace("\\n", "\n").strip()
        return value or None

    @staticmethod
    def _find_json_blocks(text: str) -> list[str]:
        """Find all top-level balanced {...} substrings, respecting string literals."""
        blocks: list[str] = []
        depth = 0
        start = -1
        in_string = False
        escape = False

        for i, ch in enumerate(text):
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue

            if ch == "{":
                if depth == 0:
                    start = i
                depth += 1
            elif ch == "}":
                if depth > 0:
                    depth -= 1
                    if depth == 0 and start >= 0:
                        blocks.append(text[start : i + 1])
                        start = -1
        return blocks

    @staticmethod
    def _try_parse_json(s: str) -> Any | None:
        """Parse JSON with light tolerance for common malformed-output patterns."""
        if not s or not s.strip():
            return None

        # Fast path
        try:
            return json.loads(s, strict=False)
        except json.JSONDecodeError:
            pass

        cleaned = s
        # 1) Trailing commas:  {"a": 1,}  →  {"a": 1}
        cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)
        # 2) Spurious extra ":" opener:  {"response":":"text...  →  {"response":"text...
        cleaned = re.sub(r'("(?:response|SQL|title|description|form)"\s*:\s*)":"',
                         r'\1"', cleaned, count=1)
        # 3) Doubled closing quotes before }:  ..."text""}  →  ..."text"}
        cleaned = re.sub(r'"{2,}\s*\}', '"}', cleaned)
        # 4) Garbage between } and outer }:  ...{}""}  →  ...{}}
        cleaned = re.sub(r"\}\s*\"+\s*\}", "}}", cleaned)
        # 5) Stray quote right before final }:  ..."}  with extra "  →  ..."}
        cleaned = re.sub(r'"\s*"\s*\}\s*$', '"}', cleaned)

        try:
            return json.loads(cleaned, strict=False)
        except json.JSONDecodeError:
            return None

llm_manager = LLMClientManager()