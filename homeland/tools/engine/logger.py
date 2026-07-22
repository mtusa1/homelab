"""Small dependency-free terminal output helpers."""

import os
import sys


USE_COLOR = (
    sys.stdout.isatty()
    and os.environ.get("NO_COLOR") is None
)


def _paint(code: str, text: str) -> str:
    if not USE_COLOR:
        return text

    return f"\033[{code}m{text}\033[0m"


def heading(text: str) -> None:
    print(_paint("1;36", f"===== {text} ====="))


def success(text: str) -> None:
    print(_paint("32", f"✓ {text}"))


def warning(text: str) -> None:
    print(_paint("33", f"WARNING: {text}"))


def error(text: str) -> None:
    print(_paint("31", f"ERROR: {text}"))


def info(text: str) -> None:
    print(text)
