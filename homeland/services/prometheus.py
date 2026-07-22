from __future__ import annotations

import math
import os
from typing import Any

import requests


PROMETHEUS_URL = os.getenv(
    "PROMETHEUS_URL",
    "http://192.168.5.134:9090",
)


def query(expression: str) -> list[dict[str, Any]]:
    """Run an instant Prometheus query and return its result list."""
    try:
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": expression},
            timeout=8,
        )
        response.raise_for_status()

        payload = response.json()
        if payload.get("status") != "success":
            return []

        return payload.get("data", {}).get("result", [])

    except (requests.RequestException, ValueError, TypeError):
        return []


def values(expression: str) -> list[str]:
    """Return only sample values from a Prometheus query."""
    results = query(expression)

    return [
        result["value"][1]
        for result in results
        if isinstance(result.get("value"), list)
        and len(result["value"]) >= 2
    ]


def first_value(expression: str) -> float | None:
    """Return the first sample value as a float."""
    results = query(expression)

    if not results:
        return None

    try:
        return float(results[0]["value"][1])
    except (KeyError, IndexError, TypeError, ValueError):
        return None


def format_bytes(value: float | None) -> str:
    if value is None or not math.isfinite(value):
        return "Unknown"

    gib = value / (1024**3)

    if gib >= 1024:
        return f"{gib / 1024:.1f} TiB"

    return f"{gib:.1f} GiB"


def format_uptime(seconds: float | None) -> str:
    if seconds is None or not math.isfinite(seconds):
        return "Unknown"

    total_seconds = max(0, int(seconds))
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes = remainder // 60

    if days:
        return f"{days}d {hours}h"

    if hours:
        return f"{hours}h {minutes}m"

    return f"{minutes}m"

def query_vector(promql):
    """
    Execute a Prometheus instant vector query and return every result.

    Returns:
        [
            {
                "metric": {...},
                "value": float
            },
            ...
        ]
    """
    import requests

    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": promql},
        timeout=10,
    )

    response.raise_for_status()

    payload = response.json()

    results = []

    for item in payload.get("data", {}).get("result", []):
        try:
            value = float(item["value"][1])
        except Exception:
            value = None

        results.append({
            "metric": item.get("metric", {}),
            "value": value,
        })

    return results
