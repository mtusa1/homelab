from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from core.config import config
from core.device_manager import device_manager
from services.prometheus import first_value, format_bytes, format_uptime


@dataclass(frozen=True)
class LinuxFilesystem:
    name: str
    mountpoint: str


def _selector(job: str, extra: str = "") -> str:
    labels = [f'job="{job}"']

    if extra:
        labels.append(extra)

    return "{" + ",".join(labels) + "}"


def get_filesystem_data(
    *,
    job: str,
    name: str,
    mountpoint: str,
) -> dict[str, Any]:
    selector = _selector(
        job,
        (
            f'mountpoint="{mountpoint}",'
            'fstype!~"tmpfs|devtmpfs|overlay|squashfs"'
        ),
    )

    total = first_value(
        f"node_filesystem_size_bytes{selector}"
    )
    available = first_value(
        f"node_filesystem_avail_bytes{selector}"
    )

    used = None
    used_percent = None

    if total is not None and available is not None:
        used = max(0.0, total - available)

        if total > 0:
            used_percent = used / total * 100.0

    return {
        "name": name,
        "mountpoint": mountpoint,
        "used_bytes": used,
        "total_bytes": total,
        "available_bytes": available,
        "used_percent": (
            round(used_percent, 1)
            if used_percent is not None
            else None
        ),
        "used": format_bytes(used),
        "total": format_bytes(total),
        "available": format_bytes(available),
    }


def get_linux_data(
    *,
    job: str,
    filesystems: Iterable[LinuxFilesystem],
    container_job: str | None = None,
) -> dict[str, Any]:
    cpu_idle = first_value(
        (
            "avg(rate("
            f'node_cpu_seconds_total{{job="{job}",mode="idle"}}[5m]'
            "))"
        )
    )

    cpu_percent = (
        None
        if cpu_idle is None
        else max(
            0.0,
            min(100.0, (1.0 - cpu_idle) * 100.0),
        )
    )

    memory_total = first_value(
        f'node_memory_MemTotal_bytes{{job="{job}"}}'
    )
    memory_available = first_value(
        f'node_memory_MemAvailable_bytes{{job="{job}"}}'
    )

    memory_used = None
    memory_percent = None
    memory_text = "Unknown"

    if memory_total is not None and memory_available is not None:
        memory_used = max(
            0.0,
            memory_total - memory_available,
        )

        if memory_total > 0:
            memory_percent = (
                memory_used
                / memory_total
                * 100.0
            )

        memory_text = (
            f"{memory_used / (1024**3):.1f} / "
            f"{memory_total / (1024**3):.1f} GiB"
        )

    uptime = first_value(
        f'time() - node_boot_time_seconds{{job="{job}"}}'
    )

    load_1m = first_value(
        f'node_load1{{job="{job}"}}'
    )
    load_5m = first_value(
        f'node_load5{{job="{job}"}}'
    )
    load_15m = first_value(
        f'node_load15{{job="{job}"}}'
    )

    containers = None

    if container_job:
        containers = first_value(
            (
                "count("
                "container_last_seen"
                f'{{job="{container_job}",name!=""}}'
                ")"
            )
        )

    filesystem_data = [
        get_filesystem_data(
            job=job,
            name=filesystem.name,
            mountpoint=filesystem.mountpoint,
        )
        for filesystem in filesystems
    ]

    status = "Online" if cpu_idle is not None else "Unknown"

    return {
        "summary": {
            "status": status,
            "cpu": (
                f"{cpu_percent:.1f}%"
                if cpu_percent is not None
                else "Unknown"
            ),
            "memory": memory_text,
            "containers": (
                f"{int(containers)} detected"
                if containers is not None
                else "Unknown"
            ),
            "uptime": format_uptime(uptime),
        },
        "cpu": {
            "used_percent": (
                round(cpu_percent, 1)
                if cpu_percent is not None
                else None
            ),
            "display": (
                f"{cpu_percent:.1f}%"
                if cpu_percent is not None
                else "Unknown"
            ),
            "load_1m": (
                round(load_1m, 2)
                if load_1m is not None
                else None
            ),
            "load_5m": (
                round(load_5m, 2)
                if load_5m is not None
                else None
            ),
            "load_15m": (
                round(load_15m, 2)
                if load_15m is not None
                else None
            ),
        },
        "memory": {
            "display": memory_text,
            "used_bytes": memory_used,
            "total_bytes": memory_total,
            "used_percent": (
                round(memory_percent, 1)
                if memory_percent is not None
                else None
            ),
        },
        "storage": {
            "filesystems": filesystem_data,
        },
        "docker": {
            "containers_detected": (
                int(containers)
                if containers is not None
                else None
            ),
        },
        "uptime": format_uptime(uptime),
    }


def get_linux_device_config(
    device_id: str,
) -> dict[str, Any] | None:
    """
    Return the approved Linux configuration for a registered device.

    Prometheus job names are read only from devices.yml and are never
    accepted directly from a URL.
    """
    device = device_manager.get(device_id)

    if device is None or not device.enabled:
        return None

    raw_devices = config.load("devices")
    raw_device = raw_devices.get(device_id, {})
    linux_config = raw_device.get("linux")

    if not isinstance(linux_config, dict):
        return None

    prometheus_job = linux_config.get("prometheus_job")

    if not prometheus_job:
        return None

    raw_filesystems = linux_config.get("filesystems", [])

    filesystems = []

    for filesystem in raw_filesystems:
        if not isinstance(filesystem, dict):
            continue

        name = filesystem.get("name")
        mountpoint = filesystem.get("mountpoint")

        if not name or not mountpoint:
            continue

        filesystems.append(
            LinuxFilesystem(
                name=str(name),
                mountpoint=str(mountpoint),
            )
        )

    return {
        "device": device,
        "description": linux_config.get(
            "description",
            "Linux Server",
        ),
        "prometheus_job": str(prometheus_job),
        "container_job": (
            str(linux_config["container_job"])
            if linux_config.get("container_job")
            else None
        ),
        "filesystems": tuple(filesystems),
    }


def get_linux_device_data(
    device_id: str,
) -> dict[str, Any] | None:
    linux_config = get_linux_device_config(device_id)

    if linux_config is None:
        return None

    return get_linux_data(
        job=linux_config["prometheus_job"],
        filesystems=linux_config["filesystems"],
        container_job=linux_config["container_job"],
    )
