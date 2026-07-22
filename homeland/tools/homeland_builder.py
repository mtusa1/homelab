#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_ROOT = PROJECT_ROOT / "tools"
PATCH_ROOT = TOOLS_ROOT / "patches"
BACKUP_ROOT = PROJECT_ROOT / "backups"
STATE_FILE = TOOLS_ROOT / "installed_patches.json"
HOMELAND_URL = "http://localhost:8088/"

IMPORTANT_PATHS = [
    "app.py",
    "templates",
    "static",
    "devices",
    "services",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
]


def heading(message: str) -> None:
    print(f"\n===== {message.upper()} =====")


def run(command: list[str], check: bool = True):
    print("$", " ".join(command))
    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        check=check,
    )


def find_compose_file() -> Path | None:
    for name in (
        "docker-compose.yml",
        "docker-compose.yaml",
        "compose.yml",
        "compose.yaml",
    ):
        path = PROJECT_ROOT / name
        if path.exists():
            return path

    return None


def check_project() -> bool:
    heading("Project check")

    required = [
        PROJECT_ROOT / "app.py",
        PROJECT_ROOT / "templates",
        PROJECT_ROOT / "static",
        PATCH_ROOT,
    ]

    missing = [
        str(path.relative_to(PROJECT_ROOT))
        for path in required
        if not path.exists()
    ]

    if missing:
        for item in missing:
            print(f"Missing: {item}")
        return False

    compose = find_compose_file()

    if compose is None:
        print("Compose file: NOT FOUND")
        return False

    print(f"Project root: {PROJECT_ROOT}")
    print(f"Compose file: {compose.name}")
    print("Project structure: OK")
    return True


