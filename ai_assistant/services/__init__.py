"""
Lightweight services package initializer.

Intentionally avoids importing heavy submodules at import time to prevent
AppRegistryNotReady or optional dependency errors during Django startup/tests.

Import concrete services directly where needed, e.g.:
    from ai_assistant.services.nlp_service import LocalNLPService
"""

from .local_stt_service import LocalSTTService  # re-export for backward compatibility
from .prompt_registry import (
    PromptNotFound,
    get_prompt,
    get_prompts_for_role,
    list_roles,
)
from .recommendation_service import RecommendationService

# Yerel LLM servisi (opsiyonel import)
try:
    from .local_llm_service import LocalLLMService
    __all__: list[str] = [
        "LocalSTTService",
        "LocalLLMService",
        "RecommendationService",
        "get_prompts_for_role",
        "get_prompt",
        "list_roles",
        "PromptNotFound",
    ]
except ImportError:
    __all__: list[str] = [
        "LocalSTTService",
        "RecommendationService",
        "get_prompts_for_role",
        "get_prompt",
        "list_roles",
        "PromptNotFound",
    ]
