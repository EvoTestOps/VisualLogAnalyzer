from os import getenv

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from dash_app import create_dash_app
from server.api.dash_redirects import dash_redirects_bp
from server.api.routes import analyze_bp

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

db = SQLAlchemy()


def create_app():
    server = Flask(__name__)

    db_url = getenv("DB_URL")
    if not db_url:
        raise ValueError("DB_URL environment variable not set")

    server.config["SQLALCHEMY_DATABASE_URI"] = db_url

    db.init_app(server)

    server.register_blueprint(analyze_bp, url_prefix="/api")
    server.register_blueprint(dash_redirects_bp)

    create_dash_app(server)

    with server.app_context():
        db.create_all()

    return server
