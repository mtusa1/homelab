"""Installed Homeland module registry."""

from __future__ import annotations

import json
from pathlib import Path

from .paths import REGISTRY_PATH


DEFAULT_REGISTRY = {
    "hdk_version": "0.2.0",
    "modules": {}
}


class Registry:
    def __init__(self):
        self.path = REGISTRY_PATH

        if self.path.exists():
            self.data = json.loads(self.path.read_text())
        else:
            self.data = DEFAULT_REGISTRY.copy()

    def save(self):
        self.path.write_text(
            json.dumps(self.data, indent=2) + "\n"
        )

    def modules(self):
        return self.data["modules"]

    def is_installed(self, name):
        return name in self.modules()

    def install(self, name, version):
        self.modules()[name] = {
            "version": version
        }
        self.save()

    def uninstall(self, name):
        self.modules().pop(name, None)
        self.save()
