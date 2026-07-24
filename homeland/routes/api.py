from __future__ import annotations

from flask import Blueprint, jsonify

from services.overview import build_overview


api_bp = Blueprint("api", __name__)


@api_bp.get("/api/overview")
def overview_api():
    return jsonify(build_overview())


@api_bp.get("/health")
def health():
    return jsonify(status="ok")
