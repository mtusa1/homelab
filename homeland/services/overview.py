from copy import deepcopy
from threading import Lock
from time import monotonic

from core.alert_manager import alert_manager
from core.device_manager import device_manager
from core.health_manager import health_manager
from devices.nuc import get_nuc_data
from services.discovery import discover_services


def _build_overview_uncached():
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


OVERVIEW_CACHE_TTL_SECONDS = 30.0
_overview_cache = None
_overview_cache_time = 0.0
_overview_cache_lock = Lock()


def build_overview(*, force_refresh: bool = False):
    """Return a briefly cached overview snapshot.

    The dashboard polls this endpoint frequently. Caching prevents each
    browser request from repeating all Prometheus and Docker queries.
    """
    global _overview_cache
    global _overview_cache_time

    now = monotonic()

    if (
        not force_refresh
        and _overview_cache is not None
        and now - _overview_cache_time < OVERVIEW_CACHE_TTL_SECONDS
    ):
        return deepcopy(_overview_cache)

    with _overview_cache_lock:
        now = monotonic()

        if (
            not force_refresh
            and _overview_cache is not None
            and now - _overview_cache_time < OVERVIEW_CACHE_TTL_SECONDS
        ):
            return deepcopy(_overview_cache)

        try:
            refreshed = _build_overview_uncached()
        except Exception:
            # Continue serving the previous snapshot if a temporary
            # Prometheus or Docker failure occurs.
            if _overview_cache is not None:
                return deepcopy(_overview_cache)
            raise

        _overview_cache = refreshed
        _overview_cache_time = monotonic()

        return deepcopy(_overview_cache)


def clear_overview_cache():
    global _overview_cache
    global _overview_cache_time

    with _overview_cache_lock:
        _overview_cache = None
        _overview_cache_time = 0.0
