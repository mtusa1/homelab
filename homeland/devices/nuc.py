from services.prometheus import first_value, format_uptime

def get_filesystem_data(name, mountpoint):
    total = first_value(
        f'node_filesystem_size_bytes{{job="nuc",mountpoint="{mountpoint}",fstype!~"tmpfs|overlay"}}'
    )

    available = first_value(
        f'node_filesystem_avail_bytes{{job="nuc",mountpoint="{mountpoint}",fstype!~"tmpfs|overlay"}}'
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

def get_nuc_data():
    cpu_idle = first_value(
        'avg(rate(node_cpu_seconds_total{job="nuc",mode="idle"}[5m]))'
    )

    cpu_percent = (
        None
        if cpu_idle is None
        else max(0.0, min(100.0, (1.0 - cpu_idle) * 100.0))
    )

    memory_total = first_value(
        'node_memory_MemTotal_bytes{job="nuc"}'
    )

    memory_available = first_value(
        'node_memory_MemAvailable_bytes{job="nuc"}'
    )

    memory_used = None
    memory_percent = None
    memory_text = "Unknown"

    if memory_total is not None and memory_available is not None:
        memory_used = max(0.0, memory_total - memory_available)

        if memory_total > 0:
            memory_percent = memory_used / memory_total * 100.0

        memory_text = (
            f"{memory_used / (1024**3):.1f} / "
            f"{memory_total / (1024**3):.1f} GiB"
        )

    uptime = first_value(
        'time() - node_boot_time_seconds{job="nuc"}'
    )

    containers = first_value(
        'count(container_last_seen{name!=""})'
    )

    load_1m = first_value(
        'node_load1{job="nuc"}'
    )

    load_5m = first_value(
        'node_load5{job="nuc"}'
    )

    load_15m = first_value(
        'node_load15{job="nuc"}'
    )

    filesystems = [
        get_filesystem_data("Ubuntu Root", "/"),
        get_filesystem_data("Media", "/media/tusa/Media"),
        get_filesystem_data("Storage", "/media/tusa/Storage"),
        get_filesystem_data("Data", "/media/tusa/Data"),
    ]

    return {
        "summary": {
            "status": "Online",
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
            "filesystems": filesystems,
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


def format_bytes(value):
    if value is None:
        return "Unknown"

    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    size = float(value)

    for unit in units:
        if abs(size) < 1024.0 or unit == units[-1]:
            return f"{size:.1f} {unit}"

        size /= 1024.0

    return "Unknown"
