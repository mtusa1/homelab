"""Compatibility loader for the structured Phase 2 Overview patch."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


PACKAGE_ROOT = Path(__file__).with_suffix("")
MANIFEST_PATH = PACKAGE_ROOT / "manifest.json"
FEATURE_PATH = PACKAGE_ROOT / "feature.py"

_manifest = json.loads(MANIFEST_PATH.read_text())

DESCRIPTION = _manifest["description"]
VERSION = _manifest["version"]

_spec = importlib.util.spec_from_file_location(
    "homeland_phase2_overview_feature",
    FEATURE_PATH,
)

if _spec is None or _spec.loader is None:
    raise RuntimeError(
        "Unable to load structured phase2_overview feature."
    )

_feature = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_feature)

install = _feature.install
uninstall = _feature.uninstall
