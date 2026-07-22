from __future__ import annotations

import docker

from services.service_registry import SERVICES


def get_docker_client():
    return docker.from_env()


def get_containers():
    client = get_docker_client()
    containers = client.containers.list(all=True)

    results = []

    for container in containers:
        registry = SERVICES.get(container.name, {})

        results.append(
            {
                "id": container.short_id,
                "name": container.name,
                "image": (
                    container.image.tags[0]
                    if container.image.tags
                    else "unknown"
                ),
                "status": container.status,
                "title": registry.get("title", container.name),
                "description": registry.get(
                    "description",
                    "Docker container",
                ),
                "icon": registry.get("icon", "📦"),
                "category": registry.get("category", "Other"),
                "url": registry.get("url"),
            }
        )

    return sorted(
        results,
        key=lambda item: (
            item["category"],
            item["title"].lower(),
        ),
    )
