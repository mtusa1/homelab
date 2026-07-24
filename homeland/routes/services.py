from __future__ import annotations

from flask import Blueprint, jsonify, render_template

from services.discovery import discover_services


services_bp = Blueprint("services", __name__)


@services_bp.get("/api/docker")
def docker_api():
    return jsonify(discover_services())


@services_bp.get("/docker")
def docker_page():
    return render_template("docker.html")
