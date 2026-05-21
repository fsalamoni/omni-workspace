"""LLM provider configuration dataclasses.

Each ``ProviderConfig`` captures the credentials, base URL, and available
models for one LLM provider.  A helper builds the full list of configs from
application ``Settings``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.config import Settings


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    """Configuration for a single LLM provider."""

    name: str
    api_key: str = ""
    base_url: str = ""
    models: list[str] = field(default_factory=list)

    @property
    def is_configured(self) -> bool:
        """True if the provider has an API key *or* is a local service like Ollama."""
        return bool(self.api_key) or self.name == "ollama"


# ────────────────────────────────────────────────────────────────────
# Factory
# ────────────────────────────────────────────────────────────────────

_OPENAI_MODELS = [
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "openai/gpt-4-turbo",
    "openai/o1-preview",
    "openai/o1-mini",
    "openai/o3-mini",
]

_ANTHROPIC_MODELS = [
    "anthropic/claude-sonnet-4-20250514",
    "anthropic/claude-3.5-sonnet-20241022",
    "anthropic/claude-3-opus-20240229",
    "anthropic/claude-3-haiku-20240307",
]

_GOOGLE_MODELS = [
    "gemini/gemini-2.5-flash",
    "gemini/gemini-2.5-pro",
    "gemini/gemini-2.0-flash",
    "gemini/gemini-1.5-pro",
]

_GROQ_MODELS = [
    "groq/llama-3.3-70b-versatile",
    "groq/llama-3.1-8b-instant",
    "groq/mixtral-8x7b-32768",
]

_OLLAMA_MODELS = [
    "ollama/llama3.2",
    "ollama/mistral",
    "ollama/codellama",
    "ollama/deepseek-coder-v2",
]


def build_provider_configs(settings: Settings) -> list[ProviderConfig]:
    """Build the list of ``ProviderConfig`` objects from application settings."""
    configs: list[ProviderConfig] = []

    configs.append(
        ProviderConfig(
            name="openai",
            api_key=settings.openai_api_key or "",
            models=_OPENAI_MODELS,
        )
    )
    configs.append(
        ProviderConfig(
            name="anthropic",
            api_key=settings.anthropic_api_key or "",
            models=_ANTHROPIC_MODELS,
        )
    )
    configs.append(
        ProviderConfig(
            name="google",
            api_key=settings.google_api_key or "",
            models=_GOOGLE_MODELS,
        )
    )
    configs.append(
        ProviderConfig(
            name="groq",
            api_key=settings.groq_api_key or "",
            models=_GROQ_MODELS,
        )
    )
    configs.append(
        ProviderConfig(
            name="ollama",
            base_url=settings.ollama_base_url,
            models=_OLLAMA_MODELS,
        )
    )

    return configs
