from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Alert:
    id: str
    severity: str
    category: str
    source: str
    message: str
    timestamp: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AlertManager:
    def __init__(self):
        self._alerts: list[Alert] = []

    def clear(self):
        self._alerts.clear()

    def add(
        self,
        *,
        alert_id: str,
        severity: str,
        category: str,
        source: str,
        message: str,
    ):
        self._alerts.append(
            Alert(
                id=alert_id,
                severity=severity,
                category=category,
                source=source,
                message=message,
                timestamp=utc_now(),
            )
        )

    def all(self) -> list[Alert]:
        return list(self._alerts)

    def as_dicts(self):
        return [a.to_dict() for a in self._alerts]


alert_manager = AlertManager()
