"""Simple Homeland terminal interface."""

from .logger import heading


WIDTH = 60


def line():
    print("─" * WIDTH)


def title(text):
    line()
    heading(text.center(WIDTH))
    line()


def section(text):
    print()
    print(text)
    print("-" * len(text))


def show_modules(installed, available):
    section("Installed Modules")

    if not installed:
        print("  (none)")
    else:
        for module in installed:
            print(f"  ✓ {module}")

    section("Available Modules")

    if not available:
        print("  (none)")
    else:
        for module in available:
            print(f"  ○ {module}")


def footer():
    print()
    line()
    print("[L]ist  [I]nstall  [U]ninstall  [V]erify  [Q]uit")
    line()
