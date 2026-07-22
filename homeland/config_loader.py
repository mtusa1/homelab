from pathlib import Path
from typing import Any

import yaml


BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"


def load_yaml(filename: str) -> dict[str, Any]:
    path = CONFIG_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as config_file:
        data = yaml.safe_load(config_file) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Configuration root must be a mapping: {path}")

    return data


def get_homeland_config() -> dict[str, Any]:
    return load_yaml("homeland.yml")
