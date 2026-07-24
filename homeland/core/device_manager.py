from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.config import config


@dataclass(frozen=True)
class Device:
    id: str
    name: str
    category: str
    hostname: str
    operating_system: str
    monitor: str
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "hostname": self.hostname,
            "operating_system": self.operating_system,
            "monitor": self.monitor,
            "enabled": self.enabled,
        }


class DeviceManager:
    def __init__(self) -> None:
        self._devices: dict[str, Device] | None = None

    def load(self) -> dict[str, Device]:
        if self._devices is not None:
            return self._devices

        raw = config.load("devices")
        devices: dict[str, Device] = {}

        for key, entry in raw.items():
            device_id = entry.get("id", key)

            devices[device_id] = Device(
                id=device_id,
                name=entry["name"],
                category=entry["category"],
                hostname=entry["hostname"],
                operating_system=entry.get("operating_system", "Unknown"),
                monitor=entry.get("monitor", "none"),
                enabled=entry.get("enabled", True),
            )

        self._devices = devices
        return devices

    def get_all(self) -> list[Device]:
        return list(self.load().values())

    def get_enabled(self) -> list[Device]:
        return [
            device
            for device in self.get_all()
            if device.enabled
        ]

    def get(self, device_id: str) -> Device | None:
        return self.load().get(device_id)

    def count_total(self) -> int:
        return len(self.get_enabled())

    def clear_cache(self) -> None:
        self._devices = None


device_manager = DeviceManager()
