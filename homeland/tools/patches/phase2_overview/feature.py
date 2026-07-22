from __future__ import annotations

import json
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = PACKAGE_ROOT / "manifest.json"

MARKER = "<!-- HOMELAND GLOBAL OVERVIEW -->"
DEVICE_GRID = '<section class="device-grid">'


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text())


def asset_path(name: str) -> Path:
    manifest = load_manifest()
    relative_path = manifest["files"][name]
    return PACKAGE_ROOT / relative_path


def install(project_root: Path) -> bool:
    dashboard = project_root / "templates" / "dashboard.html"
    html_asset = asset_path("template")

    text = dashboard.read_text()

    if MARKER in text:
        print("Global Overview HTML already exists.")
        return True

    if DEVICE_GRID not in text:
        raise RuntimeError(
            'Could not find <section class="device-grid">.'
        )

    overview_html = html_asset.read_text().strip()

    text = text.replace(
        DEVICE_GRID,
        overview_html + "\n\n" + DEVICE_GRID,
        1,
    )

    dashboard.write_text(text)
    print("Global Overview HTML installed.")
    return True


def uninstall(project_root: Path) -> bool:
    dashboard = project_root / "templates" / "dashboard.html"
    text = dashboard.read_text()

    if MARKER not in text:
        print("Global Overview HTML is not present.")
        return True

    start = text.index(MARKER)
    section_start = text.index("<section", start)

    depth = 0
    position = section_start

    while position < len(text):
        next_open = text.find("<section", position)
        next_close = text.find("</section>", position)

        if next_close == -1:
            raise RuntimeError(
                "Could not locate the end of Global Overview."
            )

        if next_open != -1 and next_open < next_close:
            depth += 1
            position = next_open + len("<section")
            continue

        depth -= 1
        position = next_close + len("</section>")

        if depth == 0:
            break

    cleaned = text[:start] + text[position:]
    dashboard.write_text(cleaned)

    print("Global Overview HTML removed.")
    return True
