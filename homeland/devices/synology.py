from __future__ import annotations

from typing import Any

from services.prometheus import (
    first_value,
    format_bytes,
    format_uptime,
    query,
    values,
)


JOB = "synology-snmp"
VOLUME_NAME = "Volume 1"


def _metric(name: str, extra_labels: str = "") -> str:
    labels = f'job="{JOB}"'

    if extra_labels:
        labels = f"{labels},{extra_labels}"

    return f"{name}{{{labels}}}"


def _status_text(value: float | None) -> str:
    if value is None:
        return "Unknown"

    return "Healthy" if value == 1 else f"Warning ({int(value)})"


def _temperature_text(value: float | None) -> str:
    if value is None:
        return "Unknown"

    return f"{value:.0f} °C"


def get_summary() -> dict[str, Any]:
    online = first_value(_metric("up"))
    uptime_ticks = first_value(_metric("sysUpTime"))
    temperature = first_value(_metric("temperature"))

    raid_status = first_value(
        _metric("raidStatus", f'raidName="{VOLUME_NAME}"')
    )
    raid_total = first_value(
        _metric("raidTotalSize", f'raidName="{VOLUME_NAME}"')
    )
    raid_free = first_value(
        _metric("raidFreeSize", f'raidName="{VOLUME_NAME}"')
    )

    disk_temperatures = [
        float(value)
        for value in values(_metric("diskTemperature"))
        if value is not None
    ]

    uptime_seconds = (
        uptime_ticks / 100
        if uptime_ticks is not None
        else None
    )

    storage_used_percent = None

    if (
        raid_total is not None
        and raid_free is not None
        and raid_total > 0
    ):
        storage_used_percent = (
            (raid_total - raid_free) / raid_total
        ) * 100

    max_disk_temperature = (
        max(disk_temperatures)
        if disk_temperatures
        else None
    )

    return {
        "status": "Online" if online == 1 else "Offline",
        "health": _status_text(raid_status),
        "uptime": format_uptime(uptime_seconds),
        "temperature": _temperature_text(temperature),
        "disk_temperature": _temperature_text(
            max_disk_temperature
        ),
        "storage": (
            f"{storage_used_percent:.1f}% used"
            if storage_used_percent is not None
            else "Unknown"
        ),
        "raid": _status_text(raid_status),
    }


def get_storage() -> dict[str, Any]:
    total = first_value(
        _metric("raidTotalSize", f'raidName="{VOLUME_NAME}"')
    )
    free = first_value(
        _metric("raidFreeSize", f'raidName="{VOLUME_NAME}"')
    )
    status = first_value(
        _metric("raidStatus", f'raidName="{VOLUME_NAME}"')
    )
    hot_spares = first_value(
        _metric("raidHotspareCnt", f'raidName="{VOLUME_NAME}"')
    )

    used = None
    used_percent = None

    if total is not None and free is not None:
        used = max(0.0, total - free)

        if total > 0:
            used_percent = used / total * 100

    return {
        "name": VOLUME_NAME,
        "status": _status_text(status),
        "total_bytes": total,
        "used_bytes": used,
        "free_bytes": free,
        "total": format_bytes(total),
        "used": format_bytes(used),
        "free": format_bytes(free),
        "used_percent": (
            round(used_percent, 1)
            if used_percent is not None
            else None
        ),
        "hot_spares": (
            int(hot_spares)
            if hot_spares is not None
            else None
        ),
    }


def get_disks() -> list[dict[str, Any]]:
    disk_metrics: dict[str, dict[str, Any]] = {}

    metric_definitions = {
        "diskModel": "model",
        "diskType": "type",
        "diskStatus": "status_code",
        "diskHealthStatus": "health_code",
        "diskTemperature": "temperature",
        "diskBadSector": "bad_sectors",
        "diskRemainLife": "remaining_life",
        "diskRetry": "retries",
        "diskIdentifyFail": "identify_failures",
    }

    for metric_name, field_name in metric_definitions.items():
        for result in query(_metric(metric_name)):
            labels = result.get("metric", {})
            disk_id = labels.get("diskID")

            if not disk_id:
                continue

            disk = disk_metrics.setdefault(
                disk_id,
                {"disk_id": disk_id},
            )

            if field_name in {"model", "type"}:
                disk[field_name] = labels.get(metric_name, "Unknown")
                continue

            try:
                disk[field_name] = float(result["value"][1])
            except (KeyError, IndexError, TypeError, ValueError):
                disk[field_name] = None

    disks = []

    for index, disk_id in enumerate(sorted(disk_metrics), start=1):
        disk = disk_metrics[disk_id]

        status_code = disk.get("status_code")
        health_code = disk.get("health_code")
        remaining_life = disk.get("remaining_life")

        disks.append(
            {
                "name": f"Drive {index}",
                "disk_id": disk_id,
                "model": disk.get("model", "Unknown"),
                "type": disk.get("type", "Unknown"),
                "status": _status_text(status_code),
                "health": _status_text(health_code),
                "temperature": _temperature_text(
                    disk.get("temperature")
                ),
                "temperature_c": disk.get("temperature"),
                "bad_sectors": int(
                    disk.get("bad_sectors") or 0
                ),
                "retries": int(disk.get("retries") or 0),
                "identify_failures": int(
                    disk.get("identify_failures") or 0
                ),
                "remaining_life": (
                    None
                    if remaining_life is None
                    or remaining_life < 0
                    else remaining_life
                ),
            }
        )

    return disks


def get_details() -> dict[str, Any]:
    return {
        "summary": get_summary(),
        "storage": get_storage(),
        "disks": get_disks(),
    }
