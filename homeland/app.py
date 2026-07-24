from __future__ import annotations

from flask import Flask, jsonify, render_template

from routes import register_blueprints
from services.discovery import discover_services


def create_app() -> Flask:
    app = Flask(__name__)
    register_blueprints(app)

    @app.get("/api/docker")
    def docker_api():
        return jsonify(discover_services())

    @app.get("/docker")
    def docker_page():
        return render_template("docker.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8088)
