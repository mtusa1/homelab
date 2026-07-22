from __future__ import annotations

from flask import Flask, jsonify, render_template
from devices.nuc import get_nuc_data
from devices.windows import get_windows_data
from services.discovery import discover_services
from services.overview import build_overview


from devices.synology import (
    get_details as get_synology_details,
    get_disks as get_synology_disks,
    get_storage as get_synology_storage,
    get_summary as get_synology_summary,
)
from services.prometheus import (
    first_value,
    format_bytes,
    format_uptime,
)


app = Flask(__name__)

@app.get("/api/overview")
def overview_api():
    return jsonify(build_overview())

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.get("/")
def dashboard():
    return render_template("dashboard.html")


@app.get("/device/synology")
def synology_page():
    return render_template("synology.html")
@app.get("/nuc")
def nuc():
    data = get_nuc_data()
    return jsonify(data["summary"])

@app.get("/api/device/nuc")
def nuc_device_api():
    return jsonify(get_nuc_data())

@app.get("/device/nuc")
def nuc_page():
    return render_template("nuc.html")

@app.get("/device/windows/<device_id>")
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


@app.get("/api/device/windows/<device_id>")
def windows_api(device_id):
    data = get_windows_data(device_id)

    if data is None:
        return jsonify(error="Unknown device"), 404

    return jsonify(data)


@app.get("/nas/synology")
def synology_status():
    """Existing Homepage-compatible endpoint."""
    return jsonify(get_synology_summary())


@app.get("/api/device/synology")
def synology_details():
    return jsonify(get_synology_details())


@app.get("/api/device/synology/storage")
def synology_storage():
    return jsonify(get_synology_storage())


@app.get("/api/device/synology/disks")
def synology_disks():
    return jsonify(get_synology_disks())

@app.get("/api/docker")
def docker_api():
    return jsonify(discover_services())

@app.get("/docker")
def docker_page():
    return render_template("docker.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8088)
