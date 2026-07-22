"""HDK status screen."""
from . import HDK_VERSION
from .manifest import discover
from .registry import Registry
from .ui import footer, show_modules, title

def show_status():
    registry = Registry()
    installed = []
    available = []
    for manifest in discover():
        label = f"{manifest.display_name} ({manifest.version})"
        target = installed if registry.is_installed(manifest.name) else available
        target.append(label)
    title(f"Homeland Development Kit v{HDK_VERSION}")
    print(f"Installed modules : {len(installed)}")
    print(f"Available modules : {len(available)}")
    show_modules(installed, available)
    footer()
    return True
