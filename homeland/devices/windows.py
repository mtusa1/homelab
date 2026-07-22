from services.prometheus import (
    first_value,
    format_bytes,
    format_uptime,
    query_vector,
)


WINDOWS_DEVICES = {
    "main-desktop": {
        "job": "windows-main-desktop",
        "name": "Main Desktop",
        "description": "Primary Windows Workstation",
    },
    "windows-workstation": {
        "job": "windows-workstation",
        "name": "Windows Workstation",
        "description": "Secondary RTX 3070 Workstation",
    },
}


def get_windows_drives(job):
    """
    Discover all normal Windows drive-letter volumes.

    Recovery/system volumes such as HarddiskVolume1 are excluded because
    only volume labels ending in ':' are accepted.
    """
    size_results = query_vector(
        f'windows_logical_disk_size_bytes{{job="{job}"}}'
    )

    free_results = query_vector(
        f'windows_logical_disk_free_bytes{{job="{job}"}}'
    )

    sizes_by_volume = {}
    free_by_volume = {}

    for result in size_results:
        metric = result.get("metric", {})
        volume = metric.get("volume")
        value = result.get("value")

        if (
            isinstance(volume, str)
            and volume.endswith(":")
            and value is not None
            and value > 0
        ):
            sizes_by_volume[volume] = value

    for result in free_results:
        metric = result.get("metric", {})
        volume = metric.get("volume")
        value = result.get("value")

        if (
            isinstance(volume, str)
            and volume.endswith(":")
            and value is not None
            and value >= 0
        ):
            free_by_volume[volume] = value

    drives = []

    for volume in sorted(sizes_by_volume):
        total_bytes = sizes_by_volume[volume]
        free_bytes = free_by_volume.get(volume)

        if free_bytes is None:
            continue

        free_bytes = max(0.0, min(free_bytes, total_bytes))
        used_bytes = max(0.0, total_bytes - free_bytes)

        used_percent = (
            used_bytes / total_bytes * 100.0
            if total_bytes > 0
            else None
        )

        drives.append(
            {
                "letter": volume,
                "total_bytes": round(total_bytes),
                "free_bytes": round(free_bytes),
                "used_bytes": round(used_bytes),
                "total_display": format_bytes(total_bytes),
                "free_display": format_bytes(free_bytes),
                "used_display": format_bytes(used_bytes),
                "used_percent": (
                    round(used_percent, 1)
                    if used_percent is not None
                    else None
                ),
                "display": (
                    f"{format_bytes(free_bytes)} free of "
                    f"{format_bytes(total_bytes)}"
                ),
            }
        )

    return drives


def get_windows_data(device_id):
    device = WINDOWS_DEVICES.get(device_id)

    if device is None:
        return None

    job = device["job"]

    up = first_value(f'up{{job="{job}"}}')

    cpu_idle = first_value(
        f'avg(rate(windows_cpu_time_total{{job="{job}",mode="idle"}}[5m]))'
    )

    cpu_percent = (
        None
        if cpu_idle is None
        else max(
            0.0,
            min(100.0, (1.0 - cpu_idle) * 100.0),
        )
    )

    memory_available = first_value(
        f'windows_memory_available_bytes{{job="{job}"}}'
    )

    memory_total = first_value(
        f'windows_memory_physical_total_bytes{{job="{job}"}}'
    )

    memory_used_gib = None
    memory_total_gib = None
    memory_percent = None
    memory_display = "Unknown"

    if (
        memory_total is not None
        and memory_available is not None
        and memory_total > 0
    ):
        memory_used = max(
            0.0,
            memory_total - memory_available,
        )

        memory_used_gib = memory_used / (1024**3)
        memory_total_gib = memory_total / (1024**3)
        memory_percent = memory_used / memory_total * 100.0

        memory_display = (
            f"{memory_used_gib:.1f} / "
            f"{memory_total_gib:.1f} GiB"
        )

    uptime_seconds = first_value(
        f'time() - windows_system_boot_time_timestamp{{job="{job}"}}'
    )

    drives = get_windows_drives(job)

    c_drive = next(
        (
            drive
            for drive in drives
            if drive["letter"] == "C:"
        ),
        None,
    )

    return {
        "device": device["name"],
        "description": device["description"],
        "status": "Online" if up == 1 else "Offline",
        "cpu": {
            "percent": (
                round(cpu_percent, 1)
                if cpu_percent is not None
                else None
            ),
            "display": (
                f"{cpu_percent:.1f}%"
                if cpu_percent is not None
                else "Unknown"
            ),
        },
        "memory": {
            "used_gib": (
                round(memory_used_gib, 1)
                if memory_used_gib is not None
                else None
            ),
            "total_gib": (
                round(memory_total_gib, 1)
                if memory_total_gib is not None
                else None
            ),
            "percent": (
                round(memory_percent, 1)
                if memory_percent is not None
                else None
            ),
            "display": memory_display,
        },
        "uptime": {
            "seconds": (
                round(uptime_seconds)
                if uptime_seconds is not None
                else None
            ),
            "display": format_uptime(uptime_seconds),
        },
        "drives": drives,

        # Temporary backward-compatible field for the current frontend.
        # This will be removed after the dynamic storage UI is installed.
        "disk_free": (
            c_drive["free_display"]
            if c_drive is not None
            else "Unknown"
        ),
    }
