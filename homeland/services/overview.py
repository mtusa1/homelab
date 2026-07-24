from services.discovery import discover_services
from devices.nuc import get_nuc_data
from core.device_manager import device_manager


def build_overview():
    nuc = get_nuc_data()
    services = discover_services()

    running_services = [
        service
        for service in services
        if service.get("status") == "running"
    ]

    registered_services = [
        service
        for service in services
        if service.get("registered") is True
    ]

    filesystems = (
        nuc
        .get("storage", {})
        .get("filesystems", [])
    )

    total_storage_bytes = sum(
        filesystem.get("total_bytes", 0)
        for filesystem in filesystems
    )

    used_storage_bytes = sum(
        filesystem.get("used_bytes", 0)
        for filesystem in filesystems
    )

    storage_percent = (
        round(
            used_storage_bytes
            / total_storage_bytes
            * 100,
            1,
        )
        if total_storage_bytes
        else 0
    )

    cpu_percent = (
        nuc
        .get("cpu", {})
        .get("used_percent", 0)
    )

    alerts = []

    for filesystem in filesystems:
        used_percent = filesystem.get("used_percent", 0)

        if used_percent >= 90:
            alerts.append(
                {
                    "level": "critical",
                    "message": (
                        f'{filesystem.get("name", "Storage")} '
                        f'is {used_percent}% full'
                    ),
                }
            )
        elif used_percent >= 80:
            alerts.append(
                {
                    "level": "warning",
                    "message": (
                        f'{filesystem.get("name", "Storage")} '
                        f'is {used_percent}% full'
                    ),
                }
            )

    stopped_services = [
        service
        for service in services
        if service.get("status") != "running"
    ]

    if stopped_services:
        alerts.append(
            {
                "level": "warning",
                "message": (
                    f"{len(stopped_services)} Docker "
                    "container(s) are not running"
                ),
            }
        )

    if not alerts:
        alerts.append(
            {
                "level": "healthy",
                "message": "All monitored systems are operating normally",
            }
        )

    health = "healthy"

    if any(
        alert.get("level") == "critical"
        for alert in alerts
    ):
        health = "critical"
    elif any(
        alert.get("level") == "warning"
        for alert in alerts
    ):
        health = "warning"

    return {
        "health": health,
        "devices": {
            "online": len(
                [
                    device
                    for device in device_manager.get_enabled()
                    if device.monitor != "none"
                ]
            ),
            "total": device_manager.count_total(),
        },
        "docker": {
            "running": len(running_services),
            "total": len(services),
            "registered": len(registered_services),
        },
        "storage": {
            "total_bytes": total_storage_bytes,
            "used_bytes": used_storage_bytes,
            "used_percent": storage_percent,
        },
        "cpu": {
            "average_percent": cpu_percent,
        },
        "alerts": alerts,
    }
