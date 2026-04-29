"""Multi-provider LLM configuration and factory."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from app.domain.ports.generation_provider import GenerationProvider


class ProviderType(str, Enum):
    """Supported LLM providers."""

    NVIDIA = "nvidia"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"


class ModelRegistry:
    """Registry of latest models for each provider as of April 2026."""

    NVIDIA_MODELS = {
        "llama-4-maverick": "meta/llama-4-maverick-17b-128e-instruct",
        "llama-4-scout": "meta/llama-4-scout-instruct",
        "nemotron-super": "nvidia/llama-3.3-nemotron-super-49b-v1",
        "nemotron-nano": "nvidia/llama-3.3-nemotron-nano-8b-v1",
    }

    OPENAI_MODELS = {
        "gpt-4.1": "gpt-4.1",
        "gpt-4.1-mini": "gpt-4.1-mini",
        "gpt-4.1-nano": "gpt-4.1-nano",
        "o4-mini": "o4-mini",
        "o3": "o3",
    }

    ANTHROPIC_MODELS = {
        "claude-sonnet-4": "claude-sonnet-4-20250514",
        "claude-opus-4": "claude-opus-4-20250514",
        "claude-3-7-sonnet": "claude-3-7-sonnet-latest",
    }

    GEMINI_MODELS = {
        "gemini-2.5-flash": "gemini-2.5-flash-preview-04-29",
        "gemini-2.5-pro": "gemini-2.5-pro-preview-04-29",
        "gemini-2.0-flash": "gemini-2.0-flash",
    }

    @classmethod
    def get_default_model(cls, provider: ProviderType) -> str:
        """Get the recommended default model for each provider."""
        defaults = {
            ProviderType.NVIDIA: cls.NVIDIA_MODELS["llama-4-maverick"],
            ProviderType.OPENAI: cls.OPENAI_MODELS["gpt-4.1"],
            ProviderType.ANTHROPIC: cls.ANTHROPIC_MODELS["claude-sonnet-4"],
            ProviderType.GEMINI: cls.GEMINI_MODELS["gemini-2.5-flash"],
        }
        return defaults.get(provider, "")

    @classmethod
    def get_all_models(cls, provider: ProviderType) -> dict[str, str]:
        """Get all available models for a provider."""
        model_map = {
            ProviderType.NVIDIA: cls.NVIDIA_MODELS,
            ProviderType.OPENAI: cls.OPENAI_MODELS,
            ProviderType.ANTHROPIC: cls.ANTHROPIC_MODELS,
            ProviderType.GEMINI: cls.GEMINI_MODELS,
        }
        return model_map.get(provider, {})


@dataclass(frozen=True, slots=True)
class LLMConfig:
    """Configuration for LLM generation with provider-agnostic parameters."""

    # Provider selection
    provider: ProviderType = field(default_factory=lambda: ProviderType.GEMINI)
    model: str = ""
    api_key: str = ""

    # Provider-specific base URL (e.g., for NVIDIA)
    base_url: str | None = None

    # Generation parameters (universal across providers)
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 40
    max_tokens: int = 4096

    # System prompt
    system_prompt: str = (
        "You are a helpful AI learning assistant. Your goal is to help users "
        "understand complex topics by providing clear, accurate, and well-structured "
        "explanations. Always cite your sources when providing information. "
        "Be encouraging and supportive in your teaching approach."
    )

    def __post_init__(self):
        """Validate and set defaults after initialization."""
        # If model not specified, use default
        if not self.model:
            object.__setattr__(
                self, "model", ModelRegistry.get_default_model(self.provider)
            )

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Auto-detect provider from environment variables."""
        # Priority order for detection
        detection_order = [
            ("NVIDIA_API_KEY", ProviderType.NVIDIA, "NVIDIA_MODEL", "NVIDIA_BASE_URL"),
            ("OPENAI_API_KEY", ProviderType.OPENAI, "OPENAI_MODEL", None),
            ("ANTHROPIC_API_KEY", ProviderType.ANTHROPIC, "ANTHROPIC_MODEL", None),
            ("GEMINI_API_KEY", ProviderType.GEMINI, "GEMINI_MODEL", None),
        ]

        for api_key_var, provider, model_var, base_url_var in detection_order:
            api_key = os.getenv(api_key_var)
            if api_key and api_key != f"{provider.value}-api-key-here":
                model = os.getenv(model_var, "") or ModelRegistry.get_default_model(provider)
                base_url = os.getenv(base_url_var) if base_url_var else None

                return cls(
                    provider=provider,
                    model=model,
                    api_key=api_key,
                    base_url=base_url,
                    temperature=float(os.getenv("DEFAULT_TEMPERATURE", "0.7")),
                    top_p=float(os.getenv("DEFAULT_TOP_P", "0.95")),
                    top_k=int(os.getenv("DEFAULT_TOP_K", "40")),
                    max_tokens=int(os.getenv("DEFAULT_MAX_TOKENS", "4096")),
                    system_prompt=os.getenv(
                        "DEFAULT_SYSTEM_PROMPT",
                        "You are a helpful AI learning assistant. Your goal is to help users "
                        "understand complex topics by providing clear, accurate, and well-structured "
                        "explanations. Always cite your sources when providing information. "
                        "Be encouraging and supportive in your teaching approach.",
                    ),
                )

        # Fallback to Gemini with empty key (will error on generation)
        return cls(
            provider=ProviderType.GEMINI,
            model=ModelRegistry.get_default_model(ProviderType.GEMINI),
            api_key=os.getenv("GEMINI_API_KEY", ""),
        )

    def with_params(
        self,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
    ) -> "LLMConfig":
        """Create a new config with updated generation parameters."""
        return LLMConfig(
            provider=self.provider,
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=temperature if temperature is not None else self.temperature,
            top_p=top_p if top_p is not None else self.top_p,
            top_k=top_k if top_k is not None else self.top_k,
            max_tokens=max_tokens if max_tokens is not None else self.max_tokens,
            system_prompt=system_prompt if system_prompt is not None else self.system_prompt,
        )
