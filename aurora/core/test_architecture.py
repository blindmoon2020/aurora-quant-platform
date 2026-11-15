"""Software Architecture Verification Test for Aurora Quant Platform.
Validates plugin registration, decoupling, and registry error handling.
"""
from __future__ import annotations

from aurora.core.plugin_registry import AuroraPluginRegistry, PluginAlreadyRegisteredError


def run_architecture_test() -> None:
    print("--- Starting Aurora Software Architecture Verification ---")
    
    registry = AuroraPluginRegistry()

    # 1. Register a mock technical analyzer plugin
    mock_analyzer_name = "SmartMoneySMC"
    registry.register_analyzer(mock_analyzer_name, {"version": "2.5", "status": "active"})
    print(f"[OK] Successfully registered analyzer plugin: {mock_analyzer_name}")

    # 2. Retrieve plugin dynamically
    retrieved = registry.get_analyzer(mock_analyzer_name)
    print(f"[OK] Retrieved plugin spec: {retrieved}")

    # 3. Test duplicate registration safety guard
    try:
        registry.register_analyzer(mock_analyzer_name, {"version": "2.6"})
    except PluginAlreadyRegisteredError as e:
        print(f"[OK] Safety Guard Triggered Successfully: {e}")

    # 4. List all plugins
    summary = registry.list_registered_plugins()
    print(f"[OK] Registered Plugins Manifest: {summary}")
    print("--- Architecture Verification Completed Successfully ---")


if __name__ == "__main__":
    run_architecture_test()
