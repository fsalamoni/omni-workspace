"""Application configuration via Pydantic Settings.

Loads all configuration from environment variables with sensible defaults.
Supports .env files via python-dotenv.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the OmniWorkspace backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── LLM API Keys ───────────────────────────────────────────────────
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    google_api_key: Optional[str] = Field(default=None, description="Google AI / Gemini API key")
    groq_api_key: Optional[str] = Field(default=None, description="Groq API key")
    deepseek_api_key: Optional[str] = Field(default=None, description="DeepSeek API key")
    openrouter_api_key: Optional[str] = Field(default=None, description="OpenRouter API key")
    mistral_api_key: Optional[str] = Field(default=None, description="Mistral API key")
    cohere_api_key: Optional[str] = Field(default=None, description="Cohere API key")
    together_api_key: Optional[str] = Field(default=None, description="Together AI API key")
    fireworks_api_key: Optional[str] = Field(default=None, description="Fireworks AI API key")
    perplexity_api_key: Optional[str] = Field(default=None, description="Perplexity API key")
    elevenlabs_api_key: Optional[str] = Field(default=None, description="ElevenLabs API key")
    fal_api_key: Optional[str] = Field(default=None, description="Fal.ai API key")
    xai_api_key: Optional[str] = Field(default=None, description="xAI (Grok) API key")
    kimi_api_key: Optional[str] = Field(default=None, description="Kimi (Moonshot) API key")
    qwen_api_key: Optional[str] = Field(default=None, description="Qwen (DashScope) API key")
    nvidia_api_key: Optional[str] = Field(default=None, description="NVIDIA API key")
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama local server base URL",
    )

    # ── Model Selection ────────────────────────────────────────────────
    omni_planning_model: str = Field(
        default="openai/gpt-4o",
        description="Model used for task planning and decomposition",
    )
    omni_execution_model: str = Field(
        default="openai/gpt-4o-mini",
        description="Model used for step execution",
    )
    omni_vision_model: str = Field(
        default="openai/gpt-4o",
        description="Model used for vision / screenshot interpretation",
    )

    # ── Server ─────────────────────────────────────────────────────────
    server_host: str = Field(default="0.0.0.0", description="Bind host")
    server_port: int = Field(default=8000, description="Bind port")
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )
    debug: bool = Field(default=False, description="Enable debug / reload mode")

    # ── Sandbox ────────────────────────────────────────────────────────
    sandbox_enabled: bool = Field(default=False, description="Enable Docker sandboxing")
    sandbox_image: str = Field(
        default="omni-sandbox:latest",
        description="Docker image for sandbox containers",
    )
    sandbox_max_containers: int = Field(default=5, description="Max concurrent containers")
    sandbox_timeout: int = Field(default=120, description="Default command timeout (seconds)")
    sandbox_memory_limit: str = Field(default="512m", description="Container memory limit")
    sandbox_cpu_quota: int = Field(default=50000, description="CPU quota (μs per 100ms)")

    # ── Memory / Vector DB ─────────────────────────────────────────────
    memory_embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence-transformers model for embeddings",
    )
    memory_embedding_dim: int = Field(default=384, description="Embedding dimension")
    memory_max_elements: int = Field(default=100_000, description="Max HNSW index elements")
    memory_ef_construction: int = Field(default=200, description="HNSW ef_construction")
    memory_m: int = Field(default=16, description="HNSW M parameter")
    memory_db_path: str = Field(
        default="data/memory.db",
        description="SQLite path for memory metadata",
    )
    memory_index_path: str = Field(
        default="data/memory.hnsw",
        description="HNSW index persistence path",
    )

    # ── MCP ─────────────────────────────────────────────────────────────
    mcp_config_path: str = Field(
        default="mcp_servers.json",
        description="Path to MCP server config JSON file",
    )

    # ── Workspace ──────────────────────────────────────────────────────
    default_workspace_path: str = Field(
        default="workspaces",
        description="Base directory for user workspaces",
    )

    # ── Security ───────────────────────────────────────────────────────
    encryption_key: Optional[str] = Field(
        default=None,
        description="Fernet key for encrypting stored API keys. Auto-generated if absent.",
    )
    session_secret: str = Field(
        default="change-me-in-production",
        description="Secret for session signing",
    )

    # ── Condensation ───────────────────────────────────────────────────
    condenser_max_tokens: int = Field(
        default=100_000,
        description="Token threshold before context condensation triggers",
    )
    condenser_keep_recent: int = Field(
        default=10,
        description="Number of recent messages to keep after condensation",
    )

    # ── Validators ─────────────────────────────────────────────────────
    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ── Helpers ─────────────────────────────────────────────────────────
    def ensure_data_dirs(self) -> None:
        """Create required data directories if they don't exist."""
        Path(self.memory_db_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.memory_index_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.default_workspace_path).mkdir(parents=True, exist_ok=True)

    def get_available_provider_keys(self) -> dict[str, str]:
        """Return a mapping of provider name → API key for configured providers."""
        keys: dict[str, str] = {}
        if self.openai_api_key: keys["openai"] = self.openai_api_key
        if self.anthropic_api_key: keys["anthropic"] = self.anthropic_api_key
        if self.google_api_key: keys["google"] = self.google_api_key
        if self.groq_api_key: keys["groq"] = self.groq_api_key
        if self.deepseek_api_key: keys["deepseek"] = self.deepseek_api_key
        if self.openrouter_api_key: keys["openrouter"] = self.openrouter_api_key
        if self.mistral_api_key: keys["mistral"] = self.mistral_api_key
        if self.cohere_api_key: keys["cohere"] = self.cohere_api_key
        if self.together_api_key: keys["together"] = self.together_api_key
        if self.fireworks_api_key: keys["fireworks"] = self.fireworks_api_key
        if self.perplexity_api_key: keys["perplexity"] = self.perplexity_api_key
        if self.elevenlabs_api_key: keys["elevenlabs"] = self.elevenlabs_api_key
        if self.fal_api_key: keys["fal"] = self.fal_api_key
        if self.xai_api_key: keys["xai"] = self.xai_api_key
        if self.kimi_api_key: keys["kimi"] = self.kimi_api_key
        if self.qwen_api_key: keys["qwen"] = self.qwen_api_key
        if self.nvidia_api_key: keys["nvidia"] = self.nvidia_api_key
        return keys

# Module-level singleton
settings = Settings()