def create_backup(label: str = "manual") -> Path:
    heading("Creating backup")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    destination = BACKUP_ROOT / f"{timestamp}-{label}"
    destination.mkdir(parents=True, exist_ok=False)

    for relative_name in IMPORTANT_PATHS:
        source = PROJECT_ROOT / relative_name

        if not source.exists():
            continue

        target = destination / relative_name

        if source.is_dir():
            shutil.copytree(
                source,
                target,
                ignore=shutil.ignore_patterns(
                    "__pycache__",
                    "*.pyc",
                ),
            )
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

        print(f"Backed up: {relative_name}")

    print(f"Backup created: {destination}")
    return destination


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"installed": {}}

    try:
        data = json.loads(STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {"installed": {}}

    if not isinstance(data, dict):
        return {"installed": {}}

    data.setdefault("installed", {})
    return data


def save_state(state: dict) -> None:
    STATE_FILE.write_text(
        json.dumps(state, indent=2, sort_keys=True) + "\n"
    )


def discover_patches() -> dict[str, Path]:
    patches = {}

    for path in sorted(PATCH_ROOT.glob("*.py")):
        if path.name.startswith("_"):
            continue

        patches[path.stem] = path

    return patches


def load_patch(name: str):
    patches = discover_patches()

    if name not in patches:
        available = ", ".join(patches) or "none"
        raise RuntimeError(
            f"Unknown patch: {name}. Available patches: {available}"
        )

    path = patches[name]
    module_name = f"homeland_patch_{name}"

    spec = importlib.util.spec_from_file_location(
        module_name,
        path,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load patch: {name}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def list_patches() -> bool:
    heading("Available patches")

    patches = discover_patches()
    state = load_state()
    installed = state["installed"]

    if not patches:
        print("No feature patches found.")
        print(f"Add patch modules to: {PATCH_ROOT}")
        return True

    for name in patches:
        status = "INSTALLED" if name in installed else "available"

        try:
            module = load_patch(name)
            description = getattr(
                module,
                "DESCRIPTION",
                "No description provided.",
            )
        except Exception as error:
            description = f"LOAD ERROR: {error}"

        print(f"{name:<28} {status:<10} {description}")

    return True


def install_patch(name: str) -> bool:
    heading(f"Installing {name}")

    state = load_state()

    if name in state["installed"]:
        print(f"Patch already installed: {name}")
        return True

    module = load_patch(name)

    if not hasattr(module, "install"):
        print("Patch does not define install(project_root).")
        return False

    backup = create_backup(f"before-{name}")

    try:
        result = module.install(PROJECT_ROOT)

        if result is False:
            raise RuntimeError("Patch returned failure.")

        state["installed"][name] = {
            "installed_at": datetime.now().isoformat(timespec="seconds"),
            "backup": str(backup.relative_to(PROJECT_ROOT)),
        }

        save_state(state)
        print(f"Patch installed: {name}")
        return True

    except Exception as error:
        print(f"Install failed: {error}")
        print(f"Backup available at: {backup}")
        return False


def uninstall_patch(name: str) -> bool:
    heading(f"Uninstalling {name}")

    state = load_state()

    if name not in state["installed"]:
        print(f"Patch is not installed: {name}")
        return True

    module = load_patch(name)

    if not hasattr(module, "uninstall"):
        print("Patch does not define uninstall(project_root).")
        return False

    backup = create_backup(f"before-uninstall-{name}")

    try:
        result = module.uninstall(PROJECT_ROOT)

        if result is False:
            raise RuntimeError("Patch returned failure.")

        del state["installed"][name]
        save_state(state)

        print(f"Patch uninstalled: {name}")
        return True

    except Exception as error:
        print(f"Uninstall failed: {error}")
        print(f"Backup available at: {backup}")
        return False


def wait_for_homeland(
    attempts: int = 30,
    delay_seconds: int = 2,
) -> bool:
    heading("Waiting for Homeland")

    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(
                HOMELAND_URL,
                timeout=4,
            ) as response:
                if response.status == 200:
                    print(
                        f"Homeland responded on attempt "
                        f"{attempt}/{attempts}."
                    )
                    return True
        except Exception:
            pass

        print(f"Waiting... {attempt}/{attempts}")
        time.sleep(delay_seconds)

    return False


def verify_homeland() -> bool:
    heading("Verifying Homeland")

    try:
        with urllib.request.urlopen(
            HOMELAND_URL,
            timeout=8,
        ) as response:
            html = response.read().decode(
                "utf-8",
                errors="replace",
            )

        checks = {
            "HTTP status": response.status == 200,
            "Homeland title": "Homeland" in html,
            "Device grid": "device-grid" in html,
            "Main Desktop card": "windows-main-card" in html,
            "Windows Workstation card":
                "windows-workstation-card" in html,
        }

        print(f"Page size: {len(html):,} characters")

        for label, passed in checks.items():
            print(f"{label}: {'OK' if passed else 'MISSING'}")

        return all(checks.values())

    except Exception as error:
        print(f"Verification failed: {error}")
        return False


def rebuild() -> bool:
    if not check_project():
        return False

    create_backup("before-rebuild")

    heading("Rebuilding containers")

    try:
        run(["docker", "compose", "up", "-d", "--build"])
    except subprocess.CalledProcessError:
        run(
            ["docker", "compose", "logs", "--tail=120"],
            check=False,
        )
        return False

    if not wait_for_homeland():
        run(["docker", "compose", "ps"], check=False)
        run(
            ["docker", "compose", "logs", "--tail=120"],
            check=False,
        )
        return False

    return verify_homeland()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Homeland feature and deployment builder."
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    subparsers.add_parser("check")
    subparsers.add_parser("backup")
    subparsers.add_parser("verify")
    subparsers.add_parser("rebuild")
    subparsers.add_parser("list")

    install_parser = subparsers.add_parser("install")
    install_parser.add_argument("feature")

    uninstall_parser = subparsers.add_parser("uninstall")
    uninstall_parser.add_argument("feature")

    args = parser.parse_args()

    try:
        if args.command == "check":
            success = check_project()
        elif args.command == "backup":
            create_backup()
            success = True
        elif args.command == "verify":
            success = verify_homeland()
        elif args.command == "rebuild":
            success = rebuild()
        elif args.command == "list":
            success = list_patches()
        elif args.command == "install":
            success = install_patch(args.feature)
        elif args.command == "uninstall":
            success = uninstall_patch(args.feature)
        else:
            success = False
    except Exception as error:
        print(f"\nError: {error}")
        success = False

    heading("Complete" if success else "Failed")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
