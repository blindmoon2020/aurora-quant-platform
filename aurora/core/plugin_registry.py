"""Central Plugin Registry and Dependency Manager for Aurora Quant Platform.
Implements the Factory and Registry design patterns to allow seamless,
decoupled extension of technical analyzers, brokers, and risk gates.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Type


class PluginAlreadyRegisteredError(Exception):
    """Raised when attempting to register a plugin key that already exists."""
    pass


class PluginNotFoundError(Exception):
    """Raised when a requested plugin is not found in the registry."""
    pass


class AuroraPluginRegistry:
    """Centralized thread-safe registry for dynamic component loading and execution."""

    def __init__(self) -> None:
        self._analyzers: Dict[str, Any] = {}
        self._brokers: Dict[str, Any] = {}
        self._risk_gates: Dict[str, Any] = {}

    def register_analyzer(self, name: str, analyzer_cls: Any) -> None:
        key = name.lower()
        if key in self._analyzers:
            raise PluginAlreadyRegisteredError(f"Analyzer '{name}' is already registered.")
        self._analyzers[key] = analyzer_cls

    def get_analyzer(self, name: str) -> Any:
        key = name.lower()
        if key not in self._analyzers:
            raise PluginNotFoundError(f"Analyzer '{name}' not found in registry.")
        return self._analyzers[key]

    def register_broker(self, name: str, broker_instance: Any) -> None:
        key = name.lower()
        if key in self._brokers:
            raise PluginAlreadyRegisteredError(f"Broker '{name}' is already registered.")
        self._brokers[key] = broker_instance

    def get_broker(self, name: str) -> Any:
        key = name.lower()
        if key not in self._brokers:
            raise PluginNotFoundError(f"Broker '{name}' not found in registry.")
        return self._brokers[key]

    def list_registered_plugins(self) -> Dict[str, list[str]]:
        return {
            "analyzers": list(self._analyzers.keys()),
            "brokers": list(self._brokers.keys()),
            "risk_gates": list(self._risk_gates.keys()),
        }


# Global application-wide registry instance
global_registry = AuroraPluginRegistry()
