from __future__ import annotations

from flask import Blueprint, jsonify, render_template

from devices.nuc import get_nuc_data
from devices.synology import (
    get_details as get_synology_details,
    get_disks as get_synology_disks,
    get_storage as get_synology_storage,
    get_summary as get_synology_summary,
)
from devices.windows import get_windows_data


devices_bp = Blueprint("devices", __name__)


@devices_bp.get("/device/synology")
def synology_page():
    return render_template("synology.html")


@devices_bp.get("/nuc")
def nuc():
    data = get_nuc_data()
    return jsonify(data["summary"])


@devices_bp.get("/api/device/nuc")
def nuc_device_api():
    return jsonify(get_nuc_data())


@devices_bp.get("/device/nuc")
def nuc_page():
    return render_template("nuc.html")


@devices_bp.get("/device/windows/<device_id>")
def windows_page(device_id):
    data = get_windows_data(device_id)

    if data is None:
        return "Unknown device", 404

    return render_template(
        "windows.html",
        device_name=data["device"],
        device_description=data["description"],
        device_id=device_id,
    )


@devices_bp.get("/api/device/windows/<device_id>")
def windows_api(device_id):
    data = get_windows_data(device_id)

    if data is None:
        return jsonify(error="Unknown device"), 404

    return jsonify(data)


@devices_bp.get("/nas/synology")
def synology_status():
    """Existing Homepage-compatible endpoint."""
    return jsonify(get_synology_summary())


@devices_bp.get("/api/device/synology")
def synology_details():
    return jsonify(get_synology_details())


@devices_bp.get("/api/device/synology/storage")
def synology_storage():
    return jsonify(get_synology_storage())


@devices_bp.get("/api/device/synology/disks")
def synology_disks():
    return jsonify(get_synology_disks())
