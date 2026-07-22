from __future__ import annotations

import docker

from services.registry import get_service


def discover_services():
    client = docker.from_env()

    discovered = []

    for container in client.containers.list(all=True):
        service = get_service(container.name)

        if service is None:
            discovered.append({
                "container": container.name,
                "title": container.name,
                "description": "Unknown service",
                "category": "Other",
                "icon": "📦",
                "status": container.status,
                "image": (
                    container.image.tags[0]
                    if container.image.tags
                    else "unknown"
                ),
                "url": None,
                "registered": False,
            })
        else:
            item = service.to_dict()
            item["status"] = container.status
            item["image"] = (
                container.image.tags[0]
                if container.image.tags
                else "unknown"
            )
            item["registered"] = True
            discovered.append(item)

    return sorted(
        discovered,
        key=lambda x: (x["category"], x["title"].lower()),
    )
