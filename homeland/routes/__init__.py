from __future__ import annotations

from flask import Flask

from routes.api import api_bp
from routes.dashboard import dashboard_bp
from routes.devices import devices_bp
from routes.services import services_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(services_bp)
