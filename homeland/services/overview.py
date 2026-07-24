from core.alert_manager import alert_manager
from core.device_manager import device_manager
from core.health_manager import health_manager
from devices.nuc import get_nuc_data
from services.discovery import discover_services


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

    memory_data = nuc.get("memory", {})

    memory_percent = memory_data.get("used_percent")

    if memory_percent is None:
        memory_percent = memory_data.get("percent")

    device_health = health_manager.check_all(
        include_disabled=True,
    )

    alerts = alert_manager.evaluate(
        filesystems=filesystems,
        services=services,
        device_health=device_health,
        cpu_percent=cpu_percent,
        memory_percent=memory_percent,
    )

    return {
        "health": alert_manager.overall_health(alerts),
        "devices": {
            "online": sum(
                result.status == "online"
                for result in device_health
            ),
            "total": device_manager.count_total(),
            "statuses": {
                status: sum(
                    result.status == status
                    for result in device_health
                )
                for status in (
                    "online",
                    "offline",
                    "degraded",
                    "unknown",
                    "disabled",
                )
            },
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
        "alerts": alert_manager.as_dicts(alerts),
    }
