"""
Backward compatibility wrapper.

This preserves the old configuration API while the new
ConfigManager becomes the canonical configuration system.
"""

from core.config import config


def load_yaml(filename: str):
    return config.load(filename)


def get_homeland_config():
    """
    Return the legacy flattened configuration expected by
    existing Homeland modules.
    """

    cfg = config.load("homeland")

    return {
        **cfg,

        # Legacy compatibility
        "prometheus": cfg.get("monitoring", {}).get("prometheus", {}),

        # Future aliases can be added here as needed.
    }
