from pathlib import Path
from typing import Any

import yaml


class ConfigError(RuntimeError):
    """Raised when Homeland configuration cannot be loaded."""


class ConfigManager:
    def __init__(self, config_dir: str | Path | None = None) -> None:
        if config_dir is None:
            config_dir = Path(__file__).resolve().parent.parent / "config"

        self.config_dir = Path(config_dir)
        self._cache: dict[str, dict[str, Any]] = {}

    def _path_for(self, name: str) -> Path:
        filename = name if name.endswith(".yml") else f"{name}.yml"
        return self.config_dir / filename

    def load(self, name: str, *, reload: bool = False) -> dict[str, Any]:
        cache_key = name.removesuffix(".yml")

        if not reload and cache_key in self._cache:
            return self._cache[cache_key]

        path = self._path_for(name)

        if not path.exists():
            raise ConfigError(f"Configuration file not found: {path}")

        try:
            with path.open("r", encoding="utf-8") as file:
                data = yaml.safe_load(file) or {}
        except yaml.YAMLError as exc:
            raise ConfigError(f"Invalid YAML in {path}: {exc}") from exc
        except OSError as exc:
            raise ConfigError(f"Could not read {path}: {exc}") from exc

        if not isinstance(data, dict):
            raise ConfigError(
                f"Top-level configuration in {path} must be a mapping."
            )

        self._cache[cache_key] = data
        return data

    def get(self, config_name: str, key: str, default: Any = None) -> Any:
        data: Any = self.load(config_name)

        for part in key.split("."):
            if not isinstance(data, dict) or part not in data:
                return default
            data = data[part]

        return data

    def reload_all(self) -> None:
        self._cache.clear()


config = ConfigManager()
