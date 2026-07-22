"""Manifest loading for Homeland modules."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .paths import PATCH_ROOT


@dataclass
class Manifest:
    name: str
    display_name: str
    version: str
    description: str
    author: str = ""
    category: str = "General"
    dependencies: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    requires_restart: bool = False

    @classmethod
    def load(cls, package_root: Path):
        manifest_path = package_root / "manifest.json"

        if not manifest_path.exists():
            raise FileNotFoundError(manifest_path)

        data = json.loads(manifest_path.read_text())

        return cls(
            name=data["name"],
            display_name=data.get("display_name", data["name"]),
            version=data["version"],
            description=data.get("description", ""),
            author=data.get("author", ""),
            category=data.get("category", "General"),
            dependencies=data.get("dependencies", []),
            conflicts=data.get("conflicts", []),
            requires_restart=data.get("requires_restart", False),
        )


def discover():
    manifests = []

    if not PATCH_ROOT.exists():
        return manifests

    for directory in sorted(PATCH_ROOT.iterdir()):
        if not directory.is_dir():
            continue

        if not (directory / "manifest.json").exists():
            continue

        manifests.append(Manifest.load(directory))

    return manifests
