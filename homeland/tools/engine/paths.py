"""Central filesystem paths used by the Homeland Development Kit."""

from pathlib import Path


TOOLS_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOLS_ROOT.parent

ENGINE_ROOT = TOOLS_ROOT / "engine"
PATCH_ROOT = TOOLS_ROOT / "patches"
BACKUP_ROOT = PROJECT_ROOT / "backups"

CONFIG_PATH = TOOLS_ROOT / "config.json"
REGISTRY_PATH = TOOLS_ROOT / "installed.json"
COMPOSE_PATH = PROJECT_ROOT / "compose.yml"


def ensure_hdk_directories() -> None:
    """Create directories required by the HDK."""

    PATCH_ROOT.mkdir(parents=True, exist_ok=True)
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
