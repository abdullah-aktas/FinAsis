"""Compatibility shim.

Historically some imports referenced 'src.settings'. The canonical settings
module is now 'src.config.settings'. This module simply re-exports everything
to avoid duplicate definitions and static analysis warnings.
"""
from src.config.settings import *  # noqa: F401,F403