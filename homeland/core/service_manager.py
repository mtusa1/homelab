from __future__ import annotations

from services.models import Service
from core.config import config


class ServiceManager:
    """
    Loads service definitions from config/services.yml
    and returns Service dataclass instances.
    """

    def __init__(self):
        self._services = None

    def load(self):
        if self._services is not None:
            return self._services

        raw = config.load("services")

        services = {}

        for key, entry in raw.items():
            services[key] = Service(
                container=entry["container"],
                title=entry["title"],
                description=entry["description"],
                category=entry["category"],
                icon=entry.get("icon", "📦"),
                url=entry.get("url"),
                homepage=entry.get("homepage", True),
            )

        self._services = services
        return services


service_manager = ServiceManager()

