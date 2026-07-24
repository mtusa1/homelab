from __future__ import annotations

from copy import deepcopy
from threading import Lock
from time import monotonic

import docker
from docker.errors import DockerException

from services.registry import get_service


DISCOVERY_CACHE_TTL_SECONDS = 60

_cache_lock = Lock()
_cache_timestamp = 0.0
_cache_data: list[dict] | None = None
_docker_client = None


def _get_docker_client():
    global _docker_client

    if _docker_client is None:
        _docker_client = docker.from_env()

    return _docker_client


def _scan_services() -> list[dict]:
    client = _get_docker_client()
    discovered = []

    for container in client.containers.list(all=True):
        service = get_service(container.name)

        image_tags = container.image.tags
        image = image_tags[0] if image_tags else "unknown"

        if service is None:
            discovered.append(
                {
                    "container": container.name,
                    "title": container.name,
                    "description": "Unknown service",
                    "category": "Other",
                    "icon": "📦",
                    "status": container.status,
                    "image": image,
                    "url": None,
                    "registered": False,
                }
            )
        else:
            item = service.to_dict()
            item["status"] = container.status
            item["image"] = image
            item["registered"] = True
            discovered.append(item)

    return sorted(
        discovered,
        key=lambda item: (
            item["category"],
            item["title"].lower(),
        ),
    )


def discover_services(
    *,
    force_refresh: bool = False,
) -> list[dict]:
    """
    Return Docker service information.

    Results are cached briefly because querying the Docker daemon can be
    expensive on a heavily loaded host. A deep copy is returned so callers
    cannot modify the cached result.
    """
    global _cache_data
    global _cache_timestamp

    now = monotonic()

    if (
        not force_refresh
        and _cache_data is not None
        and now - _cache_timestamp < DISCOVERY_CACHE_TTL_SECONDS
    ):
        return deepcopy(_cache_data)

    with _cache_lock:
        now = monotonic()

        # Another request may have refreshed the cache while this request
        # waited for the lock.
        if (
            not force_refresh
            and _cache_data is not None
            and now - _cache_timestamp < DISCOVERY_CACHE_TTL_SECONDS
        ):
            return deepcopy(_cache_data)

        try:
            discovered = _scan_services()
        except DockerException:
            # If Docker temporarily fails but previous data exists, serve the
            # stale data rather than failing the entire Homeland dashboard.
            if _cache_data is not None:
                return deepcopy(_cache_data)

            raise

        _cache_data = discovered
        _cache_timestamp = monotonic()

        return deepcopy(_cache_data)


def clear_discovery_cache() -> None:
    """Clear the service-discovery cache."""
    global _cache_data
    global _cache_timestamp

    with _cache_lock:
        _cache_data = None
        _cache_timestamp = 0.0
