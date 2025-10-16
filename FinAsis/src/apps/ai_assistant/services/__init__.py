"""
Lightweight services package initializer.

Intentionally avoids importing heavy submodules at import time to prevent
AppRegistryNotReady or optional dependency errors during Django startup/tests.

Import concrete services directly where needed, e.g.:
    from src.apps.ai_assistant.services.nlp_service import LocalNLPService
"""

from .local_stt_service import LocalSTTService  # re-export for backward compatibility

__all__: list[str] = ['LocalSTTService']