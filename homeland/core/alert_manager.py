from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from core.health_manager import DeviceHealth


DEFAULT_CONFIG_PATH = Path("config/alerts.yml")

SEVERITY_PRIORITY = {
    "critical": 0,
    "warning": 1,
    "healthy": 2,
}


@dataclass(frozen=True)
class Alert:
    id: str
    severity: str
    category: str
    source: str
    message: str
    timestamp: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)

        # Preserve compatibility with the existing homepage/API.
        data["level"] = self.severity

        return data


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AlertManager:
    def __init__(
        self,
        config_path: Path | str = DEFAULT_CONFIG_PATH,
    ) -> None:
        self.config_path = Path(config_path)
        self._config: dict[str, Any] = {}
        self.reload_config()

    def reload_config(self) -> None:
        try:
            with self.config_path.open("r", encoding="utf-8") as file:
                loaded = yaml.safe_load(file) or {}
        except FileNotFoundError:
            loaded = {}

        if not isinstance(loaded, dict):
            raise ValueError(
                f"Alert configuration must be a mapping: "
                f"{self.config_path}"
            )

        self._config = loaded

    @staticmethod
    def _number(
        value: Any,
        default: float = 0,
    ) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _slug(value: str) -> str:
        return "".join(
            character.lower()
            if character.isalnum()
            else "-"
            for character in value
        ).strip("-")

    @staticmethod
    def _alert(
        *,
        alert_id: str,
        severity: str,
        category: str,
        source: str,
        message: str,
    ) -> Alert:
        return Alert(
            id=alert_id,
            severity=severity,
            category=category,
            source=source,
            message=message,
            timestamp=utc_now(),
        )

    def _evaluate_storage(
        self,
        filesystems: list[dict[str, Any]],
    ) -> list[Alert]:
        alerts: list[Alert] = []

        config = self._config.get("storage", {})
        warning = self._number(
            config.get("warning_percent"),
            80,
        )
        critical = self._number(
            config.get("critical_percent"),
            90,
        )

        for filesystem in filesystems:
            name = str(
                filesystem.get("name")
                or filesystem.get("mountpoint")
                or "Storage"
            )

            used_percent = self._number(
                filesystem.get("used_percent"),
            )

            severity: str | None = None

            if used_percent >= critical:
                severity = "critical"
            elif used_percent >= warning:
                severity = "warning"

            if severity is None:
                continue

            alerts.append(
                self._alert(
                    alert_id=(
                        f"storage-{self._slug(name)}-{severity}"
                    ),
                    severity=severity,
                    category="storage",
                    source=name,
                    message=(
                        f"{name} is {used_percent:.1f}% full"
                    ),
                )
            )

        return alerts

    def _evaluate_cpu(
        self,
        cpu_percent: float,
    ) -> list[Alert]:
        config = self._config.get("cpu", {})
        warning = self._number(
            config.get("warning_percent"),
            85,
        )
        critical = self._number(
            config.get("critical_percent"),
            95,
        )

        severity: str | None = None

        if cpu_percent >= critical:
            severity = "critical"
        elif cpu_percent >= warning:
            severity = "warning"

        if severity is None:
            return []

        return [
            self._alert(
                alert_id=f"cpu-nuc-{severity}",
                severity=severity,
                category="cpu",
                source="Ubuntu NUC",
                message=(
                    f"Ubuntu NUC CPU usage is "
                    f"{cpu_percent:.1f}%"
                ),
            )
        ]

    def _evaluate_memory(
        self,
        memory_percent: float | None,
    ) -> list[Alert]:
        if memory_percent is None:
            return []

        config = self._config.get("memory", {})
        warning = self._number(
            config.get("warning_percent"),
            85,
        )
        critical = self._number(
            config.get("critical_percent"),
            95,
        )

        severity: str | None = None

        if memory_percent >= critical:
            severity = "critical"
        elif memory_percent >= warning:
            severity = "warning"

        if severity is None:
            return []

        return [
            self._alert(
                alert_id=f"memory-nuc-{severity}",
                severity=severity,
                category="memory",
                source="Ubuntu NUC",
                message=(
                    f"Ubuntu NUC memory usage is "
                    f"{memory_percent:.1f}%"
                ),
            )
        ]

    def _evaluate_devices(
        self,
        device_health: list[DeviceHealth],
    ) -> list[Alert]:
        alerts: list[Alert] = []

        config = self._config.get("devices", {})
        alert_offline = bool(
            config.get("alert_when_offline", True)
        )
        alert_unknown = bool(
            config.get("alert_when_unknown", False)
        )

        for result in device_health:
            if result.status == "offline" and alert_offline:
                alerts.append(
                    self._alert(
                        alert_id=(
                            f"device-{result.device_id}-offline"
                        ),
                        severity="critical",
                        category="device",
                        source=result.name,
                        message=f"{result.name} is offline",
                    )
                )

            elif result.status == "degraded":
                alerts.append(
                    self._alert(
                        alert_id=(
                            f"device-{result.device_id}-degraded"
                        ),
                        severity="warning",
                        category="device",
                        source=result.name,
                        message=f"{result.name} is degraded",
                    )
                )

            elif result.status == "unknown" and alert_unknown:
                alerts.append(
                    self._alert(
                        alert_id=(
                            f"device-{result.device_id}-unknown"
                        ),
                        severity="warning",
                        category="device",
                        source=result.name,
                        message=(
                            f"{result.name} health is unknown"
                        ),
                    )
                )

        return alerts

    def _evaluate_docker(
        self,
        services: list[dict[str, Any]],
    ) -> list[Alert]:
        config = self._config.get("docker", {})

        if not config.get(
            "alert_when_registered_service_stopped",
            True,
        ):
            return []

        stopped_registered = [
            service
            for service in services
            if service.get("registered") is True
            and service.get("status") != "running"
        ]

        if not stopped_registered:
            return []

        service_names = sorted(
            str(
                service.get("name")
                or service.get("container_name")
                or service.get("id")
                or "Unknown service"
            )
            for service in stopped_registered
        )

        count = len(service_names)

        return [
            self._alert(
                alert_id="docker-registered-services-stopped",
                severity="warning",
                category="docker",
                source="Docker",
                message=(
                    f"{count} registered Docker "
                    f"service(s) are not running: "
                    f"{', '.join(service_names)}"
                ),
            )
        ]

    def evaluate(
        self,
        *,
        filesystems: list[dict[str, Any]],
        services: list[dict[str, Any]],
        device_health: list[DeviceHealth],
        cpu_percent: float = 0,
        memory_percent: float | None = None,
    ) -> list[Alert]:
        alerts: list[Alert] = []

        alerts.extend(
            self._evaluate_storage(filesystems)
        )
        alerts.extend(
            self._evaluate_cpu(cpu_percent)
        )
        alerts.extend(
            self._evaluate_memory(memory_percent)
        )
        alerts.extend(
            self._evaluate_devices(device_health)
        )
        alerts.extend(
            self._evaluate_docker(services)
        )

        if not alerts:
            alerts.append(
                self._alert(
                    alert_id="systems-healthy",
                    severity="healthy",
                    category="system",
                    source="Homeland",
                    message=(
                        "All monitored systems are "
                        "operating normally"
                    ),
                )
            )

        return sorted(
            alerts,
            key=lambda alert: (
                SEVERITY_PRIORITY.get(
                    alert.severity,
                    99,
                ),
                alert.category,
                alert.source,
                alert.id,
            ),
        )

    @staticmethod
    def overall_health(
        alerts: list[Alert],
    ) -> str:
        severities = {
            alert.severity
            for alert in alerts
        }

        if "critical" in severities:
            return "critical"

        if "warning" in severities:
            return "warning"

        return "healthy"

    @staticmethod
    def as_dicts(
        alerts: list[Alert],
    ) -> list[dict[str, Any]]:
        return [
            alert.to_dict()
            for alert in alerts
        ]


alert_manager = AlertManager()
