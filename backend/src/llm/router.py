"""LLM Router — unified completion interface powered by LiteLLM.

Provides ``complete`` (single response) and ``stream`` (async generator)
methods.  The router auto-detects the provider from the model string
(e.g. ``openai/gpt-4o`` → OpenAI), injects the correct API key, and
supports transparent key rotation on ``AuthenticationError``.
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Any, AsyncGenerator, Optional

import litellm
from litellm import AuthenticationError as LiteLLMAuthError

from src.config import Settings
from src.llm.providers import ProviderConfig, build_provider_configs

logger = logging.getLogger(__name__)

# Silence overly-verbose litellm logging in production.
litellm.suppress_debug_info = True


class LLMRouter:
    """Thin wrapper around LiteLLM that adds key rotation, provider
    resolution, and a consistent async interface.

    Parameters
    ----------
    settings:
        Application ``Settings`` instance.
    extra_keys:
        Optional mapping of ``provider → [api_key, …]`` for key-pool
        rotation.
    """

    def __init__(
        self,
        settings: Settings,
        settings_db: Any = None,
        extra_keys: dict[str, list[str]] | None = None,
    ) -> None:
        self._settings = settings
        self.settings_db = settings_db
        self._providers: dict[str, ProviderConfig] = {
            p.name: p for p in build_provider_configs(settings)
        }

        # Key pool: provider → list of keys.  The first key is the
        # "current" one; on auth failure we rotate.
        self._key_pools: dict[str, list[str]] = defaultdict(list)
        for name, cfg in self._providers.items():
            if cfg.api_key:
                self._key_pools[name].append(cfg.api_key)
        if extra_keys:
            for prov, keys in extra_keys.items():
                self._key_pools[prov].extend(keys)

        self._lock = asyncio.Lock()

    # ── Public API ─────────────────────────────────────────────────

    async def complete(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Run a non-streaming chat completion.

        Returns the raw LiteLLM ``ModelResponse`` serialised to a dict
        with keys ``content``, ``tool_calls``, ``usage``, ``model``.
        """
        model = model or self._settings.omni_execution_model
        provider = self._provider_for(model)
        api_key = await self._current_key(provider)

        completion_kwargs = self._build_kwargs(
            messages=messages,
            model=model,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            provider=provider,
            **kwargs,
        )

        try:
            response = await litellm.acompletion(**completion_kwargs)
        except LiteLLMAuthError:
            logger.warning("Auth failed for provider=%s, rotating key…", provider)
            self._rotate_key(provider)
            completion_kwargs["api_key"] = await self._current_key(provider)
            response = await litellm.acompletion(**completion_kwargs)

        choice = response.choices[0]  # type: ignore[attr-defined]
        message = choice.message

        result: dict[str, Any] = {
            "content": message.content or "",
            "tool_calls": [],
            "usage": dict(response.usage) if response.usage else {},  # type: ignore[attr-defined]
            "model": response.model,  # type: ignore[attr-defined]
            "finish_reason": choice.finish_reason,
        }

        if message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ]

        return result

    async def stream(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream a chat completion, yielding delta dicts.

        Each yielded dict has at minimum a ``content`` key (possibly empty
        string) and optionally ``tool_calls``.
        """
        model = model or self._settings.omni_execution_model
        provider = self._provider_for(model)
        api_key = await self._current_key(provider)

        completion_kwargs = self._build_kwargs(
            messages=messages,
            model=model,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            provider=provider,
            stream=True,
            **kwargs,
        )

        try:
            response = await litellm.acompletion(**completion_kwargs)
        except LiteLLMAuthError:
            self._rotate_key(provider)
            completion_kwargs["api_key"] = await self._current_key(provider)
            response = await litellm.acompletion(**completion_kwargs)

        async for chunk in response:  # type: ignore[union-attr]
            delta = chunk.choices[0].delta
            yield {
                "content": delta.content or "",
                "tool_calls": (
                    [
                        {
                            "id": getattr(tc, "id", ""),
                            "function": {
                                "name": getattr(tc.function, "name", ""),
                                "arguments": getattr(tc.function, "arguments", ""),
                            },
                        }
                        for tc in delta.tool_calls
                    ]
                    if delta.tool_calls
                    else []
                ),
            }

    def get_available_models(self) -> list[dict[str, Any]]:
        """Return models the user has credentials for."""
        models: list[dict[str, Any]] = []
        for cfg in self._providers.values():
            if cfg.is_configured:
                for m in cfg.models:
                    models.append({"model": m, "provider": cfg.name})
        return models

    # ── Internals ──────────────────────────────────────────────────

    @staticmethod
    def _provider_for(model: str) -> str:
        """Extract provider name from a ``provider/model-name`` string."""
        if "/" in model:
            return model.split("/", 1)[0]
        return "openai"  # default

    async def _current_key(self, provider: str) -> Optional[str]:
        # First try to get it from settings_db
        if self.settings_db:
            keys = await self.settings_db._get_json("api_keys") or []
            for k in keys:
                if k.get("provider", "").lower() == provider.lower() and k.get("key"):
                    return k.get("key")
        
        pool = self._key_pools.get(provider)
        return pool[0] if pool else None

    def _rotate_key(self, provider: str) -> None:
        pool = self._key_pools.get(provider)
        if pool and len(pool) > 1:
            pool.append(pool.pop(0))
            logger.info("Rotated to next key for provider=%s", provider)

    def _build_kwargs(
        self,
        *,
        messages: list[dict[str, Any]],
        model: str,
        tools: list[dict[str, Any]] | None,
        temperature: float,
        max_tokens: int,
        api_key: Optional[str],
        provider: str,
        stream: bool = False,
        **extra: Any,
    ) -> dict[str, Any]:
        kw: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        if api_key:
            kw["api_key"] = api_key
        if tools:
            kw["tools"] = tools
            kw["tool_choice"] = "auto"

        # Provider-specific overrides.
        provider_cfg = self._providers.get(provider)
        if provider_cfg and provider_cfg.base_url:
            kw["api_base"] = provider_cfg.base_url

        kw.update(extra)
        return kw
