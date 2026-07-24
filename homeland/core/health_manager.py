from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from threading import Lock
from time import monotonic
from typing import Any

from core.device_manager import Device, device_manager
from services.prometheus import first_value


HEALTH_CACHE_TTL_SECONDS = 30.0


PROMETHEUS_JOBS = {
    "nuc": "nuc",
    "main-desktop": "windows-main-desktop",
    "windows-workstation": "windows-workstation",
    "synology": "synology-snmp",
}


@dataclass(frozen=True)
class DeviceHealth:
    device_id: str
    name: str
    status: str
    monitor: str
    message: str
    checked_at: str
    reachable: bool | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class HealthManager:
    def __init__(self) -> None:
        self._cache: dict[str, DeviceHealth] = {}
        self._cache_time: float | None = None
        self._lock = Lock()

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _disabled(self, device: Device) -> DeviceHealth:
        return DeviceHealth(
            device_id=device.id,
            name=device.name,
            status="disabled",
            monitor=device.monitor,
            message="Monitoring is disabled for this device.",
            checked_at=self._now_iso(),
            reachable=None,
        )

    def _unknown(
        self,
        device: Device,
        message: str = "No health monitor is configured.",
    ) -> DeviceHealth:
        return DeviceHealth(
            device_id=device.id,
            name=device.name,
            status="unknown",
            monitor=device.monitor,
            message=message,
            checked_at=self._now_iso(),
            reachable=None,
        )

    def _prometheus(self, device: Device) -> DeviceHealth:
        job = PROMETHEUS_JOBS.get(device.id)

        if job is None:
            return self._unknown(
                device,
                "No Prometheus job mapping exists for this device.",
            )

        up = first_value(f'up{{job="{job}"}}')

        if up == 1:
            return DeviceHealth(
                device_id=device.id,
                name=device.name,
                status="online",
                monitor=device.monitor,
                message=f'Prometheus target "{job}" is reachable.',
                checked_at=self._now_iso(),
                reachable=True,
            )

        if up == 0:
            return DeviceHealth(
                device_id=device.id,
                name=device.name,
                status="offline",
                monitor=device.monitor,
                message=f'Prometheus target "{job}" is down.',
                checked_at=self._now_iso(),
                reachable=False,
            )

        return DeviceHealth(
            device_id=device.id,
            name=device.name,
            status="unknown",
            monitor=device.monitor,
            message=f'Prometheus returned no status for "{job}".',
            checked_at=self._now_iso(),
            reachable=None,
        )

    def check(self, device: Device) -> DeviceHealth:
        if not device.enabled:
            return self._disabled(device)

        if device.monitor == "none":
            return self._unknown(device)

        if device.monitor in {"prometheus", "synology-api"}:
            return self._prometheus(device)

        return self._unknown(
            device,
            f'Unsupported monitor type: "{device.monitor}".',
        )

    def _cache_is_fresh(self) -> bool:
        if self._cache_time is None:
            return False

        return (
            monotonic() - self._cache_time
            < HEALTH_CACHE_TTL_SECONDS
        )

    def check_all(
        self,
        *,
        force_refresh: bool = False,
        include_disabled: bool = False,
    ) -> list[DeviceHealth]:
        with self._lock:
            if (
                not force_refresh
                and self._cache
                and self._cache_is_fresh()
            ):
                results = list(self._cache.values())
            else:
                previous_cache = self._cache
                refreshed: dict[str, DeviceHealth] = {}

                for device in device_manager.get_all():
                    try:
                        result = self.check(device)
                    except Exception as exc:
                        previous = previous_cache.get(device.id)

                        if previous is not None:
                            result = DeviceHealth(
                                device_id=device.id,
                                name=device.name,
                                status=previous.status,
                                monitor=device.monitor,
                                message=(
                                    "Health probe failed; showing previous "
                                    f"result. {type(exc).__name__}: {exc}"
                                ),
                                checked_at=self._now_iso(),
                                reachable=previous.reachable,
                            )
                        else:
                            result = self._unknown(
                                device,
                                (
                                    "Health probe failed: "
                                    f"{type(exc).__name__}: {exc}"
                                ),
                            )

                    refreshed[device.id] = result

                self._cache = refreshed
                self._cache_time = monotonic()
                results = list(refreshed.values())

        if not include_disabled:
            results = [
                result
                for result in results
                if result.status != "disabled"
            ]

        return deepcopy(results)

    def get_status(
        self,
        device_id: str,
        *,
        force_refresh: bool = False,
    ) -> DeviceHealth | None:
        results = self.check_all(
            force_refresh=force_refresh,
            include_disabled=True,
        )

        for result in results:
            if result.device_id == device_id:
                return result

        return None

    def count_online(self) -> int:
        return sum(
            result.status == "online"
            for result in self.check_all()
        )

    def count_by_status(self) -> dict[str, int]:
        counts = {
            "online": 0,
            "offline": 0,
            "degraded": 0,
            "unknown": 0,
            "disabled": 0,
        }

        for result in self.check_all(include_disabled=True):
            counts[result.status] = counts.get(result.status, 0) + 1

        return counts

    def clear_cache(self) -> None:
        with self._lock:
            self._cache = {}
            self._cache_time = None


health_manager = HealthManager()
