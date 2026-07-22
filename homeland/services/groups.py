from __future__ import annotations

SERVICE_GROUPS = {
    "Immich": [
        "immich_server",
        "immich_postgres",
        "immich_redis",
        "immich_machine_learning",
    ],

    "Monitoring": [
        "prometheus",
        "grafana",
        "cadvisor",
        "node-exporter",
        "snmp-exporter",
    ],
}
