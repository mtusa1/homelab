from __future__ import annotations

import docker


def get_docker_client():
    return docker.from_env()


def get_containers():
    client = get_docker_client()
    containers = client.containers.list(all=True)

    return [
        {
            "id": container.short_id,
            "name": container.name,
            "image": container.image.tags[0] if container.image.tags else "unknown",
            "status": container.status,
        }
        for container in containers
    ]
