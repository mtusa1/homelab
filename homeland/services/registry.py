from __future__ import annotations

from services.models import Service


SERVICES = {
    "inventory-api": Service(
        container="inventory-api",
        title="Homeland",
        description="Mission Control",
        category="Core",
        icon="🏠",
        url="/",
    ),
    "jellyfin": Service(
        container="jellyfin",
        title="Jellyfin",
        description="Movies, television, and media",
        category="Media",
        icon="🎬",
        url="http://nuc-ubuntu:8096",
    ),
    "kavita": Service(
        container="kavita",
        title="Kavita",
        description="Comics, manga, and books",
        category="Media",
        icon="📚",
        url="http://nuc-ubuntu:5000",
    ),
    "immich_server": Service(
        container="immich_server",
        title="Immich",
        description="Photo and video library",
        category="Media",
        icon="📸",
        url="http://nuc-ubuntu:2283",
    ),
    "grafana": Service(
        container="grafana",
        title="Grafana",
        description="Monitoring dashboards",
        category="Monitoring",
        icon="📊",
        url="http://nuc-ubuntu:3000",
    ),
    "prometheus": Service(
        container="prometheus",
        title="Prometheus",
        description="Metrics collection",
        category="Monitoring",
        icon="📈",
        url="http://nuc-ubuntu:9090",
    ),
    "uptime-kuma": Service(
        container="uptime-kuma",
        title="Uptime Kuma",
        description="Service uptime monitoring",
        category="Monitoring",
        icon="🟢",
        url="http://nuc-ubuntu:3001",
    ),
    "portainer": Service(
        container="portainer",
        title="Portainer",
        description="Docker administration",
        category="Infrastructure",
        icon="🐳",
        url="https://nuc-ubuntu:9443",
    ),
}


def get_service(container_name: str) -> Service | None:
    return SERVICES.get(container_name)
