from __future__ import annotations

from devices.linux import get_linux_device_data


def get_nuc_data() -> dict:
    """
    Backward-compatible NUC collector.

    New code should use get_linux_device_data("nuc").
    """
    data = get_linux_device_data("nuc")

    if data is None:
        return {
            "summary": {
                "status": "Unknown",
                "cpu": "Unknown",
                "memory": "Unknown",
                "containers": "Unknown",
                "uptime": "Unknown",
            },
            "cpu": {
                "used_percent": None,
                "display": "Unknown",
                "load_1m": None,
                "load_5m": None,
                "load_15m": None,
            },
            "memory": {
                "display": "Unknown",
                "used_bytes": None,
                "total_bytes": None,
                "used_percent": None,
            },
            "storage": {
                "filesystems": [],
            },
            "docker": {
                "containers_detected": None,
            },
            "uptime": "Unknown",
        }

    return data
