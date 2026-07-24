from __future__ import annotations

from core.service_manager import service_manager

SERVICES = service_manager.load()


def get_service(container_name: str):
    return SERVICES.get(container_name)
